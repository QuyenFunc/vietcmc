"""
Test Enhanced Moderation System
Test các cải tiến về độ chính xác của hệ thống kiểm duyệt

Usage:
    cd services/moderation-worker
    python test_enhanced_accuracy.py
"""

import logging
import sys
import os

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nlp.context_analyzer import EnhancedModerationAnalyzer, get_enhanced_analyzer
from nlp.inference_multitask import MultiTaskModerationInference

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_context_analyzer():
    """Test context analyzer independently"""
    print("\n" + "=" * 80)
    print("🔍 TEST CONTEXT ANALYZER")
    print("=" * 80)
    
    analyzer = get_enhanced_analyzer()
    
    test_cases = [
        # ===== SHOULD BE ALLOWED (Legitimate negative feedback) =====
        {
            'text': 'Sản phẩm tệ quá, chất lượng kém, không đáng tiền',
            'expected_action': 'allowed',
            'category': 'Legitimate negative feedback'
        },
        {
            'text': 'Hàng giao chậm, đóng gói không cẩn thận, thất vọng',
            'expected_action': 'allowed',
            'category': 'Legitimate complaint'
        },
        {
            'text': 'Shop này dịch vụ kém, không recommend',
            'expected_action': 'allowed',
            'category': 'Legitimate recommendation'
        },
        {
            'text': 'Đánh giá 1 sao, sản phẩm không như mô tả',
            'expected_action': 'allowed',
            'category': 'Star rating feedback'
        },
        {
            'text': 'Hài lòng với sản phẩm, sẽ mua lại',
            'expected_action': 'allowed',
            'category': 'Positive feedback'
        },
        {
            'text': 'Du lịch Đà Nẵng vui quá',
            'expected_action': 'allowed',
            'category': 'Travel content'
        },
        {
            'text': 'Tình hình gay gắt, cần giải quyết',
            'expected_action': 'allowed',
            'category': 'Normal Vietnamese phrase'
        },
        {
            'text': 'Các bạn ơi, sản phẩm này tốt không?',
            'expected_action': 'allowed',
            'category': 'Question'
        },
        
        # ===== SHOULD BE REVIEW (Borderline cases) =====
        {
            'text': 'Đồ rác vl, shop ngu thật',
            'expected_action': 'review',
            'category': 'Profanity in feedback'
        },
        
        # ===== SHOULD BE REJECT (Clear violations) =====
        {
            'text': 'Mày ngu thế, thằng này khùng quá',
            'expected_action': 'reject',
            'category': 'Personal attack'
        },
        {
            'text': 'Bọn gay đáng ghét, nên chết hết',
            'expected_action': 'reject',
            'category': 'Hate speech'
        },
        {
            'text': 'Đm mày, tao giết mày',
            'expected_action': 'reject',
            'category': 'Threat + profanity'
        },
    ]
    
    passed = 0
    failed = 0
    
    for case in test_cases:
        result = analyzer.analyze(case['text'], flagged_words=[])
        actual_action = result['action']
        expected = case['expected_action']
        
        status = "✅ PASS" if actual_action == expected else "❌ FAIL"
        if actual_action == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status} | {case['category']}")
        print(f"   Text: {case['text'][:60]}...")
        print(f"   Expected: {expected} | Actual: {actual_action}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Intent: {result['intent']}")
        if result['is_legitimate_criticism']:
            print(f"   ✓ Legitimate criticism detected")
    
    print(f"\n{'='*80}")
    print(f"Results: {passed}/{passed+failed} passed ({passed/(passed+failed)*100:.1f}%)")
    print(f"{'='*80}")
    
    return passed, failed


