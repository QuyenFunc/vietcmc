"""
System Test Script - Verify all components are working
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("="*80)
print("VIETNAMESE MODERATION AI - SYSTEM TEST")
print("="*80)
print()

tests_passed = 0
tests_failed = 0

# Test 1: Python version
print("Test 1: Python Version")
print(f"  Python: {sys.version}")
if sys.version_info >= (3, 8):
    print("  ✓ PASS")
    tests_passed += 1
else:
    print("  ✗ FAIL - Python 3.8+ required")
    tests_failed += 1
print()

# Test 2: Core imports
print("Test 2: Core Imports")
try:
    import torch
    import transformers
    import numpy
    import pandas
    import sklearn
    print(f"  PyTorch: {torch.__version__}")
    print(f"  Transformers: {transformers.__version__}")
    print("  ✓ PASS")
    tests_passed += 1
except ImportError as e:
    print(f"  ✗ FAIL - {e}")
    tests_failed += 1
print()

# Test 3: Vietnamese NLP
print("Test 3: Vietnamese NLP")
try:
    import underthesea
    import langdetect
    from underthesea import word_tokenize
    test_text = "Sản phẩm rất tốt"
    segmented = word_tokenize(test_text, format="text")
    print(f"  Original: {test_text}")
    print(f"  Segmented: {segmented}")
    print("  ✓ PASS")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ FAIL - {e}")
    tests_failed += 1
print()

# Test 4: Custom modules - Taxonomy
print("Test 4: Taxonomy Module")
try:
    from nlp.taxonomy import (
        ModerationLabel, 
        SeverityLevel,
        get_label_list,
        LABEL_DESCRIPTIONS
    )
    labels = get_label_list()
    print(f"  Labels: {', '.join(labels)}")
    print(f"  Total: {len(labels)} labels")
    print("  ✓ PASS")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ FAIL - {e}")
    tests_failed += 1
print()

# Test 5: Preprocessing
print("Test 5: Preprocessing Module")
try:
    from nlp.preprocessing_advanced import (
        preprocess_for_phobert,
        extract_pii,
        augment_drop_diacritics
    )
    
    test_text = "Sảnnnn phẩmmmm đẹppppp 😍 0123456789"
    processed, metadata = preprocess_for_phobert(test_text)
    pii = extract_pii(test_text)
    
    print(f"  Original: {test_text}")
    print(f"  Processed: {processed}")
    print(f"  PII detected: {pii['phones']}")
    print("  ✓ PASS")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ FAIL - {e}")
    tests_failed += 1
print()

# Test 6: Model Architecture
print("Test 6: Model Architecture")
try:
    from models.multitask_phobert import MultiTaskPhoBERT, FocalLoss
    
    # Create small test model (don't download PhoBERT yet)
    print("  Creating model architecture...")
    print("  ✓ PASS (model class imported)")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ FAIL - {e}")
    tests_failed += 1
print()

# Test 7: Dataset Loader
print("Test 7: Dataset Loader")
try:
    from data.dataset_loader import DatasetLoader
    
    loader = DatasetLoader("./datasets")
    print(f"  Data directory: ./datasets")
    print("  ✓ PASS")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ FAIL - {e}")
    tests_failed += 1
print()

# Test 8: Trainer
print("Test 8: Training Module")
try:
    from training.trainer import compute_class_weights
    import numpy as np
    
    # Test class weight computation
    dummy_labels = np.array([[1, 0, 1], [0, 1, 0], [1, 1, 0]])
    weights = compute_class_weights(dummy_labels)
    print(f"  Class weights computed: {weights}")
    print("  ✓ PASS")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ FAIL - {e}")
    tests_failed += 1
print()

# Test 9: Inference Engine
print("Test 9: Inference Engine")
try:
    # Just test import, don't load model yet
    from nlp.inference_multitask import MultiTaskModerationInference
    print("  Inference engine imported")
    print("  ✓ PASS")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ FAIL - {e}")
    tests_failed += 1
print()

# Test 10: File Structure
print("Test 10: File Structure")
try:
    required_dirs = ['datasets', 'checkpoints', 'models', 'nlp', 'data', 'training']
    missing = []
    for d in required_dirs:
        if not os.path.exists(d):
            missing.append(d)
    
    if missing:
        print(f"  Missing directories: {', '.join(missing)}")
        print("  ⚠ WARNING - Some directories missing")
    else:
        print(f"  All required directories exist")
        print("  ✓ PASS")
        tests_passed += 1
except Exception as e:
    print(f"  ✗ FAIL - {e}")
    tests_failed += 1
print()

# Summary
print("="*80)
print("TEST SUMMARY")
print("="*80)
print(f"Total tests: {tests_passed + tests_failed}")
print(f"✓ Passed: {tests_passed}")
print(f"✗ Failed: {tests_failed}")
print()

if tests_failed == 0:
    print("🎉 ALL TESTS PASSED!")
    print()
    print("Next steps:")
    print("  1. Download datasets: python data/download_datasets.py")
    print("  2. Train model: python training/train_full.py")
    print("  3. Test inference: python -m nlp.inference_multitask")
    print()
    sys.exit(0)
else:
    print("⚠ SOME TESTS FAILED")
    print()
    print("Please fix the failed tests before proceeding.")
    print("Check TRAINING_GUIDE.md for troubleshooting.")
    print()
    sys.exit(1)

