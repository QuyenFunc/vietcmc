export class ModerationAPIError extends Error {
  public statusCode: number;
  public error: any;
  
  constructor(statusCode: number, error: any) {
    super(`API Error ${statusCode}: ${error.message || 'Unknown error'}`);
    this.statusCode = statusCode;
    this.error = error;
    this.name = 'ModerationAPIError';
  }
}

