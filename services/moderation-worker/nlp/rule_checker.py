"""
Layer B: Enhanced Rule-Based / Lexicon Check
=============================================

Fast, cheap, and catches obvious violations with certainty.
This is the "guardrail" layer that:
1. Catches profanity + obfuscated variants
2. Reduces load on ML model
3. Never lets obvious toxicity slip through

Key improvements:
- Uses multiple text versions from Layer A
- Adds HARASSMENT/BODY-SHAMING patterns (non-profane but harmful)
- Adds HATE SPEECH patterns for racial discrimination
- Context-aware flagging (only flag insults when targeting a person)

Version: 2.0.0
Last Updated: 2026-01-30
"""

import re
from typing import Dict, List, Tuple, Optional, Set, Any
import logging

logger = logging.getLogger(__name__)


# ==================== STEM-BASED TOXIC PATTERNS ====================
# Using regex stems to catch variations

# Core profanity stems (Vietnamese)
PROFANITY_STEMS = {
    # ĐỤ/ĐỊT family
    'dit': {
        'patterns': [
            r'\bđ[ịiìíỉĩ]t\b',
            r'\bd[ịiìíỉĩ]t\b',
            r'\bdjt\b',
            r'\bđjt\b',
            r'\bd1t\b',
            r'\bđ1t\b',
            r'\bd!t\b',
            r'\bđ!t\b',
            # địt mẹ/má patterns
            r'\bđ[ịiìíỉĩ]t\s+m[ẹeèéẻẽẹ]',  # địt mẹ
            r'\bđ[ịiìíỉĩ]t\s+m[áaàảãạ]',   # địt má
        ],
        'stripped_pattern': r'\bdit\b',  # For no-diacritics version
        'severity': 'severe',
        'labels': ['toxicity', 'profanity'],
    },
    
    # ĐM/DCM family  
    'dm': {
        'patterns': [
            r'\bđm+\b',
            r'\bdm+\b',
            r'\bđcm+\b',
            r'\bdcm+\b',
            r'\bđkm+\b',
            r'\bdkm+\b',
            r'\bđ[ụu]\s*m[áaẹe]',  # đụ má, đụ mẹ
            r'\bd[ịi]t\s*m[áaẹe]', # địt má, địt mẹ
        ],
        'stripped_pattern': r'\bdm+\b',
        'severity': 'severe',
        'labels': ['toxicity', 'profanity'],
    },
    
    # LỒN family
    'lon': {
        'patterns': [
            r'\bl[ồôoòóỏõọ]n\b',
            r'\bl0n\b',
            r'\b1on\b',
            r'\b10n\b',
        ],
        'stripped_pattern': r'\blon\b',
        'severity': 'severe',
        'labels': ['toxicity', 'profanity'],
        # Safe contexts where "lon" is OK
        'safe_contexts': [
            'lon bia', 'bia lon', 'lon nước', 'nước lon',
            'lon coca', 'lon pepsi', 'lon 7up', 'lon redbull',
            'hài lòng', 'vui lòng', 'lòng tin', 'lòng tốt',
            'tấm lòng', 'toàn lòng', 'xin lòng',
        ],
    },
    
    # CẶC family
    'cac': {
        'patterns': [
            r'\bc[ặăắằẳẵạa]c\b',
            r'\bc@c\b',
            r'\bc4c\b',
            r'\bkac\b',
            r'\bk[ặăa]c\b',
        ],
        'stripped_pattern': r'\bcac\b',
        'severity': 'severe',
        'labels': ['toxicity', 'profanity'],
        'safe_contexts': [
            'các bạn', 'các anh', 'các chị', 'các em', 'các bác',
            'các ông', 'các bà', 'các cháu', 'các con',
            'một cách', 'bằng cách', 'theo cách', 'có cách',
            'các loại', 'các kiểu', 'các dạng',
        ],
    },
    
    # VCL/VL family
    'vcl': {
        'patterns': [
            r'\bvcl\b',
            r'\bvkl\b',
            r'\bvl\b',
            r'\bvãi\s*l[ồôo]n',
            r'\bvai\s*lon\b',
            r'\bvờ\s*cờ\s*lờ\b',
        ],
        'stripped_pattern': r'\b(vcl|vkl|vl)\b',
        'severity': 'severe',
        'labels': ['toxicity', 'profanity'],
    },
    
    # CC family (con/cái cặc)
    'cc': {
        'patterns': [
            r'\bcc\b',
            r'\bcờ\s*cờ\b',
        ],
        'stripped_pattern': r'\bcc\b',
        'severity': 'moderate',
        'labels': ['toxicity', 'profanity'],
    },
    
    # CLM/CTM family
    'clm': {
        'patterns': [
            r'\bclm\b',
            r'\bctm\b',
            r'\bcmm\b',
        ],
        'stripped_pattern': r'\b(clm|ctm|cmm)\b',
        'severity': 'severe',
        'labels': ['toxicity', 'profanity'],
    },
    
    # NGU family (context-dependent)
    'ngu': {
        'patterns': [
            r'\bngu\s+(như|thế|thí|vậy|quá|vãi|vcl|vl|vkl)',
            r'\bngu\s+ngốc\b',
            r'\bngu\s+si\b',
            r'\bngu\s+xuẩn\b',
        ],
        'stripped_pattern': r'\bngu\s+(nhu|the|thi|vay|qua|ngoc|si|xuan)\b',
        'severity': 'moderate',
        'labels': ['insult'],
        'safe_contexts': [
            'ngủ', 'nguồn', 'người', 'nguyên', 'nguyễn',
            'nguội', 'ngước', 'ngựa', 'ngứa', 'ngư dân',
        ],
        'context_required': True,  # Must match full pattern, not just "ngu"
    },
    
    # Brain/Head insults (standalone patterns)
    'brain_insults': {
        'patterns': [
            r'\bnão\s+(lợn|chó|bò|gà|cá\s*vàng|gối|đất)\b',
            r'\bóc\s+(lợn|chó|bò|gà|cá\s*vàng|gối|đất|chim)\b',
            r'\bđầu\s+(lợn|chó|bò|gà|gối|đất|bò|cá)\b',
        ],
        'severity': 'moderate',
        'labels': ['insult'],
    },
    
    # Standalone insults (only flag when obfuscated)
    'obfuscated_insults': {
        'patterns': [
            # These are flagged ONLY when obfuscation is detected
            # Normal "ngu" standalone is not flagged
            # But "n.g.u" or "n-g-u" signals intentional bypass
        ],
        'standalone_words': ['ngu', 'ngốc', 'điên', 'khùng', 'dở'],  # Special handling
        'severity': 'moderate',
        'labels': ['insult', 'obfuscation_bypass'],
        'only_when_obfuscated': True,  # Key flag
    },
}


