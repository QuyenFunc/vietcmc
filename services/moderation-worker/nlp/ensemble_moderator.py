"""
Ensemble Moderation Engine for Vietnamese Content
Combines multiple approaches for highest accuracy:
- Rule-based detection (fast, high precision)
- ML model prediction (good generalization)
- Context analysis (reduce false positives)
- Variant detection (catch obfuscation)

Version: 1.0.0
Last Updated: 2025-12-19
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class ModerationMethod(Enum):
    """Methods used for moderation decision"""
    RULE_BASED = "rule_based"
    ML_MODEL = "ml_model"
    CONTEXT_ANALYSIS = "context_analysis"
    VARIANT_DETECTION = "variant_detection"
    ENSEMBLE = "ensemble"


class ModerationAction(Enum):
    """Possible moderation actions"""
    ALLOWED = "allowed"
    REVIEW = "review"
    REJECT = "reject"


@dataclass
class ModerationResult:
    """Complete moderation result with all metadata"""
    action: ModerationAction
    confidence: float
    reasoning: str
    
    # Contributing factors
    methods_used: List[ModerationMethod]
    rule_based_result: Optional[Dict] = None
    ml_result: Optional[Dict] = None
    context_result: Optional[Dict] = None
    variant_result: Optional[Dict] = None
    
    # Labels and flags
    labels: List[str] = None
    flagged_words: List[str] = None
    severity_score: float = 0.0
    
    # Metadata
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            'action': self.action.value,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'methods_used': [m.value for m in self.methods_used],
            'labels': self.labels or [],
            'flagged_words': self.flagged_words or [],
            'severity_score': self.severity_score,
            'processing_time_ms': self.processing_time_ms,
        }


class EnsembleWeights:
    """Configurable weights for ensemble decision"""
    
    # Method weights (how much to trust each method)
    RULE_BASED_WEIGHT = 0.35
    ML_MODEL_WEIGHT = 0.30
    CONTEXT_WEIGHT = 0.20
    VARIANT_WEIGHT = 0.15
    
    # Threshold for final decision
    REJECT_THRESHOLD = 0.75
    REVIEW_THRESHOLD = 0.45
    
    # Boost factors for specific scenarios
    HATE_SPEECH_BOOST = 1.5
    PERSONAL_ATTACK_BOOST = 1.3
    SEXUAL_CONTENT_BOOST = 1.5
    OBFUSCATION_PENALTY = 1.2  # More suspicious if obfuscation used
    
    # Reduction factors
    LEGITIMATE_CRITICISM_REDUCTION = 0.5
    SAFE_CONTEXT_REDUCTION = 0.6
    QUESTION_REDUCTION = 0.7


class EnsembleModerator:
    """
    Main ensemble moderator that combines all approaches
    """
    
    def __init__(
        self,
        ml_inference=None,  # MultiTaskModerationInference instance
        use_context_analyzer: bool = True,
        use_variant_detector: bool = True,
        weights: EnsembleWeights = None
    ):
        self.ml_inference = ml_inference
        self.weights = weights or EnsembleWeights()
        
        # Initialize components
        self.context_analyzer = None
        self.variant_detector = None
        
        if use_context_analyzer:
            try:
                from nlp.context_analyzer import get_enhanced_analyzer
                self.context_analyzer = get_enhanced_analyzer()
                logger.info("Context analyzer loaded for ensemble")
            except Exception as e:
                logger.warning(f"Could not load context analyzer: {e}")
        
        if use_variant_detector:
            try:
                from nlp.variant_detector import get_variant_detector
                self.variant_detector = get_variant_detector()
                logger.info("Variant detector loaded for ensemble")
            except Exception as e:
                logger.warning(f"Could not load variant detector: {e}")
    
    def _run_rule_based(self, text: str) -> Optional[Dict[str, Any]]:
        """Run rule-based detection"""
        if self.ml_inference and hasattr(self.ml_inference, 'rule_based_check'):
            return self.ml_inference.rule_based_check(text)
        return None
    
    def _run_ml_model(self, text: str) -> Optional[Dict[str, Any]]:
        """Run ML model prediction"""
        if self.ml_inference:
            try:
                # Get raw ML prediction without rule-based
                original_flag = getattr(self.ml_inference, 'use_rule_based_fallback', True)
                self.ml_inference.use_rule_based_fallback = False
                result = self.ml_inference.predict(text)
                self.ml_inference.use_rule_based_fallback = original_flag
                return result
            except Exception as e:
                logger.error(f"ML model error: {e}")
        return None
    
    def _run_context_analysis(self, text: str, flagged_words: List[str] = None) -> Optional[Dict[str, Any]]:
        """Run context analysis"""
        if self.context_analyzer:
            try:
                return self.context_analyzer.analyze(text, flagged_words or [])
            except Exception as e:
                logger.error(f"Context analysis error: {e}")
        return None
    
    def _run_variant_detection(self, text: str) -> Optional[Dict[str, Any]]:
        """Run variant detection"""
        if self.variant_detector:
            try:
                return self.variant_detector.analyze(text)
            except Exception as e:
                logger.error(f"Variant detection error: {e}")
        return None
    
    def _calculate_ensemble_score(
        self,
        rule_result: Optional[Dict],
        ml_result: Optional[Dict],
        context_result: Optional[Dict],
        variant_result: Optional[Dict]
    ) -> Tuple[float, List[str], str]:
        """
        Calculate ensemble score from all methods
        
        Returns:
            (score, labels, reasoning)
        """
        scores = []
        labels = set()
        reasoning_parts = []
        
        # 1. Rule-based score
        if rule_result:
            action = rule_result.get('action', 'allowed')
            if action == 'reject':
                rule_score = 1.0
            elif action == 'review':
                rule_score = 0.6
            else:
                rule_score = 0.0
            
            scores.append(('rule', rule_score, self.weights.RULE_BASED_WEIGHT))
            
            if rule_result.get('labels'):
                labels.update(rule_result['labels'])
            
            if rule_score > 0:
                reasoning_parts.append(f"Rule: {rule_result.get('reasoning', 'violation detected')[:50]}")
        
        # 2. ML model score
        if ml_result:
            action = ml_result.get('action', 'allowed')
            ml_confidence = ml_result.get('confidence', 0.5)
            
            if action == 'reject':
                ml_score = 0.7 + (ml_confidence * 0.3)
            elif action == 'review':
                ml_score = 0.4 + (ml_confidence * 0.2)
            else:
                ml_score = 1.0 - ml_confidence
            
            scores.append(('ml', ml_score, self.weights.ML_MODEL_WEIGHT))
            
            if ml_result.get('labels'):
                labels.update(ml_result['labels'])
            
            if ml_score > 0.3:
                reasoning_parts.append(f"ML: {ml_result.get('reasoning', 'model prediction')[:50]}")
        
        # 3. Variant detection score (NEW: Direct scoring)
        variant_score = 0.0
        variant_boost = 1.0
        if variant_result:
            if variant_result.get('has_violations'):
                variants = variant_result.get('detected_variants', [])
                severity = variant_result.get('overall_severity', 'low')
                
                # Direct score based on severity
                if severity == 'high':
                    variant_score = 0.9
                    variant_boost = 1.5
                elif severity == 'medium':
                    variant_score = 0.7
                    variant_boost = 1.3
                else:
                    variant_score = 0.5
                    variant_boost = 1.1
                
                # Add variant detection as a scored method
                scores.append(('variant', variant_score, self.weights.VARIANT_WEIGHT))
                
                for v in variants:
                    labels.add(v.get('normalized', 'toxicity'))
                
                reasoning_parts.append(f"Variant: {len(variants)} toxic words detected (severity: {severity})")
            
            if variant_result.get('has_obfuscation') and variant_result.get('has_violations'):
                variant_boost *= self.weights.OBFUSCATION_PENALTY
                reasoning_parts.append("Obfuscation detected - higher severity")
        
        # 4. Context analysis adjustment
        context_modifier = 1.0
        if context_result:
            intent = context_result.get('intent', 'neutral')
            
            if context_result.get('is_legitimate_criticism'):
                context_modifier *= self.weights.LEGITIMATE_CRITICISM_REDUCTION
                reasoning_parts.append("Context: legitimate criticism")
            
            if context_result.get('severity_modifier', 1.0) < 0.7:
                context_modifier *= self.weights.SAFE_CONTEXT_REDUCTION
                reasoning_parts.append("Context: safe context detected")
            
            if intent == 'question':
                context_modifier *= self.weights.QUESTION_REDUCTION
            elif intent == 'hate_speech':
                context_modifier *= self.weights.HATE_SPEECH_BOOST
                # Force high score for hate speech
                if variant_score < 0.9:
                    variant_score = 0.95
                    scores.append(('hate_speech', 0.95, 0.4))
                labels.add('hate')
            elif intent == 'personal_attack':
                context_modifier *= self.weights.PERSONAL_ATTACK_BOOST
                labels.add('harassment')
        
        # Calculate weighted score
        if scores:
            total_weight = sum(w for _, _, w in scores)
            weighted_sum = sum(s * w for _, s, w in scores)
            base_score = weighted_sum / total_weight
        else:
            base_score = 0.0
        
        # Apply modifiers
        # For violations, only boost (don't reduce)
        if base_score > 0.3:
            final_score = base_score * variant_boost
        else:
            final_score = base_score * context_modifier
        
        final_score = max(0.0, min(1.0, final_score))
        
        # Build reasoning
        if not reasoning_parts:
            reasoning = "No violations detected"
        else:
            reasoning = " | ".join(reasoning_parts)
        
        return final_score, list(labels), reasoning
    
    def _determine_action(self, score: float) -> ModerationAction:
        """Determine action based on score"""
        if score >= self.weights.REJECT_THRESHOLD:
            return ModerationAction.REJECT
        elif score >= self.weights.REVIEW_THRESHOLD:
            return ModerationAction.REVIEW
        else:
            return ModerationAction.ALLOWED
    
    def moderate(self, text: str) -> ModerationResult:
        """
        Run full ensemble moderation
        
        Args:
            text: Input text to moderate
            
        Returns:
            ModerationResult with complete analysis
        """
        import time
        start_time = time.time()
        
        methods_used = []
        
        # 1. Rule-based check (fast, do first)
        rule_result = self._run_rule_based(text)
        if rule_result:
            methods_used.append(ModerationMethod.RULE_BASED)
        
        # 2. Variant detection (catch obfuscation)
        variant_result = self._run_variant_detection(text)
        if variant_result:
            methods_used.append(ModerationMethod.VARIANT_DETECTION)
        
        # 3. Get flagged words for context analysis
        flagged_words = []
        if rule_result and rule_result.get('flagged_words'):
            flagged_words.extend(rule_result['flagged_words'])
        if variant_result and variant_result.get('detected_variants'):
            flagged_words.extend([v['normalized'] for v in variant_result['detected_variants']])
        
        # 4. Context analysis
        context_result = self._run_context_analysis(text, flagged_words)
        if context_result:
            methods_used.append(ModerationMethod.CONTEXT_ANALYSIS)
        
        # 5. ML model (slower, run last)
        ml_result = None
        # Only run ML if we need more info or inconclusive
        needs_ml = (
            rule_result is None or
            rule_result.get('action') == 'review' or
            (context_result and context_result.get('is_legitimate_criticism'))
        )
        
        if needs_ml:
            ml_result = self._run_ml_model(text)
            if ml_result:
                methods_used.append(ModerationMethod.ML_MODEL)
        
        # 6. Calculate ensemble score
        score, labels, reasoning = self._calculate_ensemble_score(
            rule_result, ml_result, context_result, variant_result
        )
        
        # 7. Determine final action
        action = self._determine_action(score)
        methods_used.append(ModerationMethod.ENSEMBLE)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Build result
        return ModerationResult(
            action=action,
            confidence=score,
            reasoning=reasoning,
            methods_used=methods_used,
            rule_based_result=rule_result,
            ml_result=ml_result,
            context_result=context_result,
            variant_result=variant_result,
            labels=labels,
            flagged_words=flagged_words,
            severity_score=score,
            processing_time_ms=processing_time,
        )
    
    def batch_moderate(self, texts: List[str]) -> List[ModerationResult]:
        """
        Moderate multiple texts
        
        For better performance with ML model, considers batching
        """
        # For now, just loop - can optimize later with batch ML inference
        return [self.moderate(text) for text in texts]


# ==================== CONFIDENCE CALIBRATION ====================

class MLConfidenceCalibrator:
    """
    Calibrate ML model confidence based on historical accuracy
    Uses Platt scaling or similar techniques
    """
    
    def __init__(self):
        # Default calibration parameters (can be trained)
        self.scale = 1.0
        self.shift = 0.0
        
        # Thresholds for different label types
        self.label_thresholds = {
            'toxicity': 0.6,
            'hate': 0.5,  # Lower = more sensitive
            'harassment': 0.55,
            'threat': 0.5,
            'sexual': 0.5,
            'pii': 0.4,
            'profanity': 0.7,  # Higher = less sensitive
            'spam': 0.6,
        }
    
    def calibrate(self, raw_confidence: float, label: str = None) -> float:
        """
        Calibrate raw model confidence
        
        Args:
            raw_confidence: Raw confidence from model
            label: Optional label for label-specific calibration
            
        Returns:
            Calibrated confidence
        """
        # Basic Platt scaling
        calibrated = raw_confidence * self.scale + self.shift
        
        # Apply sigmoid if needed
        # calibrated = 1 / (1 + np.exp(-calibrated))
        
        # Clip to valid range
        return max(0.0, min(1.0, calibrated))
    
    def get_threshold(self, label: str) -> float:
        """Get decision threshold for a label"""
        return self.label_thresholds.get(label, 0.5)
    
    def train(self, predictions: List[float], ground_truth: List[int]):
        """
        Train calibration parameters on validation data
        
        Args:
            predictions: Model confidence scores
            ground_truth: Actual labels (0 or 1)
        """
        # Simple training: find optimal scale and shift
        # This is a placeholder - implement proper Platt scaling or isotonic regression
        
        predictions = np.array(predictions)
        ground_truth = np.array(ground_truth)
        
        # Calculate basic statistics
        tp_confidences = predictions[ground_truth == 1]
        tn_confidences = predictions[ground_truth == 0]
        
        if len(tp_confidences) > 0 and len(tn_confidences) > 0:
            tp_mean = np.mean(tp_confidences)
            tn_mean = np.mean(tn_confidences)
            
            # Adjust scale to separate true positives and true negatives
            if tp_mean > tn_mean:
                self.scale = 1.0 / (tp_mean - tn_mean)
            
            logger.info(f"Calibration trained: scale={self.scale:.4f}")


# ==================== FACTORY FUNCTION ====================

_ensemble_instance = None

def create_ensemble_moderator(
    model_path: str = 'vinai/phobert-base-v2',
    device: str = 'cpu',
    use_ml: bool = True
) -> EnsembleModerator:
    """
    Factory function to create ensemble moderator
    
    Args:
        model_path: Path to PhoBERT model
        device: Device for ML model ('cpu' or 'cuda')
        use_ml: Whether to use ML model
        
    Returns:
        Configured EnsembleModerator
    """
    global _ensemble_instance
    
    if _ensemble_instance is not None:
        return _ensemble_instance
    
    ml_inference = None
    if use_ml:
        try:
            from nlp.inference_multitask import MultiTaskModerationInference
            ml_inference = MultiTaskModerationInference(
                model_path=model_path,
                device=device,
                use_context_analyzer=False  # We use our own
            )
            logger.info("ML inference loaded for ensemble")
        except Exception as e:
            logger.warning(f"Could not load ML inference: {e}")
    
    _ensemble_instance = EnsembleModerator(
        ml_inference=ml_inference,
        use_context_analyzer=True,
        use_variant_detector=True
    )
    
    return _ensemble_instance


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test ensemble moderator
    moderator = create_ensemble_moderator(use_ml=False)  # Skip ML for quick test
    
    test_cases = [
        # Clean content
        "Sản phẩm rất tốt, tôi rất hài lòng!",
        
        # Legitimate criticism
        "Sản phẩm tệ quá, chất lượng kém, không đáng tiền",
        "Hàng giao chậm, thất vọng",
        
        # Obfuscated toxic
        "đ.ụ m.á mày",
        "v@i l0n",
        
        # Clear toxic
        "Thằng ngu vãi lồn",
        "Bọn gay đáng ghét, nên chết hết",
        
        # Edge cases
        "Các bạn ơi, sản phẩm này tốt không?",
        "Du lịch Đà Nẵng vui quá",
        "Tình hình gay gắt",
    ]
    
    print("=" * 80)
    print("ENSEMBLE MODERATION TEST")
    print("=" * 80)
    
    for text in test_cases:
        result = moderator.moderate(text)
        
        icon = "✅" if result.action == ModerationAction.ALLOWED else (
            "⚠️" if result.action == ModerationAction.REVIEW else "🚫"
        )
        
        print(f"\n{icon} '{text[:50]}...'")
        print(f"   Action: {result.action.value}")
        print(f"   Confidence: {result.confidence:.2%}")
        print(f"   Methods: {[m.value for m in result.methods_used]}")
        print(f"   Labels: {result.labels}")
        print(f"   Reasoning: {result.reasoning[:80]}...")
        print(f"   Time: {result.processing_time_ms:.2f}ms")
