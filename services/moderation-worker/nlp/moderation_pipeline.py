"""
Enhanced 3-Layer Moderation Pipeline
=====================================

Integrates all 3 layers for comprehensive Vietnamese content moderation:

Layer A: Text Normalization & Anti-Obfuscation
  - Creates multiple text versions for detection
  - Handles Unicode, homoglyphs, leetspeak, separators, diacritics

Layer B: Rule-Based / Lexicon Check (Fast & Cheap)
  - Catches obvious profanity + obfuscated variants
  - Detects harassment/body-shaming (non-profane but harmful)
  - Detects hate speech (racial discrimination, etc.)
  - Context-aware flagging

Layer C: ML Model (Context Understanding)
  - PhoBERT multi-task model for nuanced detection
  - Handles subtle harassment, sarcasm, innuendo
  - Runs on BOTH original and normalized text
  - Takes MAX score across versions for each label

Best Practice:
  - Model runs on original + normalized versions
  - Max score per label across versions
  - Combines with rule-based findings

Version: 1.0.0
Last Updated: 2026-01-30
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class ThreeLayerModerationPipeline:
    """
    Main pipeline integrating all 3 moderation layers.
    """
    
    def __init__(
        self, 
        text_model=None,
        use_rule_based: bool = True,
        use_ml_model: bool = True,
        ml_runs_on_multiple_versions: bool = True,
    ):
        """
        Args:
            text_model: ML model instance (MultiTaskModerationInference)
            use_rule_based: Enable Layer B rule-based checking
            use_ml_model: Enable Layer C ML model
            ml_runs_on_multiple_versions: Run ML on original + normalized (take max)
        """
        self.text_model = text_model
        self.use_rule_based = use_rule_based
        self.use_ml_model = use_ml_model
        self.ml_runs_on_multiple_versions = ml_runs_on_multiple_versions
        
        # Initialize Layer A: Normalizer
        try:
            from nlp.text_normalizer import get_normalizer
            self.normalizer = get_normalizer()
            logger.info("Layer A: Text normalizer initialized")
        except ImportError:
            try:
                from text_normalizer import get_normalizer
                self.normalizer = get_normalizer()
                logger.info("Layer A: Text normalizer initialized (direct import)")
            except ImportError:
                logger.error("Failed to import text_normalizer")
                self.normalizer = None
        
        # Initialize Layer B: Rule checker
        if self.use_rule_based:
            try:
                from nlp.rule_checker import get_rule_checker
                self.rule_checker = get_rule_checker()
                logger.info("Layer B: Rule checker initialized")
            except ImportError:
                try:
                    from rule_checker import get_rule_checker
                    self.rule_checker = get_rule_checker()
                    logger.info("Layer B: Rule checker initialized (direct import)")
                except ImportError:
                    logger.warning("Failed to import rule_checker, disabling")
                    self.rule_checker = None
                    self.use_rule_based = False
        else:
            self.rule_checker = None
    
    def _run_layer_a(self, text: str) -> Dict[str, Any]:
        """
        Layer A: Normalize text and create versions
        """
        if not self.normalizer:
            return {
                'original': text,
                'fully_normalized': text.lower(),
                'no_diacritics': text.lower(),
                'metadata': {'has_obfuscation': False, 'obfuscation_types': []},
            }
        
        return self.normalizer.create_all_versions(text)
    
    def _run_layer_b(
        self, 
        text: str, 
        normalized: str, 
        no_diacritics: str,
        metadata: Dict
    ) -> Optional[Dict[str, Any]]:
        """
        Layer B: Rule-based check
        
        Returns result if violation found, None otherwise
        """
        if not self.use_rule_based or not self.rule_checker:
            return None
        
        return self.rule_checker.check(
            text=text,
            normalized_text=normalized,
            no_diacritics_text=no_diacritics,
            metadata=metadata
        )
    
    def _run_layer_c_single(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Run ML model on a single text version
        """
        if not self.use_ml_model or not self.text_model:
            return None
        
        try:
            return self.text_model.predict(text)
        except Exception as e:
            logger.error(f"ML model prediction failed: {e}")
            return None
    
    def _run_layer_c(
        self, 
        original: str, 
        normalized: str,
        versions: Dict
    ) -> Optional[Dict[str, Any]]:
        """
        Layer C: ML model prediction
        
        If ml_runs_on_multiple_versions is True, runs on both original
        and normalized, then takes max score per label.
        """
        if not self.use_ml_model or not self.text_model:
            return None
        
        try:
            # Run on original
            result_original = self.text_model.predict(original)
            
            if not self.ml_runs_on_multiple_versions:
                return result_original
            
            # Also run on normalized version (if different)
            if normalized != original.lower():
                result_normalized = self.text_model.predict(normalized)
                
                # Merge results: take max probabilities
                result = self._merge_ml_results(result_original, result_normalized)
                return result
            else:
                return result_original
        
        except Exception as e:
            logger.error(f"ML model prediction failed: {e}")
            return None
    
    def _merge_ml_results(
        self, 
        result1: Dict[str, Any], 
        result2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge two ML results by taking max probabilities per label
        """
        # If either is a clear reject, use that
        if result1.get('action') == 'reject':
            return result1
        if result2.get('action') == 'reject':
            return result2
        
        # Merge probabilities
        probs1 = result1.get('all_probabilities', {})
        probs2 = result2.get('all_probabilities', {})
        
        merged_probs = {}
        all_labels = set(probs1.keys()) | set(probs2.keys())
        
        for label in all_labels:
            p1 = probs1.get(label, 0)
            p2 = probs2.get(label, 0)
            merged_probs[label] = max(p1, p2)
        
        # Re-determine triggered labels based on merged probs
        threshold = 0.5
        triggered_labels = [l for l, p in merged_probs.items() if p >= threshold]
        
        # Determine action based on merged labels
        harmful_labels = {'toxicity', 'hate', 'harassment', 'threat', 'pii', 'sexual'}
        triggered_harmful = [l for l in triggered_labels if l in harmful_labels]
        
        if triggered_harmful:
            # Has harmful labels
            max_prob = max(merged_probs.get(l, 0) for l in triggered_harmful)
            action = 'reject' if max_prob >= 0.7 else 'review'
        else:
            action = 'allowed'
        
        # Build merged result
        merged = {
            'labels': triggered_labels,
            'action': action,
            'confidence': max(result1.get('confidence', 0), result2.get('confidence', 0)),
            'all_probabilities': merged_probs,
            'reasoning': f"ML model (merged): {', '.join(triggered_labels) if triggered_labels else 'clean'}",
            'method': 'ml_model_merged',
        }
        
        # Copy other fields from the more severe result
        if result1.get('action') in ['reject', 'review']:
            for key in ['severities', 'severity_score', 'probabilities']:
                if key in result1:
                    merged[key] = result1[key]
        elif result2.get('action') in ['reject', 'review']:
            for key in ['severities', 'severity_score', 'probabilities']:
                if key in result2:
                    merged[key] = result2[key]
        
        return merged
    
    def _combine_results(
        self, 
        rule_result: Optional[Dict], 
        ml_result: Optional[Dict],
        versions: Dict
    ) -> Dict[str, Any]:
        """
        Combine rule-based and ML results
        
        Priority:
        1. If rule finds hate speech/severe profanity → use rule result
        2. If ML finds harmful content → use ML result
        3. If rule finds moderate violation → use rule result
        4. Otherwise → clean
        """
        # If no results, return clean
        if not rule_result and not ml_result:
            return {
                'action': 'allowed',
                'labels': [],
                'confidence': 0.9,
                'reasoning': 'Clean content, no violation',
                'method': 'none',
            }
        
        # Rule-based found something severe
        if rule_result and rule_result.get('action') == 'reject':
            # Check if ML agrees (boost confidence)
            if ml_result and ml_result.get('action') in ['reject', 'review']:
                rule_result['confidence'] = min(0.99, rule_result.get('confidence', 0.9) + 0.05)
                rule_result['ml_agrees'] = True
            return rule_result
        
        # ML found harmful content
        if ml_result and ml_result.get('action') == 'reject':
            # Add rule findings if any
            if rule_result:
                ml_result['rule_findings'] = rule_result.get('findings', [])
            return ml_result
        
        # Rule found moderate violation
        if rule_result and rule_result.get('action') == 'review':
            return rule_result
        
        # ML found something worth reviewing
        if ml_result and ml_result.get('action') == 'review':
            return ml_result
        
        # Nothing harmful found
        return {
            'action': 'allowed',
            'labels': ml_result.get('labels', []) if ml_result else [],
            'confidence': 0.85,
            'reasoning': 'No harmful content detected',
            'method': 'combined',
        }
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Main prediction method.
        
        Args:
            text: Input Vietnamese text
        
        Returns:
            Dict with action, labels, confidence, reasoning, etc.
        """
        # Layer A: Normalize
        versions = self._run_layer_a(text)
        
        original = versions['original']
        normalized = versions['fully_normalized']
        no_diacritics = versions['no_diacritics']
        metadata = versions['metadata']
        
        # Log obfuscation detection
        if metadata.get('has_obfuscation'):
            logger.info(f"Obfuscation detected: {metadata['obfuscation_types']}")
        
        # Layer B: Rule-based check
        rule_result = self._run_layer_b(original, normalized, no_diacritics, metadata)
        
        # If rule found severe violation with obfuscation, short-circuit
        if rule_result and rule_result.get('action') == 'reject':
            if metadata.get('has_obfuscation') or 'hate' in rule_result.get('labels', []):
                # Add obfuscation info
                rule_result['normalized_text'] = normalized
                rule_result['obfuscation'] = metadata
                return rule_result
        
        # Layer C: ML model
        ml_result = self._run_layer_c(original, normalized, versions)
        
        # Combine results
        final_result = self._combine_results(rule_result, ml_result, versions)
        
        # Add metadata
        final_result['text_versions'] = {
            'original': original,
            'normalized': normalized,
            'no_diacritics': no_diacritics,
        }
        final_result['obfuscation_detected'] = metadata.get('has_obfuscation', False)
        
        return final_result
    
    def batch_predict(self, texts: List[str], batch_size: int = 32) -> List[Dict[str, Any]]:
        """
        Batch prediction for multiple texts
        """
        results = []
        
        for text in texts:
            result = self.predict(text)
            results.append(result)
        
        return results


# ==================== FACTORY FUNCTION ====================

_pipeline_instance = None

def get_moderation_pipeline(
    text_model=None,
    use_rule_based: bool = True,
    use_ml_model: bool = True,
) -> ThreeLayerModerationPipeline:
    """
    Get or create moderation pipeline instance
    """
    global _pipeline_instance
    
    if _pipeline_instance is None or text_model is not None:
        _pipeline_instance = ThreeLayerModerationPipeline(
            text_model=text_model,
            use_rule_based=use_rule_based,
            use_ml_model=use_ml_model,
        )
    
    return _pipeline_instance


# ==================== TEST ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test without ML model (rule-based only)
    pipeline = ThreeLayerModerationPipeline(
        text_model=None,
        use_rule_based=True,
        use_ml_model=False,
    )
    
    test_cases = [
        # From screenshots - should be REJECTED
        "Bọn da đen bẩn thỉu cút về nước đi",  # Hate speech
        "n.g.u",  # Obfuscated profanity
        "Sao mày xấu thế, nhìn mặt mày tao muốn nôn",  # Body-shaming
        "d:m",  # Obfuscated DM
        "d:m,m",  # Obfuscated DMM
        
        # Should be ALLOWED
        "Sản phẩm tốt quá",
        "Lon bia này ngon",
        "Tôi không hài lòng với dịch vụ",  # Valid complaint
    ]
    
    print("=" * 80)
    print("3-LAYER MODERATION PIPELINE TEST (Rule-Based Only)")
    print("=" * 80)
    
    for text in test_cases:
        print(f"\n📝 Input: '{text}'")
        
        result = pipeline.predict(text)
        
        action = result.get('action', 'unknown')
        labels = result.get('labels', [])
        reasoning = result.get('reasoning', '')
        confidence = result.get('confidence', 0)
        obfuscation = result.get('obfuscation_detected', False)
        
        if action == 'reject':
            print(f"   ❌ REJECTED: {reasoning}")
        elif action == 'review':
            print(f"   ⚠️ REVIEW: {reasoning}")
        else:
            print(f"   ✅ ALLOWED: {reasoning}")
        
        print(f"   Labels: {labels}, Confidence: {confidence:.2%}")
        if obfuscation:
            print(f"   ⚡ Obfuscation detected")
        
        print("-" * 60)
