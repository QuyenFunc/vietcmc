"""Exception classes for VietCMS Moderation SDK"""


class ModerationAPIError(Exception):
    """Exception raised for API errors"""
    
    def __init__(self, status_code: int, error: dict):
        self.status_code = status_code
        self.error = error
        super().__init__(f"API Error {status_code}: {error.get('message', 'Unknown error')}")

