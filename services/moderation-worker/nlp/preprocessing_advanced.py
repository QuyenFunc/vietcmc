"""
Advanced Vietnamese Text Preprocessing for PhoBERT
- Word segmentation (critical for PhoBERT performance)
- Teencode normalization
- Diacritics handling
- Character-level obfuscation detection
- Emoji mapping
"""

import re
import unicodedata
from typing import Tuple, List, Dict, Optional
from underthesea import word_tokenize
import logging

logger = logging.getLogger(__name__)


# ==================== TEENCODE NORMALIZATION ====================

TEENCODE_MAP = {
    # Common Vietnamese teencode
    'vk': 'vợ',
    'ck': 'chồng',
    'k': 'không',
    'ko': 'không',
    'kh': 'không',
    'hk': 'không',
    'khong': 'không',
    'khg': 'không',
    'kg': 'không',
    'kô': 'không',
    'hem': 'không',
    'hong': 'không',
    
    'đc': 'được',
    'dc': 'được',
    'dk': 'được',
    'duoc': 'được',
    
    'ntn': 'như thế nào',
    'tn': 'thế nào',
    'tnao': 'thế nào',
    
    'vs': 'với',
    'voi': 'với',
    'v': 'với',
    
    'nv': 'như vậy',
    'vay': 'vậy',
    
    'lm': 'làm',
    'lam': 'làm',
    
    'j': 'gì',
    'gi': 'gì',
    'z': 'vậy',
    
    'tks': 'thanks',
    'thank': 'cảm ơn',
    'thanks': 'cảm ơn',
    'tnks': 'cảm ơn',
    
    'sr': 'sorry',
    'sory': 'sorry',
    
    'ok': 'okay',
    'oke': 'okay',
    'okie': 'okay',
    'okela': 'okay',
    
    'r': 'rồi',
    'rui': 'rồi',
    'roy': 'rồi',
    
    'nhg': 'nhưng',
    'nhug': 'nhưng',
    'nhung': 'nhưng',
    'ng': 'nhưng',
    
    'ms': 'mới',
    'moi': 'mới',
    
    'mn': 'mọi người',
    'mng': 'mọi người',
    
    'e': 'em',
    'a': 'anh',
    'c': 'chị',
    
    'bik': 'biết',
    'bit': 'biết',
    'biet': 'biết',
    
    'nch': 'nói chuyện',
    'nc': 'nói chuyện',
    
    'hum': 'hôm',
    'h': 'giờ',
    
    'onl': 'online',
    'ol': 'online',
    
    'off': 'offline',
    'of': 'offline',
    
    # Numbers as words
    '2': 'hai',
    '3': 'ba',
    '4': 'bốn',
    '5': 'năm',
    '10': 'mười',
}


# ==================== L33T SPEAK / OBFUSCATION ====================

OBFUSCATION_MAP = {
    # Character substitutions to evade filters
    '@': 'a',
    '4': 'a',
    '3': 'e',
    '1': 'i',
    '0': 'o',
    '5': 's',
    '7': 't',
    '$': 's',
    '€': 'e',
    
    # Vietnamese-specific
    'đ': 'd',
    'Đ': 'd',
}


# Common obfuscated profanity patterns
OBFUSCATED_PATTERNS = {
    r'v\W*[a@]i?\W*l': 'vãi lồn',  # v@~i l, v**l, vai l
    r'd\W*[m3]\W*': 'đ.m',  # d*m, d.m, dm
    r'c\W*[h]*\W*o': 'dog',  # dog, c.ho
    r'l\W*[o0]\W*n': 'lồn',  # l.on, l0n
    r'c\W*[a@]\W*c': 'cặc',  # c@c, c*c
    r'd\W*[i1]\W*t': 'đ*t',  # dit, d1t
}


# ==================== EMOJI MAPPING ====================

EMOJI_MAP = {
    '😊': ' happy ',
    '😃': ' happy ',
    '😄': ' happy ',
    '😁': ' happy ',
    '🙂': ' happy ',
    '😍': ' like ',
    '❤️': ' love ',
    '💕': ' love ',
    '💖': ' love ',
    '👍': ' good ',
    '👌': ' good ',
    '✅': ' good ',
    '✔️': ' good ',
    
    '😢': ' sad ',
    '😭': ' sad ',
    '😔': ' sad ',
    '😞': ' sad ',
    '😠': ' angry ',
    '😡': ' angry ',
    '🤬': ' curse ',
    '😤': ' annoyed ',
    '👎': ' bad ',
    '❌': ' no ',
    '✖️': ' no ',
    
    '😐': ' neutral ',
    '😑': ' neutral ',
    '🤔': ' thinking ',
}


# ==================== DIACRITICS HANDLING ====================

