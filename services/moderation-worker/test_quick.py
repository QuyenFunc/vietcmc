#!/usr/bin/env python3
"""Quick test for improved moderation"""

from nlp.inference import ModerationInference

print("Loading model...")
model = ModerationInference()
print("Model loaded!\n")

test_cases = [
    "Tốt",
    "Khá tốt", 
    "Rất tốt",
    "Đẹp",
    "Ngon",
    "Tệ",
    "Không tốt",
    "Đồ ngu",
]

for text in test_cases:
    result = model.predict(text)
    print(f"Text: '{text}'")
    print(f"  Sentiment: {result['sentiment']}")
    print(f"  Moderation: {result['moderation_result']}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Reasoning: {result['reasoning']}")
    print()

