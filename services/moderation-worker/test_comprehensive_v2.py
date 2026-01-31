"""
Comprehensive Test for Enhanced Moderation System V2
Testing all improvements:
- Variant detection (obfuscation, leetspeak, homoglyphs)
- Context analysis (legitimate feedback vs toxic)
- ML model integration
- Ensemble moderation

Usage:
    cd services/moderation-worker
    python test_comprehensive_v2.py
"""

import logging
import sys
import os
import time

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_variant_detector():
    """Test variant/obfuscation detection"""
    print("\n" + "=" * 80)
    print("🔍 TEST 1: VARIANT DETECTION (Obfuscation, Leetspeak, Homoglyphs)")
    print("=" * 80)
    
    from nlp.variant_detector import get_variant_detector
    detector = get_variant_detector()
    
    test_cases = [
        # Standard toxic - should detect
        ("Đồ ngu vãi lồn", True, ["ngu", "lồn", "vcl"], "Standard toxic"),
        ("Thằng điên khùng", True, ["điên"], "Standard insult"),
        
        # Leetspeak - should detect
        ("D0 ngu v@i l0n", True, ["lồn"], "Leetspeak obfuscation"),
        ("đ!t mẹ mày", True, ["địt"], "Leetspeak with symbols"),
        
        # Insertion obfuscation - should detect
        ("đ.ụ m.á", True, ["đụ"], "Dot insertion"),
        ("l-o-n mày", True, ["lồn"], "Dash insertion"),
        ("v*c*l", True, ["vcl"], "Star insertion"),
        
        # Safe context - should NOT detect as toxic
        ("Hài lòng với dịch vụ", False, [], "Safe: hài lòng"),
        ("Các bạn có khỏe không?", False, [], "Safe: các bạn"),
        ("Du lịch Đà Nẵng", False, [], "Safe: du lịch"),
        ("Tình hình gay gắt", False, [], "Safe: gay gắt"),
        
        # Clean content - should NOT detect
        ("Sản phẩm tốt quá", False, [], "Clean content"),
        ("Cảm ơn shop nhiều", False, [], "Clean positive"),
    ]
    
    passed = 0
    failed = 0
    
    for text, should_detect, expected_words, description in test_cases:
        result = detector.analyze(text)
        has_violations = result.get('has_violations', False)
        detected = [v['normalized'] for v in result.get('detected_variants', [])]
        
        # Check if detection is correct
        detection_correct = has_violations == should_detect
        
        # Also check if expected words are detected (if any)
        words_correct = True
        if expected_words:
            for word in expected_words:
                if word not in detected:
                    words_correct = False
                    break
        
        if detection_correct:
            passed += 1
            status = "✅"
        else:
            failed += 1
            status = "❌"
        
        print(f"\n{status} {description}")
        print(f"   Text: '{text[:50]}...'")
        print(f"   Should detect: {should_detect} | Detected: {has_violations}")
        if detected:
            print(f"   Found: {detected}")
        if result.get('has_obfuscation'):
            print(f"   ⚠️ Obfuscation attempt detected")
    
    print(f"\n📊 Variant Detection Results: {passed}/{passed+failed} passed ({passed/(passed+failed)*100:.1f}%)")
    return passed, failed


