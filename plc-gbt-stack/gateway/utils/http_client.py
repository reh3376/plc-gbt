"""
Base HTTP Client with Retry Logic
Extracted common HTTP handling patterns from proxy files
"""

import asyncio
import aiohttp
import structlog
from typing import Dict, Any, Optional
from dataclasses import dataclass
from fastapi import HTTPException

logger = structlog.get_logger()

@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    timeout: float = 30.0

class HTTPClientBase:
    """Base HTTP client with retry logic and error handling"""
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None, 
                 retry_config: Optional[RetryConfig] = None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.retry_config = retry_config or RetryConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=self.retry_config.timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling"""
        if not self.session:
            raise RuntimeError("HTTP session not initialized - use as context manager")
        
        url = f"{self.base_url}{endpoint}"
        retries = 0
        
        while retries <= self.retry_config.max_retries:
            try:
                async with self._execute_request(method, url, data, params) as response:
                    return await self._handle_response(response)
                    
            except aiohttp.ClientError as e:
                retries += 1
                if retries > self.retry_config.max_retries:
                    logger.error(f"HTTP request failed after {self.retry_config.max_retries} retries", 
                               url=url, error=str(e))
                    raise HTTPException(
                        status_code=503,
                        detail=f"Service unavailable: {str(e)}"
                    )
                
                # Exponential backoff with jitter
                delay = min(
                    self.retry_config.base_delay * (self.retry_config.exponential_base ** retries),
                    self.retry_config.max_delay
                )
                await asyncio.sleep(delay)
                logger.warning(f"Retrying request in {delay:.1f}s", 
                             url=url, attempt=retries)
    
    async def _execute_request(self, method: str, url: str, data: Optional[Dict], 
                             params: Optional[Dict]):
        """Execute the actual HTTP request"""
        method = method.upper()
        if method == "GET":
            return self.session.get(url, params=params)
        elif method == "POST":
            return self.session.post(url, json=data, params=params)
        elif method == "PUT":
            return self.session.put(url, json=data, params=params)
        elif method == "DELETE":
            return self.session.delete(url, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle HTTP response and common error cases"""
        if response.status == 200:
            return await response.json()
        elif response.status == 401:
            raise HTTPException(status_code=401, detail="Authentication failed")
        elif response.status == 404:
            raise HTTPException(status_code=404, detail="Endpoint not found")
        elif response.status == 429:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        elif response.status >= 500:
            error_text = await response.text()
            logger.error(f"Server error", status=response.status, error=error_text)
            raise HTTPException(
                status_code=response.status,
                detail=f"Server error: {error_text}"
            )
        else:
            error_text = await response.text()
            logger.error(f"HTTP request failed", status=response.status, error=error_text)
            raise HTTPException(
                status_code=response.status,
                detail=f"Request failed: {error_text}"
            ) 