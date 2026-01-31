"""
Advanced Variant Detection for Vietnamese Toxic Content
- Homoglyph detection: detect similar Unicode characters
- Leetspeak normalization: normalize leetspeak
- Insertion attack detection: detect special character insertion
- Pattern-based obfuscation detection: detect complex obfuscation

Version: 1.0.0
Last Updated: 2025-12-19
"""

import re
from typing import Dict, List, Tuple, Set, Any
import unicodedata
import logging

logger = logging.getLogger(__name__)


HOMOGLYPHS = {
    # Latin lookalikes
    'а': 'a',  # Cyrillic
    'е': 'e',  # Cyrillic
    'і': 'i',  # Cyrillic
    'о': 'o',  # Cyrillic
    'р': 'p',  # Cyrillic
    'с': 'c',  # Cyrillic
    'ⅰ': 'i',  # Roman numeral
    'ⅱ': 'ii',
    'ⅲ': 'iii',
    'ⅳ': 'iv',
    'ⅴ': 'v',
    'ⅵ': 'vi',
    'ⅶ': 'vii',
    'ⅷ': 'viii',
    'ⅸ': 'ix',
    'ⅹ': 'x',
    
    # Full-width characters
    'ａ': 'a', 'ｂ': 'b', 'ｃ': 'c', 'ｄ': 'd', 'ｅ': 'e',
    'ｆ': 'f', 'ｇ': 'g', 'ｈ': 'h', 'ｉ': 'i', 'ｊ': 'j',
    'ｋ': 'k', 'ｌ': 'l', 'ｍ': 'm', 'ｎ': 'n', 'ｏ': 'o',
    'ｐ': 'p', 'ｑ': 'q', 'ｒ': 'r', 'ｓ': 's', 'ｔ': 't',
    'ｕ': 'u', 'ｖ': 'v', 'ｗ': 'w', 'ｘ': 'x', 'ｙ': 'y', 'ｚ': 'z',
    
    # Special symbols
    '@': 'a', '4': 'a', '∂': 'a',
    '3': 'e', '€': 'e', 'ë': 'e', 'ê': 'e',
    '1': 'i', '!': 'i', '|': 'i', 'ï': 'i', 'î': 'i',
    '0': 'o', 'ø': 'o', 'ô': 'o', 'ö': 'o',
    '5': 's', '$': 's', 'š': 's',
    '7': 't', '+': 't',
    'ü': 'u', 'û': 'u', 'ú': 'u', 'ù': 'u',
    '¥': 'y', 'ÿ': 'y',
    '2': 'z',
    
    # Vietnamese specific homoglyphs
    'đ': 'd', 'Đ': 'd',
    'ð': 'd',  # Icelandic eth
    
    # Math symbols that look like letters
    '×': 'x',
    '÷': 't',
    '∞': 'oo',
}

# ==================== LEETSPEAK MAPPING ====================

LEETSPEAK_TO_LETTER = {
    # Numbers to letters
    '0': 'o',
    '1': 'i',
    '2': 'z',
    '3': 'e',
    '4': 'a',
    '5': 's',
    '6': 'g',
    '7': 't',
    '8': 'b',
    '9': 'g',
    
    # Symbols
    '@': 'a',
    '!': 'i',
    '$': 's',
    '+': 't',
    '(': 'c',
    ')': 'c',
    '[': 'c',
    ']': 'c',
    '|': 'i',
    '\\': 'l',
    '/': 'l',
    '^': 'a',
    '<': 'c',
    '>': 'c',
    '{': 'c',
    '}': 'c',
    '~': 'n',
    '*': 'x',
    '#': 'h',
    '%': 'x',
    '&': 'and',
}

# ==================== INSERTION PATTERNS ====================
# Patterns for special characters inserted between letters

INSERTION_CHARS = [
    '.', '-', '_', ' ', '*', '~', '^', "'", '"',
    '`', '|', '/', '\\', '+', '=', '#', '@',
    '•', '·', '°', '◦', '○', '●', '◯', '★', '☆',
    '♡', '♥', '❤', '💕', '🔥', '✨', '💯',
]

# ==================== VIETNAMESE TOXIC VARIANTS ====================

