from enum import Enum
from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class ErrorCode(Enum):
    # Auth Errors
    AUTHENTICATION_FAILED = "AUTH_1001"
    TOKEN_EXPIRED = "AUTH_1002"
    INVALID_CREDENTIALS = "AUTH_1003"
    
    # Database Errors
    DATABASE_CONNECTION_ERROR = "DB_2001"
    DATABASE_QUERY_ERROR = "DB_2002"
    RECORD_NOT_FOUND = "DB_2003"
    
    # Financial Agent Errors
    AGENT_PROCESSING_ERROR = "AGENT_3001"
    RATE_LIMIT_EXCEEDED = "AGENT_3002"
    INVALID_ANALYSIS_TYPE = "AGENT_3003"
    
    # Data Validation Errors
    INVALID_INPUT = "VAL_4001"
    MISSING_REQUIRED_FIELD = "VAL_4002"

class AppException(HTTPException):
    def __init__(
        self,
        error_code: ErrorCode,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code.value,
                "message": detail
            },
            headers=headers
        )