# ==================== HARASSMENT / BODY-SHAMING ====================
# These are NOT profane but still harmful when targeting a person

HARASSMENT_PATTERNS = {
    # Body-shaming / Appearance attacks
    'appearance_attack': {
        'patterns': [
            # Direct insults about appearance
            r'\b(mày|mi|nó|đứa\s*này|thằng\s*này|con\s*này)\s+(xấu|xí|bẩn|ghê|kinh|tởm|gớm)',
            r'\b(mặt|da|người|thân|body)\s+(mày|mi|nó)\s+(xấu|bẩn|ghê|kinh)',
            r'\b(xấu|xí|bẩn|ghê|kinh|tởm)\s+(quá|thế|vậy|quá\s*trời|vãi)',
            
            # "nhìn mặt mày... muốn nôn" pattern
            r'\bnhìn\s+(mặt|mày|mi|nó).*?(muốn\s*nôn|ghê\s*tởm|kinh\s*tởm|ớn|ghét)',
            
            # "mày/mi xấu..." direct attack
            r'\b(sao\s+)?(mày|mi|nó)\s+(xấu|xí|bẩn|hôi|thối|dơ)',
        ],
        'severity': 'moderate',
        'labels': ['harassment', 'body_shaming'],
        'requires_target': True,  # Must target a person (mày/mi/nó)
    },
    
    # Personal attack indicators
    'personal_attack': {
        'patterns': [
            # "đồ X" pattern (đồ ngu, đồ khốn, đồ chó...)
            r'\bđồ\s+(ngu|ngốc|khốn|chó|lợn|bò|súc\s*vật|rác|vô\s*dụng|hèn)',
            
            # "thằng/con X" pattern
            r'\b(thằng|con)\s+(ngu|ngốc|khốn|chó|lợn|điên|khùng|rồ|dở)',
            
            # "thằng/con này ngu" pattern
            r'\b(thằng|con)\s+(này|đó|kia)\s+(ngu|ngốc|khốn|điên)',
            
            # "mày là đồ X"
            r'\b(mày|mi|nó)\s+(là\s+)?(đồ|thằng|con)\s+(ngu|ngốc|khốn|chó)',
        ],
        'severity': 'moderate',
        'labels': ['harassment', 'insult'],
        'requires_target': False,  # These patterns inherently indicate targeting
    },
    
    # Contempt expressions
    'contempt': {
        'patterns': [
            r'\b(ghét|khinh|tởm|gớm|ớn|chán)\s+(mày|mi|nó|bọn\s*này)',
            r'\b(mày|mi|nó).*?(đáng\s*khinh|đáng\s*ghét|đáng\s*chết)',
            r'\b(vô\s*dụng|vô\s*giá\s*trị|không\s*ra\s*gì)\s*$',
        ],
        'severity': 'moderate',
        'labels': ['harassment'],
        'requires_target': True,
    },
}