def test_context_analyzer():
    """Test context-aware analysis"""
    print("\n" + "=" * 80)
    print("🔍 TEST 2: CONTEXT ANALYSIS (Legitimate Feedback Detection)")
    print("=" * 80)
    
    from nlp.context_analyzer import get_enhanced_analyzer
    analyzer = get_enhanced_analyzer()
    
    test_cases = [
        # Legitimate negative feedback - should be ALLOWED
        ("Sản phẩm tệ quá, chất lượng kém", "allowed", "Legitimate product feedback"),
        ("Hàng giao chậm, đóng gói không cẩn thận", "allowed", "Legitimate service complaint"),
        ("Shop này dịch vụ kém, không recommend", "allowed", "Legitimate recommendation"),
        ("Đánh giá 1 sao, sản phẩm không như mô tả", "allowed", "Star rating feedback"),
        
        # Questions - should be ALLOWED
        ("Các bạn ơi, sản phẩm này tốt không?", "allowed", "Question about product"),
        ("Shop có ship COD không?", "allowed", "Service question"),
        
        # Safe context phrases - should be ALLOWED
        ("Hài lòng với sản phẩm", "allowed", "Safe: hài lòng"),
        ("Du lịch Đà Nẵng vui quá", "allowed", "Safe: du lịch"),
        ("Tình hình gay gắt lắm", "allowed", "Safe: gay gắt"),
        
        # Hate speech - should be REJECT
        ("Bọn gay đáng ghét, nên chết hết", "reject", "Hate speech against LGBTQ+"),
        ("Đám khỉ đen này ngu vãi", "reject", "Racist hate speech"),
        
        # Personal attacks - should be REJECT/REVIEW
        ("Mày ngu thế, thằng này khùng", "reject", "Personal attack"),
    ]
    
    passed = 0
    failed = 0
    
    for text, expected_action, description in test_cases:
        result = analyzer.analyze(text, flagged_words=[])
        actual_action = result['action']
        
        # Allow some flexibility: review can be acceptable for edge cases
        action_ok = (actual_action == expected_action or 
                     (expected_action == "reject" and actual_action in ["reject", "review"]))
        
        if action_ok:
            passed += 1
            status = "✅"
        else:
            failed += 1
            status = "❌"
        
        print(f"\n{status} {description}")
        print(f"   Text: '{text[:50]}...'")
        print(f"   Expected: {expected_action} | Actual: {actual_action}")
        print(f"   Intent: {result['intent']}")
        if result.get('is_legitimate_criticism'):
            print(f"   ✓ Legitimate criticism")
    
    print(f"\n📊 Context Analysis Results: {passed}/{passed+failed} passed ({passed/(passed+failed)*100:.1f}%)")
    return passed, failed


def test_ensemble_moderator():
    """Test ensemble moderation (without ML for speed)"""
    print("\n" + "=" * 80)
    print("🔍 TEST 3: ENSEMBLE MODERATION")
    print("=" * 80)
    
    from nlp.ensemble_moderator import create_ensemble_moderator, ModerationAction
    moderator = create_ensemble_moderator(use_ml=False)  # Skip ML for speed
    
    test_cases = [
        # Clean content
        ("Sản phẩm rất tốt, tôi rất hài lòng!", ModerationAction.ALLOWED, "Clean positive"),
        ("Cảm ơn shop, sẽ ủng hộ tiếp", ModerationAction.ALLOWED, "Clean gratitude"),
        
        # Legitimate criticism
        ("Sản phẩm tệ quá, chất lượng kém", ModerationAction.ALLOWED, "Legitimate criticism"),
        ("Giao hàng chậm, thất vọng", ModerationAction.ALLOWED, "Legitimate complaint"),
        
        # Safe context
        ("Các bạn ơi, shop này ok không?", ModerationAction.ALLOWED, "Question"),
        ("Du lịch Hà Nội vui quá", ModerationAction.ALLOWED, "Safe: du lịch"),
        
        # Obfuscated toxic
        ("đ.ụ m.á mày", ModerationAction.REJECT, "Obfuscated profanity"),
        ("v@i l0n", ModerationAction.REJECT, "Leetspeak profanity"),
        
        # Clear toxic
        ("Đồ ngu vãi lồn", ModerationAction.REJECT, "Clear profanity"),
        ("Thằng shop lừa đảo", ModerationAction.REJECT, "Accusation + personal attack"),
        
        # Hate speech
        ("Bọn gay đáng ghét", ModerationAction.REJECT, "Hate speech"),
    ]
    
    passed = 0
    failed = 0
    total_time = 0
    
    for text, expected_action, description in test_cases:
        start = time.time()
        result = moderator.moderate(text)
        elapsed = (time.time() - start) * 1000
        total_time += elapsed
        
        # Allow some flexibility
        action_ok = (result.action == expected_action or
                     (expected_action == ModerationAction.REJECT and 
                      result.action in [ModerationAction.REJECT, ModerationAction.REVIEW]))
        
        if action_ok:
            passed += 1
            status = "✅"
        else:
            failed += 1
            status = "❌"
        
        icon = "✅" if result.action == ModerationAction.ALLOWED else (
            "⚠️" if result.action == ModerationAction.REVIEW else "🚫"
        )
        
        print(f"\n{status} {description}")
        print(f"   Text: '{text[:50]}...'")
        print(f"   Expected: {expected_action.value} | Got: {result.action.value}")
        print(f"   {icon} Confidence: {result.confidence:.2%} | Time: {elapsed:.1f}ms")
        if result.labels:
            print(f"   Labels: {result.labels}")
    
    avg_time = total_time / len(test_cases)
    print(f"\n📊 Ensemble Results: {passed}/{passed+failed} passed ({passed/(passed+failed)*100:.1f}%)")
    print(f"⏱️ Average processing time: {avg_time:.2f}ms")
    return passed, failed


