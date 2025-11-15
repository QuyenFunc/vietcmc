import crypto from 'crypto';

export class WebhookHandler {
  private hmacSecret: string;
  
  constructor(config: { hmacSecret: string }) {
    this.hmacSecret = config.hmacSecret;
  }
  
  verifySignature(body: Buffer, signatureHeader: string): boolean {
    if (!signatureHeader || !signatureHeader.startsWith('sha256=')) {
      return false;
    }
    
    const receivedSignature = signatureHeader.substring(7);
    
    const hmac = crypto.createHmac('sha256', this.hmacSecret);
    hmac.update(body);
    const expectedSignature = hmac.digest('hex');
    
    return crypto.timingSafeEqual(
      Buffer.from(receivedSignature),
      Buffer.from(expectedSignature)
    );
  }
}

