"""
Test script for upgraded OCR image moderation
Tests the enhanced OCR system with critical word detection
"""

import logging
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image.inference_image import (
    check_critical_ocr_text,
    normalize_text,
    remove_vietnamese_accents,
    CRITICAL_OCR_WORDS
)

def test_critical_word_detection():
    """Test the critical word detection function"""
    print("=" * 60)
    print("TEST: Critical OCR Word Detection")
    print("=" * 60)
    
    test_cases = [
        # Should REJECT
        ("NGU", True, "Single word - uppercase"),
        ("ngu", True, "Single word - lowercase"),
        ("Ngu", True, "Single word - mixed case"),
        ("DM", True, "Abbreviation - uppercase"),
        ("vcl", True, "Abbreviation - lowercase"),
        ("CC", True, "Abbreviation - uppercase"),
        ("đm", True, "Vietnamese abbreviation"),
        ("đụ", True, "Vietnamese profanity"),
        ("FUCK", True, "English profanity - uppercase"),
        ("fuck", True, "English profanity - lowercase"),
        ("bitch", True, "English profanity"),
        
        # Edge cases - Should REJECT
        ("N G U", True, "Spaced letters"),
        ("n.g.u", True, "Dotted letters"),
        ("NGU ", True, "With trailing space"),
        (" NGU", True, "With leading space"),
        
        # Should ALLOW
        ("Hello", False, "Normal word"),
        ("Xin chào", False, "Vietnamese greeting"),
        ("LOGO", False, "Normal word"),
        ("nguồn", False, "Contains 'ngu' but valid word"),  # This might be tricky
        
        # Combined text
        ("NGU VCL", True, "Multiple bad words"),
        ("Đây là NGU", True, "Bad word in sentence"),
    ]
    
    passed = 0
    failed = 0
    
    for text, should_reject, description in test_cases:
        result = check_critical_ocr_text(text)
        is_violation = result is not None and result.get('is_violation', False)
        
        if is_violation == should_reject:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"\n{status}: {description}")
        print(f"  Input: '{text}'")
        print(f"  Expected: {'REJECT' if should_reject else 'ALLOW'}")
        print(f"  Got: {'REJECT' if is_violation else 'ALLOW'}")
        if result:
            print(f"  Detected: {result.get('detected_words', [])}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


def test_normalize_functions():
    """Test text normalization functions"""
    print("\n" + "=" * 60)
    print("TEST: Text Normalization Functions")
    print("=" * 60)
    
    # Test normalize_text
    assert normalize_text("  Hello  World  ") == "hello world"
    assert normalize_text("NGU") == "ngu"
    print("✅ normalize_text works correctly")
    
    # Test remove_vietnamese_accents
    assert remove_vietnamese_accents("đụ") == "du"
    assert remove_vietnamese_accents("lồn") == "lon"
    assert remove_vietnamese_accents("đéo") == "deo"
    print("✅ remove_vietnamese_accents works correctly")
    
    return True


def test_critical_words_coverage():
    """Test that critical words list covers important cases"""
    print("\n" + "=" * 60)
    print("TEST: Critical Words Coverage")
    print("=" * 60)
    
    required_words = [
        'ngu', 'dm', 'đm', 'vcl', 'vl', 'cc', 
        'đụ', 'địt', 'lồn', 'cặc',
        'fuck', 'shit', 'bitch'
    ]
    
    missing = []
    for word in required_words:
        if word not in CRITICAL_OCR_WORDS:
            missing.append(word)
    
    if missing:
        print(f"❌ Missing critical words: {missing}")
        return False
    else:
        print(f"✅ All {len(required_words)} required critical words are present")
        print(f"   Total critical words in list: {len(CRITICAL_OCR_WORDS)}")
        return True


def main():
    print("\n" + "=" * 60)
    print("OCR UPGRADE TEST SUITE")
    print("=" * 60 + "\n")
    
    all_passed = True
    
    # Run tests
    all_passed &= test_normalize_functions()
    all_passed &= test_critical_words_coverage()
    all_passed &= test_critical_word_detection()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️ SOME TESTS FAILED")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
