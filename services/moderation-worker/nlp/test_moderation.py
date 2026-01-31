"""
Comprehensive Test Suite for Vietnamese Content Moderation
==========================================================

Tests all 3 layers:
- Layer A: Text normalization & anti-obfuscation
- Layer B: Enhanced rule-based check
- Layer C: ML model (integration test if available)

Categories tested:
- Profanity (standard + obfuscated)
- Hate speech (racism, xenophobia, LGBTQ+)
- Harassment / Body-shaming
- Sexual content
- Safe content (false positive prevention)

Version: 1.0.0
Last Updated: 2026-01-30
"""

import logging
import sys
import os
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules
try:
    from nlp.text_normalizer import get_normalizer
    from nlp.rule_checker import get_rule_checker
    from nlp.moderation_pipeline import ThreeLayerModerationPipeline
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    MODULES_AVAILABLE = False


# ==================== TEST CASES ====================

# Format: (input_text, expected_action, expected_labels, description)
# expected_action: 'reject', 'review', 'allowed'
# expected_labels: list of labels that should be present (can be empty for 'allowed')

TEST_CASES = {
    # ===== PROFANITY: Standard =====
    'profanity_standard': [
        ("đm mày", 'reject', ['profanity', 'toxicity'], "Direct profanity - đm"),
        ("vcl", 'reject', ['profanity', 'toxicity'], "Abbreviation - vcl"),
        ("dm con chó", 'reject', ['profanity', 'toxicity'], "DM with context"),
        ("đcm mày ngu", 'reject', ['profanity', 'toxicity'], "DCM variant"),
        ("địt mẹ mày", 'reject', ['profanity', 'toxicity'], "Full phrase"),
        ("đụ má", 'reject', ['profanity', 'toxicity'], "Đụ má variant"),
        ("vl luôn", 'reject', ['profanity', 'toxicity'], "VL abbreviation"),
        ("clm", 'reject', ['profanity', 'toxicity'], "CLM abbreviation"),
        ("ctm", 'reject', ['profanity', 'toxicity'], "CTM abbreviation"),
    ],
    
    # ===== PROFANITY: Obfuscated =====
    'profanity_obfuscated': [
        ("d.m", 'reject', ['profanity', 'toxicity'], "Dot separator"),
        ("đ.m", 'reject', ['profanity', 'toxicity'], "Dot separator with đ"),
        ("d:m", 'reject', ['profanity', 'toxicity'], "Colon separator"),
        ("d:m,m", 'reject', ['profanity', 'toxicity'], "Multiple separators"),
        ("d*m", 'reject', ['profanity', 'toxicity'], "Asterisk separator"),
        ("d-m", 'reject', ['profanity', 'toxicity'], "Dash separator"),
        ("d_m", 'reject', ['profanity', 'toxicity'], "Underscore separator"),
        ("d  m", 'reject', ['profanity', 'toxicity'], "Double space"),
        ("đ.ị.t", 'reject', ['profanity', 'toxicity'], "Full obfuscation"),
        ("l.o.n", 'reject', ['profanity', 'toxicity'], "LON obfuscated"),
        ("c.a.c", 'reject', ['profanity', 'toxicity'], "CAC obfuscated - should NOT match 'các'"),
        ("v.c.l", 'reject', ['profanity', 'toxicity'], "VCL obfuscated"),
        ("dмм", 'reject', ['profanity', 'toxicity'], "Cyrillic м"),
        ("νcl", 'reject', ['profanity', 'toxicity'], "Greek ν"),
        ("ｄｍ", 'reject', ['profanity', 'toxicity'], "Full-width chars"),
        ("đ​m​m", 'reject', ['profanity', 'toxicity'], "Zero-width spaces"),
        ("d1t me", 'reject', ['profanity', 'toxicity'], "Leetspeak 1=i"),
        ("l0n", 'reject', ['profanity', 'toxicity'], "Leetspeak 0=o"),
        ("c@c", 'reject', ['profanity', 'toxicity'], "Leetspeak @=a"),
    ],
    
    # ===== PROFANITY: Context-dependent (NGU) =====
    'profanity_ngu': [
        ("ngu quá", 'review', ['insult'], "Ngu with intensifier"),
        ("ngu ngốc", 'review', ['insult'], "Ngu ngốc compound"),
        ("thằng này ngu", 'review', ['insult'], "Targeting with ngu"),
        ("đồ ngu ngốc", 'review', ['insult'], "Đồ ngu ngốc pattern"),
        ("n.g.u", 'review', ['insult', 'obfuscation_bypass'], "Obfuscated ngu"),
        ("não cá vàng", 'review', ['insult'], "Brain insult"),
        ("đầu đất", 'review', ['insult'], "Head insult"),
    ],
    
    # ===== HATE SPEECH: Racism =====
    'hate_speech_racism': [
        ("Bọn da đen bẩn thỉu cút về nước đi", 'reject', ['hate', 'racism'], "Anti-black racism"),
        ("bọn da đen", 'reject', ['hate', 'racism'], "Group targeting blacks"),
        ("lũ mọi đen", 'reject', ['hate', 'racism'], "Derogatory term for blacks"),
        ("khỉ đen", 'reject', ['hate', 'racism'], "Animal dehumanization"),
        ("tàu khựa", 'reject', ['hate', 'racism'], "Anti-Chinese slur"),
        ("bọn tàu", 'reject', ['hate', 'racism'], "Group targeting Chinese"),
        ("lũ tàu cộng", 'reject', ['hate', 'racism'], "Political anti-Chinese"),
    ],
    
    # ===== HATE SPEECH: LGBTQ+ =====
    'hate_speech_lgbtq': [
        ("đồ gay", 'reject', ['hate', 'lgbtq_discrimination'], "Anti-gay insult"),
        ("bọn pê đê", 'reject', ['hate', 'lgbtq_discrimination'], "Anti-gay slur"),
        ("thằng bê đê", 'reject', ['hate', 'lgbtq_discrimination'], "Individual targeting"),
        ("gay đáng chết", 'reject', ['hate', 'lgbtq_discrimination'], "Death wish"),
    ],
    
    # ===== HATE SPEECH: Xenophobia =====
    'hate_speech_xenophobia': [
        ("cút về nước đi bọn da đen", 'reject', ['hate', 'xenophobia'], "Xenophobic + racial"),
        ("biến đi người nước ngoài", 'reject', ['hate', 'xenophobia'], "Anti-foreigner with context"),
    ],
    
    # ===== HARASSMENT: Body-shaming =====
    'harassment_bodyshaming': [
        ("Sao mày xấu thế, nhìn mặt mày tao muốn nôn", 'reject', ['harassment', 'body_shaming'], "Severe body-shaming - escalated"),
        ("mày xấu quá", 'review', ['harassment', 'body_shaming'], "Simple body-shaming"),
        ("mặt mày ghê tởm", 'reject', ['harassment', 'body_shaming'], "Severe expression - escalated"),
        ("nó xấu xí kinh tởm", 'reject', ['harassment', 'body_shaming'], "Multiple severe expressions"),
        ("mày xấu", 'review', ['harassment', 'body_shaming'], "Basic body-shaming"),
        ("mi bẩn thỉu", 'review', ['harassment', 'body_shaming'], "Cleanliness attack"),
    ],
    
    # ===== HARASSMENT: Personal attacks =====
    'harassment_personal': [
        ("đồ ngu", 'review', ['harassment', 'insult'], "Đồ ngu pattern"),
        ("thằng khốn", 'review', ['harassment', 'insult'], "Thằng + insult"),
        ("con điên", 'review', ['harassment', 'insult'], "Con + insult"),
        ("đồ vô dụng", 'review', ['harassment', 'insult'], "Đồ vô dụng"),
        ("đồ súc vật", 'review', ['harassment', 'insult'], "Dehumanizing"),
    ],
    
    # ===== SAFE CONTENT: Valid feedback =====
    'safe_feedback': [
        ("Sản phẩm tốt quá", 'allowed', [], "Positive feedback"),
        ("Tôi không hài lòng với dịch vụ", 'allowed', [], "Valid complaint"),
        ("Sản phẩm tệ quá, thất vọng", 'allowed', [], "Negative but valid feedback"),
        ("Chất lượng không như mong đợi", 'allowed', [], "Disappointed but valid"),
        ("Giao hàng chậm, cần cải thiện", 'allowed', [], "Constructive criticism"),
        ("Mình không recommend sản phẩm này", 'allowed', [], "Honest review"),
        ("Tệ quá, 1 sao", 'allowed', [], "Low rating but valid"),
    ],
    
    # ===== SAFE CONTENT: False positive prevention =====
    'safe_false_positives': [
        ("Lon bia này ngon", 'allowed', [], "Lon bia context"),
        ("Nước lon pepsi", 'allowed', [], "Lon nước context"),
        ("Các bạn có khỏe không?", 'allowed', [], "Các bạn - not cặc"),
        ("Hài lòng với dịch vụ", 'allowed', [], "Lòng - not lồn"),
        ("Các loại sản phẩm", 'allowed', [], "Các loại - not cặc"),
        ("Một cách tiện lợi", 'allowed', [], "Cách - not cặc"),
        ("Du lịch Đà Nẵng", 'allowed', [], "Du lịch - not đụ"),
        ("Du học sinh", 'allowed', [], "Du học - not đụ"),
        ("Nguyễn văn A", 'allowed', [], "Nguồn - not ngu"),
        ("Nguồn gốc sản phẩm", 'allowed', [], "Nguồn - not ngu"),
        ("Người bán hàng tốt", 'allowed', [], "Người - not ngu"),
        ("Tấm lòng nhân ái", 'allowed', [], "Lòng - not lồn"),
    ],
    
    # ===== EDGE CASES =====
    'edge_cases': [
        ("", 'allowed', [], "Empty string"),
        ("   ", 'allowed', [], "Whitespace only"),
        ("👍👍👍", 'allowed', [], "Emoji only"),
        ("1234567890", 'allowed', [], "Numbers only"),
        ("abc", 'allowed', [], "Short text"),
        ("OK", 'allowed', [], "Very short text"),
        # Mixed content
        ("Sản phẩm dm tốt", 'reject', ['profanity', 'toxicity'], "DM hidden in sentence"),
        ("dm sản phẩm tốt", 'reject', ['profanity', 'toxicity'], "DM at start"),
        ("sản phẩm tốt dm", 'reject', ['profanity', 'toxicity'], "DM at end"),
    ],
}


