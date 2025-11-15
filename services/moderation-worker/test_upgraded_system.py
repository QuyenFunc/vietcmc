"""
Test Upgraded Moderation System with Real Failed Cases
"""

import sys
import os
import io

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nlp.inference import ModerationInference

def test_failed_cases():
    """Test with the exact cases that failed before"""
    
    engine = ModerationInference(model_path='vinai/phobert-base-v2', device='cpu')
    
    # Các case đã thất bại
    test_cases = [
        {
            'text': 'Cái quan điểm ngu si vãi lồn',
            'expected': 'reject',  # Vì có "vãi lồn" - profanity nghiêm trọng
            'reason': 'Profanity nghiêm trọng dù có "quan điểm"'
        },
        {
            'text': 'Bọn gay đáng bị khinh thường',
            'expected': 'reject',
            'reason': 'Hate speech - Phân biệt đối xử LGBTQ+'
        },
        {
            'text': 'Gái xinh thế này chắc bú cu giỏi nhỉ',
            'expected': 'reject',
            'reason': 'Nội dung tình dục rõ ràng'
        },
        {
            'text': 'Sản phẩm tệ quá',
            'expected': 'allowed',
            'reason': 'Đánh giá sản phẩm hợp lệ'
        },
        {
            'text': 'Quan điểm ngu ngốc',
            'expected': 'allowed',
            'reason': 'Phê bình ý kiến, không phải cá nhân'
        },
    ]
    
    print("="*100)
    print("TESTING UPGRADED MODERATION SYSTEM")
    print("="*100)
    print()
    
    passed = 0
    failed = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*100}")
        print(f"TEST CASE {i}:")
        print(f"Text: {case['text']}")
        print(f"Expected: {case['expected']}")
        print(f"Reason: {case['reason']}")
        print("-"*100)
        
        result = engine.predict(case['text'])
        
        actual = result['moderation_result']
        sentiment = result['sentiment']
        confidence = result['confidence']
        reasoning = result['reasoning']
        
        print(f"✅ Result: {actual}")
        print(f"   Sentiment: {sentiment}")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Reasoning: {reasoning}")
        
        if 'toxicity_score' in result:
            print(f"   Toxicity Score: {result['toxicity_score']}")
        
        if 'flagged_words' in result and result['flagged_words']:
            print(f"   Flagged Words: {', '.join(result['flagged_words'][:5])}")
        
        # Check if passed
        if actual == case['expected']:
            print(f"✅ PASSED")
            passed += 1
        else:
            print(f"❌ FAILED - Expected {case['expected']}, got {actual}")
            failed += 1
    
    print(f"\n{'='*100}")
    print(f"SUMMARY:")
    print(f"  Passed: {passed}/{len(test_cases)}")
    print(f"  Failed: {failed}/{len(test_cases)}")
    print(f"  Success Rate: {passed/len(test_cases)*100:.1f}%")
    print("="*100)

if __name__ == "__main__":
    test_failed_cases()

