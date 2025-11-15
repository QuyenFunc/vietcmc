"""
End-to-End Training Script for Vietnamese Content Moderation

Usage:
    python train_full.py --data-path ./datasets/combined.csv --output-dir ./checkpoints
"""

import argparse
import logging
import sys
import os
from pathlib import Path

import pandas as pd
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.multitask_phobert import MultiTaskPhoBERT
from training.trainer import ModerationDataset, ModerationTrainer, compute_class_weights
from data.dataset_loader import DatasetLoader
from nlp.taxonomy import get_label_list

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('training.log')
    ]
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train Multi-Task PhoBERT for Vietnamese Content Moderation"
    )
    
    # Data arguments
    parser.add_argument(
        '--data-path',
        type=str,
        default=None,
        help='Path to combined dataset CSV. If not provided, will load and combine datasets.'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='./datasets',
        help='Directory containing raw datasets'
    )
    parser.add_argument(
        '--include-emotion',
        action='store_true',
        help='Include emotion corpus (UIT-VSMEC)'
    )
    parser.add_argument(
        '--include-sentiment',
        action='store_true',
        help='Include sentiment corpus (UIT-VSFC)'
    )
    
    # Model arguments
    parser.add_argument(
        '--model-name',
        type=str,
        default='vinai/phobert-base-v2',
        help='PhoBERT model name or path'
    )
    parser.add_argument(
        '--max-length',
        type=int,
        default=256,
        help='Maximum sequence length'
    )
    parser.add_argument(
        '--use-span-detection',
        action='store_true',
        help='Enable span detection task (requires ViHOS)'
    )
    
    # Training arguments
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./checkpoints',
        help='Output directory for checkpoints'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=16,
        help='Training batch size'
    )
    parser.add_argument(
        '--gradient-accumulation',
        type=int,
        default=2,
        help='Gradient accumulation steps'
    )
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=2e-5,
        help='Learning rate'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=10,
        help='Number of training epochs'
    )
    parser.add_argument(
        '--warmup-ratio',
        type=float,
        default=0.1,
        help='Warmup ratio for learning rate scheduler'
    )
    parser.add_argument(
        '--early-stopping-patience',
        type=int,
        default=3,
        help='Early stopping patience (epochs)'
    )
    
    # Loss arguments
    parser.add_argument(
        '--use-focal-loss',
        action='store_true',
        default=True,
        help='Use Focal Loss for multi-label classification'
    )
    parser.add_argument(
        '--focal-gamma',
        type=float,
        default=2.0,
        help='Focal loss gamma parameter'
    )
    parser.add_argument(
        '--no-class-weights',
        action='store_true',
        help='Disable class weighting'
    )
    
    # Data split
    parser.add_argument(
        '--test-size',
        type=float,
        default=0.15,
        help='Test set size (proportion)'
    )
    parser.add_argument(
        '--val-size',
        type=float,
        default=0.15,
        help='Validation set size (proportion)'
    )
    parser.add_argument(
        '--random-seed',
        type=int,
        default=42,
        help='Random seed for reproducibility'
    )
    
    # Augmentation
    parser.add_argument(
        '--augment-prob',
        type=float,
        default=0.3,
        help='Probability of applying augmentation'
    )
    parser.add_argument(
        '--no-augmentation',
        action='store_true',
        help='Disable data augmentation'
    )
    
    # Device
    parser.add_argument(
        '--device',
        type=str,
        default='cuda' if torch.cuda.is_available() else 'cpu',
        help='Device to use for training'
    )
    
    return parser.parse_args()


def load_or_prepare_data(args):
    """Load or prepare training data"""
    
    if args.data_path and os.path.exists(args.data_path):
        logger.info(f"Loading data from {args.data_path}")
        data = pd.read_csv(args.data_path)
    else:
        logger.info("Loading and combining datasets...")
        loader = DatasetLoader(args.data_dir)
        
        data = loader.combine_datasets(
            include_emotion=args.include_emotion,
            include_sentiment=args.include_sentiment
        )
        
        if data.empty:
            logger.error("No data loaded! Please download datasets first.")
            logger.info("Run: python data/download_datasets.py --dataset all")
            sys.exit(1)
        
        # Save combined dataset
        output_path = Path(args.data_dir) / 'combined_moderation_dataset.csv'
        data.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Saved combined dataset to {output_path}")
    
    return data


def prepare_labels(data, label_names):
    """Prepare label matrices"""
    
    # Multi-label matrix
    labels_multi = np.zeros((len(data), len(label_names)), dtype=int)
    
    for i, label_name in enumerate(label_names):
        if label_name in data.columns:
            labels_multi[:, i] = data[label_name].values
    
    # Severity labels
    if 'severity' in data.columns:
        severity_labels = data['severity'].values
    else:
        # Infer severity from labels
        severity_labels = np.max(labels_multi, axis=1) * 2  # 0, 1, or 2
    
    return labels_multi, severity_labels


