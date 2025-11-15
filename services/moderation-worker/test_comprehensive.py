"""
Comprehensive Test Suite for Moderation System v3.0
Tests all categories and edge cases
"""

import sys
import os
import io

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nlp.inference import ModerationInference

def run_comprehensive_tests():
    """Run comprehensive tests across all categories"""
    
    engine = ModerationInference(model_path='vinai/phobert-base-v2', device='cpu')
    
    test_suites = {
        '🔴 HATE SPEECH - LGBTQ+': [
            ('Bọn gay đáng bị khinh thường', 'reject'),
            ('Gay đáng ghét', 'reject'),
            ('Đồ pê đê', 'reject'),
            ('Thằng gay bệnh hoạn', 'reject'),
            ('Họ là gay và tôi tôn trọng', 'allowed'),  # Neutral mention
        ],
        '🔴 HATE SPEECH - Racism': [
            ('Đồ tàu khựa', 'reject'),
            ('Bọn khỉ đen', 'reject'),
            ('Mọi rợ rừng núi', 'reject'),
            ('Người Trung Quốc rất thông minh', 'allowed'),  # Neutral/positive
        ],
        '🔴 SEXUAL CONTENT - Explicit': [
            ('Gái xinh bú cu giỏi nhỉ', 'reject'),
            ('Bú lồn ngon', 'reject'),
            ('Chịch nhau sướng', 'reject'),
            ('Blowjob skills', 'reject'),
        ],
        '🔴 SEXUAL CONTENT - Solicitation': [
            ('Đi nhà nghỉ không em', 'reject'),
            ('Bao nhiêu một đêm', 'reject'),
            ('Ngủ với anh đi', 'reject'),
            ('Đi xem phim không', 'allowed'),  # Normal invite
        ],
        '🟠 PROFANITY - Severe': [
            ('Đụ má', 'reject'),
            ('Vãi lồn', 'reject'),
            ('Cái cặc', 'reject'),
            ('Địt mẹ', 'reject'),
            ('Fuck you', 'reject'),
        ],
        '🟠 PROFANITY - Variants/Bypass': [
            ('d.u.m', 'reject'),  # Dot separator
            ('l0n', 'reject'),  # Leet speak
            ('c@c', 'reject'),  # Symbol replacement
            ('đ ụ', 'reject'),  # Space separator
        ],
        '🟡 INSULTS - Personal Attack': [
            ('Mày ngu vcl', 'reject'),
            ('Thằng khốn', 'reject'),
            ('Đồ rác rưởi', 'reject'),
            ('Ngu như lợn', 'reject'),
        ],
        '✅ CONTEXT AWARENESS - Opinion': [
            ('Quan điểm ngu ngốc', 'allowed'),  # Opinion criticism
            ('Ý kiến này ngu', 'allowed'),
            ('Cái tư tưởng ngu', 'allowed'),
        ],
        '✅ CONTEXT AWARENESS - Product': [
            ('Sản phẩm tệ quá', 'allowed'),
            ('Dịch vụ kém', 'allowed'),
            ('Shop lừa đảo', 'review'),  # May need review
            ('Chất lượng rác', 'allowed'),
        ],
        '✅ LEGITIMATE NEGATIVE': [
            ('Không hài lòng với đơn hàng', 'allowed'),
            ('Thất vọng về chất lượng', 'allowed'),
            ('Giá đắt quá', 'allowed'),
            ('Giao hàng chậm', 'allowed'),
        ],
        '✅ POSITIVE CONTENT': [
            ('Sản phẩm tốt lắm', 'allowed'),
            ('Rất hài lòng', 'allowed'),
            ('Tuyệt vời', 'allowed'),
            ('Chất lượng tốt', 'allowed'),
        ],
    }
    
    print("="*100)
    print("COMPREHENSIVE MODERATION SYSTEM TEST SUITE")
    print("="*100)
    print()
    
    total_passed = 0
    total_failed = 0
    suite_results = {}
    
    for suite_name, test_cases in test_suites.items():
        print(f"\n{'='*100}")
        print(f"{suite_name}")
        print(f"{'='*100}")
        
        passed = 0
        failed = 0
        
        for text, expected in test_cases:
            result = engine.predict(text)
            actual = result['moderation_result']
            
            status = '✅' if actual == expected else '❌'
            
            if actual == expected:
                passed += 1
                total_passed += 1
            else:
                failed += 1
                total_failed += 1
                
            print(f"{status} [{expected.upper():6s} → {actual.upper():6s}] {text[:60]}")
            
            # Show details for failures
            if actual != expected:
                print(f"     Reason: {result['reasoning']}")
                print(f"     Score: {result.get('toxicity_score', 'N/A')}")
        
        suite_results[suite_name] = {
            'passed': passed,
            'failed': failed,
            'total': len(test_cases)
        }
        
        success_rate = (passed / len(test_cases)) * 100
        print(f"\n{suite_name}: {passed}/{len(test_cases)} ({success_rate:.1f}%)")
    
    # Summary
    print(f"\n{'='*100}")
    print("📊 SUMMARY")
    print(f"{'='*100}")
    print()
    
    for suite_name, results in suite_results.items():
        rate = (results['passed'] / results['total']) * 100
        status = '✅' if rate >= 90 else '⚠️' if rate >= 70 else '❌'
        print(f"{status} {suite_name:45s} {results['passed']:2d}/{results['total']:2d} ({rate:5.1f}%)")
    
    print(f"\n{'='*100}")
    total = total_passed + total_failed
    overall_rate = (total_passed / total) * 100
    print(f"🎯 OVERALL: {total_passed}/{total} ({overall_rate:.1f}%)")
    
    if overall_rate >= 95:
        print("✅ EXCELLENT - System performing at enterprise level!")
    elif overall_rate >= 85:
        print("✅ GOOD - System performing well, minor tuning recommended")
    elif overall_rate >= 75:
        print("⚠️ FAIR - System needs tuning")
    else:
        print("❌ POOR - System requires major improvements")
    
    print("="*100)
    
    return overall_rate >= 90

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)

