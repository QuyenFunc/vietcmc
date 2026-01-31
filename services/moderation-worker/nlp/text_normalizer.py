"""
Layer A: Vietnamese Text Normalizer & Anti-Obfuscation
=====================================================

This module creates MULTIPLE versions of text for comprehensive detection:
1. NFC Normalized (clean Unicode)
2. Lowercase + whitespace normalized  
3. Repeated chars collapsed
4. Special char separators removed
5. Leet-speak mapped to letters
6. Vietnamese diacritics removed (for "dit me", "dm" patterns)

Key point: We must catch "dm / đ.m / d*m / d m / dмм" BEFORE passing to model.

Version: 1.0.0
Last Updated: 2026-01-30
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Set
import logging

logger = logging.getLogger(__name__)


# ==================== UNICODE NORMALIZATION ====================

# Zero-width and invisible characters to remove
ZERO_WIDTH_CHARS = [
    '\u200b',  # Zero Width Space
    '\u200c',  # Zero Width Non-Joiner
    '\u200d',  # Zero Width Joiner
    '\u2060',  # Word Joiner
    '\ufeff',  # Zero Width No-Break Space (BOM)
    '\u00ad',  # Soft Hyphen
    '\u034f',  # Combining Grapheme Joiner
    '\u2063',  # Invisible Separator
    '\u2064',  # Invisible Plus
]

# Invisible whitespace characters to normalize
INVISIBLE_WHITESPACE = [
    '\u00a0',  # Non-breaking space
    '\u2000',  # En Quad
    '\u2001',  # Em Quad
    '\u2002',  # En Space
    '\u2003',  # Em Space
    '\u2004',  # Three-Per-Em Space
    '\u2005',  # Four-Per-Em Space
    '\u2006',  # Six-Per-Em Space
    '\u2007',  # Figure Space
    '\u2008',  # Punctuation Space
    '\u2009',  # Thin Space
    '\u200a',  # Hair Space
    '\u202f',  # Narrow No-Break Space
    '\u205f',  # Medium Mathematical Space
    '\u3000',  # Ideographic Space
]


# ==================== HOMOGLYPH / LOOKALIKE CHARS ====================

# Cyrillic lookalikes (very common bypass)
CYRILLIC_TO_LATIN = {
    'а': 'a', 'А': 'A',  # Cyrillic A
    'е': 'e', 'Е': 'E',  # Cyrillic E
    'і': 'i', 'І': 'I',  # Cyrillic I (Ukrainian)
    'о': 'o', 'О': 'O',  # Cyrillic O
    'р': 'p', 'Р': 'P',  # Cyrillic R
    'с': 'c', 'С': 'C',  # Cyrillic S
    'у': 'y', 'У': 'Y',  # Cyrillic U
    'х': 'x', 'Х': 'X',  # Cyrillic Kha
    'м': 'm', 'М': 'M',  # Cyrillic M  ← CRITICAL for "dмм"
    'н': 'n', 'Н': 'N',  # Cyrillic N
    'т': 't', 'Т': 'T',  # Cyrillic T
    'к': 'k', 'К': 'K',  # Cyrillic K
    'в': 'v', 'В': 'V',  # Cyrillic V
    'ь': '',             # Cyrillic Soft Sign - remove
    'ъ': '',             # Cyrillic Hard Sign - remove
}

# Greek lookalikes
GREEK_TO_LATIN = {
    'α': 'a', 'Α': 'A',  # Alpha
    'β': 'b', 'Β': 'B',  # Beta
    'ε': 'e', 'Ε': 'E',  # Epsilon
    'η': 'n', 'Η': 'H',  # Eta
    'ι': 'i', 'Ι': 'I',  # Iota
    'κ': 'k', 'Κ': 'K',  # Kappa
    'μ': 'm', 'Μ': 'M',  # Mu ← CRITICAL
    'ν': 'v', 'Ν': 'N',  # Nu
    'ο': 'o', 'Ο': 'O',  # Omicron
    'ρ': 'p', 'Ρ': 'P',  # Rho
    'τ': 't', 'Τ': 'T',  # Tau
    'υ': 'u', 'Υ': 'Y',  # Upsilon
    'χ': 'x', 'Χ': 'X',  # Chi
}

# Mathematical/Symbol lookalikes
MATH_TO_LATIN = {
    'ℓ': 'l',  # Script l
    'ⅰ': 'i',  # Roman numeral 1
    'ⅱ': 'ii', # Roman numeral 2
    '×': 'x',  # Multiplication sign
    '∂': 'd',  # Partial derivative
    '∞': 'oo', # Infinity
    '∫': 'f',  # Integral
    '†': 't',  # Dagger
    '‡': 't',  # Double dagger
}

# Full-width to half-width
FULLWIDTH_TO_HALFWIDTH = {chr(i + 0xff00 - 0x20): chr(i) for i in range(0x21, 0x7f)}


# ==================== LEETSPEAK / NUMBER SUBSTITUTION ====================

LEETSPEAK_MAP = {
    # Numbers to letters
    '0': 'o',
    '1': 'i',
    '2': 'z',  # Sometimes 2 = to
    '3': 'e',
    '4': 'a',
    '5': 's',
    '6': 'g',
    '7': 't',
    '8': 'b',
    '9': 'g',  # Sometimes 9 = q
    
    # Symbols to letters
    '@': 'a',
    '$': 's',
    '!': 'i',
    '|': 'i',
    '+': 't',
    '(': 'c',
    '[': 'c',
    ')': 'd',  # Sometimes
    '{': 'c',
    '}': 'd',
    '<': 'c',
    '>': 'd',
    '^': 'a',
    # '*' removed - handled as separator
    '#': 'h',
    '%': 'x',
    '~': 'n',
    '`': '',   # Remove
    '\\': 'l',
    '/': 'l',
}


# ==================== VIETNAMESE DIACRITICS ====================

# Vietnamese vowel mappings for diacritic removal
VIETNAMESE_DIACRITICS_MAP = {
    # A variants
    'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
    'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'Á': 'A', 'À': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A',
    'Ă': 'A', 'Ắ': 'A', 'Ằ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A',
    'Â': 'A', 'Ấ': 'A', 'Ầ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A',
    
    # E variants
    'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'É': 'E', 'È': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E',
    'Ê': 'E', 'Ế': 'E', 'Ề': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E',
    
    # I variants
    'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    'Í': 'I', 'Ì': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I',
    
    # O variants
    'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
    'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'Ó': 'O', 'Ò': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O',
    'Ô': 'O', 'Ố': 'O', 'Ồ': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O',
    'Ơ': 'O', 'Ớ': 'O', 'Ờ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O',
    
    # U variants
    'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
    'Ú': 'U', 'Ù': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U',
    'Ư': 'U', 'Ứ': 'U', 'Ừ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U',
    
    # Y variants
    'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    'Ý': 'Y', 'Ỳ': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
    
    # D variant
    'đ': 'd', 'Đ': 'D',
}


# ==================== SEPARATOR CHARS ====================

# Characters commonly used to break up words
SEPARATOR_CHARS = set([
    '.', '-', '_', ' ', '*', '~', '^', "'", '"',
    '`', '|', '/', '\\', '+', '=', '#', '@',
    ':', ';', ',', '!', '?', '(', ')', '[', ']',
    '{', '}', '<', '>', '•', '·', '°', '◦', '○', '●',
])


# ==================== MAIN NORMALIZER CLASS ====================

class VietnameseTextNormalizer:
    """
    Creates multiple normalized versions of text for toxic content detection.
    
    This is Layer A of the 3-layer moderation system.
    """
    
    def __init__(self):
        # Build combined homoglyph map
        self.homoglyph_map = {}
        self.homoglyph_map.update(CYRILLIC_TO_LATIN)
        self.homoglyph_map.update(GREEK_TO_LATIN)
        self.homoglyph_map.update(MATH_TO_LATIN)
        self.homoglyph_map.update(FULLWIDTH_TO_HALFWIDTH)
        
        # Regex patterns for separator removal
        self._build_separator_pattern()
    
    def _build_separator_pattern(self):
        """Build regex pattern for separator characters between letters"""
        # Use a simpler approach - manually list common separators
        # These are: . - _ * ~ ^ ' " ` | / \ + = # @ : ; , ! ?
        sep_pattern = r'[.\-_*~^\'"`|/\\+=\#@:;,!?()\[\]{}<>•·°◦○●]'
        
        # Pattern: letter + separator(s) + letter
        # This will match: d.m, n.g.u, l-o-n, etc.
        viet_letters = r'[a-zA-ZàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ]'
        
        self.separator_between_letters = re.compile(
            f'({viet_letters})' + sep_pattern + f'+({viet_letters})',
            re.UNICODE
        )
    
    def normalize_unicode(self, text: str) -> str:
        """
        Step 1: Unicode NFC normalization + remove invisible chars
        """
        # NFC normalize (compose decomposed chars)
        text = unicodedata.normalize('NFC', text)
        
        # Remove zero-width characters
        for char in ZERO_WIDTH_CHARS:
            text = text.replace(char, '')
        
        # Normalize invisible whitespace to regular space
        for char in INVISIBLE_WHITESPACE:
            text = text.replace(char, ' ')
        
        return text
    
    def normalize_homoglyphs(self, text: str) -> Tuple[str, List[str]]:
        """
        Step 2: Replace lookalike Unicode characters with ASCII equivalents
        
        Returns:
            (normalized_text, list of replacements made)
        """
        result = []
        replacements = []
        
        for char in text:
            if char in self.homoglyph_map:
                replacement = self.homoglyph_map[char]
                result.append(replacement)
                if replacement:  # Don't log empty replacements
                    replacements.append(f"{char}→{replacement}")
            else:
                result.append(char)
        
        return ''.join(result), replacements
    
    def normalize_leetspeak(self, text: str) -> Tuple[str, List[str]]:
        """
        Step 3: Map common leetspeak/number substitutions to letters
        
        Returns:
            (normalized_text, list of conversions)
        """
        result = []
        conversions = []
        
        for char in text:
            if char in LEETSPEAK_MAP:
                replacement = LEETSPEAK_MAP[char]
                result.append(replacement)
                if replacement:
                    conversions.append(f"{char}→{replacement}")
            else:
                result.append(char)
        
        return ''.join(result), conversions
    
    def collapse_repeated_chars(self, text: str) -> str:
        """
        Step 4: Collapse repeated characters (3+ → 2)
        "đmmmmm" → "đmm"
        "nguuuuu" → "nguu"
        """
        return re.sub(r'(.)\1{2,}', r'\1\1', text)
    
    def remove_separators_between_letters(self, text: str) -> Tuple[str, int]:
        """
        Step 5: Remove separator characters between SINGLE letters (obfuscation patterns)
        "đ.m" → "đm", "n.g.u" → "ngu", "d:m" → "dm"
        
        ALSO handles whitespace-separated single letters:
        "d  m" → "dm", "n g u" → "ngu"
        
        BUT preserves normal word boundaries:
        "sản phẩm tốt" → "sản phẩm tốt" (unchanged)
        
        Returns:
            (cleaned_text, count of separators removed)
        """
        count = 0
        
        # PRE-PROCESSING: Handle excess whitespace between single letters
        # Pattern: single_letter + space(s) + single_letter  (repeated)
        # This catches: "d  m", "n g u", "d   m   m"
        viet_letter = r'[a-zA-ZđĐ]'
        
        # Find sequences of single letters separated by whitespace
        # Match: (single_letter)(\s+)(single_letter)
        def join_single_letters(m):
            return m.group(1) + m.group(3)
        
        # Iteratively join single letters separated by whitespace
        prev_text = None
        working_text = text
        while prev_text != working_text:
            prev_text = working_text
            # Pattern: single_letter at word boundary + spaces + single_letter at word boundary
            new_text = re.sub(
                rf'(?<![a-zA-ZđĐ])({viet_letter})(\s+)({viet_letter})(?![a-zA-ZđĐ])',
                join_single_letters,
                working_text
            )
            if new_text != working_text:
                count += 1
                working_text = new_text
        
        # Split into words
        words = working_text.split()
        result_words = []
        
        for word in words:
            # Only process words that look like obfuscation attempts:
            # - Short (2-10 chars)
            # - Contains separator chars
            # - Has letter-separator-letter pattern
            
            if len(word) <= 10 and any(c in SEPARATOR_CHARS for c in word):
                # Apply separator removal to this word only
                prev_word = None
                while prev_word != word:
                    prev_word = word
                    new_word = self.separator_between_letters.sub(r'\1\2', word)
                    if new_word != word:
                        count += 1
                        word = new_word
            
            result_words.append(word)
        
        return ' '.join(result_words), count
    
    def normalize_whitespace(self, text: str) -> str:
        """
        Step 6: Normalize all whitespace to single spaces
        """
        # Replace multiple spaces/tabs/newlines with single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def remove_vietnamese_diacritics(self, text: str) -> str:
        """
        Step 7: Remove Vietnamese diacritics
        "địt mẹ" → "dit me"
        "đéo" → "deo"
        
        WARNING: This should be used as a PARALLEL check, not replacement
        """
        result = []
        for char in text:
            if char in VIETNAMESE_DIACRITICS_MAP:
                result.append(VIETNAMESE_DIACRITICS_MAP[char])
            else:
                result.append(char)
        return ''.join(result)
    
    def create_all_versions(self, text: str) -> Dict[str, any]:
        """
        Main entry point: Create all normalized versions of text
        
        Returns dict with:
            - original: Original text
            - nfc: NFC normalized
            - lowercase: Lowercased
            - homoglyph_normalized: Lookalike chars replaced
            - leetspeak_normalized: Numbers/symbols replaced
            - collapsed: Repeated chars collapsed
            - separator_removed: Separators between letters removed
            - no_diacritics: Vietnamese diacritics removed
            - fully_normalized: All normalizations applied
            - metadata: Info about what was detected
        """
        metadata = {
            'homoglyph_replacements': [],
            'leetspeak_conversions': [],
            'separators_removed': 0,
            'has_obfuscation': False,
            'obfuscation_types': [],
        }
        
        # Step 1: Unicode NFC
        nfc = self.normalize_unicode(text)
        
        # Step 2: Lowercase
        lowercase = nfc.lower()
        
        # Step 3: Homoglyphs
        homoglyph_norm, homoglyph_reps = self.normalize_homoglyphs(lowercase)
        metadata['homoglyph_replacements'] = homoglyph_reps
        if homoglyph_reps:
            metadata['has_obfuscation'] = True
            metadata['obfuscation_types'].append('homoglyph')
        
        # Step 4: Leetspeak  
        leetspeak_norm, leetspeak_convs = self.normalize_leetspeak(homoglyph_norm)
        metadata['leetspeak_conversions'] = leetspeak_convs
        if leetspeak_convs:
            metadata['has_obfuscation'] = True
            metadata['obfuscation_types'].append('leetspeak')
        
        # Step 5: Collapse repeated
        collapsed = self.collapse_repeated_chars(leetspeak_norm)
        
        # Step 6: Remove separators
        separator_removed, sep_count = self.remove_separators_between_letters(collapsed)
        metadata['separators_removed'] = sep_count
        if sep_count > 0:
            metadata['has_obfuscation'] = True
            metadata['obfuscation_types'].append('separator_insertion')
        
        # Step 7: Normalize whitespace
        fully_normalized = self.normalize_whitespace(separator_removed)
        
        # Step 8: No diacritics version (parallel check)
        no_diacritics = self.remove_vietnamese_diacritics(fully_normalized)
        
        return {
            'original': text,
            'nfc': nfc,
            'lowercase': lowercase,
            'homoglyph_normalized': homoglyph_norm,
            'leetspeak_normalized': leetspeak_norm,
            'collapsed': collapsed,
            'separator_removed': separator_removed,
            'no_diacritics': no_diacritics,
            'fully_normalized': fully_normalized,
            'metadata': metadata,
        }
    
    def get_texts_for_checking(self, text: str) -> List[Tuple[str, str]]:
        """
        Get list of (text_version, version_name) tuples to check against rules
        
        This is the main method to use in the moderation pipeline
        """
        versions = self.create_all_versions(text)
        
        return [
            (versions['original'], 'original'),
            (versions['fully_normalized'], 'normalized'),
            (versions['no_diacritics'], 'no_diacritics'),
        ]


# ==================== SINGLETON INSTANCE ====================

_normalizer_instance = None

def get_normalizer() -> VietnameseTextNormalizer:
    """Get singleton normalizer instance"""
    global _normalizer_instance
    if _normalizer_instance is None:
        _normalizer_instance = VietnameseTextNormalizer()
    return _normalizer_instance


# ==================== TEST ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    normalizer = get_normalizer()
    
    test_cases = [
        # Standard
        "Sản phẩm tốt quá",
        
        # Separator obfuscation
        "đ.m mày",
        "d*m",
        "n.g.u",
        "d:m",
        "d:m,m",
        "l-o-n",
        "c.a.c",
        
        # Leetspeak
        "d1t me",
        "l0n",
        "c@c",
        "n9u",
        
        # Cyrillic/Greek lookalikes
        "dмм",  # Cyrillic м instead of m
        "νcl",  # Greek ν instead of v
        
        # Repeated chars
        "đmmmmm",
        "nguuuuu",
        
        # No diacritics
        "dit me may",
        "dm con cho",
        
        # Combined obfuscation
        "đ.м.м",  # Separator + Cyrillic
        "d*!*t",  # Multiple symbols
        
        # Zero-width characters (invisible)
        "đ\u200bm\u200bm",  # Zero-width spaces
        
        # Full-width characters
        "ｄｍ",  # Full-width dm
        
        # Spacing bypass
        "d  m",
        "đ   m",
    ]
    
    print("=" * 80)
    print("VIETNAMESE TEXT NORMALIZER TEST")
    print("=" * 80)
    
    for text in test_cases:
        print(f"\n📝 Input: '{text}'")
        
        # Show repr for invisible chars
        if any(ord(c) > 127 or c in '\u200b\u200c\u200d' for c in text):
            print(f"   Repr: {repr(text)}")
        
        versions = normalizer.create_all_versions(text)
        
        print(f"   Normalized: '{versions['fully_normalized']}'")
        print(f"   No diacritics: '{versions['no_diacritics']}'")
        
        meta = versions['metadata']
        if meta['has_obfuscation']:
            print(f"   ⚠️ OBFUSCATION DETECTED: {meta['obfuscation_types']}")
            if meta['homoglyph_replacements']:
                print(f"      Homoglyphs: {meta['homoglyph_replacements']}")
            if meta['leetspeak_conversions']:
                print(f"      Leetspeak: {meta['leetspeak_conversions']}")
            if meta['separators_removed']:
                print(f"      Separators removed: {meta['separators_removed']}")
        
        print("-" * 60)
