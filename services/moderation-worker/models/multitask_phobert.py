"""
Multi-Task PhoBERT Model for Vietnamese Content Moderation

Architecture:
- Shared backbone: PhoBERT-base-v2
- Task A: Multi-label sequence classification (7 labels)
- Task B: Severity regression (0-2 scale)
- Task C: Token-level span detection (for highlighting violations)
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoConfig
from typing import Dict, Optional, Tuple


class MultiTaskPhoBERT(nn.Module):
    """
    Multi-task PhoBERT model for content moderation
    
    Tasks:
    1. Multi-label classification (toxicity, hate, harassment, threat, sexual, spam, pii)
    2. Severity regression (0-2 continuous)
    3. Span detection (token-level binary classification)
    """
    
    def __init__(
        self,
        model_name: str = "vinai/phobert-base-v2",
        num_labels: int = 7,  # Number of moderation labels
        num_severity_levels: int = 3,  # 0, 1, 2
        hidden_dropout_prob: float = 0.1,
        use_span_detection: bool = True,
        freeze_backbone: bool = False
    ):
        super().__init__()
        
        self.num_labels = num_labels
        self.num_severity_levels = num_severity_levels
        self.use_span_detection = use_span_detection
        
        # Load PhoBERT backbone
        self.config = AutoConfig.from_pretrained(model_name)
        self.phobert = AutoModel.from_pretrained(model_name, config=self.config)
        
        # Freeze backbone if specified (for fine-tuning only task heads)
        if freeze_backbone:
            for param in self.phobert.parameters():
                param.requires_grad = False
        
        hidden_size = self.config.hidden_size  # 768 for base
        
        # Dropout
        self.dropout = nn.Dropout(hidden_dropout_prob)
        
        # =============== TASK A: Multi-label Classification ===============
        # Independent binary classifiers for each label
        self.multi_label_classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(hidden_dropout_prob),
            nn.Linear(hidden_size // 2, num_labels)
        )
        
        # =============== TASK B: Severity Regression ===============
        # Predict severity score (0-2 continuous)
        self.severity_regressor = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(hidden_dropout_prob),
            nn.Linear(hidden_size // 4, 1),
            nn.Sigmoid()  # Output in [0, 1], then scale to [0, 2]
        )
        
        # =============== TASK C: Span Detection ===============
        # Token-level binary classification (is this token part of violation?)
        if use_span_detection:
            self.span_detector = nn.Sequential(
                nn.Linear(hidden_size, hidden_size // 4),
                nn.ReLU(),
                nn.Dropout(hidden_dropout_prob),
                nn.Linear(hidden_size // 4, 2)  # Binary: span or not
            )
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        labels_multi: Optional[torch.Tensor] = None,  # Multi-label targets [batch, num_labels]
        severity_labels: Optional[torch.Tensor] = None,  # Severity targets [batch]
        span_labels: Optional[torch.Tensor] = None,  # Span targets [batch, seq_len]
        return_dict: bool = True
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass
        
        Args:
            input_ids: [batch_size, seq_len]
            attention_mask: [batch_size, seq_len]
            token_type_ids: [batch_size, seq_len]
            labels_multi: [batch_size, num_labels] - binary for each label
            severity_labels: [batch_size] - severity level 0, 1, or 2
            span_labels: [batch_size, seq_len] - binary for each token
            
        Returns:
            Dict with logits and losses
        """
        # Get PhoBERT outputs
        outputs = self.phobert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            return_dict=True
        )
        
        # [CLS] token embedding for sequence-level tasks
        cls_output = outputs.last_hidden_state[:, 0, :]  # [batch, hidden_size]
        cls_output = self.dropout(cls_output)
        
        # Token-level embeddings for span detection
        token_outputs = outputs.last_hidden_state  # [batch, seq_len, hidden_size]
        
        # =============== TASK A: Multi-label Classification ===============
        multi_label_logits = self.multi_label_classifier(cls_output)  # [batch, num_labels]
        
        # =============== TASK B: Severity Regression ===============
        severity_logits = self.severity_regressor(cls_output)  # [batch, 1]
        severity_logits = severity_logits.squeeze(-1) * 2  # Scale [0,1] to [0,2]
        
        # =============== TASK C: Span Detection ===============
        span_logits = None
        if self.use_span_detection:
            span_logits = self.span_detector(token_outputs)  # [batch, seq_len, 2]
        
        # =============== Compute Losses ===============
        loss = None
        loss_dict = {}
        
        if labels_multi is not None:
            # Binary Cross Entropy with Logits (for multi-label)
            loss_fct_multi = nn.BCEWithLogitsLoss()
            loss_multi = loss_fct_multi(
                multi_label_logits,
                labels_multi.float()
            )
            loss_dict['multi_label_loss'] = loss_multi
            loss = loss_multi if loss is None else loss + loss_multi
        
        if severity_labels is not None:
            # MSE Loss for regression
            loss_fct_severity = nn.MSELoss()
            loss_severity = loss_fct_severity(
                severity_logits,
                severity_labels.float()
            )
            loss_dict['severity_loss'] = loss_severity
            loss = loss_severity if loss is None else loss + 0.5 * loss_severity
        
        if span_labels is not None and self.use_span_detection:
            # Cross Entropy for token classification
            loss_fct_span = nn.CrossEntropyLoss(ignore_index=-100)
            loss_span = loss_fct_span(
                span_logits.view(-1, 2),
                span_labels.view(-1)
            )
            loss_dict['span_loss'] = loss_span
            loss = loss_span if loss is None else loss + 0.3 * loss_span
        
        if not return_dict:
            output = (multi_label_logits, severity_logits, span_logits)
            return ((loss,) + output) if loss is not None else output
        
        return {
            'loss': loss,
            'multi_label_logits': multi_label_logits,
            'severity_logits': severity_logits,
            'span_logits': span_logits,
            **loss_dict
        }
    
    def predict(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        threshold: float = 0.5
    ) -> Dict[str, torch.Tensor]:
        """
        Inference mode
        
        Args:
            input_ids: [batch_size, seq_len]
            attention_mask: [batch_size, seq_len]
            token_type_ids: [batch_size, seq_len]
            threshold: Threshold for multi-label classification
            
        Returns:
            Dict with predictions
        """
        self.eval()
        
        with torch.no_grad():
            outputs = self.forward(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids,
                return_dict=True
            )
        
        # Multi-label predictions (apply sigmoid + threshold)
        multi_label_probs = torch.sigmoid(outputs['multi_label_logits'])
        multi_label_preds = (multi_label_probs > threshold).long()
        
        # Severity predictions (round to nearest integer)
        severity_preds = torch.round(outputs['severity_logits']).long()
        severity_preds = torch.clamp(severity_preds, 0, 2)  # Ensure in [0, 2]
        
        # Span predictions
        span_preds = None
        if self.use_span_detection and outputs['span_logits'] is not None:
            span_preds = torch.argmax(outputs['span_logits'], dim=-1)  # [batch, seq_len]
        
        return {
            'multi_label_preds': multi_label_preds,
            'multi_label_probs': multi_label_probs,
            'severity_preds': severity_preds,
            'severity_scores': outputs['severity_logits'],
            'span_preds': span_preds
        }