def test_safe_context_detection():
    """Test detection of safe contexts for words that look toxic"""
    print("\n" + "=" * 80)
    print("🔍 TEST SAFE CONTEXT DETECTION")
    print("=" * 80)
    
    analyzer = get_enhanced_analyzer()
    
    test_cases = [
        # Words that look toxic but are in safe context
        ('Tình hình gay gắt quá', 'gay', True, 'gay gắt = tense'),
        ('Hài lòng với dịch vụ', 'lon', True, 'hài lòng = satisfied'),
        ('Du lịch Việt Nam', 'du', True, 'du lịch = travel'),
        ('Các bạn có khỏe không', 'các', True, 'các = plural marker'),
        ('Lon bia lạnh ngon', 'lon', True, 'lon bia = beer can'),
        
        # Words that ARE toxic (should NOT be filtered)
        ('Đồ ngu', 'ngu', False, 'ngu = stupid (toxic)'),
        ('Thằng điên', 'điên', False, 'điên = crazy (toxic)'),
    ]
    
    passed = 0
    for text, word, expected_safe, description in test_cases:
        is_safe = analyzer.context_analyzer.is_safe_context(text, word)
        status = "✅" if is_safe == expected_safe else "❌"
        if is_safe == expected_safe:
            passed += 1
        
        print(f"{status} '{word}' in '{text[:40]}...' - Safe: {is_safe} (expected: {expected_safe})")
        print(f"   Reason: {description}")
    
    print(f"\nResults: {passed}/{len(test_cases)} passed")
    return passed, len(test_cases) - passed


def test_severity_modifier():
    """Test severity modifier calculation"""
    print("\n" + "=" * 80)
    print("🔍 TEST SEVERITY MODIFIER")
    print("=" * 80)
    
    analyzer = get_enhanced_analyzer()
    
    test_cases = [
        ('Sản phẩm tốt', 'Should have modifier ≈ 1.0'),
        ('Sản phẩm tệ quá', 'Should reduce severity (product feedback)'),
        ('Đùa thôi', 'Should reduce severity (joking)'),
        ('Tao giết mày', 'Should increase severity (threat)'),
        ('Không phải vậy', 'Should reduce severity (negation)'),
    ]
    
    for text, description in test_cases:
        result = analyzer.context_analyzer.analyze(text)
        modifier = result.severity_modifier
        
        indicator = "🔻" if modifier < 0.9 else ("🔺" if modifier > 1.1 else "➖")
        print(f"{indicator} Modifier: {modifier:.2f} | Text: '{text}'")
        print(f"   {description}")
    
    print("\nLegend: 🔻 = Reduced severity, 🔺 = Increased severity, ➖ = Normal")


def test_inference_with_context():
    """Test full inference with context analyzer"""
    print("\n" + "=" * 80)
    print("🔍 TEST INFERENCE WITH CONTEXT ANALYZER")
    print("=" * 80)
    
    try:
        inference = MultiTaskModerationInference(
            model_path='vinai/phobert-base-v2',
            device='cpu',
            use_context_analyzer=True
        )
        
        test_texts = [
            # Should be ALLOWED
            "Sản phẩm rất tốt, tôi rất hài lòng!",
            "Hàng giao chậm, chất lượng tệ",
            "Du lịch Đà Nẵng thật vui",
            "Các bạn nên thử sản phẩm này",
            
            # Should be REVIEW or REJECT
            "Đồ rác vãi lồn",
            "Thằng shop này lừa đảo",
            
            # Should be REJECT
            "Bọn khỉ đen này ngu vãi",
        ]
        
        for text in test_texts:
            result = inference.predict(text)
            action = result.get('action', 'unknown')
            confidence = result.get('confidence', 0)
            method = result.get('method', 'unknown')
            
            icon = "✅" if action == 'allowed' else ("⚠️" if action == 'review' else "🚫")
            print(f"\n{icon} [{action.upper()}] {confidence:.1%} | {text[:50]}...")
            print(f"   Method: {method}")
            if result.get('reasoning'):
                print(f"   Reason: {result['reasoning'][:80]}...")
    
    except Exception as e:
        print(f"⚠️ Could not run full inference test: {e}")
        print("   (This is expected if running without full model setup)")


def main():
    print("\n" + "🚀" * 40)
    print("ENHANCED MODERATION ACCURACY TEST")
    print("🚀" * 40)
    
    # Test 1: Context Analyzer
    passed1, failed1 = test_context_analyzer()
    
    # Test 2: Safe Context Detection
    passed2, failed2 = test_safe_context_detection()
    
    # Test 3: Severity Modifier
    test_severity_modifier()
    
    # Test 4: Full Inference (optional)
    test_inference_with_context()
    
    # Summary
    total_passed = passed1 + passed2
    total_failed = failed1 + failed2
    
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_passed + total_failed}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {total_passed/(total_passed+total_failed)*100:.1f}%")
    
    if total_failed == 0:
        print("\n🎉 All tests passed! Enhanced moderation is working correctly.")
    else:
        print(f"\n⚠️ {total_failed} tests failed. Please review the results above.")


if __name__ == "__main__":
    main()
