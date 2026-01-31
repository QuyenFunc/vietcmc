import re
import unicodedata
from typing import Optional
import langdetect


def normalize_vietnamese_chars(text: str) -> str:
    """Normalize Vietnamese characters to standard form"""
    # Normalize to NFC form
    text = unicodedata.normalize('NFC', text)
    
    # Fix common Vietnamese typos
    replacements = {
        'òa': 'oà', 'óa': 'oá', 'ỏa': 'oả', 
        'õa': 'oã', 'ọa': 'oạ',
    }
    
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    
    return text


def preprocess_vietnamese_text(text: str) -> str:
    """
    Preprocess Vietnamese text for NLP inference
    
    Args:
        text: Input text
    
    Returns:
        Preprocessed text
    """
    # Lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Normalize Vietnamese characters
    text = normalize_vietnamese_chars(text)
    
    return text


def detect_language(text: str) -> str:
    """
    Detect language of text
    
    Args:
        text: Input text
    
    Returns:
        Language code (e.g., 'vi', 'en')
    """
    try:
        return langdetect.detect(text)
    except:
        return 'unknown'


def is_spam(text: str) -> bool:
    """
    Check if text appears to be spam
    Emoji-only content is NOT spam (common on social media)
    
    Args:
        text: Input text
    
    Returns:
        True if text is likely spam
    """
    # Check if text is only emojis/unicode symbols
    # Emoji range: U+1F000 to U+1FFFF and common symbols
    text_without_spaces = text.replace(' ', '')
    if text_without_spaces and all(ord(c) > 0x1F000 or c in '👍👎❤️😊😢😡🔥✨⭐💯🎉😃😄😁🥰😍🤩💕💖👌🌟😞😭😠🤬💔❌⚠️😐😶🙂😑🤔😕🤷' for c in text_without_spaces):
        # Pure emoji content - common on social media, NOT spam
        return False
    
    # Check for excessive special characters (EXCLUDING emojis)
    if len(text) > 0:
        # Don't count emojis as special chars
        text_no_emoji = re.sub(r'[\U0001F000-\U0001FFFF]', '', text)
        if len(text_no_emoji) > 0:
            special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s\u0080-\uFFFF]', text_no_emoji)) / len(text_no_emoji)
            if special_char_ratio > 0.6:  # Increased threshold
                return True
    
    # Check for repeated characters (but not repeated emojis)
    if re.search(r'(.)\1{10,}', text):  # Increased from 5 to 10
        return True
    
    # Check for excessive caps
    if len(text) > 10:
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
        if caps_ratio > 0.8:  # Increased from 0.7
            return True
    
    return False


def is_text_valid(text: str, min_length: int = 1) -> tuple[bool, Optional[str]]:
    """
    Validate text for processing
    
    Args:
        text: Input text
        min_length: Minimum word count (changed to 1 to allow short texts)
    
    Returns:
        (is_valid, reason)
    """
    # Check if text is empty
    if not text or not text.strip():
        return False, "Empty text"
    
    # Check length - allow short texts (1 word minimum)
    words = text.split()
    if len(words) < min_length:
        return False, "Text too short"
    
    # For very short texts (1-2 words), skip language detection
    # as it's unreliable for short strings
    if len(words) >= 3:
        # Check language
        lang = detect_language(text)
        if lang not in ['vi', 'en', 'unknown']:
            return False, f"Unsupported language: {lang}"
    
    # Check spam
    if is_spam(text):
        return False, "Spam/excessive special characters detected"
    
    return True, None

