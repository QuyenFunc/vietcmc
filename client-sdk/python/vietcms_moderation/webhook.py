import hmac
import hashlib


class WebhookHandler:
    """Utility for handling webhook callbacks"""
    
    def __init__(self, hmac_secret: str):
        self.hmac_secret = hmac_secret
    
    def verify_signature(self, body: bytes, signature_header: str) -> bool:
        """
        Verify webhook signature
        
        Args:
            body: Request body as bytes
            signature_header: X-Hub-Signature-256 header value
            
        Returns:
            True if signature is valid
        """
        if not signature_header or not signature_header.startswith('sha256='):
            return False
        
        received_signature = signature_header[7:]
        
        expected_signature = hmac.new(
            self.hmac_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(received_signature, expected_signature)