def split_data(texts, labels_multi, severity_labels, args):
    """Split data into train/val/test"""
    
    # First split: train+val vs test
    train_val_texts, test_texts, \
    train_val_labels, test_labels, \
    train_val_sev, test_sev = train_test_split(
        texts, labels_multi, severity_labels,
        test_size=args.test_size,
        random_state=args.random_seed,
        stratify=severity_labels  # Stratify by severity
    )
    
    # Second split: train vs val
    val_ratio = args.val_size / (1 - args.test_size)
    train_texts, val_texts, \
    train_labels, val_labels, \
    train_sev, val_sev = train_test_split(
        train_val_texts, train_val_labels, train_val_sev,
        test_size=val_ratio,
        random_state=args.random_seed,
        stratify=train_val_sev
    )
    
    logger.info(f"\nData split:")
    logger.info(f"  Train: {len(train_texts)} samples")
    logger.info(f"  Val:   {len(val_texts)} samples")
    logger.info(f"  Test:  {len(test_texts)} samples")
    
    return (train_texts, train_labels, train_sev), \
           (val_texts, val_labels, val_sev), \
           (test_texts, test_labels, test_sev)


def main():
    args = parse_args()
    
    logger.info("="*80)
    logger.info("VIETNAMESE CONTENT MODERATION - TRAINING")
    logger.info("="*80)
    logger.info(f"\nConfiguration:")
    for arg, value in vars(args).items():
        logger.info(f"  {arg}: {value}")
    
    # Set random seed
    torch.manual_seed(args.random_seed)
    np.random.seed(args.random_seed)
    
    # Load data
    logger.info("\n" + "="*80)
    logger.info("STEP 1: Loading Data")
    logger.info("="*80)
    data = load_or_prepare_data(args)
    
    # Get label names
    label_names = get_label_list(include_optional=False)
    logger.info(f"\nLabels: {label_names}")
    
    # Prepare labels
    texts = data['text'].tolist()
    labels_multi, severity_labels = prepare_labels(data, label_names)
    
    logger.info(f"\nLabel distribution:")
    for i, label_name in enumerate(label_names):
        count = labels_multi[:, i].sum()
        pct = count / len(labels_multi) * 100
        logger.info(f"  {label_name}: {count} ({pct:.1f}%)")
    
    logger.info(f"\nSeverity distribution:")
    for sev in [0, 1, 2]:
        count = (severity_labels == sev).sum()
        pct = count / len(severity_labels) * 100
        logger.info(f"  Level {sev}: {count} ({pct:.1f}%)")
    
    # Split data
    logger.info("\n" + "="*80)
    logger.info("STEP 2: Splitting Data")
    logger.info("="*80)
    train_data, val_data, test_data = split_data(
        texts, labels_multi, severity_labels, args
    )
    
    # Compute class weights
    class_weights = None
    if not args.no_class_weights:
        logger.info("\n" + "="*80)
        logger.info("STEP 3: Computing Class Weights")
        logger.info("="*80)
        class_weights = compute_class_weights(train_data[1])
        logger.info(f"\nClass weights:")
        for i, (label_name, weight) in enumerate(zip(label_names, class_weights)):
            logger.info(f"  {label_name}: {weight:.2f}")
    
    # Load tokenizer
    logger.info("\n" + "="*80)
    logger.info("STEP 4: Loading Tokenizer")
    logger.info("="*80)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    logger.info(f"Tokenizer loaded: {args.model_name}")
    
    # Create datasets
    logger.info("\n" + "="*80)
    logger.info("STEP 5: Creating Datasets")
    logger.info("="*80)
    
    train_dataset = ModerationDataset(
        texts=train_data[0],
        labels_multi=train_data[1],
        severity_labels=train_data[2],
        tokenizer=tokenizer,
        max_length=args.max_length,
        augment=not args.no_augmentation,
        augment_prob=args.augment_prob
    )
    
    val_dataset = ModerationDataset(
        texts=val_data[0],
        labels_multi=val_data[1],
        severity_labels=val_data[2],
        tokenizer=tokenizer,
        max_length=args.max_length,
        augment=False
    )
    
    logger.info(f"Train dataset: {len(train_dataset)} samples")
    logger.info(f"Val dataset: {len(val_dataset)} samples")
    logger.info(f"Augmentation: {'enabled' if not args.no_augmentation else 'disabled'}")
    
    # Create model
    logger.info("\n" + "="*80)
    logger.info("STEP 6: Creating Model")
    logger.info("="*80)
    
    model = MultiTaskPhoBERT(
        model_name=args.model_name,
        num_labels=len(label_names),
        use_span_detection=args.use_span_detection
    )
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    logger.info(f"\nModel: MultiTaskPhoBERT")
    logger.info(f"Backbone: {args.model_name}")
    logger.info(f"Total parameters: {total_params:,}")
    logger.info(f"Trainable parameters: {trainable_params:,}")
    logger.info(f"Span detection: {'enabled' if args.use_span_detection else 'disabled'}")
    
    # Create trainer
    logger.info("\n" + "="*80)
    logger.info("STEP 7: Creating Trainer")
    logger.info("="*80)
    
    trainer = ModerationTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation,
        learning_rate=args.learning_rate,
        num_epochs=args.epochs,
        warmup_ratio=args.warmup_ratio,
        use_focal_loss=args.use_focal_loss,
        focal_gamma=args.focal_gamma,
        class_weights=class_weights,
        early_stopping_patience=args.early_stopping_patience,
        device=args.device
    )
    
    effective_batch_size = args.batch_size * args.gradient_accumulation
    logger.info(f"\nTraining configuration:")
    logger.info(f"  Batch size: {args.batch_size}")
    logger.info(f"  Gradient accumulation: {args.gradient_accumulation}")
    logger.info(f"  Effective batch size: {effective_batch_size}")
    logger.info(f"  Learning rate: {args.learning_rate}")
    logger.info(f"  Epochs: {args.epochs}")
    logger.info(f"  Warmup ratio: {args.warmup_ratio}")
    logger.info(f"  Device: {args.device}")
    logger.info(f"  Focal loss: {'enabled' if args.use_focal_loss else 'disabled'}")
    if args.use_focal_loss:
        logger.info(f"  Focal gamma: {args.focal_gamma}")
    logger.info(f"  Class weights: {'enabled' if class_weights is not None else 'disabled'}")
    logger.info(f"  Early stopping patience: {args.early_stopping_patience}")
    
    # Train
    logger.info("\n" + "="*80)
    logger.info("STEP 8: Training")
    logger.info("="*80)
    
    trainer.train()
    
    # Evaluate on test set
    logger.info("\n" + "="*80)
    logger.info("STEP 9: Final Evaluation on Test Set")
    logger.info("="*80)
    
    test_dataset = ModerationDataset(
        texts=test_data[0],
        labels_multi=test_data[1],
        severity_labels=test_data[2],
        tokenizer=tokenizer,
        max_length=args.max_length,
        augment=False
    )
    
    # Load best model
    best_model_path = Path(args.output_dir) / 'best_model'
    if best_model_path.exists():
        logger.info(f"Loading best model from {best_model_path}")
        
        # Reload model
        best_model = MultiTaskPhoBERT(
            model_name=str(best_model_path),
            num_labels=len(label_names),
            use_span_detection=args.use_span_detection
        )
        
        # Load task heads
        task_heads_path = best_model_path / 'task_heads.pt'
        if task_heads_path.exists():
            checkpoint = torch.load(task_heads_path, map_location=args.device)
            best_model.multi_label_classifier.load_state_dict(checkpoint['multi_label_classifier'])
            best_model.severity_regressor.load_state_dict(checkpoint['severity_regressor'])
            if args.use_span_detection and checkpoint.get('span_detector'):
                best_model.span_detector.load_state_dict(checkpoint['span_detector'])
        
        best_model.to(args.device)
        
        # Create temporary trainer for evaluation
        from torch.utils.data import DataLoader
        test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False)
        
        best_model.eval()
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in test_loader:
                input_ids = batch['input_ids'].to(args.device)
                attention_mask = batch['attention_mask'].to(args.device)
                labels_multi = batch['labels_multi'].to(args.device)
                
                preds = best_model.predict(input_ids=input_ids, attention_mask=attention_mask)
                
                all_preds.append(preds['multi_label_preds'].cpu().numpy())
                all_labels.append(labels_multi.cpu().numpy())
        
        all_preds = np.vstack(all_preds)
        all_labels = np.vstack(all_labels)
        
        # Compute metrics
        from sklearn.metrics import f1_score, classification_report
        
        logger.info("\nTest Set Results:")
        logger.info("="*80)
        
        # Per-label F1
        f1_scores = []
        for i, label_name in enumerate(label_names):
            f1 = f1_score(all_labels[:, i], all_preds[:, i], average='binary', zero_division=0)
            f1_scores.append(f1)
            logger.info(f"  {label_name:15s} F1: {f1:.4f}")
        
        # Macro F1
        macro_f1 = np.mean(f1_scores)
        logger.info(f"\n  {'Macro F1':15s} : {macro_f1:.4f}")
        
        # Save test results
        results_path = Path(args.output_dir) / 'test_results.json'
        import json
        with open(results_path, 'w') as f:
            json.dump({
                'macro_f1': float(macro_f1),
                'per_label_f1': {
                    label_names[i]: float(f1) for i, f1 in enumerate(f1_scores)
                }
            }, f, indent=2)
        
        logger.info(f"\nTest results saved to {results_path}")
    
    logger.info("\n" + "="*80)
    logger.info("TRAINING COMPLETED!")
    logger.info("="*80)
    logger.info(f"\nBest model saved to: {Path(args.output_dir) / 'best_model'}")
    logger.info(f"Training history saved to: {Path(args.output_dir) / 'training_history.json'}")
    logger.info(f"Test results saved to: {Path(args.output_dir) / 'test_results.json'}")
    logger.info("\nNext steps:")
    logger.info("  1. Review training history")
    logger.info("  2. Test inference with: python -m nlp.inference_multitask")
    logger.info("  3. Deploy to production")
    logger.info("\n✅ Done!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nTraining interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n\nTraining failed with error: {e}", exc_info=True)
        sys.exit(1)