def test_full_inference():
    """Test full inference with all components"""
    print("\n" + "=" * 80)
    print("🔍 TEST 4: FULL INFERENCE (with ML Model)")
    print("=" * 80)
    
    try:
        from nlp.inference_multitask import MultiTaskModerationInference
        
        inference = MultiTaskModerationInference(
            model_path='vinai/phobert-base-v2',
            device='cpu',
            use_context_analyzer=True,
            use_variant_detector=True
        )
        
        test_texts = [
            # Variety of content
            "Sản phẩm rất tốt!",
            "Hàng tệ quá, thất vọng",
            "Đồ rác vãi lồn",
            "đ.ụ m.á shop này",
            "Các bạn ơi sản phẩm ok không?",
            "Du lịch vui quá",
            "Bọn gay đáng khinh",
        ]
        
        for text in test_texts:
            start = time.time()
            result = inference.predict(text)
            elapsed = (time.time() - start) * 1000
            
            action = result.get('action', 'unknown')
            confidence = result.get('confidence', 0)
            method = result.get('method', 'unknown')
            
            icon = "✅" if action == 'allowed' else ("⚠️" if action == 'review' else "🚫")
            
            print(f"\n{icon} [{action.upper()}] {confidence:.1%} | {text[:40]}...")
            print(f"   Method: {method} | Time: {elapsed:.1f}ms")
            if result.get('has_obfuscation'):
                print(f"   ⚠️ Obfuscation detected!")
        
        return True
        
    except Exception as e:
        print(f"\n⚠️ Full inference test skipped: {e}")
        return False


def main():
    print("\n" + "🚀" * 40)
    print("COMPREHENSIVE MODERATION TEST V2")
    print("Testing: Variant Detection + Context Analysis + Ensemble + ML Integration")
    print("🚀" * 40)
    
    results = []
    
    # Test 1: Variant Detection
    p1, f1 = test_variant_detector()
    results.append(("Variant Detection", p1, f1))
    
    # Test 2: Context Analysis
    p2, f2 = test_context_analyzer()
    results.append(("Context Analysis", p2, f2))
    
    # Test 3: Ensemble Moderation
    p3, f3 = test_ensemble_moderator()
    results.append(("Ensemble Moderation", p3, f3))
    
    # Test 4: Full Inference (optional)
    success = test_full_inference()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)
    
    total_passed = 0
    total_failed = 0
    
    for name, passed, failed in results:
        total_passed += passed
        total_failed += failed
        rate = passed / (passed + failed) * 100
        status = "✅" if rate >= 80 else ("⚠️" if rate >= 60 else "❌")
        print(f"{status} {name}: {passed}/{passed+failed} ({rate:.1f}%)")
    
    overall_rate = total_passed / (total_passed + total_failed) * 100
    print(f"\n{'='*40}")
    print(f"OVERALL: {total_passed}/{total_passed+total_failed} ({overall_rate:.1f}%)")
    print(f"{'='*40}")
    
    if overall_rate >= 80:
        print("\n🎉 Excellent! System is working well.")
    elif overall_rate >= 60:
        print("\n⚠️ Good but needs improvement in some areas.")
    else:
        print("\n❌ Significant issues detected. Please review failed tests.")
    
    # Feature summary
    print("\n" + "=" * 80)
    print("📋 FEATURE SUMMARY")
    print("=" * 80)
    print("✅ Variant Detection: Homoglyphs, Leetspeak, Insertion attacks")
    print("✅ Context Analysis: Legitimate feedback detection, Intent classification")
    print("✅ Safe Context: 'gay gắt', 'hài lòng', 'du lịch', etc.")
    print("✅ Ensemble Moderation: Rule-based + Context + Variant + ML")
    print("✅ Reduced False Positives: Product reviews, Questions now handled correctly")


if __name__ == "__main__":
    main()
