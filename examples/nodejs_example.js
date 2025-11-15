/**
 * Example usage of VietCMS Moderation SDK for NodeJS
 */

const { ModerationClient, WebhookHandler } = require('@vietcms/moderation-sdk');
const express = require('express');

// Initialize client
const client = new ModerationClient({
  apiKey: 'your-api-key-here',
  hmacSecret: 'your-hmac-secret-here',
  baseUrl: 'http://localhost/api/v1'
});

// Example 1: Submit a comment
async function example1() {
  console.log('Example 1: Submit single comment');
  console.log('='.repeat(50));
  
  try {
    const result = await client.submitJob({
      text: 'Sản phẩm rất tốt, tôi rất hài lòng!',
      commentId: 'comment_001',
      metadata: {
        userId: 'user_123',
        postId: 'post_456'
      }
    });
    
    console.log(`Job ID: ${result.jobId}`);
    console.log(`Status: ${result.status}`);
    
    // Wait and check status
    console.log('\nWaiting for processing...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    const status = await client.getJobStatus(result.jobId);
    console.log(`Current status: ${status.status}`);
    
    if (status.status === 'completed') {
      console.log(`Sentiment: ${status.result.sentiment}`);
      console.log(`Moderation: ${status.result.moderationResult}`);
      console.log(`Confidence: ${status.result.confidence}`);
    }
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Example 2: Webhook handler with Express
function example2() {
  console.log('\n\nExample 2: Webhook Handler');
  console.log('='.repeat(50));
  
  const app = express();
  const webhookHandler = new WebhookHandler({
    hmacSecret: 'your-hmac-secret-here'
  });
  
  app.post('/webhooks/moderation', express.raw({ type: 'application/json' }), (req, res) => {
    const signature = req.headers['x-hub-signature-256'];
    
    // Verify signature
    if (!webhookHandler.verifySignature(req.body, signature)) {
      return res.status(403).json({ error: 'Invalid signature' });
    }
    
    // Process webhook
    const payload = JSON.parse(req.body.toString());
    
    console.log(`Received webhook for job: ${payload.job_id}`);
    console.log(`Result: ${payload.moderation_result}`);
    console.log(`Sentiment: ${payload.sentiment}`);
    
    // Handle in your application
    // updateCommentStatus(payload.comment_id, payload.moderation_result);
    
    res.json({ received: true });
  });
  
  console.log('Webhook server ready on http://localhost:3000/webhooks/moderation');
  // app.listen(3000);
}

// Run examples
if (require.main === module) {
  example1().then(() => {
    example2();
  });
}

