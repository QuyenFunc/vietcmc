"""
Training Pipeline for Multi-Task PhoBERT Moderation Model

Features:
- Focal Loss for class imbalance
- Class weighting
- Over/under sampling
- Data augmentation
- Early stopping on Macro-F1
- Mixed precision training
- Gradient accumulation
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torch.cuda.amp import autocast, GradScaler
from transformers import AutoTokenizer, get_linear_schedule_with_warmup
from sklearn.metrics import f1_score, precision_recall_fscore_support, classification_report
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging
from tqdm import tqdm
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.multitask_phobert import MultiTaskPhoBERT, MultiTaskLoss, FocalLoss
from nlp.preprocessing_advanced import preprocess_for_phobert, augment_drop_diacritics, augment_teencode, augment_insert_chars
from nlp.taxonomy import get_label_list, DEFAULT_LABELS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModerationDataset(Dataset):
    """Dataset for Vietnamese content moderation"""
    
    def __init__(
        self,
        texts: List[str],
        labels_multi: np.ndarray,  # [N, num_labels]
        severity_labels: np.ndarray,  # [N]
        tokenizer,
        max_length: int = 256,
        augment: bool = False,
        augment_prob: float = 0.3
    ):
        self.texts = texts
        self.labels_multi = labels_multi
        self.severity_labels = severity_labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.augment = augment
        self.augment_prob = augment_prob
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        
        # Apply augmentation during training
        if self.augment and np.random.random() < self.augment_prob:
            aug_choice = np.random.choice(['diacritics', 'teencode', 'insert', 'none'])
            
            if aug_choice == 'diacritics':
                text = augment_drop_diacritics(text, ratio=0.3)
            elif aug_choice == 'teencode':
                text = augment_teencode(text, ratio=0.2)
            elif aug_choice == 'insert':
                text = augment_insert_chars(text, ratio=0.1)
        
        # Preprocess (with word segmentation for PhoBERT)
        processed_text, _ = preprocess_for_phobert(text)
        
        # Tokenize
        encoding = self.tokenizer(
            processed_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'labels_multi': torch.tensor(self.labels_multi[idx], dtype=torch.float),
            'severity_labels': torch.tensor(self.severity_labels[idx], dtype=torch.float)
        }


class ModerationTrainer:
    """Trainer for multi-task moderation model"""
    
    def __init__(
        self,
        model: MultiTaskPhoBERT,
        tokenizer,
        train_dataset: ModerationDataset,
        val_dataset: ModerationDataset,
        output_dir: str = "./checkpoints",
        batch_size: int = 16,
        gradient_accumulation_steps: int = 2,
        learning_rate: float = 2e-5,
        num_epochs: int = 10,
        warmup_ratio: float = 0.1,
        max_grad_norm: float = 1.0,
        use_focal_loss: bool = True,
        focal_gamma: float = 2.0,
        class_weights: Optional[torch.Tensor] = None,
        early_stopping_patience: int = 3,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    ):
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.batch_size = batch_size
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.warmup_ratio = warmup_ratio
        self.max_grad_norm = max_grad_norm
        self.early_stopping_patience = early_stopping_patience
        self.device = device
        
        # Loss function
        self.criterion = MultiTaskLoss(
            num_labels=model.num_labels,
            use_focal_loss=use_focal_loss,
            focal_gamma=focal_gamma,
            class_weights=class_weights.to(device) if class_weights is not None else None
        )
        
        # Data loaders
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=True
        )
        
        # Optimizer
        self.optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=0.01
        )
        
        # Scheduler
        total_steps = len(self.train_loader) * num_epochs // gradient_accumulation_steps
        warmup_steps = int(total_steps * warmup_ratio)
        
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps
        )
        
        # Mixed precision training
        self.scaler = GradScaler() if device == 'cuda' else None
        
        # Metrics tracking
        self.best_f1 = 0.0
        self.patience_counter = 0
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'val_f1_macro': [],
            'val_f1_per_label': []
        }
    
    def train_epoch(self) -> float:
        """Train one epoch"""
        self.model.train()
        total_loss = 0
        
        progress_bar = tqdm(self.train_loader, desc="Training")
        
        for step, batch in enumerate(progress_bar):
            # Move to device
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels_multi = batch['labels_multi'].to(self.device)
            severity_labels = batch['severity_labels'].to(self.device)
            
            # Forward pass with mixed precision
            if self.scaler is not None:
                with autocast():
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels_multi=labels_multi,
                        severity_labels=severity_labels
                    )
                    loss = outputs['loss'] / self.gradient_accumulation_steps
                
                # Backward pass
                self.scaler.scale(loss).backward()
                
                # Gradient accumulation
                if (step + 1) % self.gradient_accumulation_steps == 0:
                    self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                    self.scheduler.step()
                    self.optimizer.zero_grad()
            else:
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels_multi=labels_multi,
                    severity_labels=severity_labels
                )
                loss = outputs['loss'] / self.gradient_accumulation_steps
                loss.backward()
                
                if (step + 1) % self.gradient_accumulation_steps == 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)
                    self.optimizer.step()
                    self.scheduler.step()
                    self.optimizer.zero_grad()
            
            total_loss += loss.item() * self.gradient_accumulation_steps
            progress_bar.set_postfix({'loss': total_loss / (step + 1)})
        
        return total_loss / len(self.train_loader)
    
    def evaluate(self) -> Tuple[float, Dict]:
        """Evaluate on validation set"""
        self.model.eval()
        total_loss = 0
        all_preds = []
        all_labels = []
        all_severity_preds = []
        all_severity_labels = []
        
        with torch.no_grad():
            for batch in tqdm(self.val_loader, desc="Evaluating"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels_multi = batch['labels_multi'].to(self.device)
                severity_labels = batch['severity_labels'].to(self.device)
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels_multi=labels_multi,
                    severity_labels=severity_labels
                )
                
                total_loss += outputs['loss'].item()
                
                # Get predictions
                preds = self.model.predict(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                all_preds.append(preds['multi_label_preds'].cpu().numpy())
                all_labels.append(labels_multi.cpu().numpy())
                all_severity_preds.append(preds['severity_preds'].cpu().numpy())
                all_severity_labels.append(severity_labels.cpu().numpy())
        
        # Concatenate all batches
        all_preds = np.vstack(all_preds)
        all_labels = np.vstack(all_labels)
        all_severity_preds = np.concatenate(all_severity_preds)
        all_severity_labels = np.concatenate(all_severity_labels)
        
        # Compute metrics
        avg_loss = total_loss / len(self.val_loader)
        
        # Per-label F1 scores
        f1_per_label = []
        label_names = [label.value for label in DEFAULT_LABELS]
        
        for i, label_name in enumerate(label_names):
            f1 = f1_score(all_labels[:, i], all_preds[:, i], average='binary', zero_division=0)
            f1_per_label.append((label_name, f1))
        
        # Macro F1 (average across all labels)
        f1_macro = np.mean([f1 for _, f1 in f1_per_label])
        
        # Severity accuracy
        severity_acc = (all_severity_preds == all_severity_labels).mean()
        
        metrics = {
            'loss': avg_loss,
            'f1_macro': f1_macro,
            'f1_per_label': f1_per_label,
            'severity_accuracy': severity_acc
        }
        
        return f1_macro, metrics
    
    def train(self):
        """Full training loop"""
        logger.info(f"Starting training for {self.num_epochs} epochs")
        logger.info(f"Train samples: {len(self.train_dataset)}")
        logger.info(f"Val samples: {len(self.val_dataset)}")
        logger.info(f"Batch size: {self.batch_size}")
        logger.info(f"Gradient accumulation steps: {self.gradient_accumulation_steps}")
        logger.info(f"Effective batch size: {self.batch_size * self.gradient_accumulation_steps}")
        logger.info(f"Device: {self.device}")
        
        for epoch in range(self.num_epochs):
            logger.info(f"\n{'='*60}")
            logger.info(f"Epoch {epoch + 1}/{self.num_epochs}")
            logger.info(f"{'='*60}")
            
            # Train
            train_loss = self.train_epoch()
            self.history['train_loss'].append(train_loss)
            logger.info(f"Train Loss: {train_loss:.4f}")
            
            # Evaluate
            val_f1, metrics = self.evaluate()
            self.history['val_loss'].append(metrics['loss'])
            self.history['val_f1_macro'].append(val_f1)
            self.history['val_f1_per_label'].append(metrics['f1_per_label'])
            
            logger.info(f"Val Loss: {metrics['loss']:.4f}")
            logger.info(f"Val F1 (Macro): {val_f1:.4f}")
            logger.info(f"Severity Accuracy: {metrics['severity_accuracy']:.4f}")
            logger.info("\nPer-label F1 scores:")
            for label_name, f1 in metrics['f1_per_label']:
                logger.info(f"  {label_name}: {f1:.4f}")
            
            # Early stopping based on Macro F1
            if val_f1 > self.best_f1:
                self.best_f1 = val_f1
                self.patience_counter = 0
                
                # Save best model
                self.save_checkpoint('best_model')
                logger.info(f"✅ New best F1: {val_f1:.4f} - Model saved!")
            else:
                self.patience_counter += 1
                logger.info(f"No improvement. Patience: {self.patience_counter}/{self.early_stopping_patience}")
                
                if self.patience_counter >= self.early_stopping_patience:
                    logger.info("Early stopping triggered!")
                    break
            
            # Save checkpoint every epoch
            self.save_checkpoint(f'epoch_{epoch+1}')
        
        # Save final model and history
        self.save_checkpoint('final_model')
        self.save_history()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Training completed!")
        logger.info(f"Best F1 (Macro): {self.best_f1:.4f}")
        logger.info(f"{'='*60}")
    
    def save_checkpoint(self, name: str):
        """Save model checkpoint"""
        checkpoint_dir = self.output_dir / name
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        self.model.phobert.save_pretrained(checkpoint_dir)
        self.tokenizer.save_pretrained(checkpoint_dir)
        
        # Save task heads
        torch.save({
            'multi_label_classifier': self.model.multi_label_classifier.state_dict(),
            'severity_regressor': self.model.severity_regressor.state_dict(),
            'span_detector': self.model.span_detector.state_dict() if self.model.use_span_detection else None,
            'config': {
                'num_labels': self.model.num_labels,
                'num_severity_levels': self.model.num_severity_levels,
                'use_span_detection': self.model.use_span_detection
            }
        }, checkpoint_dir / 'task_heads.pt')
        
        logger.info(f"Checkpoint saved to {checkpoint_dir}")
    
    def save_history(self):
        """Save training history"""
        history_path = self.output_dir / 'training_history.json'
        
        # Convert to serializable format
        history = {
            'train_loss': self.history['train_loss'],
            'val_loss': self.history['val_loss'],
            'val_f1_macro': self.history['val_f1_macro'],
            'best_f1': self.best_f1
        }
        
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info(f"Training history saved to {history_path}")


def compute_class_weights(labels: np.ndarray) -> torch.Tensor:
    """
    Compute class weights for imbalanced dataset
    
    Args:
        labels: [N, num_labels] binary matrix
        
    Returns:
        weights: [num_labels] tensor
    """
    num_samples = labels.shape[0]
    num_labels = labels.shape[1]
    
    weights = []
    for i in range(num_labels):
        pos_count = labels[:, i].sum()
        neg_count = num_samples - pos_count
        
        # Inverse frequency weighting
        if pos_count > 0:
            weight = neg_count / pos_count
        else:
            weight = 1.0
        
        weights.append(weight)
    
    return torch.tensor(weights, dtype=torch.float)


if __name__ == "__main__":
    # Example training script
    logger.info("Loading datasets...")
    
    # TODO: Load your actual dataset
    # For now, create dummy data
    num_samples = 1000
    texts = [f"Sample text {i}" for i in range(num_samples)]
    labels = np.random.randint(0, 2, (num_samples, 7))
    severities = np.random.randint(0, 3, num_samples)
    
    # Split
    train_texts, val_texts, train_labels, val_labels, train_sev, val_sev = train_test_split(
        texts, labels, severities, test_size=0.2, random_state=42
    )
    
    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained('vinai/phobert-base-v2')
    
    # Datasets
    train_dataset = ModerationDataset(
        train_texts, train_labels, train_sev,
        tokenizer, max_length=256, augment=True
    )
    
    val_dataset = ModerationDataset(
        val_texts, val_labels, val_sev,
        tokenizer, max_length=256, augment=False
    )
    
    # Compute class weights
    class_weights = compute_class_weights(train_labels)
    logger.info(f"Class weights: {class_weights}")
    
    # Model
    model = MultiTaskPhoBERT(
        num_labels=7,
        use_span_detection=False  # Disable for this example
    )
    
    # Trainer
    trainer = ModerationTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        output_dir="./checkpoints",
        batch_size=16,
        gradient_accumulation_steps=2,
        learning_rate=2e-5,
        num_epochs=10,
        use_focal_loss=True,
        focal_gamma=2.0,
        class_weights=class_weights
    )
    
    # Train
    trainer.train()

