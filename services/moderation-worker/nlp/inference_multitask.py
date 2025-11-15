"""
Multi-Task Inference Engine for Vietnamese Content Moderation

Supports:
- Multi-label classification (7 labels)
- Severity prediction (0-2)
- Span detection (optional)
- Rule-based fallback for edge cases
"""

import torch
import numpy as np
from transformers import AutoTokenizer
from typing import Dict, Any, List, Optional, Tuple
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.multitask_phobert import MultiTaskPhoBERT
from nlp.preprocessing_advanced import preprocess_for_phobert, extract_pii, mask_pii
from nlp.taxonomy import (
    ModerationLabel, 
    SeverityLevel, 
    DEFAULT_LABELS, 
    combine_predictions,
    severity_to_action,
    LABEL_DESCRIPTIONS
)
from nlp.toxic_words import (
    get_critical_words,
    get_hate_speech_words,
    get_sexual_content_words,
    SEVERITY_SCORES,
    REJECT_THRESHOLD,
    REVIEW_THRESHOLD,
    AUTO_REJECT_CATEGORIES,
)
from nlp.sentiment_words import HIGHLY_NEGATIVE, MODERATELY_NEGATIVE

logger = logging.getLogger(__name__)


class MultiTaskModerationInference:
    """
    Enhanced inference engine with multi-label and severity prediction
    """
    
    def __init__(
        self,
        model_path: str,
        device: str = 'cpu',
        confidence_threshold: float = 0.5,
        use_rule_based_fallback: bool = True
    ):
        self.model_path = model_path
        self.device = device
        self.confidence_threshold = confidence_threshold
        self.use_rule_based_fallback = use_rule_based_fallback
        
        self.label_names = [label.value for label in DEFAULT_LABELS]
        self.num_labels = len(self.label_names)
        
        # Load model and tokenizer
        self.load_model()
    
    def load_model(self):
        """Load trained multi-task model"""
        try:
            logger.info(f"Loading multi-task model from {self.model_path}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            
            # Load task heads config
            task_heads_path = os.path.join(self.model_path, 'task_heads.pt')
            
            if os.path.exists(task_heads_path):
                checkpoint = torch.load(task_heads_path, map_location=self.device)
                config = checkpoint['config']
                
                # Initialize model
                self.model = MultiTaskPhoBERT(
                    model_name=self.model_path,
                    num_labels=config['num_labels'],
                    num_severity_levels=config['num_severity_levels'],
                    use_span_detection=config.get('use_span_detection', False)
                )
                
                # Load task head weights
                self.model.multi_label_classifier.load_state_dict(
                    checkpoint['multi_label_classifier']
                )
                self.model.severity_regressor.load_state_dict(
                    checkpoint['severity_regressor']
                )
                if config.get('use_span_detection') and checkpoint.get('span_detector'):
                    self.model.span_detector.load_state_dict(
                        checkpoint['span_detector']
                    )
                
                logger.info("Loaded trained multi-task model with task heads")
            else:
                # Fallback: load base model (untrained task heads)
                logger.warning("Task heads not found, loading base model")
                self.model = MultiTaskPhoBERT(
                    model_name=self.model_path,
                    num_labels=self.num_labels,
                    use_span_detection=False
                )
            
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("Model loaded successfully")
        
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def rule_based_check(self, text: str) -> Optional[Dict[str, Any]]:
        """
        ENHANCED Rule-based pre-check with multi-category detection
        Returns None if no clear violation, otherwise returns result dict
        """
        text_lower = text.lower()
        
        # ===== 1. CHECK PII FIRST =====
        pii = extract_pii(text)
        has_pii = any(len(v) > 0 for v in pii.values())
        
        if has_pii:
            return {
                'labels': ['pii'],
                'severities': [SeverityLevel.MODERATE],
                'action': 'review',
                'confidence': 0.95,
                'reasoning': f'Phát hiện thông tin cá nhân: {", ".join([k for k, v in pii.items() if v])}',
                'pii_detected': pii,
                'method': 'rule_based_pii'
            }
        
        # ===== 2. CHECK HATE SPEECH (HIGHEST PRIORITY) =====
        hate_speech_words = get_hate_speech_words()
        detected_hate = []
        
        for word in hate_speech_words:
            if word in text_lower:
                detected_hate.append(word)
        
        if detected_hate:
            # Auto-reject hate speech
            return {
                'labels': ['hate'],
                'severities': [SeverityLevel.SEVERE],
                'action': 'reject',
                'confidence': 0.95,
                'reasoning': f'🚫 HATE SPEECH: Phân biệt đối xử - {", ".join(detected_hate[:3])}',
                'flagged_words': detected_hate,
                'method': 'rule_based_hate_speech'
            }
        
        # ===== 3. CHECK SEXUAL CONTENT =====
        sexual_words = get_sexual_content_words()
        detected_sexual = []
        
        for word in sexual_words:
            if word in text_lower:
                detected_sexual.append(word)
        
        if detected_sexual:
            # Auto-reject explicit sexual content
            return {
                'labels': ['sexual'],
                'severities': [SeverityLevel.SEVERE],
                'action': 'reject',
                'confidence': 0.9,
                'reasoning': f'🚫 NỘI DUNG TÌNH DỤC: {", ".join(detected_sexual[:3])}',
                'flagged_words': detected_sexual,
                'method': 'rule_based_sexual'
            }
        
        # ===== 4. CHECK CRITICAL TOXIC WORDS =====
        critical_words = get_critical_words()
        detected_critical = []
        
        for word in critical_words:
            if word in text_lower:
                detected_critical.append(word)
        
        if detected_critical:
            # Very severe violation
            return {
                'labels': ['toxicity'],
                'severities': [SeverityLevel.SEVERE],
                'action': 'reject',
                'confidence': 0.9,
                'reasoning': f'Vi phạm nghiêm trọng: {", ".join(detected_critical[:3])}',
                'flagged_words': detected_critical,
                'method': 'rule_based_toxicity'
            }
        
        # No clear rule-based violation
        return None
    
    def predict(self, text: str, return_spans: bool = False) -> Dict[str, Any]:
        """
        Predict moderation labels and severity
        
        Args:
            text: Input Vietnamese text
            return_spans: Whether to return span predictions
            
        Returns:
            Dict with labels, severities, action, confidence, reasoning
        """
        # Step 1: Rule-based pre-check
        if self.use_rule_based_fallback:
            rule_result = self.rule_based_check(text)
            if rule_result is not None:
                return rule_result
        
        # Step 2: Preprocess
        processed_text, metadata = preprocess_for_phobert(text)
        
        # Check if preprocessing detected obfuscations
        if metadata.get('obfuscations'):
            logger.info(f"Detected obfuscations: {metadata['obfuscations']}")
        
        # Step 3: Tokenize
        inputs = self.tokenizer(
            processed_text,
            max_length=256,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Step 4: Model inference
        self.model.eval()
        with torch.no_grad():
            predictions = self.model.predict(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                threshold=self.confidence_threshold
            )
        
        # Step 5: Parse predictions
        multi_label_preds = predictions['multi_label_preds'][0].cpu().numpy()  # [num_labels]
        multi_label_probs = predictions['multi_label_probs'][0].cpu().numpy()  # [num_labels]
        severity_pred = predictions['severity_preds'][0].item()
        severity_score = predictions['severity_scores'][0].item()
        
        # Get triggered labels
        triggered_indices = np.where(multi_label_preds == 1)[0]
        triggered_labels = [self.label_names[i] for i in triggered_indices]
        triggered_probs = [float(multi_label_probs[i]) for i in triggered_indices]
        
        # If no labels triggered, it's clean
        if not triggered_labels:
            return {
                'labels': [],
                'severities': [],
                'action': 'allowed',
                'confidence': float(1 - multi_label_probs.max()),
                'reasoning': 'Nội dung sạch, không vi phạm',
                'all_probabilities': {
                    label: float(prob) 
                    for label, prob in zip(self.label_names, multi_label_probs)
                },
                'method': 'ml_model'
            }
        
        # Filter: Only block truly harmful content (toxic, hate, harassment)
        # Allow negative feedback/complaints - those are valid customer opinions
        harmful_labels = {'toxicity', 'hate', 'harassment', 'threat', 'pii', 'sexual'}
        triggered_harmful = [l for l in triggered_labels if l in harmful_labels]
        
        # If only mild labels (like 'spam' or 'profanity' with low confidence), allow
        if not triggered_harmful:
            # Check if any profanity with high confidence
            profanity_idx = self.label_names.index('profanity') if 'profanity' in self.label_names else -1
            if profanity_idx >= 0 and multi_label_preds[profanity_idx] == 1:
                if multi_label_probs[profanity_idx] < 0.8:  # Not very confident
                    return {
                        'labels': [],
                        'severities': [],
                        'action': 'allowed',
                        'confidence': 0.6,
                        'reasoning': 'Ngôn từ hơi mạnh nhưng không vi phạm nghiêm trọng',
                        'method': 'ml_model_filtered'
                    }
            else:
                return {
                    'labels': [],
                    'severities': [],
                    'action': 'allowed',
                    'confidence': 0.7,
                    'reasoning': 'Đánh giá tiêu cực nhưng hợp lệ (ý kiến khách hàng)',
                    'method': 'ml_model_filtered'
                }
        
        # Map to action based on severity
        action = severity_to_action(severity_pred)
        
        # Generate reasoning
        reasoning_parts = []
        for label, prob in zip(triggered_labels, triggered_probs):
            label_desc = LABEL_DESCRIPTIONS.get(
                ModerationLabel(label), {}
            ).get('vi', label)
            reasoning_parts.append(f"{label_desc} ({prob:.2%})")
        
        reasoning = f"Phát hiện vi phạm: {', '.join(reasoning_parts)} | Mức độ: {severity_pred}"
        
        # Build result
        result = {
            'labels': triggered_labels,
            'severities': [severity_pred] * len(triggered_labels),
            'probabilities': {label: prob for label, prob in zip(triggered_labels, triggered_probs)},
            'action': action,
            'confidence': float(np.mean(triggered_probs)) if triggered_probs else 0.5,
            'reasoning': reasoning,
            'severity_score': float(severity_score),
            'all_probabilities': {
                label: float(prob) 
                for label, prob in zip(self.label_names, multi_label_probs)
            },
            'method': 'ml_model'
        }
        
        # Add span predictions if requested
        if return_spans and predictions['span_preds'] is not None:
            span_preds = predictions['span_preds'][0].cpu().numpy()
            result['span_predictions'] = self._extract_spans(
                processed_text, span_preds, inputs['attention_mask'][0]
            )
        
        return result
    
    def _extract_spans(
        self, 
        text: str, 
        span_preds: np.ndarray, 
        attention_mask: torch.Tensor
    ) -> List[Dict[str, Any]]:
        """
        Extract violation spans from token-level predictions
        
        Args:
            text: Processed text
            span_preds: [seq_len] token predictions (0 or 1)
            attention_mask: [seq_len] attention mask
            
        Returns:
            List of span dicts with start, end, text
        """
        # Get valid tokens (not padding)
        valid_length = attention_mask.sum().item()
        valid_preds = span_preds[:valid_length]
        
        # Tokenize to get token-to-char mapping
        tokens = self.tokenizer.tokenize(text)
        
        spans = []
        current_span = None
        
        for i, (token, pred) in enumerate(zip(tokens, valid_preds)):
            if pred == 1:  # Violation token
                if current_span is None:
                    current_span = {
                        'start': i,
                        'tokens': [token]
                    }
                else:
                    current_span['tokens'].append(token)
            else:
                if current_span is not None:
                    # End current span
                    current_span['end'] = i
                    current_span['text'] = ' '.join(current_span['tokens'])
                    spans.append(current_span)
                    current_span = None
        
        # Close last span if exists
        if current_span is not None:
            current_span['end'] = len(tokens)
            current_span['text'] = ' '.join(current_span['tokens'])
            spans.append(current_span)
        
        return spans
    
    def batch_predict(
        self, 
        texts: List[str], 
        batch_size: int = 32
    ) -> List[Dict[str, Any]]:
        """
        Batch prediction for multiple texts
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            List of prediction dicts
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            
            for text in batch_texts:
                result = self.predict(text)
                results.append(result)
        
        return results


# Backward compatibility wrapper
class ModerationInference:
    """
    Wrapper for backward compatibility with existing code
    Maps multi-label output to single sentiment/moderation result
    """
    
    def __init__(self, model_path: str = None, device: str = 'cpu'):
        self.model_path = model_path or 'vinai/phobert-base-v2'
        self.device = device
        
        # Try to load multi-task model, fallback to rule-based
        try:
            self.engine = MultiTaskModerationInference(
                model_path=self.model_path,
                device=device
            )
            self.use_ml = True
        except Exception as e:
            logger.warning(f"Failed to load ML model: {e}, using rule-based only")
            self.use_ml = False
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict with backward compatible output format
        
        Returns:
            Dict with sentiment, moderation_result, confidence, reasoning
        """
        if self.use_ml:
            result = self.engine.predict(text)
            
            # Map to old format
            action_map = {
                'allowed': 'allowed',
                'review': 'review',
                'reject': 'reject'
            }
            
            # Determine sentiment from labels
            if 'toxicity' in result['labels'] or 'hate' in result['labels']:
                sentiment = 'negative'
            elif not result['labels']:
                sentiment = 'positive'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'moderation_result': action_map.get(result['action'], 'review'),
                'confidence': result['confidence'],
                'reasoning': result['reasoning'],
                'labels': result['labels'],  # Extra info
                'flagged_words': []
            }
        else:
            # Fallback to simple rule-based
            from nlp.inference import ModerationInference as OldInference
            old_engine = OldInference(model_path=self.model_path, device=self.device)
            return old_engine.predict(text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test inference
    test_texts = [
        "Sản phẩm rất tốt, tôi rất hài lòng!",
        "Đồ rác vãi lồn, không mua nữa",
        "Shop lừa đảo, inbox mua hàng 0123456789",
        "Bọn khỉ đen này ngu vãi",
        "Sản phẩm bình thường, giá hơi cao",
    ]
    
    print("="*80)
    print("MULTI-TASK INFERENCE TEST")
    print("="*80)
    
    # Test with base model (not trained)
    engine = MultiTaskModerationInference(
        model_path='vinai/phobert-base-v2',
        device='cpu'
    )
    
    for text in test_texts:
        print(f"\nText: {text}")
        result = engine.predict(text)
        print(f"Labels: {result['labels']}")
        print(f"Action: {result['action']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Reasoning: {result['reasoning']}")
        if 'all_probabilities' in result:
            print("All probabilities:")
            for label, prob in result['all_probabilities'].items():
                if prob > 0.3:
                    print(f"  {label}: {prob:.2%}")