class FocalLoss(nn.Module):
    """
    Focal Loss for handling class imbalance
    
    FL(p_t) = -α_t * (1 - p_t)^γ * log(p_t)
    
    Focuses training on hard examples
    """
    
    def __init__(
        self,
        alpha: Optional[torch.Tensor] = None,
        gamma: float = 2.0,
        reduction: str = 'mean'
    ):
        super().__init__()
        self.alpha = alpha  # Class weights [num_classes]
        self.gamma = gamma  # Focusing parameter
        self.reduction = reduction
    
    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            inputs: Logits [batch_size, num_classes]
            targets: Binary labels [batch_size, num_classes]
        """
        # Apply sigmoid
        p = torch.sigmoid(inputs)
        
        # Binary cross entropy
        ce_loss = nn.functional.binary_cross_entropy_with_logits(
            inputs, targets, reduction='none'
        )
        
        # Calculate p_t
        p_t = p * targets + (1 - p) * (1 - targets)
        
        # Focal loss
        focal_weight = (1 - p_t) ** self.gamma
        loss = focal_weight * ce_loss
        
        # Apply alpha weighting
        if self.alpha is not None:
            alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
            loss = alpha_t * loss
        
        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss


class MultiTaskLoss(nn.Module):
    """
    Combined loss for multi-task learning with automatic weighting
    """
    
    def __init__(
        self,
        num_labels: int = 7,
        use_focal_loss: bool = True,
        focal_gamma: float = 2.0,
        class_weights: Optional[torch.Tensor] = None,
        task_weights: Optional[Dict[str, float]] = None
    ):
        super().__init__()
        
        self.num_labels = num_labels
        self.use_focal_loss = use_focal_loss
        
        # Multi-label classification loss
        if use_focal_loss:
            self.multi_label_loss = FocalLoss(
                alpha=class_weights,
                gamma=focal_gamma
            )
        else:
            self.multi_label_loss = nn.BCEWithLogitsLoss(
                pos_weight=class_weights
            )
        
        # Severity regression loss
        self.severity_loss = nn.MSELoss()
        
        # Span detection loss
        self.span_loss = nn.CrossEntropyLoss(ignore_index=-100)
        
        # Task weights (default: balanced)
        self.task_weights = task_weights or {
            'multi_label': 1.0,
            'severity': 0.5,
            'span': 0.3
        }
    
    def forward(
        self,
        multi_label_logits: torch.Tensor,
        multi_label_targets: torch.Tensor,
        severity_logits: Optional[torch.Tensor] = None,
        severity_targets: Optional[torch.Tensor] = None,
        span_logits: Optional[torch.Tensor] = None,
        span_targets: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Compute combined loss
        
        Returns:
            (total_loss, loss_dict)
        """
        losses = {}
        total_loss = 0.0
        
        # Multi-label loss
        loss_ml = self.multi_label_loss(multi_label_logits, multi_label_targets.float())
        losses['multi_label'] = loss_ml
        total_loss += self.task_weights['multi_label'] * loss_ml
        
        # Severity loss
        if severity_logits is not None and severity_targets is not None:
            loss_sev = self.severity_loss(severity_logits, severity_targets.float())
            losses['severity'] = loss_sev
            total_loss += self.task_weights['severity'] * loss_sev
        
        # Span loss
        if span_logits is not None and span_targets is not None:
            loss_span = self.span_loss(
                span_logits.view(-1, 2),
                span_targets.view(-1)
            )
            losses['span'] = loss_span
            total_loss += self.task_weights['span'] * loss_span
        
        losses['total'] = total_loss
        
        return total_loss, losses


