import hmac
import hashlib
import json
import requests
from typing import Optional, Dict, Any, List


class ModerationAPIError(Exception):
    """Exception raised for API errors"""
    def __init__(self, status_code: int, error: Dict[str, Any]):
        self.status_code = status_code
        self.error = error
        super().__init__(f"API Error {status_code}: {error.get('message')}")


class ModerationClient:
    """Synchronous client for VietCMS Moderation API"""
    
    def __init__(
        self,
        api_key: str,
        hmac_secret: str,
        base_url: str = "https://api.vietcms-moderation.com/v1",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.hmac_secret = hmac_secret
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def _generate_signature(self, body: str) -> str:
        """Generate HMAC-SHA256 signature for request body"""
        signature = hmac.new(
            self.hmac_secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def submit_job(
        self,
        text: str,
        comment_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Submit a comment for moderation"""
        payload = {"text": text}
        
        if comment_id:
            payload["comment_id"] = comment_id
        
        if metadata:
            payload["metadata"] = metadata
        
        body = json.dumps(payload, ensure_ascii=False)
        signature = self._generate_signature(body)
        
        headers = {'X-Hub-Signature-256': signature}
        
        response = self.session.post(
            f"{self.base_url}/submit",
            data=body,
            headers=headers,
            timeout=self.timeout
        )
        
        if response.status_code == 202:
            return response.json()['data']
        else:
            raise ModerationAPIError(
                response.status_code,
                response.json().get('error', {})
            )
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a job"""
        response = self.session.get(
            f"{self.base_url}/status/{job_id}",
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            return response.json()['data']
        else:
            raise ModerationAPIError(
                response.status_code,
                response.json().get('error', {})
            )
    
    def close(self):
        """Close session"""
        self.session.close()


class AsyncModerationClient:
    """Async client for VietCMS Moderation API"""
    
    def __init__(self, api_key: str, hmac_secret: str, base_url: str = "https://api.vietcms-moderation.com/v1"):
        self.api_key = api_key
        self.hmac_secret = hmac_secret
        self.base_url = base_url.rstrip('/')
    
    async def submit_job(self, text: str, comment_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Submit a comment for moderation (async)"""
        import aiohttp
        
        payload = {"text": text}
        if comment_id:
            payload["comment_id"] = comment_id
        if metadata:
            payload["metadata"] = metadata
        
        body = json.dumps(payload, ensure_ascii=False)
        signature = hmac.new(
            self.hmac_secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'X-API-Key': self.api_key,
            'X-Hub-Signature-256': f"sha256={signature}",
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/submit", data=body, headers=headers) as response:
                if response.status == 202:
                    data = await response.json()
                    return data['data']
                else:
                    error = await response.json()
                    raise ModerationAPIError(response.status, error.get('error', {}))
    
    async def get_job_status(self, job_id: str):
        """Get status of a job (async)"""
        import aiohttp
        
        headers = {'X-API-Key': self.api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/status/{job_id}", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data']
                else:
                    error = await response.json()
                    raise ModerationAPIError(response.status, error.get('error', {}))