# Variants of Vietnamese toxic words
TOXIC_VARIANTS = {
    # ===== ĐỤ/ĐỊT family =====
    'du': {
        'normalized': 'đụ',
        'variants': [
            # ONLY match EXACT obfuscation patterns - DO NOT match standalone 'đụ', 'dụ'
            'đut', 'dut', 'đụt', 'dụt',
            'đ.u', 'd.u', 'đ_u', 'd_u', 'đ-u', 'd-u',
            'đ u', 'd u', 'đ  u', 'd  u',
            'đ*u', 'd*u', 'đ@u', 'd@u',
            # Leetspeak
            'du7', 'd07', 'dv', 'đv',
            # Unicode
            'ɗụ', 'ɗu', 'đµ', 'dμ',
            # NOTE: 'đụ', 'dụ', 'đu', 'dù', 'dư', 'dự' REMOVED - too common
        ],
        'severity': 'high',
        'require_word_boundary': True,  # ONLY detect when word stands alone
        # CRITICAL: Safe contexts - EXPANDED to reduce false positives
        'safe_contexts': [
            # ===== Du lịch family =====
            'du lịch', 'du học', 'du khách', 'du xuân', 'du hành',
            'du thuyền', 'du ngoạn', 'du ca', 'hướng dẫn du',
            'khách du', 'tour du', 'chuyến du', 'đi du', 'công ty du',
            
            # ===== Duyên family - VERY IMPORTANT =====
            'duyên', 'duyên dáng', 'duyên phận', 'duyên nợ', 'duyên số',
            'có duyên', 'hữu duyên', 'vô duyên', 'nhân duyên', 'tình duyên',
            'duyên hải', 'duyên do', 'duyên cớ',
            
            # ===== Duyệt family - VERY COMMON =====
            'duyệt', 'kiểm duyệt', 'phê duyệt', 'xét duyệt', 'thẩm duyệt',
            'duyệt binh', 'duyệt xét', 'được duyệt', 'chờ duyệt',
            'nội dung duyệt', 'hệ thống duyệt', 'tự động duyệt',
            
            # ===== Dụ/Dụng family =====
            'ví dụ', 'dụng cụ', 'sử dụng', 'tác dụng', 'công dụng', 'ứng dụng',
            'dụ dỗ', 'dụng', 'thiết bị', 'phụ dung', 'dung lượng', 'dung môi',
            'dung dị', 'dung nham', 'dung túng', 'bao dung',
            
            # ===== Dư/Dữ family =====
            'dư thừa', 'dư giả', 'dư luận', 'còn dư', 'dư âm', 'thặng dư',
            'dữ liệu', 'dữ dội', 'dữ kiện', 'cơ sở dữ', 'lưu trữ dữ',
            
            # ===== Dự family =====
            'dự án', 'dự báo', 'dự kiến', 'dự đoán', 'dự phòng',
            'dự trữ', 'dự thầu', 'dự thi', 'tham dự', 'dự định',
            
            # ===== Dũng/Dưỡng family =====
            'dũng cảm', 'anh dũng', 'dũng sĩ', 'dũng mãnh',
            'dưỡng', 'bảo dưỡng', 'chăm dưỡng', 'dinh dưỡng', 'tu dưỡng',
            
            # ===== Giáo dục context =====
            'giáo dục', 'đào tạo', 'huấn luyện', 'đắc lực',
            
            # ===== PROPER NAMES - NEED WHITELIST =====
            'phúc du',  # Rapper Phúc Du
            'du hí', 'du mục', 'du kích', 'du đảng',
        ],
    },
    
    'dit': {
        'normalized': 'địt',
        'variants': [
            'địt', 'dit', 'đit', 'dịt', 'địt',
            'đ.i.t', 'd.i.t', 'đ_i_t', 'd_i_t', 'đ-i-t', 'd-i-t',
            'đ i t', 'd i t', 'đ  i  t', 'd  i  t',
            'đ*t', 'd*t', 'đ!t', 'd!t', 'đ1t', 'd1t',
            'djt', 'đjt', 'dít', 'đít',
            # Leetspeak
            'd!7', 'đ!7', 'd17', 'đ17',
            # Unicode
            'ɗịt', 'ɗit', 'đīt', 'dīt',
        ],
        'severity': 'high',
    },
    
    # ===== LỒN family =====
    'lon': {
        'normalized': 'lồn',
        'variants': [
            'lồn', 'lon', 'lòn', 'lón', 'lốn', 'lổn', 'lộn',
            'l.o.n', 'l_o_n', 'l-o-n', 'l o n', 'l  o  n',
            'l*n', 'l@n', 'l0n', 'l0.n', 'l.0.n',
            'lồl', 'lol', 'lonn', 'lonnn',
            # Leetspeak
            '10n', '1on', 'l0n', '10ŋ',
            # Unicode
            'ɭồn', 'ɭon', 'łồn', 'łon',
        ],
        'severity': 'high',
        'safe_contexts': ['hài lòng', 'vui lòng', 'lòng tin', 'lon bia', 'bia lon', 'lon nước'],
    },
    
    # ===== CẶC family =====
    'cac': {
        'normalized': 'cặc',
        'variants': [
            'cặc', 'cac', 'cak', 'cắc', 'cạc', 'căc',
            'c.a.c', 'c_a_c', 'c-a-c', 'c a c', 'c  a  c',
            'c*c', 'c@c', 'c4c', 'kac', 'kặc',
            'cacc', 'caccc',
            # Leetspeak  
            '(4(', 'c4c', '(a(',
            # Unicode
            'ςặc', 'ςac', 'çặc', 'çac',
        ],
        'severity': 'high',
        'safe_contexts': ['các bạn', 'các anh', 'các chị', 'một cách', 'bằng cách'],
    },
    
    # ===== VCL/VL family =====
    'vcl': {
        'normalized': 'vcl',
        'variants': [
            'vcl', 'vkl', 'v.c.l', 'v_c_l', 'v-c-l', 'v c l',
            'vãi lồn', 'vai lon', 'vãi lon', 'vai lồn',
            'vờ cờ lờ', 'vo co lo', 'vơ cơ lơ',
            # Short forms
            'vl', 'v.l', 'v_l', 'v-l', 'v l',
            # Leetspeak
            'v(1', 'vc1', 'vk1', '\\/cl', '\\/l',
            # Unicode
            'νcl', 'νl', 'ѵcl', 'ѵl',
        ],
        'severity': 'high',
    },
    
    # ===== ĐM/DCM family =====
    'dm': {
        'normalized': 'đm',
        'variants': [
            'đm', 'dm', 'đ.m', 'd.m', 'đ_m', 'd_m', 'đ-m', 'd-m',
            'đ m', 'd m', 'đ  m', 'd  m',
            'đmm', 'dmm', 'đmmm', 'dmmm',
            'đcm', 'dcm', 'đ.c.m', 'd.c.m',
            'đờ mờ', 'do mo', 'đơ mơ', 'dơ mơ',
            # Full forms
            'đụ má', 'du ma', 'địt mẹ', 'dit me', 'đụ mẹ', 'du me',
            # Leetspeak
            'đ/m', 'd/m', '|)m', 'đ|\/|',
            # Unicode
            'ɗm', 'ɗ.m', 'đɱ',
        ],
        'severity': 'high',
    },
    
    # ===== CC family =====
    'cc': {
        'normalized': 'cc',
        'variants': [
            'cc', 'c.c', 'c_c', 'c-c', 'c c',
            'cờ cờ', 'co co', 'cơ cơ',
            # Leetspeak
            '((', 'c(', '(c',
            # Unicode
            'ςς', 'çç',
        ],
        'severity': 'medium',
    },
    
    # ===== Chết tiệt family =====
    'chettiet': {
        'normalized': 'chết tiệt',
        'variants': [
            'chết tiệt', 'chet tiet', 'chết tiêt', 'chet tiet',
            'ch.ế.t', 'c.h.e.t', 'ch*t', 'ch3t',
        ],
        'severity': 'low',
    },
    
    # ===== Ngu family =====
    'ngu': {
        'normalized': 'ngu',
        'variants': [
            # ONLY match CLEAR obfuscation patterns - DO NOT match standalone 'ngu'
            'nguu', 'nguuu', 'nqư',
            'n.g.u', 'n_g_u', 'n-g-u', 'n g u',
            'nqu',
            # Leetspeak
            'n9u', 'ngu7',
            # Unicode
            'ŋgu', 'ŋu',
            # NOTE: 'ngu' alone REMOVED - too common as substring in:
            # người, những, nguy, nguồn, ngủ, nguyễn, nguyên, etc.
        ],
        'severity': 'medium',
        'context_dependent': True,  # VERY context dependent!
        # CRITICAL: All Vietnamese words containing 'ngu' substring
        'safe_contexts': [
            # Common words containing 'ngu' - NOT an insult
            'nguồn', 'ngủ', 'ngũ',
            'nguyễn', 'nguyên', 'nguyen', 'nguyển',
            'ngủi', 'ngứa', 'ngựa', 'ngụ',
            'nguội', 'nguồi', 'ngước', 'nguệch', 'nguyện',
            'ngu ngốc',  # Explicit insult - still need combo context
            'cẩn ngư',  # Fishing related
            'ngư dân', 'ngư nghiệp', 'ngư trường', 'ngư lưới',
            # Confucianism / Philosophy context
            'nho bác', 'khổng giáo', 'nho giáo',
            # Common verb patterns
            'mọi người', 'nhiều người', 'ai người', 'còn người',
            'con người', 'của người', 'cho người', 'với người',
            'từ người', 'đến người', 'như người', 'là người',
            'có người', 'và người', 'được người', 'bởi người',
        ],
    },
    
    # ===== Điên/Khùng family =====
    'dien': {
        'normalized': 'điên',
        'variants': [
            'điên', 'dien', 'đien', 'điện', 'đìên',
            'đ.i.ê.n', 'd.i.e.n',
            'điên khùng', 'dien khung',
        ],
        'severity': 'medium',
        'context_dependent': True,
    },
    
    # ===== Khốn nạn family =====
    'khonnan': {
        'normalized': 'khốn nạn',
        'variants': [
            'khốn nạn', 'khon nan', 'khốn nan', 'khon nạn',
            'khốn kiếp', 'khon kiep', 'khốn kiêp',
            'k.h.ố.n', 'kh*n', 'khôn nạn',
        ],
        'severity': 'medium',
    },
}