if __name__ == "__main__":
    # Test model
    print("Testing MultiTaskPhoBERT...")
    
    model = MultiTaskPhoBERT(
        num_labels=7,
        use_span_detection=True
    )
    
    # Dummy input
    batch_size = 4
    seq_len = 128
    
    input_ids = torch.randint(0, 1000, (batch_size, seq_len))
    attention_mask = torch.ones(batch_size, seq_len)
    labels_multi = torch.randint(0, 2, (batch_size, 7)).float()
    severity_labels = torch.randint(0, 3, (batch_size,)).float()
    span_labels = torch.randint(0, 2, (batch_size, seq_len))
    
    # Forward pass
    outputs = model(
        input_ids=input_ids,
        attention_mask=attention_mask,
        labels_multi=labels_multi,
        severity_labels=severity_labels,
        span_labels=span_labels
    )
    
    print("\nOutput keys:", outputs.keys())
    print(f"Multi-label logits shape: {outputs['multi_label_logits'].shape}")
    print(f"Severity logits shape: {outputs['severity_logits'].shape}")
    print(f"Span logits shape: {outputs['span_logits'].shape}")
    print(f"Total loss: {outputs['loss'].item():.4f}")
    
    # Test prediction
    predictions = model.predict(input_ids=input_ids, attention_mask=attention_mask)
    print("\nPrediction keys:", predictions.keys())
    print(f"Multi-label predictions: {predictions['multi_label_preds'][0]}")
    print(f"Multi-label probabilities: {predictions['multi_label_probs'][0]}")
    print(f"Severity prediction: {predictions['severity_preds'][0]}")
    
    print("\n✅ Model test passed!")