# ==================== HATE SPEECH PATTERNS ====================
# Discrimination based on race, ethnicity, nationality

HATE_SPEECH_PATTERNS = {
    # Racial discrimination
    'racism': {
        'patterns': [
            # Anti-black
            r'\b(bọn|lũ|đám|thằng|con)\s*(da\s*đen|đen|mọi)\b',
            r'\b(da\s*đen|người\s*đen).*?(bẩn|thối|xấu|ghê|cút|về\s*nước)',
            r'\b(cút|biến|đi\s*chỗ\s*khác|về\s*nước).*?(da\s*đen|đen)',
            r'\bkhỉ\s*đen\b',
            r'\bmọi\s*đen\b',
            
            # Anti-Chinese
            r'\b(bọn|lũ|đám|thằng)\s*tàu\s*(khựa|cộng|giặc)?\b',
            r'\btàu\s*(khựa|cộng|giặc)\b',
            r'\b(chink|ching\s*chong)\b',
            
            # Anti-minority
            r'\b(bọn|lũ|đám)\s*(mọi|thổ\s*dân|rừng\s*núi)\b',
            r'\b(dân\s*tộc|miền\s*núi).*?(ngu|dốt|lạc\s*hậu|bẩn)',
        ],
        'severity': 'severe',
        'labels': ['hate', 'racism'],
    },
    
    # LGBTQ+ discrimination
    'lgbtq_hate': {
        'patterns': [
            r'\b(đồ|thằng|con|bọn)\s*(gay|đồng\s*tính|pê\s*đê|bê\s*đê|les)',
            r'\b(gay|đồng\s*tính).*?(bệnh|đáng\s*chết|tởm|ghê|kinh)',
            r'\b(tiêu\s*diệt|giết|đánh)\s*(gay|đồng\s*tính|pê\s*đê)',
        ],
        'severity': 'severe',
        'labels': ['hate', 'lgbtq_discrimination'],
    },
    
    # Xenophobia
    'xenophobia': {
        'patterns': [
            r'\b(cút|biến|đi|về)\s*(về\s*nước|đi\s*chỗ\s*khác|khỏi\s*đây)',
            r'\b(ngoại\s*quốc|người\s*nước\s*ngoài|dân\s*nhập\s*cư).*?(cút|biến|về|bẩn)',
            # "biến đi (người nước ngoài/ngoại quốc)"
            r'\b(biến|cút)\s+(đi\s+)?(người\s*nước\s*ngoài|ngoại\s*quốc|dân\s*nhập\s*cư)',
        ],
        'severity': 'moderate',
        'labels': ['hate', 'xenophobia'],
        # NOTE: Removed additional_context - these patterns are already specific
    },
}


# ==================== PERSONAL PRONOUNS (targeting indicators) ====================

PERSONAL_ATTACK_INDICATORS = {
    # Second person pronouns (targeting someone)
    'target_pronouns': ['mày', 'mi', 'ngươi', 'bay', 'chúng mày', 'tụi mày', 'bọn mày'],
    
    # Third person (talking about someone)
    'third_person': ['nó', 'thằng này', 'con này', 'đứa này', 'thằng kia', 'con kia'],
    
    # First person (speaker)
    'speaker_pronouns': ['tao', 'tau', 'tui', 'tớ'],
}


