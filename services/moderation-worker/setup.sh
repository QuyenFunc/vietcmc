#!/bin/bash

# Vietnamese Content Moderation AI - Automated Setup Script
# This script automates the entire setup process

set -e  # Exit on error

echo "=================================="
echo "VIETNAMESE MODERATION AI - SETUP"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if ! python -c 'import sys; assert sys.version_info >= (3, 8)' 2>/dev/null; then
    echo -e "${RED}Error: Python 3.8+ required${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python version OK${NC}"
echo ""

# Step 2: Create directories
echo "Step 2: Creating directories..."
mkdir -p datasets
mkdir -p checkpoints
mkdir -p models
mkdir -p data
mkdir -p training
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Step 3: Install dependencies
echo "Step 3: Installing dependencies..."
echo "This may take a few minutes..."

# Update requirements.txt with all needed packages
cat > requirements.txt << 'EOF'
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
EOF

pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 4: Download datasets
echo "Step 4: Downloading datasets..."
echo "This will attempt to download Vietnamese moderation datasets"
python data/download_datasets.py --data-dir ./datasets --dataset all || {
    echo -e "${YELLOW}⚠ Some datasets may require manual download${NC}"
    echo "Please check TRAINING_GUIDE.md for download instructions"
}
echo ""

# Step 5: Create __init__.py files
echo "Step 5: Setting up Python modules..."
touch nlp/__init__.py
touch models/__init__.py
touch training/__init__.py
touch data/__init__.py
echo -e "${GREEN}✓ Modules initialized${NC}"
echo ""

# Step 6: Test imports
echo "Step 6: Testing imports..."
python -c "
import torch
import transformers
import underthesea
from nlp.taxonomy import ModerationLabel, get_label_list
from nlp.preprocessing_advanced import preprocess_for_phobert
from models.multitask_phobert import MultiTaskPhoBERT
print('All imports successful!')
" || {
    echo -e "${RED}Error: Import test failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ All imports working${NC}"
echo ""

# Step 7: Download PhoBERT model
echo "Step 7: Downloading PhoBERT model..."
python -c "
from transformers import AutoTokenizer, AutoModel
print('Downloading PhoBERT-base-v2...')
tokenizer = AutoTokenizer.from_pretrained('vinai/phobert-base-v2')
model = AutoModel.from_pretrained('vinai/phobert-base-v2')
tokenizer.save_pretrained('./models/phobert-base-v2')
model.save_pretrained('./models/phobert-base-v2')
print('PhoBERT downloaded and cached!')
" || {
    echo -e "${YELLOW}⚠ PhoBERT download failed, will download during training${NC}"
}
echo ""

# Step 8: Create quick start script
echo "Step 8: Creating quick start scripts..."

cat > quick_train.sh << 'EOF'
#!/bin/bash
# Quick training script with recommended settings

echo "Starting training with recommended settings..."
python training/train_full.py \
    --data-dir ./datasets \
    --output-dir ./checkpoints \
    --batch-size 16 \
    --gradient-accumulation 2 \
    --epochs 10 \
    --learning-rate 2e-5 \
    --max-length 256 \
    --use-focal-loss \
    --focal-gamma 2.0 \
    --augment-prob 0.3 \
    --device cuda
EOF

chmod +x quick_train.sh

cat > quick_test.sh << 'EOF'
#!/bin/bash
# Quick test script

echo "Testing inference..."
python -c "
from nlp.inference_multitask import MultiTaskModerationInference
import sys

# Test texts
test_texts = [
    'Sản phẩm rất tốt, tôi rất hài lòng!',
    'Đồ rác vãi lồn, không mua nữa',
    'Shop lừa đảo, inbox mua hàng 0123456789',
]

try:
    engine = MultiTaskModerationInference(
        model_path='./checkpoints/best_model',
        device='cpu'
    )
    print('Model loaded successfully!')
    
    for text in test_texts:
        print(f'\nText: {text}')
        result = engine.predict(text)
        print(f'Action: {result[\"action\"]}')
        print(f'Labels: {result[\"labels\"]}')
        print(f'Confidence: {result[\"confidence"]:.2%}')