# ==================== ADVANCED PATTERN DETECTION ====================

# Regex patterns for complex obfuscation
ADVANCED_OBFUSCATION_PATTERNS = [
    # Zero-width characters
    (r'[\u200b\u200c\u200d\u2060\ufeff]', ''),
    
    # Combining diacritical marks abuse
    (r'[\u0300-\u036f]', ''),
    
    # Invisible characters
    (r'[\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]', ' '),
    
    # Repeated spaces (bypass attempt)
    (r'\s{2,}', ' '),
    
    # Dots/dashes between every character
    (r'([a-zA-Zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ])[.\-_~\*]{1,2}(?=[a-zA-Zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ])', r'\1'),
    
    # Emoji spam between letters (common bypass)
    (r'([a-zA-Zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ])[\U0001F300-\U0001F9FF]{1,3}(?=[a-zA-Zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ])', r'\1'),
]


class VariantDetector:
    """
    Detects variants and obfuscated forms of toxic words
    """
    
    def __init__(self):
        self.toxic_variants = TOXIC_VARIANTS
        self.homoglyphs = HOMOGLYPHS
        self.leetspeak = LEETSPEAK_TO_LETTER
        self.obfuscation_patterns = [(re.compile(p), r) for p, r in ADVANCED_OBFUSCATION_PATTERNS]
        
        # Build variant lookup
        self._build_variant_index()
    
    def _build_variant_index(self):
        """Build reverse index from variant -> normalized form"""
        self.variant_to_normalized = {}
        self.variant_severity = {}
        
        for key, info in self.toxic_variants.items():
            normalized = info['normalized']
            severity = info.get('severity', 'medium')
            
            for variant in info['variants']:
                variant_lower = variant.lower()
                self.variant_to_normalized[variant_lower] = normalized
                self.variant_severity[variant_lower] = severity
    
    def normalize_homoglyphs(self, text: str) -> Tuple[str, List[str]]:
        """
        Replace homoglyph characters with their ASCII equivalents
        
        Returns:
            (normalized_text, list of replaced characters)
        """
        result = []
        replacements = []
        
        for char in text:
            if char in self.homoglyphs:
                replacement = self.homoglyphs[char]
                result.append(replacement)
                replacements.append(f"{char} -> {replacement}")
            else:
                result.append(char)
        
        return ''.join(result), replacements
    
    def normalize_leetspeak(self, text: str) -> Tuple[str, List[str]]:
        """
        Convert leetspeak characters to letters
        
        Returns:
            (normalized_text, list of conversions)
        """
        result = []
        conversions = []
        
        for char in text:
            if char in self.leetspeak:
                replacement = self.leetspeak[char]
                result.append(replacement)
                conversions.append(f"{char} -> {replacement}")
            else:
                result.append(char)
        
        return ''.join(result), conversions
    
    def remove_insertion_chars(self, text: str) -> Tuple[str, int]:
        """
        Remove inserted characters between letters
        
        Returns:
            (cleaned_text, count of removed chars)
        """
        count = 0
        result = text
        
        for char in INSERTION_CHARS:
            if char in result:
                # Only remove if between letters
                pattern = f'([a-zA-Zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]){re.escape(char)}([a-zA-Zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ])'
                new_result = re.sub(pattern, r'\1\2', result, flags=re.IGNORECASE)
                if new_result != result:
                    count += 1
                    result = new_result
        
        return result, count
    
    def apply_obfuscation_patterns(self, text: str) -> Tuple[str, int]:
        """
        Apply advanced obfuscation detection patterns
        
        Returns:
            (cleaned_text, count of patterns applied)
        """
        result = text
        count = 0
        
        for pattern, replacement in self.obfuscation_patterns:
            new_result = pattern.sub(replacement, result)
            if new_result != result:
                count += 1
                result = new_result
        
        return result, count
    
    def normalize_repeated_chars(self, text: str) -> str:
        """
        Normalize repeated characters (e.g., 'nguuuuu' -> 'nguu')
        """
        # Reduce 3+ repeated chars to 2
        return re.sub(r'(.)\1{2,}', r'\1\1', text)
    
    def full_normalize(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Apply all normalization steps
        
        Returns:
            (fully_normalized_text, metadata)
        """
        metadata = {
            'original': text,
            'homoglyphs': [],
            'leetspeak': [],
            'insertions': 0,
            'obfuscation_patterns': 0,
        }
        
        # Step 1: Homoglyphs
        text, homoglyphs = self.normalize_homoglyphs(text)
        metadata['homoglyphs'] = homoglyphs
        
        # Step 2: Leetspeak
        text, leetspeak = self.normalize_leetspeak(text)
        metadata['leetspeak'] = leetspeak
        
        # Step 3: Insertion chars
        text, insertions = self.remove_insertion_chars(text)
        metadata['insertions'] = insertions
        
        # Step 4: Advanced patterns
        text, patterns = self.apply_obfuscation_patterns(text)
        metadata['obfuscation_patterns'] = patterns
        
        # Step 5: Repeated chars
        text = self.normalize_repeated_chars(text)
        
        # Step 6: Lowercase for matching
        text = text.lower()
        
        metadata['normalized'] = text
        metadata['has_obfuscation'] = (
            len(homoglyphs) > 0 or
            len(leetspeak) > 0 or
            insertions > 0 or
            patterns > 0
        )
        
        return text, metadata
    
    def detect_variants(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect toxic word variants in text
        
        Returns:
            List of detected variants with info
        """
        # First normalize
        normalized, metadata = self.full_normalize(text)
        
        detected = []
        
        # Check each word
        words = normalized.split()
        for word in words:
            # Clean word for matching
            clean_word = re.sub(r'[^\w]', '', word)
            
            if clean_word in self.variant_to_normalized:
                detected.append({
                    'original': word,
                    'normalized': self.variant_to_normalized[clean_word],
                    'severity': self.variant_severity.get(clean_word, 'medium'),
                    'type': 'exact_variant'
                })
                continue
            
            # Check if word contains a variant as substring
            # BUT only if it's NOT part of a larger legitimate word
            for variant, normalized_form in self.variant_to_normalized.items():
                if len(variant) >= 2 and variant in clean_word:
                    # Skip if the word is longer than the variant by more than 2 chars
                    # (likely a legitimate word containing the variant as substring)
                    if len(clean_word) > len(variant) + 2:
                        continue
                    
                    # Skip common Vietnamese words that contain toxic substrings
                    vietnamese_safe_words = {
                        'người', 'những', 'nguy', 'nguồn', 'ngủ', 'ngũ',
                        'nguyễn', 'nguyên', 'nguyen', 'nguyện', 'nguội',
                        'ngước', 'ngựa', 'ngứa', 'ngụ', 'ngũi', 'nguệch',
                        'dụng', 'dụ', 'dưỡng', 'dũng', 'dung', 'dự', 'dữ', 'dư',
                        'giáo', 'huấn', 'tập', 'luyện', 'mục', 'đích',
                        'phục', 'tùng', 'đày', 'tớ', 'đắc', 'lực',
                        'chương', 'trình', 'trọng', 'trách', 'tiết', 'tháo',
                        'uyên', 'thâm', 'nghịch', 'cảnh', 'thuận',
                        'trí', 'huệ',  # Philosophy terms
                    }
                    if clean_word in vietnamese_safe_words:
                        continue
                    
                    detected.append({
                        'original': word,
                        'variant_found': variant,
                        'normalized': normalized_form,
                        'severity': self.variant_severity.get(variant, 'medium'),
                        'type': 'substring_variant'
                    })
                    break
        
        # Also check for multi-word variants
        for key, info in self.toxic_variants.items():
            for variant in info['variants']:
                if ' ' in variant and variant in normalized:
                    detected.append({
                        'original': variant,
                        'normalized': info['normalized'],
                        'severity': info.get('severity', 'medium'),
                        'type': 'phrase_variant'
                    })
        
        return detected
    
    def is_safe_context(self, text: str, normalized_word: str) -> bool:
        """
        Check if the word appears in a safe context
        """
        text_lower = text.lower()
        
        # Find the variant info
        for key, info in self.toxic_variants.items():
            if info['normalized'] == normalized_word:
                safe_contexts = info.get('safe_contexts', [])
                for context in safe_contexts:
                    if context in text_lower:
                        return True
        
        return False
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Full analysis of text for variants
        
        Returns:
            Analysis result dict
        """
        normalized, metadata = self.full_normalize(text)
        variants = self.detect_variants(text)
        
        # Filter out safe context variants
        actual_violations = []
        safe_context_matches = []
        
        for variant in variants:
            if self.is_safe_context(text, variant['normalized']):
                safe_context_matches.append(variant)
            else:
                actual_violations.append(variant)
        
        # Calculate severity
        if any(v['severity'] == 'high' for v in actual_violations):
            overall_severity = 'high'
        elif any(v['severity'] == 'medium' for v in actual_violations):
            overall_severity = 'medium'
        elif actual_violations:
            overall_severity = 'low'
        else:
            overall_severity = 'none'
        
        return {
            'original_text': text,
            'normalized_text': normalized,
            'normalization_metadata': metadata,
            'detected_variants': actual_violations,
            'safe_context_matches': safe_context_matches,
            'overall_severity': overall_severity,
            'has_violations': len(actual_violations) > 0,
            'has_obfuscation': metadata['has_obfuscation'],
        }


# Singleton instance
_detector_instance = None

def get_variant_detector() -> VariantDetector:
    """Get singleton instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = VariantDetector()
    return _detector_instance


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    detector = get_variant_detector()
    
    test_cases = [
        # Normal text
        "Sản phẩm tốt quá",
        
        # Standard toxic
        "Đồ ngu vãi lồn",
        
        # Leetspeak variants
        "Đ0 ngu v@i l0n",
        "đ!t mẹ mày",
        "d.m mày ngu v.l",
        
        # Homoglyph variants
        "νcl đồ ngυ",  # Using Greek letters
        
        # Insertion variants
        "đ.ụ m.á",
        "l-o-n mày",
        "v*c*l*",
        
        # Safe context
        "Hài lòng với dịch vụ",
        "Các bạn có khỏe không?",
        
        # Complex obfuscation
        "🔥đ🔥ụ🔥m🔥á🔥",  # Emoji insertion
        "đ​ụ​m​á",  # Zero-width spaces
    ]
    
    print("=" * 80)
    print("VARIANT DETECTION TEST")
    print("=" * 80)
    
    for text in test_cases:
        print(f"\n📝 Text: '{text}'")
        result = detector.analyze(text)
        
        print(f"   Normalized: '{result['normalized_text']}'")
        print(f"   Has Obfuscation: {result['has_obfuscation']}")
        print(f"   Severity: {result['overall_severity']}")
        
        if result['detected_variants']:
            print(f"   ⚠️ Detected: {[v['normalized'] for v in result['detected_variants']]}")
        if result['safe_context_matches']:
            print(f"   ✅ Safe context: {[v['normalized'] for v in result['safe_context_matches']]}")
        
        if result['normalization_metadata']['homoglyphs']:
            print(f"   🔤 Homoglyphs: {result['normalization_metadata']['homoglyphs']}")
        if result['normalization_metadata']['leetspeak']:
            print(f"   🔢 Leetspeak: {result['normalization_metadata']['leetspeak']}")
        
        print("-" * 60)
