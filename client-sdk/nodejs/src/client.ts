import axios, { AxiosInstance } from 'axios';
import crypto from 'crypto';
import { ModerationClientConfig, SubmitJobParams, JobResult, JobStatus } from './types';
import { ModerationAPIError } from './errors';

export class ModerationClient {
  private apiKey: string;
  private hmacSecret: string;
  private client: AxiosInstance;
  
  constructor(config: ModerationClientConfig) {
    this.apiKey = config.apiKey;
    this.hmacSecret = config.hmacSecret;
    
    this.client = axios.create({
      baseURL: config.baseUrl || 'https://api.vietcms-moderation.com/v1',
      timeout: config.timeout || 30000,
      headers: {
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json'
      }
    });
  }
  
  private generateSignature(body: string): string {
    const hmac = crypto.createHmac('sha256', this.hmacSecret);
    hmac.update(body);
    return `sha256=${hmac.digest('hex')}`;
  }
  
  async submitJob(params: SubmitJobParams): Promise<JobResult> {
    const payload: any = {
      text: params.text
    };
    
    if (params.commentId) {
      payload.comment_id = params.commentId;
    }
    
    if (params.metadata) {
      payload.metadata = params.metadata;
    }
    
    const body = JSON.stringify(payload);
    const signature = this.generateSignature(body);
    
    try {
      const response = await this.client.post('/submit', body, {
        headers: {
          'X-Hub-Signature-256': signature
        }
      });
      
      return response.data.data;
    } catch (error: any) {
      if (error.response) {
        throw new ModerationAPIError(
          error.response.status,
          error.response.data.error || {}
        );
      }
      throw error;
    }
  }
  
  async getJobStatus(jobId: string): Promise<JobStatus> {
    try {
      const response = await this.client.get(`/status/${jobId}`);
      return response.data.data;
    } catch (error: any) {
      if (error.response) {
        throw new ModerationAPIError(
          error.response.status,
          error.response.data.error || {}
        );
      }
      throw error;
    }
  }
}