# ==================== TEST RUNNER ====================

class TestRunner:
    """Run comprehensive tests and generate report"""
    
    def __init__(self):
        self.normalizer = get_normalizer()
        self.rule_checker = get_rule_checker()
        self.pipeline = ThreeLayerModerationPipeline(
            text_model=None,  # Rule-based only
            use_rule_based=True,
            use_ml_model=False,
        )
        
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'categories': {},
        }
        self.failures = []
    
    def run_single_test(self, text: str, expected_action: str, expected_labels: List[str], description: str) -> bool:
        """Run a single test case"""
        result = self.pipeline.predict(text)
        
        actual_action = result.get('action', 'unknown')
        actual_labels = set(result.get('labels', []))
        expected_labels_set = set(expected_labels)
        
        # Check action
        action_match = actual_action == expected_action
        
        # Check labels (expected should be subset of actual for reject/review)
        if expected_action in ['reject', 'review']:
            labels_match = expected_labels_set.issubset(actual_labels)
        else:
            labels_match = len(actual_labels) == 0 or expected_labels_set == actual_labels
        
        passed = action_match and labels_match
        
        if not passed:
            self.failures.append({
                'text': text,
                'description': description,
                'expected_action': expected_action,
                'actual_action': actual_action,
                'expected_labels': list(expected_labels_set),
                'actual_labels': list(actual_labels),
                'reasoning': result.get('reasoning', ''),
            })
        
        return passed
    
    def run_category(self, category: str, test_cases: List[Tuple]) -> Dict:
        """Run all tests in a category"""
        category_results = {
            'total': len(test_cases),
            'passed': 0,
            'failed': 0,
        }
        
        for text, expected_action, expected_labels, description in test_cases:
            self.results['total'] += 1
            
            if self.run_single_test(text, expected_action, expected_labels, description):
                self.results['passed'] += 1
                category_results['passed'] += 1
            else:
                self.results['failed'] += 1
                category_results['failed'] += 1
        
        self.results['categories'][category] = category_results
        return category_results
    
    def run_all(self) -> Dict:
        """Run all test categories"""
        print("=" * 80)
        print("COMPREHENSIVE CONTENT MODERATION TEST SUITE")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        for category, test_cases in TEST_CASES.items():
            print(f"\n📋 Testing: {category}")
            results = self.run_category(category, test_cases)
            
            status = "✅" if results['failed'] == 0 else "❌"
            print(f"   {status} {results['passed']}/{results['total']} passed")
        
        return self.results
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total = self.results['total']
        passed = self.results['passed']
        failed = self.results['failed']
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n📊 Overall: {passed}/{total} tests passed ({pass_rate:.1f}%)")
        
        print("\n📁 By Category:")
        for category, cat_results in self.results['categories'].items():
            status = "✅" if cat_results['failed'] == 0 else "❌"
            cat_rate = (cat_results['passed'] / cat_results['total'] * 100) if cat_results['total'] > 0 else 0
            print(f"   {status} {category}: {cat_results['passed']}/{cat_results['total']} ({cat_rate:.1f}%)")
        
        if self.failures:
            print("\n❌ FAILURES:")
            print("-" * 60)
            for i, failure in enumerate(self.failures[:10], 1):  # Show first 10
                print(f"\n{i}. {failure['description']}")
                print(f"   Input: '{failure['text']}'")
                print(f"   Expected: {failure['expected_action']} with {failure['expected_labels']}")
                print(f"   Actual: {failure['actual_action']} with {failure['actual_labels']}")
                if failure['reasoning']:
                    print(f"   Reason: {failure['reasoning'][:60]}...")
            
            if len(self.failures) > 10:
                print(f"\n   ... and {len(self.failures) - 10} more failures")
        
        print("\n" + "=" * 80)
        
        return pass_rate >= 90  # Return True if pass rate >= 90%


# ==================== MAIN ====================

def main():
    """Main entry point"""
    if not MODULES_AVAILABLE:
        print("❌ Required modules not available. Exiting.")
        return False
    
    logging.basicConfig(level=logging.WARNING)  # Reduce noise
    
    runner = TestRunner()
    runner.run_all()
    success = runner.print_summary()
    
    if success:
        print("\n🎉 TEST SUITE PASSED!")
    else:
        print("\n⚠️ TEST SUITE NEEDS ATTENTION")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
