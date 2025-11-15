# Vietnamese Content Moderation AI - Automated Setup Script (Windows PowerShell)
# This script automates the entire setup process for Windows

$ErrorActionPreference = "Stop"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "VIETNAMESE MODERATION AI - SETUP" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python version
Write-Host "Step 1: Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion"

try {
    python -c "import sys; assert sys.version_info >= (3, 8)"
    Write-Host "✓ Python version OK" -ForegroundColor Green
} catch {
    Write-Host "Error: Python 3.8+ required" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Create directories
Write-Host "Step 2: Creating directories..." -ForegroundColor Yellow
$directories = @("datasets", "checkpoints", "models", "data", "training", "logs")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✓ Directories created" -ForegroundColor Green
Write-Host ""

# Step 3: Install dependencies
Write-Host "Step 3: Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..."

# Update requirements.txt
@"
# Core ML
numpy==1.26.4
torch==2.1.1
transformers==4.35.2
scikit-learn==1.3.2

# Vietnamese NLP
underthesea==6.7.0
langdetect==1.0.9

# Data processing
pandas==2.1.4
openpyxl==3.1.2

# Optimization (optional but recommended)
onnxruntime==1.16.3
optimum[onnxruntime]==1.15.0

# Database & messaging
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
aio-pika==9.3.1

# Utils
python-dotenv==1.0.0
tqdm==4.66.1
requests==2.31.0

# Training & evaluation
tensorboard==2.15.1
matplotlib==3.8.2
seaborn==0.13.0
"@ | Out-File -FilePath requirements.txt -Encoding UTF8

pip install -r requirements.txt --quiet
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 4: Download datasets
Write-Host "Step 4: Downloading datasets..." -ForegroundColor Yellow
Write-Host "This will attempt to download Vietnamese moderation datasets"
try {
    python data/download_datasets.py --data-dir ./datasets --dataset all
} catch {
    Write-Host "⚠ Some datasets may require manual download" -ForegroundColor Yellow
    Write-Host "Please check TRAINING_GUIDE.md for download instructions"
}
Write-Host ""

# Step 5: Create __init__.py files
Write-Host "Step 5: Setting up Python modules..." -ForegroundColor Yellow
$modules = @("nlp", "models", "training", "data")
foreach ($module in $modules) {
    $initFile = Join-Path $module "__init__.py"
    if (-not (Test-Path $initFile)) {
        New-Item -ItemType File -Path $initFile -Force | Out-Null
    }
}
Write-Host "✓ Modules initialized" -ForegroundColor Green
Write-Host ""

# Step 6: Test imports
Write-Host "Step 6: Testing imports..." -ForegroundColor Yellow
try {
    python -c @"
import torch
import transformers
import underthesea
from nlp.taxonomy import ModerationLabel, get_label_list
from nlp.preprocessing_advanced import preprocess_for_phobert
from models.multitask_phobert import MultiTaskPhoBERT
print('All imports successful!')
"@
    Write-Host "✓ All imports working" -ForegroundColor Green
} catch {
    Write-Host "Error: Import test failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 7: Download PhoBERT model
Write-Host "Step 7: Downloading PhoBERT model..." -ForegroundColor Yellow
try {
    python -c @"
from transformers import AutoTokenizer, AutoModel
print('Downloading PhoBERT-base-v2...')
tokenizer = AutoTokenizer.from_pretrained('vinai/phobert-base-v2')
model = AutoModel.from_pretrained('vinai/phobert-base-v2')
tokenizer.save_pretrained('./models/phobert-base-v2')
model.save_pretrained('./models/phobert-base-v2')
print('PhoBERT downloaded and cached!')
"@
} catch {
    Write-Host "⚠ PhoBERT download failed, will download during training" -ForegroundColor Yellow
}
Write-Host ""

# Step 8: Create quick start scripts
Write-Host "Step 8: Creating quick start scripts..." -ForegroundColor Yellow

# Training script
@"
# Quick training script with recommended settings
Write-Host "Starting training with recommended settings..." -ForegroundColor Cyan

python training/train_full.py ``
    --data-dir ./datasets ``
    --output-dir ./checkpoints ``
    --batch-size 16 ``
    --gradient-accumulation 2 ``
    --epochs 10 ``
    --learning-rate 2e-5 ``
    --max-length 256 ``
    --use-focal-loss ``
    --focal-gamma 2.0 ``
    --augment-prob 0.3 ``
    --device cuda
"@ | Out-File -FilePath quick_train.ps1 -Encoding UTF8

# Test script
@"
# Quick test script
Write-Host "Testing inference..." -ForegroundColor Cyan

python -c @'
from nlp.inference_multitask import MultiTaskModerationInference
import sys

# Test texts
test_texts = [
    "Sản phẩm rất tốt, tôi rất hài lòng!",
    "Đồ rác vãi lồn, không mua nữa",
    "Shop lừa đảo, inbox mua hàng 0123456789",
]

try:
    engine = MultiTaskModerationInference(
        model_path="./checkpoints/best_model",
        device="cpu"
    )
    print("Model loaded successfully!")
    
    for text in test_texts:
        print(f"\nText: {text}")
        result = engine.predict(text)
        print(f"Action: {result['action']}")
        print(f"Labels: {result['labels']}")
        print(f"Confidence: {result['confidence']:.2%}")
except Exception as e:
    print(f"Error: {e}")
    print("Note: Train model first with ./quick_train.ps1")
    sys.exit(1)
'@
"@ | Out-File -FilePath quick_test.ps1 -Encoding UTF8

Write-Host "✓ Quick start scripts created" -ForegroundColor Green
Write-Host ""

# Step 9: Create configuration file
Write-Host "Step 9: Creating configuration..." -ForegroundColor Yellow

@"
# Vietnamese Content Moderation Configuration

model:
  name: vinai/phobert-base-v2
  max_length: 256
  num_labels: 7
  use_span_detection: false

training:
  batch_size: 16
  gradient_accumulation: 2
  learning_rate: 2.0e-5
  epochs: 10
  warmup_ratio: 0.1
  early_stopping_patience: 3

loss:
  use_focal_loss: true
  focal_gamma: 2.0
  use_class_weights: true

data:
  test_size: 0.15
  val_size: 0.15
  augment_prob: 0.3
  include_emotion: true
  include_sentiment: true

labels:
  - toxicity
  - hate
  - harassment
  - threat
  - sexual
  - spam
  - pii

severity_levels:
  clean: 0
  moderate: 1
  severe: 2

actions:
  0: allowed
  1: review
  2: reject
"@ | Out-File -FilePath config.yaml -Encoding UTF8

Write-Host "✓ Configuration created" -ForegroundColor Green
Write-Host ""

# Final summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✓ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Directory structure:"
Write-Host "  ✓ datasets/     - Vietnamese datasets"
Write-Host "  ✓ models/       - PhoBERT cached"
Write-Host "  ✓ checkpoints/  - Model checkpoints"
Write-Host "  ✓ training/     - Training scripts"
Write-Host ""
Write-Host "Quick start:"
Write-Host "  1. Train model:  .\quick_train.ps1" -ForegroundColor Cyan
Write-Host "  2. Test model:   .\quick_test.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentation:"
Write-Host "  📖 TRAINING_GUIDE.md  - Full guide"
Write-Host "  📖 README_SETUP.md    - Setup summary"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review datasets in ./datasets/"
Write-Host "  2. Start training with .\quick_train.ps1"
Write-Host "  3. Check TRAINING_GUIDE.md for details"
Write-Host ""
Write-Host "Happy training! 🚀" -ForegroundColor Magenta

