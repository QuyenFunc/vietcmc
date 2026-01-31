"""
Advanced Context Analyzer for Vietnamese Content Moderation
- Context-aware classification: distinguish valid negative context vs toxic
- Semantic similarity checking: detect semantic variants
- Intent detection: determine user intent
- Multi-factor scoring: multi-factor evaluation

Version: 1.0.0
Last Updated: 2025-12-19
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ContentIntent(Enum):
    """Classify content intent"""
    FEEDBACK_NEGATIVE = "feedback_negative"  # Negative review of product/service
    FEEDBACK_POSITIVE = "feedback_positive"  # Positive review
    COMPLAINT = "complaint"                  # Complaint/claim
    PERSONAL_ATTACK = "personal_attack"      # Personal attack
    HATE_SPEECH = "hate_speech"              # Hate speech
    SPAM = "spam"                            # Spam/advertising
    NEUTRAL = "neutral"                      # Neutral
    QUESTION = "question"                    # Question


@dataclass
class ContextAnalysisResult:
    """Context analysis result"""
    intent: ContentIntent
    confidence: float
    is_legitimate_criticism: bool
    targets_product: bool
    targets_person: bool
    has_valid_reason: bool
    severity_modifier: float  # 0.0 - 2.0 (< 1.0 = giảm, > 1.0 = tăng)
    reasoning: str


# ==================== CONTEXT INDICATORS ====================

# Words indicating product/service reviews (LEGITIMATE FEEDBACK)
PRODUCT_REVIEW_INDICATORS = [
    # Product quality
    'sản phẩm', 'hàng', 'đồ', 'món', 'sản phẩm này', 'món này', 'đồ này',
    'hàng này', 'order', 'đơn hàng', 'gói hàng',
    
    # Service
    'dịch vụ', 'phục vụ', 'nhân viên', 'shop', 'cửa hàng', 'store',
    'giao hàng', 'ship', 'đóng gói', 'bao bì', 'packaging',
    
    # Price
    'giá', 'tiền', 'chi phí', 'phí', 'giá tiền', 'đắt', 'rẻ', 'đáng tiền',
    'không đáng', 'hời', 'lỗ', 'được giá', 'giá cao', 'giá thấp',
    
    # Quality
    'chất lượng', 'chất liệu', 'vải', 'màu', 'size', 'kích thước',
    'form', 'dáng', 'kiểu', 'mẫu', 'thiết kế', 'design',
    
    # Usage evaluation
    'dùng', 'sử dụng', 'xài', 'mặc', 'đi', 'ăn', 'uống',
    'test', 'thử', 'review', 'đánh giá',
    
    # Comparison
    'khác hình', 'không giống', 'giống hình', 'như hình', 'đúng mô tả',
    'sai mô tả', 'không đúng', 'khác xa',
]

# Words indicating VALID negative feedback about products
LEGITIMATE_NEGATIVE_FEEDBACK = [
    # Disappointment
    'thất vọng', 'hụt hẫng', 'không hài lòng', 'không vừa ý', 'không ưng',
    'không ok', 'không ổn', 'chán', 'tệ', 'dở', 'kém',
    
    # Specific complaints
    'lỗi', 'hỏng', 'rách', 'bể', 'vỡ', 'không hoạt động', 'không chạy',
    'chậm', 'trễ', 'delay', 'giao muộn', 'đợi lâu', 'lâu quá',
    
    # Not worth the money
    'phí tiền', 'tốn tiền', 'mất tiền', 'lãng phí', 'không đáng',
    'đắt vô lý', 'đắt quá', 'chất lượng kém', 'dở', 'tệ hại',
    
    # Recommendation
    'không nên mua', 'đừng mua', 'tránh xa', 'không recommend',
    'one star', '1 sao', 'đánh giá thấp',
    
    # Valid negative emotions
    'bực', 'khổ', 'thất vọng', 'buồn', 'tiếc',
]

# Words indicating PERSONAL ATTACK (needs moderation)
PERSONAL_ATTACK_INDICATORS = [
    # Personal pronouns
    'mày', 'mi', 'mầy', 'tau', 'tao', 'thằng mày', 'con mày',
    'thằng kia', 'con kia', 'đứa kia', 'người kia',
    
    # Disrespectful terms
    'thằng', 'con', 'đứa', 'lũ', 'bọn', 'tụi', 'nhóm',
    'thằng chủ shop', 'thằng shipper', 'con bé', 'thằng cha',
    
    # Direct insults
    'chửi mày', 'đánh mày', 'giết mày', 'chém mày',
    'biến đi', 'cút đi', 'get lost',
]

# Words indicating HATE SPEECH (reject immediately)
HATE_SPEECH_GROUP_INDICATORS = [
    # LGBTQ+ groups
    'gay', 'les', 'đồng tính', 'pê đê', 'bê đê', 'chuyển giới',
    
    # Ethnic groups
    'tàu', 'khựa', 'mọi', 'mường', 'thổ dân', 'miền núi',
    
    # Religious groups
    'phật tử', 'công giáo', 'hồi giáo', 'tín đồ',
]

# Words showing contempt/hatred towards groups
HATRED_MODIFIERS = [
    'ghét', 'khinh', 'chết đi', 'nên chết', 'biến đi', 'tiêu diệt',
    'diệt', 'bẩn', 'dơ', 'tởm', 'kinh tởm', 'đáng ghét', 'đáng khinh',
    'bệnh hoạn', 'biến thái', 'điên', 'khùng', 'mất dạy', 'vô văn hóa',
]

# Spam keywords
SPAM_KEYWORDS = [
    'inbox', 'zalo', 'liên hệ', 'hotline', 'sdt', 'số điện thoại',
    'click', 'mua ngay', 'đặt hàng ngay', 'khuyến mãi', 'sale',
    'giảm giá', 'free', 'miễn phí', 'link', 'http', 'www',
    'tặng', 'nhận ngay', 'cơ hội', 'duy nhất', 'có hạn',
]

# ==================== ALLOWED CONTEXT PATTERNS ====================

# Context reducing severity
SEVERITY_REDUCING_CONTEXTS = [
    # Negation
    (r'\b(?:không|chẳng|chả|đâu có|đâu|hông|ko|k)\b', 0.5),
    
    # Joking
    (r'\b(?:đùa thôi|đùa mà|joke|kidding|vui thôi|nói đùa|đùa)\b', 0.3),
    
    # Self-reference
    (r'\b(?:tôi|mình|em|t)\s+(?:ngu|dốt|kém)\b', 0.2),
    
    # Quote
    (r'["\'].*?["\']', 0.4),
    
    # Assumption
    (r'\b(?:nếu|giả sử|ví dụ|imagine)\b', 0.5),
]

# Context increasing severity
SEVERITY_INCREASING_CONTEXTS = [
    # Threat
    (r'\b(?:tao|tau)\s+(?:sẽ|sẽ|phải)\b', 1.5),
    
    # Repeated insults
    (r'(?:vcl|vl|đm|dm|cc)\s*(?:vcl|vl|đm|dm|cc)', 1.8),
    
    # Targeting a group
    (r'\b(?:bọn|lũ|tụi|nhóm)\s+\w+', 1.5),
    
    # Call for violence
    (r'\b(?:giết|chém|đánh|đập)\s+(?:hết|sạch|tất cả)', 2.0),
]


# ==================== SAFE WORD PATTERNS ====================

# SAFE words/phrases despite containing toxic substrings
SAFE_WORD_PATTERNS = {
    # "gay" in positive context
    'gay': [
        r'\bhứng\s+gay\b',          # hứng gay = high interest
        r'\bvui\s+gay\b',           # vui gay = joyful
        r'\bgay\s+gắt\b',           # gay gắt = intense
        r'\bnóng\s+gay\b',          # nóng gay = burning hot
        r'\bgay\s+go\b',            # gay go = difficult
    ],
    
    # "cac" / "các" in normal context
    'cac': [
        r'\bcác\s+(?:bạn|anh|chị|em|ông|bà|sản phẩm|dịch vụ|loại|nhà)\b',
        r'\bcác\s+(?:bác|cô|chú|thầy|cô|giáo)\b',
        r'\bmột\s+cách\b',
        r'\bbằng\s+cách\b',
        r'\btheo\s+cách\b',
    ],
    
    # "lon" in normal context
    'lon': [
        r'\b(?:hài|vui|xin|làm ơn|làm)\s+lòng\b',  # hài lòng, vui lòng
        r'\b(?:bia|nước|coca|pepsi|7up|lon\s+nước)\s+lon\b',  # lon bia
        r'\blon\s+(?:bia|nước|coca|pepsi)\b',
    ],
    
    # "dit" in other context
    'dit': [
        r'\bedit\b',                # edit
        r'\bcredit\b',              # credit
        r'\breadit\b',              # reddit
    ],
    
    # "du" in other context
    'du': [
        r'\bdu\s+lịch\b',           # travel
        r'\bdu\s+học\b',            # study abroad
        r'\bdu\s+khách\b',          # tourist
        r'\bdu\s+xuân\b',           # spring travel
        r'\bhướng\s+dẫn\s+du\b',    # tour guide
    ],
}


class ContextAnalyzer:
    """
    Advanced context analysis to determine intent and severity
    """
    
    def __init__(self):
        self.safe_patterns = self._compile_safe_patterns()
        self.reducing_patterns = [(re.compile(p, re.IGNORECASE), m) for p, m in SEVERITY_REDUCING_CONTEXTS]
        self.increasing_patterns = [(re.compile(p, re.IGNORECASE), m) for p, m in SEVERITY_INCREASING_CONTEXTS]
    
    def _compile_safe_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile các pattern an toàn"""
        compiled = {}
        for word, patterns in SAFE_WORD_PATTERNS.items():
            compiled[word] = [re.compile(p, re.IGNORECASE) for p in patterns]
        return compiled
    
    def is_safe_context(self, text: str, flagged_word: str) -> bool:
        """
        Check if the flagged word is in a safe context
        
        Args:
            text: Văn bản gốc
            flagged_word: Từ bị flag là toxic
            
        Returns:
            True nếu từ nằm trong ngữ cảnh an toàn
        """
        text_lower = text.lower()
        
        # Check safe patterns cho từ cụ thể
        for word_key, patterns in self.safe_patterns.items():
            if word_key in flagged_word.lower():
                for pattern in patterns:
                    if pattern.search(text_lower):
                        logger.debug(f"Safe context detected for '{flagged_word}' in: {text[:50]}...")
                        return True
        
        return False
    
    def detect_intent(self, text: str) -> ContentIntent:
        """
        Determine content intent
        
        Args:
            text: Văn bản cần phân tích
            
        Returns:
            ContentIntent enum
        """
        text_lower = text.lower()
        
        # Check câu hỏi
        if any(q in text_lower for q in ['?', 'làm sao', 'như thế nào', 'ở đâu', 'bao nhiêu', 'khi nào', 'ai', 'cái gì']):
            return ContentIntent.QUESTION
        
        # Check spam
        spam_count = sum(1 for kw in SPAM_KEYWORDS if kw in text_lower)
        if spam_count >= 3:
            return ContentIntent.SPAM
        
        # Check hate speech
        has_group = any(grp in text_lower for grp in HATE_SPEECH_GROUP_INDICATORS)
        has_hatred = any(mod in text_lower for mod in HATRED_MODIFIERS)
        if has_group and has_hatred:
            return ContentIntent.HATE_SPEECH
        
        # Check personal attack
        personal_count = sum(1 for ind in PERSONAL_ATTACK_INDICATORS if ind in text_lower)
        if personal_count >= 2:
            return ContentIntent.PERSONAL_ATTACK
        
        # Check product review (negative or positive)
        product_count = sum(1 for ind in PRODUCT_REVIEW_INDICATORS if ind in text_lower)
        negative_count = sum(1 for fb in LEGITIMATE_NEGATIVE_FEEDBACK if fb in text_lower)
        
        if product_count >= 1:
            if negative_count >= 1:
                return ContentIntent.FEEDBACK_NEGATIVE
            # Check positive indicators
            positive_words = ['tốt', 'đẹp', 'ok', 'ổn', 'hài lòng', 'thích', 'recommend', 'ưng', 'chất lượng']
            if any(pw in text_lower for pw in positive_words):
                return ContentIntent.FEEDBACK_POSITIVE
            return ContentIntent.COMPLAINT
        
        return ContentIntent.NEUTRAL
    
    def analyze_target(self, text: str) -> Tuple[bool, bool]:
        """
        Analyze targeted objects
        
        Returns:
            (targets_product, targets_person)
        """
        text_lower = text.lower()
        
        # Check targets product
        targets_product = any(ind in text_lower for ind in PRODUCT_REVIEW_INDICATORS)
        
        # Check targets person
        targets_person = any(ind in text_lower for ind in PERSONAL_ATTACK_INDICATORS)
        
        return targets_product, targets_person
    
    def calculate_severity_modifier(self, text: str) -> float:
        """
        Calculate severity modifier
        
        Returns:
            float: 0.0 - 2.0 
            < 1.0 = giảm mức độ
            > 1.0 = tăng mức độ
        """
        modifier = 1.0
        text_lower = text.lower()
        
        # Apply reducing patterns
        for pattern, reduce_factor in self.reducing_patterns:
            if pattern.search(text_lower):
                modifier *= reduce_factor
        
        # Apply increasing patterns
        for pattern, increase_factor in self.increasing_patterns:
            if pattern.search(text_lower):
                modifier *= increase_factor
        
        # Clamp to range
        return max(0.1, min(2.0, modifier))
    
    def analyze(self, text: str, flagged_words: List[str] = None) -> ContextAnalysisResult:
        """
        Comprehensive context analysis
        
        Args:
            text: Văn bản cần phân tích
            flagged_words: Danh sách từ đã bị flag là toxic
            
        Returns:
            ContextAnalysisResult
        """
        # Detect intent
        intent = self.detect_intent(text)
        
        # Analyze targets
        targets_product, targets_person = self.analyze_target(text)
        
        # Calculate severity modifier
        severity_modifier = self.calculate_severity_modifier(text)
        
        # Check safe context for flagged words
        safe_word_count = 0
        if flagged_words:
            for word in flagged_words:
                if self.is_safe_context(text, word):
                    safe_word_count += 1
            
            # Adjust modifier if many flagged words are in safe context
            if safe_word_count > 0:
                safe_ratio = safe_word_count / len(flagged_words)
                severity_modifier *= (1 - safe_ratio * 0.5)
        
        # Determine if legitimate criticism
        is_legitimate = (
            intent in [ContentIntent.FEEDBACK_NEGATIVE, ContentIntent.COMPLAINT, ContentIntent.QUESTION]
            and targets_product
            and not targets_person
        )
        
        # Has valid reason?
        text_lower = text.lower()
        has_valid_reason = any(fb in text_lower for fb in LEGITIMATE_NEGATIVE_FEEDBACK)
        
        # Calculate confidence
        if intent == ContentIntent.HATE_SPEECH:
            confidence = 0.95
        elif intent == ContentIntent.PERSONAL_ATTACK:
            confidence = 0.85
        elif is_legitimate:
            confidence = 0.8
        else:
            confidence = 0.6
        
        # Build reasoning
        reasoning_parts = []
        reasoning_parts.append(f"Intent: {intent.value}")
        if targets_product:
            reasoning_parts.append("Mentions product/service")
        if targets_person:
            reasoning_parts.append("Targets individual")
        if is_legitimate:
            reasoning_parts.append("Valid feedback/criticism")
        if has_valid_reason:
            reasoning_parts.append("Specific reason provided")
        if safe_word_count > 0:
            reasoning_parts.append(f"{safe_word_count} words in safe context")
        
        return ContextAnalysisResult(
            intent=intent,
            confidence=confidence,
            is_legitimate_criticism=is_legitimate,
            targets_product=targets_product,
            targets_person=targets_person,
            has_valid_reason=has_valid_reason,
            severity_modifier=severity_modifier,
            reasoning=" | ".join(reasoning_parts)
        )


