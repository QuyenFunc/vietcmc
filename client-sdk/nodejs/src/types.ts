export interface ModerationClientConfig {
  apiKey: string;
  hmacSecret: string;
  baseUrl?: string;
  timeout?: number;
}

export interface SubmitJobParams {
  text: string;
  commentId?: string;
  metadata?: Record<string, any>;
}

export interface JobResult {
  jobId: string;
  status: string;
  createdAt: string;
  estimatedProcessingTimeMs: number;
}

export interface JobStatus {
  jobId: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  commentId?: string;
  text?: string;
  result?: {
    sentiment: 'positive' | 'neutral' | 'negative';
    moderationResult: 'allowed' | 'review' | 'reject';
    confidence: number;
    reasoning?: string;
  };
  createdAt: string;
  completedAt?: string;
  processingDurationMs?: number;
}