except Exception as e:
    print(f'Error: {e}')
    print('Note: Train model first with ./quick_train.sh')
    sys.exit(1)
"
EOF

chmod +x quick_test.sh

echo -e "${GREEN}✓ Quick start scripts created${NC}"
echo ""

# Step 9: Create configuration file
echo "Step 9: Creating configuration..."

cat > config.yaml << 'EOF'
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
EOF

echo -e "${GREEN}✓ Configuration created${NC}"
echo ""

# Step 10: Create README
echo "Step 10: Creating README..."

cat > README_SETUP.md << 'EOF'
# Setup Complete! 🎉

## What's Installed

✅ Python dependencies (PyTorch, Transformers, Underthesea, etc.)
✅ Directory structure
✅ PhoBERT model (cached)
✅ Vietnamese datasets (downloaded/ready to download)
✅ Training scripts
✅ Inference engine
✅ Quick start scripts

## Next Steps

### 1. Check Downloaded Datasets

```bash
ls datasets/
```

If some datasets are missing, download manually:
- ViHSD: https://github.com/ongocthanhvan/ViHSD
- ViHOS: https://github.com/tarudesu/ViHOS
- UIT-ViCTSD: Contact nlp@uit.edu.vn

### 2. Train the Model

**Quick training (recommended settings):**
```bash
./quick_train.sh
```

**Custom training:**
```bash
python training/train_full.py \
    --data-dir ./datasets \
    --output-dir ./checkpoints \
    --batch-size 16 \
    --epochs 10 \
    --use-focal-loss
```

### 3. Test Inference

```bash
./quick_test.sh
```

Or manually:
```bash
python -m nlp.inference_multitask
```

## File Structure

```
.
├── data/                   # Data loading scripts
│   ├── dataset_loader.py
│   └── download_datasets.py
├── models/                 # Model architectures
│   └── multitask_phobert.py
├── nlp/                    # NLP utilities
│   ├── taxonomy.py
│   ├── preprocessing_advanced.py
│   ├── inference_multitask.py
│   ├── toxic_words.py
│   └── sentiment_words.py
├── training/               # Training scripts
│   ├── trainer.py
│   └── train_full.py
├── datasets/               # Downloaded datasets
├── checkpoints/            # Trained models
├── TRAINING_GUIDE.md       # Comprehensive guide
└── requirements.txt        # Python dependencies
```

## Documentation

📖 **Full Training Guide:** `TRAINING_GUIDE.md`
📊 **Taxonomy:** See `nlp/taxonomy.py`
🔧 **Configuration:** `config.yaml`

## Troubleshooting

### CUDA Out of Memory
- Reduce `--batch-size` (try 8 or 4)
- Increase `--gradient-accumulation` (try 4 or 8)

### Dataset Not Found
- Run manual download: `python data/download_datasets.py`
- Check dataset directory: `ls datasets/`

### Word Segmentation Errors
- Update underthesea: `pip install -U underthesea`

### Import Errors
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## Support

- 📧 Email: nlp@uit.edu.vn
- 📚 Documentation: TRAINING_GUIDE.md
- 🐛 Issues: GitHub Issues

Happy Training! 🚀
EOF

echo -e "${GREEN}✓ README created${NC}"
echo ""

# Final summary
echo ""
echo "=========================================="
echo -e "${GREEN}✓ SETUP COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "Directory structure:"
echo "  ✓ datasets/     - Vietnamese datasets"
echo "  ✓ models/       - PhoBERT cached"
echo "  ✓ checkpoints/  - Model checkpoints"
echo "  ✓ training/     - Training scripts"
echo ""
echo "Quick start:"
echo "  1. Train model:  ./quick_train.sh"
echo "  2. Test model:   ./quick_test.sh"
echo ""
echo "Documentation:"
echo "  📖 TRAINING_GUIDE.md  - Full guide"
echo "  📖 README_SETUP.md    - Setup summary"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review datasets in ./datasets/"
echo "  2. Start training with ./quick_train.sh"
echo "  3. Check TRAINING_GUIDE.md for details"
echo ""
echo "Happy training! 🚀"