def remove_diacritics(text: str) -> str:
    """Remove Vietnamese diacritics"""
    # Decompose Unicode characters
    nfd = unicodedata.normalize('NFD', text)
    # Filter out combining characters (diacritics)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def normalize_diacritics(text: str) -> str:
    """Normalize diacritics to standard form (NFC)"""
    return unicodedata.normalize('NFC', text)


# ==================== MAIN PREPROCESSING ====================

def normalize_teencode(text: str) -> str:
    """
    Normalize teencode to standard Vietnamese
    
    Args:
        text: Input text with teencode
        
    Returns:
        Normalized text
    """
    text_lower = text.lower()
    words = text_lower.split()
    
    normalized_words = []
    for word in words:
        # Remove non-alphanumeric except Vietnamese chars
        clean_word = re.sub(r'[^\w\s]', '', word)
        
        # Check if it's in teencode map
        if clean_word in TEENCODE_MAP:
            normalized_words.append(TEENCODE_MAP[clean_word])
        else:
            normalized_words.append(word)
    
    return ' '.join(normalized_words)


def detect_obfuscation(text: str) -> Tuple[str, List[str]]:
    """
    Detect and normalize obfuscated profanity
    
    Args:
        text: Input text
        
    Returns:
        (normalized_text, detected_patterns)
    """
    text_lower = text.lower()
    detected = []
    
    # Replace character substitutions
    for char, replacement in OBFUSCATION_MAP.items():
        text_lower = text_lower.replace(char, replacement)
    
    # Detect obfuscated patterns
    for pattern, word in OBFUSCATED_PATTERNS.items():
        matches = re.findall(pattern, text_lower)
        if matches:
            detected.extend(matches)
            text_lower = re.sub(pattern, word, text_lower)
    
    return text_lower, detected