# ==================== SEMANTIC SIMILARITY CHECK ====================

class SemanticChecker:
    """
    Semantic similarity check to detect variants
    Uses simple techniques without external embeddings
    """
    
    # Synonyms of toxic words
    TOXIC_SYNONYMS = {
        # Ngu/dốt variations
        'ngu': ['đần', 'khờ', 'ngốc', 'dốt', 'u mê', 'thiểu năng', 'chậm hiểu', 'kém thông minh'],
        
        # Xấu/tệ variations
        'tệ': ['dở', 'chán', 'kém', 'kém cỏi', 'tồi', 'tồi tệ', 'ghê', 'kinh'],
        
        # Lừa đảo variations
        'lừa': ['lừa đảo', 'lừa gạt', 'gian lận', 'dối trá', 'gian dối', 'bịp bợm', 'lọc lừa'],
        
        # Đe dọa variations
        'giết': ['chém', 'đâm', 'bắn', 'tiêu diệt', 'hủy', 'xử', 'ra tay'],
    }
    
    # Alternative spellings of toxic words
    TOXIC_SPELLINGS = {
        'ngu': ['ngu', 'nguu', 'n.g.u', 'nqu', 'nqư', 'ngư', 'ngù'],
        'dm': ['dm', 'đm', 'd.m', 'đ.m', 'đ m', 'd m', 'đờ mờ', 'do mo'],
        'vcl': ['vcl', 'vkl', 'v.c.l', 'v-c-l', 'vờ cờ lờ', 'vãi lồn'],
        'dit': ['dit', 'địt', 'địt', 'd!t', 'đ!t', 'd1t', 'đ1t'],
    }
    
    def __init__(self):
        # Build reverse map for quick lookup
        self.reverse_synonyms = {}
        for base_word, synonyms in self.TOXIC_SYNONYMS.items():
            for syn in synonyms:
                self.reverse_synonyms[syn.lower()] = base_word
        
        self.reverse_spellings = {}
        for base_word, spellings in self.TOXIC_SPELLINGS.items():
            for sp in spellings:
                self.reverse_spellings[sp.lower()] = base_word
    
    def normalize_spelling(self, text: str) -> Tuple[str, List[str]]:
        """
        Normalize spelling and return normalized words
        
        Returns:
            (normalized_text, list of detected variations)
        """
        text_lower = text.lower()
        detected = []
        
        # Check spellings
        words = text_lower.split()
        normalized_words = []
        
        for word in words:
            # Remove special chars for matching
            clean_word = re.sub(r'[^a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', '', word)
            
            if clean_word in self.reverse_spellings:
                base = self.reverse_spellings[clean_word]
                detected.append(f"{word} -> {base}")
                normalized_words.append(base)
            else:
                normalized_words.append(word)
        
        return ' '.join(normalized_words), detected
    
    def find_synonyms(self, text: str) -> List[str]:
        """
        Find synonyms of toxic words
        
        Returns:
            List of detected toxic synonyms
        """
        text_lower = text.lower()
        detected = []
        
        for word in text_lower.split():
            clean_word = re.sub(r'[^a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', '', word)
            if clean_word in self.reverse_synonyms:
                base = self.reverse_synonyms[clean_word]
                detected.append(f"{word} (~{base})")
        
        return detected
    
    def check(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive semantic check
        
        Returns:
            Dict với thông tin về các biến thể được phát hiện
        """
        normalized, spelling_variations = self.normalize_spelling(text)
        synonyms = self.find_synonyms(text)
        
        return {
            'normalized_text': normalized,
            'spelling_variations': spelling_variations,
            'detected_synonyms': synonyms,
            'has_variations': len(spelling_variations) > 0 or len(synonyms) > 0
        }


# ==================== CONFIDENCE CALIBRATOR ====================

class ConfidenceCalibrator:
    """
    Adjust confidence score based on multiple factors
    """
    
    # Factors affecting confidence
    CONFIDENCE_FACTORS = {
        # Increase confidence
        'has_multiple_toxic_words': 0.15,
        'has_personal_attack': 0.20,
        'has_hate_group_target': 0.25,
        'short_toxic_only': 0.10,  # Short message with only toxic words
        
        # Decrease confidence  
        'is_product_review': -0.20,
        'has_valid_reason': -0.15,
        'is_question': -0.10,
        'long_context': -0.10,  # Long message with clear context
        'has_safe_context': -0.25,
    }
    
    def calibrate(
        self,
        base_confidence: float,
        text: str,
        context_result: ContextAnalysisResult,
        toxic_word_count: int = 0
    ) -> float:
        """
        Adjust confidence score
        
        Args:
            base_confidence: Confidence ban đầu từ model
            text: Văn bản gốc
            context_result: Kết quả phân tích context
            toxic_word_count: Số lượng từ toxic được phát hiện
            
        Returns:
            float: Confidence đã điều chỉnh (0.0 - 1.0)
        """
        adjustment = 0.0
        
        # Tăng confidence
        if toxic_word_count >= 2:
            adjustment += self.CONFIDENCE_FACTORS['has_multiple_toxic_words']
        
        if context_result.targets_person:
            adjustment += self.CONFIDENCE_FACTORS['has_personal_attack']
        
        if context_result.intent == ContentIntent.HATE_SPEECH:
            adjustment += self.CONFIDENCE_FACTORS['has_hate_group_target']
        
        if len(text.split()) <= 5 and toxic_word_count > 0:
            adjustment += self.CONFIDENCE_FACTORS['short_toxic_only']
        
        # Giảm confidence
        if context_result.targets_product:
            adjustment += self.CONFIDENCE_FACTORS['is_product_review']
        
        if context_result.has_valid_reason:
            adjustment += self.CONFIDENCE_FACTORS['has_valid_reason']
        
        if context_result.intent == ContentIntent.QUESTION:
            adjustment += self.CONFIDENCE_FACTORS['is_question']
        
        if len(text.split()) >= 20:
            adjustment += self.CONFIDENCE_FACTORS['long_context']
        
        if context_result.severity_modifier < 0.7:
            adjustment += self.CONFIDENCE_FACTORS['has_safe_context']
        
        # Apply adjustment
        calibrated = base_confidence + adjustment
        
        # Clamp to valid range
        return max(0.0, min(1.0, calibrated))


# ==================== MAIN ENHANCED ANALYZER ====================

class EnhancedModerationAnalyzer:
    """
    Advanced moderation analysis combining all components
    """
    
    def __init__(self):
        self.context_analyzer = ContextAnalyzer()
        self.semantic_checker = SemanticChecker()
        self.confidence_calibrator = ConfidenceCalibrator()
    
    def analyze(
        self,
        text: str,
        flagged_words: List[str] = None,
        base_confidence: float = 0.5
    ) -> Dict[str, Any]:
        """
        Comprehensive text analysis
        
        Args:
            text: Văn bản cần kiểm duyệt
            flagged_words: Danh sách từ đã bị flag
            base_confidence: Confidence ban đầu từ ML model
            
        Returns:
            Dict với kết quả phân tích chi tiết
        """
        if flagged_words is None:
            flagged_words = []
        
        # 1. Context analysis
        context_result = self.context_analyzer.analyze(text, flagged_words)
        
        # 2. Semantic check
        semantic_result = self.semantic_checker.check(text)
        
        # 3. Filter out safe context words
        safe_words = []
        actual_flagged = []
        for word in flagged_words:
            if self.context_analyzer.is_safe_context(text, word):
                safe_words.append(word)
            else:
                actual_flagged.append(word)
        
        # 4. Calibrate confidence
        calibrated_confidence = self.confidence_calibrator.calibrate(
            base_confidence,
            text,
            context_result,
            len(actual_flagged)
        )
        
        # 5. Determine final action
        if context_result.intent == ContentIntent.HATE_SPEECH:
            action = 'reject'
            reasoning = '🚫 HATE SPEECH detected'
        elif context_result.is_legitimate_criticism and len(actual_flagged) == 0:
            action = 'allowed'
            reasoning = '✅ Valid feedback/criticism'
        elif calibrated_confidence >= 0.8 and len(actual_flagged) > 0:
            action = 'reject'
            reasoning = f'⛔ Serious violation: {", ".join(actual_flagged[:3])}'
        elif calibrated_confidence >= 0.5 and len(actual_flagged) > 0:
            action = 'review'
            reasoning = f'⚠️ Review needed: {", ".join(actual_flagged[:3])}'
        else:
            action = 'allowed'
            reasoning = '✅ Acceptable content'
        
        return {
            'action': action,
            'confidence': calibrated_confidence,
            'reasoning': reasoning,
            
            # Context details
            'intent': context_result.intent.value,
            'is_legitimate_criticism': context_result.is_legitimate_criticism,
            'targets_product': context_result.targets_product,
            'targets_person': context_result.targets_person,
            'severity_modifier': context_result.severity_modifier,
            
            # Flagged words details
            'flagged_words': actual_flagged,
            'safe_context_words': safe_words,
            
            # Semantic details
            'semantic_variations': semantic_result.get('spelling_variations', []),
            'detected_synonyms': semantic_result.get('detected_synonyms', []),
            
            # Raw context reasoning
            'context_reasoning': context_result.reasoning
        }


# Singleton instance
_analyzer_instance = None

def get_enhanced_analyzer() -> EnhancedModerationAnalyzer:
    """Get singleton instance of enhanced analyzer"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = EnhancedModerationAnalyzer()
    return _analyzer_instance


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.DEBUG)
    
    analyzer = EnhancedModerationAnalyzer()
    
    test_cases = [
        # Legitimate negative feedback
        "Sản phẩm tệ quá, chất lượng kém, không đáng tiền",
        "Hàng giao chậm, đóng gói không cẩn thận, thất vọng",
        "Shop này dịch vụ kém, không recommend",
        
        # Toxic but product-related
        "Đồ rác vl, shop ngu thật",
        
        # Personal attack
        "Mày ngu thế, thằng này khùng quá",
        
        # Hate speech
        "Bọn gay đáng ghét, nên chết hết",
        
        # Safe context
        "Hài lòng với sản phẩm",
        "Các bạn ơi, sản phẩm này tốt không?",
        "Du lịch vui quá",
        
        # Spam
        "Inbox nhận ngay, zalo 0123456789, giảm giá 50%",
    ]
    
    print("=" * 80)
    print("ENHANCED MODERATION ANALYZER TEST")
    print("=" * 80)
    
    for text in test_cases:
        print(f"\n📝 Text: {text}")
        result = analyzer.analyze(text, flagged_words=[])
        print(f"   Action: {result['action']}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Intent: {result['intent']}")
        print(f"   Reasoning: {result['reasoning']}")
        if result['is_legitimate_criticism']:
            print(f"   ✅ Legitimate criticism")
        print("-" * 60)
