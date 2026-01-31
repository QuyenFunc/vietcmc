# -*- coding: utf-8 -*-
"""Test script to verify 'các' is not flagged as toxic"""

import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Pattern from toxic_words.py that matches "cặc" variants
pattern = r'\bc[aăắằẳẵặâấầẩẫậáảãạặ@][ckpc]\b'

# Words that should be whitelisted
common_words = {'các', 'cách', 'cục', 'cắc', 'cạc', 'cấc'}

# Test words
test_cases = [
    ('các', False, 'Common Vietnamese word - plural marker'),
    ('cách', False, 'Method/way'),
    ('cục', False, 'Block/department'),
    ('cặc', True, 'Vulgar word - should be caught'),
    ('cac', True, 'Non-accent version of cặc'),
]

print("=" * 60)
print("TEST: Pattern Matching False Positive Fix")
print("=" * 60)

passed = 0
failed = 0

for word, should_flag, description in test_cases:
    match = re.search(pattern, word, re.IGNORECASE)
    
    if match:
        matched_text = match.group().lower()
        # Check if whitelisted
        if matched_text in common_words:
            actually_flagged = False
        else:
            actually_flagged = True
    else:
        actually_flagged = False
    
    if actually_flagged == should_flag:
        status = "✅ PASS"
        passed += 1
    else:
        status = "❌ FAIL"
        failed += 1
    
    print(f"\n{status}: {description}")
    print(f"  Word: '{word}'")
    print(f"  Expected: {'FLAGGED' if should_flag else 'ALLOWED'}")
    print(f"  Got: {'FLAGGED' if actually_flagged else 'ALLOWED'}")
    if match:
        print(f"  Pattern matched: '{match.group()}'")
        print(f"  Whitelisted: {match.group().lower() in common_words}")

print("\n" + "=" * 60)
print(f"Results: {passed} passed, {failed} failed")
print("=" * 60)

# Test the full sentence
print("\n\n" + "=" * 60)
print("TEST: Full Sentence")
print("=" * 60)

sentence = "Đối tượng áp dụng, tất cả người nước ngoài cư trú các"
print(f"\nSentence: '{sentence}'")

matches = re.findall(pattern, sentence.lower(), re.IGNORECASE)
print(f"Matches found: {matches}")

# After whitelist filter
filtered_matches = [m for m in matches if m.lower() not in common_words]
print(f"After whitelist: {filtered_matches}")

if not filtered_matches:
    print("✅ RESULT: No violations - sentence is CLEAN")
else:
    print(f"❌ RESULT: Found violations: {filtered_matches}")