def normalize_repeated_chars(text: str) -> str:
    """
    Normalize repeated characters (e.g., 'đẹpppppp' -> 'đẹp')
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    # Replace 3+ repeated chars with 2
    # Keep some repetition as it can indicate emotion
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    return text


def map_emojis(text: str) -> str:
    """
    Map emojis to Vietnamese words
    
    Args:
        text: Input text with emojis
        
    Returns:
        Text with emojis replaced by words
    """
    for emoji, word in EMOJI_MAP.items():
        text = text.replace(emoji, word)
    return text


def preprocess_for_phobert(
    text: str,
    word_segment: bool = True,
    normalize_teen: bool = True,
    detect_obfusc: bool = True,
    map_emoji: bool = True,
    normalize_repeats: bool = True
) -> Tuple[str, Dict[str, any]]:
    """
    Complete preprocessing pipeline for PhoBERT
    
    PhoBERT was pretrained on word-segmented text, so we need to
    segment before tokenization for best performance.
    
    Args:
        text: Input Vietnamese text
        word_segment: Apply word segmentation (CRITICAL for PhoBERT)
        normalize_teen: Normalize teencode
        detect_obfusc: Detect obfuscated profanity
        map_emoji: Map emojis to words
        normalize_repeats: Normalize repeated characters
        
    Returns:
        (preprocessed_text, metadata)
    """
    metadata = {
        'original_length': len(text),
        'obfuscations': [],
        'has_emoji': False,
        'has_teencode': False
    }
    
    # 1. Map emojis first (before lowercasing)
    if map_emoji and any(emoji in text for emoji in EMOJI_MAP):
        text = map_emojis(text)
        metadata['has_emoji'] = True
    
    # 2. Normalize Unicode to NFC
    text = normalize_diacritics(text)
    
    # 3. Remove URLs
    text = re.sub(r'http\S+|www\.\S+', ' ', text)
    
    # 4. Remove emails
    text = re.sub(r'\S+@\S+', ' ', text)
    
    # 5. Normalize whitespace (but keep newlines for now)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # 6. Normalize repeated characters
    if normalize_repeats:
        text = normalize_repeated_chars(text)
    
    # 7. Detect obfuscation (must be before teencode for profanity detection)
    if detect_obfusc:
        text, obfuscations = detect_obfuscation(text)
        if obfuscations:
            metadata['obfuscations'] = obfuscations
    
    # 8. Normalize teencode
    if normalize_teen:
        original = text
        text = normalize_teencode(text)
        if text != original:
            metadata['has_teencode'] = True
    
    # 9. Remove special characters but keep Vietnamese
    # Keep: letters, numbers, Vietnamese chars, basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]', ' ', text, flags=re.IGNORECASE)
    
    # 10. Final whitespace cleanup
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 11. Word segmentation (CRITICAL for PhoBERT)
    # PhoBERT expects space-separated syllables
    if word_segment and text:
        try:
            # underthesea word_tokenize returns space-separated syllables
            text = word_tokenize(text, format="text")
        except Exception as e:
            logger.warning(f"Word segmentation failed: {e}, using original text")
    
    metadata['final_length'] = len(text)
    
    return text, metadata


def extract_pii(text: str) -> Dict[str, List[str]]:
    """
    Extract Personal Identifiable Information (PII)
    
    Args:
        text: Input text
        
    Returns:
        Dict of PII types and detected values
    """
    pii = {
        'phones': [],
        'emails': [],
        'urls': [],
        'addresses': []
    }
    
    # Phone numbers (Vietnamese format)
    # 10-11 digits, can start with 0, +84, 84
    phone_patterns = [
        r'\b0\d{9,10}\b',  # 0123456789
        r'\b84\d{9,10}\b',  # 84123456789
        r'\+84\d{9,10}\b',  # +84123456789
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'  # 123-456-7890
    ]
    
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        pii['phones'].extend(matches)
    
    # Emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    pii['emails'] = re.findall(email_pattern, text)
    
    # URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    pii['urls'] = re.findall(url_pattern, text)
    
    # Social media mentions
    social_patterns = [
        r'\b(?:zalo|telegram|viber|whatsapp)[:\s]+\d+',
        r'\b(?:fb|facebook|ig|instagram)[:\s]+[\w\.]+',
        r'@[\w\.]+',
    ]
    
    for pattern in social_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        pii['addresses'].extend(matches)
    
    # Remove duplicates
    for key in pii:
        pii[key] = list(set(pii[key]))
    
    return pii


def mask_pii(text: str, pii: Dict[str, List[str]] = None) -> str:
    """
    Mask PII in text
    
    Args:
        text: Input text
        pii: Optional pre-extracted PII dict
        
    Returns:
        Text with PII masked
    """
    if pii is None:
        pii = extract_pii(text)
    
    # Mask phones
    for phone in pii['phones']:
        text = text.replace(phone, '[PHONE]')
    
    # Mask emails
    for email in pii['emails']:
        text = text.replace(email, '[EMAIL]')
    
    # Mask URLs
    for url in pii['urls']:
        text = text.replace(url, '[URL]')
    
    # Mask social
    for addr in pii['addresses']:
        text = text.replace(addr, '[CONTACT]')
    
    return text


# ==================== DATA AUGMENTATION ====================

def augment_drop_diacritics(text: str, ratio: float = 0.3) -> str:
    """
    Augmentation: randomly drop diacritics
    Simulates users typing without diacritics
    
    Args:
        text: Input text
        ratio: Probability of dropping diacritics per word
        
    Returns:
        Augmented text
    """
    import random
    
    words = text.split()
    augmented = []
    
    for word in words:
        if random.random() < ratio:
            # Drop diacritics from this word
            augmented.append(remove_diacritics(word))
        else:
            augmented.append(word)
    
    return ' '.join(augmented)


def augment_teencode(text: str, ratio: float = 0.2) -> str:
    """
    Augmentation: convert words to teencode
    
    Args:
        text: Input text
        ratio: Probability of converting per word
        
    Returns:
        Augmented text
    """
    import random
    
    # Reverse teencode map
    reverse_map = {v: k for k, v in TEENCODE_MAP.items()}
    
    words = text.split()
    augmented = []
    
    for word in words:
        if word in reverse_map and random.random() < ratio:
            augmented.append(reverse_map[word])
        else:
            augmented.append(word)
    
    return ' '.join(augmented)


def augment_insert_chars(text: str, chars: str = ' .-_', ratio: float = 0.1) -> str:
    """
    Augmentation: insert random characters/spaces
    Simulates obfuscation attempts
    
    Args:
        text: Input text
        chars: Characters to insert
        ratio: Probability of insertion per character
        
    Returns:
        Augmented text
    """
    import random
    
    result = []
    for char in text:
        result.append(char)
        if random.random() < ratio:
            result.append(random.choice(chars))
    
    return ''.join(result)


if __name__ == "__main__":
    # Test preprocessing
    test_texts = [
        "Sản phẩm đẹp quá, tôi rất thích ❤️",
        "đồ ngu vl, k mua nữa",
        "Liên hệ: 0123456789 hoặc email@example.com",
        "Sảnnnn phẩmmmm đẹppppp quáááá",
        "v@~i l*n, d.m mày",
        "shop ntn, dc k",
    ]
    
    print("=" * 80)
    print("PREPROCESSING TESTS")
    print("=" * 80)
    
    for text in test_texts:
        processed, meta = preprocess_for_phobert(text)
        print(f"\nOriginal: {text}")
        print(f"Processed: {processed}")
        print(f"Metadata: {meta}")
        
        pii = extract_pii(text)
        if any(pii.values()):
            print(f"PII detected: {pii}")
            masked = mask_pii(text, pii)
            print(f"Masked: {masked}")