# ==================== SAFE WORDS / WHITELIST ====================

# Words that should never trigger detection even if containing toxic substrings
GLOBAL_SAFE_WORDS = {
    # Common Vietnamese words
    'các', 'cách', 'cục', 'lon', 'lòng', 'người', 'những', 'nguồn', 'ngủ',
    'nguyên', 'nguyễn', 'duyên', 'duyệt', 'du lịch', 'du học', 'giáo dục',
    'sử dụng', 'ứng dụng', 'dự án', 'dữ liệu',
    
    # Product review context
    'sản phẩm', 'dịch vụ', 'chất lượng', 'giao hàng', 'đóng gói',
    'shop', 'cửa hàng', 'đánh giá', 'review',
    
    # Edit/Credit/Reddit
    'edit', 'credit', 'reddit', 'editor',
}


# ==================== MAIN CHECKER CLASS ====================

class EnhancedRuleChecker:
    """
    Enhanced rule-based / lexicon checker (Layer B)
    
    Uses multiple text versions from Layer A for comprehensive detection.
    """
    
    def __init__(self):
        # Compile all patterns
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for performance"""
        self.compiled_profanity = {}
        for key, info in PROFANITY_STEMS.items():
            self.compiled_profanity[key] = {
                'patterns': [re.compile(p, re.IGNORECASE | re.UNICODE) for p in info['patterns']],
                'stripped': re.compile(info['stripped_pattern'], re.IGNORECASE) if 'stripped_pattern' in info else None,
                'info': info,
            }
        
        self.compiled_harassment = {}
        for key, info in HARASSMENT_PATTERNS.items():
            self.compiled_harassment[key] = {
                'patterns': [re.compile(p, re.IGNORECASE | re.UNICODE) for p in info['patterns']],
                'info': info,
            }
        
        self.compiled_hate = {}
        for key, info in HATE_SPEECH_PATTERNS.items():
            self.compiled_hate[key] = {
                'patterns': [re.compile(p, re.IGNORECASE | re.UNICODE) for p in info['patterns']],
                'info': info,
            }
    
    def _has_target_pronoun(self, text: str) -> bool:
        """Check if text contains pronouns indicating target (mày/mi/nó...)"""
        text_lower = text.lower()
        
        for pronoun in PERSONAL_ATTACK_INDICATORS['target_pronouns']:
            if pronoun in text_lower:
                return True
        
        for pronoun in PERSONAL_ATTACK_INDICATORS['third_person']:
            if pronoun in text_lower:
                return True
        
        return False
    
    def _is_in_safe_context(self, text: str, word: str, safe_contexts: List[str]) -> bool:
        """Check if word appears in a safe context"""
        text_lower = text.lower()
        
        for context in safe_contexts:
            if context in text_lower:
                return True
        
        return False
    
    def _check_profanity(self, text: str, text_no_diacritics: str) -> List[Dict]:
        """Check for profanity patterns"""
        findings = []
        text_lower = text.lower()
        
        for key, compiled in self.compiled_profanity.items():
            info = compiled['info']
            
            # Check safe contexts
            safe_contexts = info.get('safe_contexts', [])
            if safe_contexts and self._is_in_safe_context(text, key, safe_contexts):
                continue
            
            # Check if context required (like "ngu" needs full pattern)
            if info.get('context_required'):
                # Only match full patterns, not standalone
                for pattern in compiled['patterns']:
                    match = pattern.search(text_lower)
                    if match:
                        findings.append({
                            'type': 'profanity',
                            'key': key,
                            'matched': match.group(),
                            'severity': info['severity'],
                            'labels': info['labels'],
                        })
                        break
            else:
                # Check main patterns
                for pattern in compiled['patterns']:
                    match = pattern.search(text_lower)
                    if match:
                        findings.append({
                            'type': 'profanity',
                            'key': key,
                            'matched': match.group(),
                            'severity': info['severity'],
                            'labels': info['labels'],
                        })
                        break
                
                # Also check stripped pattern on no-diacritics version
                if not findings or findings[-1]['key'] != key:
                    if compiled['stripped']:
                        match = compiled['stripped'].search(text_no_diacritics)
                        if match:
                            # Double-check not in safe context
                            if not self._is_in_safe_context(text, key, safe_contexts):
                                findings.append({
                                    'type': 'profanity',
                                    'key': key,
                                    'matched': match.group(),
                                    'severity': info['severity'],
                                    'labels': info['labels'],
                                    'from_stripped': True,
                                })
        
        return findings
    
    def _check_harassment(self, text: str) -> List[Dict]:
        """Check for harassment/body-shaming patterns"""
        findings = []
        text_lower = text.lower()
        
        for key, compiled in self.compiled_harassment.items():
            info = compiled['info']
            
            # Check if requires target
            if info.get('requires_target') and not self._has_target_pronoun(text):
                continue
            
            for pattern in compiled['patterns']:
                match = pattern.search(text_lower)
                if match:
                    findings.append({
                        'type': 'harassment',
                        'key': key,
                        'matched': match.group(),
                        'severity': info['severity'],
                        'labels': info['labels'],
                    })
                    break
        
        return findings
    
    def _check_hate_speech(self, text: str) -> List[Dict]:
        """Check for hate speech patterns"""
        findings = []
        text_lower = text.lower()
        
        for key, compiled in self.compiled_hate.items():
            info = compiled['info']
            
            # Check additional context requirement
            additional_context = info.get('additional_context', [])
            if additional_context:
                has_context = any(ctx in text_lower for ctx in additional_context)
                if not has_context:
                    continue
            
            for pattern in compiled['patterns']:
                match = pattern.search(text_lower)
                if match:
                    findings.append({
                        'type': 'hate_speech',
                        'key': key,
                        'matched': match.group(),
                        'severity': info['severity'],
                        'labels': info['labels'],
                    })
                    break
        
        return findings
    
    def check(
        self, 
        text: str, 
        normalized_text: str = None, 
        no_diacritics_text: str = None,
        metadata: Dict = None
    ) -> Optional[Dict[str, Any]]:
        """
        Main check method.
        
        Args:
            text: Original text
            normalized_text: Fully normalized text from Layer A
            no_diacritics_text: Text with Vietnamese diacritics removed
            metadata: Normalization metadata from Layer A
        
        Returns:
            Result dict if violation found, None if clean
        """
        # Use original if normalized not provided
        if normalized_text is None:
            normalized_text = text.lower()
        if no_diacritics_text is None:
            no_diacritics_text = text.lower()
        
        all_findings = []
        
        # Check all categories
        profanity = self._check_profanity(normalized_text, no_diacritics_text)
        all_findings.extend(profanity)
        
        harassment = self._check_harassment(text)  # Use original for pronoun checking
        all_findings.extend(harassment)
        
        hate = self._check_hate_speech(text)  # Use original for full context
        all_findings.extend(hate)
        
        # Special check: obfuscated insults
        # If obfuscation was detected and normalized text contains insult words,
        # this indicates intentional bypass attempt
        if metadata and metadata.get('has_obfuscation'):
            obfuscated_insults_info = PROFANITY_STEMS.get('obfuscated_insults', {})
            standalone_words = obfuscated_insults_info.get('standalone_words', [])
            
            for word in standalone_words:
                # Check if normalized text contains this word as standalone
                if re.search(rf'\b{word}\b', normalized_text, re.IGNORECASE):
                    # Check if original text didn't contain it (meaning it was obfuscated)
                    if not re.search(rf'\b{word}\b', text.lower(), re.IGNORECASE):
                        all_findings.append({
                            'type': 'obfuscated_insult',
                            'key': 'obfuscated_insults',
                            'matched': word,
                            'severity': 'moderate',
                            'labels': ['insult', 'obfuscation_bypass'],
                        })
                        break
        
        if not all_findings:
            return None
        
        # Determine overall severity and action
        has_severe = any(f['severity'] == 'severe' for f in all_findings)
        has_hate = any(f['type'] == 'hate_speech' for f in all_findings)
        has_harassment = any(f['type'] == 'harassment' for f in all_findings)
        has_body_shaming = 'body_shaming' in [l for f in all_findings for l in f.get('labels', [])]
        
        # NEW: Escalation logic for body-shaming
        # Escalate to reject if severe expressions are used
        escalate_body_shaming = False
        if has_body_shaming or has_harassment:
            text_lower = text.lower() if 'text' in dir() else normalized_text
            severe_expressions = [
                'muốn nôn', 'ghê tởm', 'kinh tởm', 'kinh khủng', 'ghê ghớm',
                'đáng chết', 'chết đi', 'biến đi', 'cút đi',
                'xấu kinh', 'xấu ghê', 'xấu tởm', 'xấu khủng',
                'béo như lợn', 'gầy như que', 'đen như than',
                'mặt như l*', 'mặt l*', 'mặt như đít',
            ]
            for expr in severe_expressions:
                if expr in text_lower:
                    escalate_body_shaming = True
                    break
        
        # Collect all labels
        all_labels = set()
        for f in all_findings:
            all_labels.update(f['labels'])
        
        # Determine action
        if has_hate or has_severe or escalate_body_shaming:
            action = 'reject'
            confidence = 0.95
        else:
            action = 'review'
            confidence = 0.80
        
        # Build reasoning
        matched_items = [f['matched'] for f in all_findings[:3]]
        types = set(f['type'] for f in all_findings)
        
        reasoning_parts = []
        if 'hate_speech' in types:
            reasoning_parts.append('🚫 HATE SPEECH')
        if 'harassment' in types or 'obfuscated_insult' in types:
            if escalate_body_shaming:
                reasoning_parts.append('🚫 SEVERE HARASSMENT')
            else:
                reasoning_parts.append('⚠️ HARASSMENT')
        if 'profanity' in types:
            reasoning_parts.append('⚠️ PROFANITY')
        
        reasoning = f"{', '.join(reasoning_parts)}: {', '.join(matched_items)}"
        
        # Add obfuscation note if detected
        if metadata and metadata.get('has_obfuscation'):
            reasoning += f" (obfuscation: {', '.join(metadata['obfuscation_types'])})"
        
        return {
            'action': action,
            'labels': list(all_labels),
            'confidence': confidence,
            'reasoning': reasoning,
            'findings': all_findings,
            'method': 'rule_based_enhanced',
            'has_obfuscation': metadata.get('has_obfuscation', False) if metadata else False,
            'escalated': escalate_body_shaming,
        }


# ==================== SINGLETON INSTANCE ====================

_checker_instance = None

def get_rule_checker() -> EnhancedRuleChecker:
    """Get singleton checker instance"""
    global _checker_instance
    if _checker_instance is None:
        _checker_instance = EnhancedRuleChecker()
    return _checker_instance


# ==================== TEST ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    # Import normalizer
    try:
        from text_normalizer import get_normalizer
    except ImportError:
        from nlp.text_normalizer import get_normalizer
    
    normalizer = get_normalizer()
    checker = get_rule_checker()
    
    test_cases = [
        # Profanity
        "đm mày",
        "vcl",
        "dm con chó",
        
        # Obfuscated profanity
        "d.m",
        "đ.m",
        "n.g.u",
        "d:m",
        "d:m,m",
        
        # Harassment / body-shaming (key test cases from screenshots)
        "Sao mày xấu thế, nhìn mặt mày tao muốn nôn",
        "đồ ngu ngốc",
        "thằng này ngu quá",
        
        # Hate speech (key test case from screenshot)
        "Bọn da đen bẩn thỉu cút về nước đi",
        "tàu khựa",
        
        # Safe content
        "Sản phẩm tốt quá",
        "Lon bia này ngon",
        "Các bạn có khỏe không?",
        "Hài lòng với dịch vụ",
        
        # Edge cases
        "Sản phẩm tệ quá, thất vọng",  # Negative but valid feedback
        "Tôi không hài lòng với dịch vụ",  # Valid complaint
    ]
    
    print("=" * 80)
    print("ENHANCED RULE CHECKER TEST")
    print("=" * 80)
    
    for text in test_cases:
        print(f"\n📝 Input: '{text}'")
        
        # Get normalized versions
        versions = normalizer.create_all_versions(text)
        
        # Run checker
        result = checker.check(
            text=text,
            normalized_text=versions['fully_normalized'],
            no_diacritics_text=versions['no_diacritics'],
            metadata=versions['metadata']
        )
        
        if result:
            print(f"   ❌ VIOLATION: {result['reasoning']}")
            print(f"   Action: {result['action']}, Labels: {result['labels']}")
            print(f"   Confidence: {result['confidence']:.2%}")
        else:
            print(f"   ✅ CLEAN")
        
        print("-" * 60)
