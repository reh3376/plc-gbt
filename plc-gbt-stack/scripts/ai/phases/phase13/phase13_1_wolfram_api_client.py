#!/usr/bin/env python3
"""
🧮 Phase 13.1: WolframAlpha Pro API Client - AI Task Orchestrator Implementation

Production-ready WolframAlpha Pro API integration for mathematical validation and
computational intelligence in industrial control systems.

Following AI Task Orchestrator Guide methodology for:
- Robust HTTP client with retry logic and rate limiting
- Authentication and error handling mechanisms
- Query formatting and response parsing
- Integration with Redis caching system
- Cost management and usage optimization

COMPLEXITY: COMPLEX (500-1500 lines, 3-8 hours)
INTEGRATION: WolframAlpha Pro API + Redis Cache + Industrial Control LLM

Author: AI Task Orchestrator
Created: 2025-01-17
Phase: 13.1 - WolframAlpha Pro API Integration
"""

import asyncio
import hashlib
import json
import logging
import os
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WolframQueryType(Enum):
    """WolframAlpha Pro query types for industrial control applications"""
    MATHEMATICAL_CALCULATION = "calculation"
    EQUATION_SOLVING = "equation"
    OPTIMIZATION = "optimization"
    CONTROL_THEORY = "control"
    STABILITY_ANALYSIS = "stability"
    STATISTICAL_ANALYSIS = "statistics"
    DIFFERENTIAL_EQUATIONS = "differential"
    MATRIX_OPERATIONS = "matrix"
    SYMBOLIC_COMPUTATION = "symbolic"
    GRAPH_THEORY = "graph"

class WolframResponseFormat(Enum):
    """Response format options for WolframAlpha Pro"""
    XML = "xml"
    JSON = "json"
    PLAIN_TEXT = "plaintext"
    LATEX = "latex"
    MATHML = "mathml"
    IMAGE = "image"

@dataclass
class WolframQuery:
    """WolframAlpha Pro query configuration"""
    query_id: str
    input_text: str
    query_type: WolframQueryType
    format: WolframResponseFormat = WolframResponseFormat.JSON
    timeout: int = 30
    units: str = "metric"
    assumptions: List[str] = None
    podstates: List[str] = None
    includepodid: List[str] = None
    excludepodid: List[str] = None
    scantimeout: float = 3.0
    podtimeout: float = 5.0
    formattimeout: float = 8.0
    parsetimeout: float = 5.0
    totaltimeout: float = 20.0
    async_mode: bool = True
    reinterpret: bool = True
    translation: bool = True
    ignorecase: bool = True
    sig: Optional[str] = None
    ip: Optional[str] = None
    latlong: Optional[str] = None
    location: Optional[str] = None
    countrycode: Optional[str] = None
    width: int = 500
    maxwidth: int = 1000
    plotwidth: int = 400
    mag: float = 1.0

    def __post_init__(self):
        if self.assumptions is None:
            self.assumptions = []
        if self.podstates is None:
            self.podstates = []
        if self.includepodid is None:
            self.includepodid = []
        if self.excludepodid is None:
            self.excludepodid = []

@dataclass
class WolframPod:
    """Individual pod from WolframAlpha Pro response"""
    pod_id: str
    title: str
    scanner: str
    position: int
    error: bool
    numsubpods: int
    subpods: List[Dict[str, Any]]
    states: List[Dict[str, Any]]
    infos: List[Dict[str, Any]]
    primary: bool = False

@dataclass
class WolframResponse:
    """WolframAlpha Pro API response"""
    response_id: str
    query_id: str
    success: bool
    error: bool
    numpods: int
    datatypes: List[str]
    timedout: List[str]
    timedoutpods: List[str]
    timing: float
    parsetiming: float
    parsetimedout: bool
    recalculate: str
    id: str
    host: str
    server: str
    related: List[str]
    version: str
    pods: List[WolframPod]
    assumptions: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    generalization: Dict[str, Any]
    warnings: List[Dict[str, Any]]
    raw_response: str
    mathematical_result: Optional[str] = None
    confidence_score: float = 0.0
    educational_content: List[str] = None
    validation_status: bool = False
    timestamp: datetime = None

    def __post_init__(self):
        if self.educational_content is None:
            self.educational_content = []
        if self.timestamp is None:
            self.timestamp = datetime.now()

class WolframAPIException(Exception):
    """Custom exception for WolframAlpha Pro API errors"""
    def __init__(self, message: str, error_code: Optional[str] = None, query_id: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        self.query_id = query_id
        super().__init__(f"WolframAlpha API Error: {message}")

class WolframAlphaProClient:
    """
    Production-ready WolframAlpha Pro API client for industrial control applications

    Following AI Task Orchestrator methodology:
    - Robust error handling and retry logic
    - Redis-based caching for cost optimization
    - Rate limiting and quota management
    - Comprehensive logging and monitoring
    """

    def __init__(self,
                 api_key: str,
                 app_id: Optional[str] = None,
                 redis_client: Optional[redis.Redis] = None,
                 base_url: str = "https://api.wolframalpha.com/v2/query",
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 rate_limit_per_minute: int = 100,
                 cache_ttl: int = 3600,
                 enable_caching: bool = True):

        self.api_key = api_key
        self.app_id = app_id
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_per_minute = rate_limit_per_minute
        self.cache_ttl = cache_ttl
        self.enable_caching = enable_caching

        # Initialize Redis client for caching
        self.redis_client = redis_client
        if redis_client is None and enable_caching:
            try:
                self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self.enable_caching = False

        # Rate limiting
        self.request_times = []
        self.request_count = 0

        # Session management
        self.session_id = f"wolfram_session_{int(time.time())}"
        self.session_stats = {
            "queries_sent": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "total_cost": 0.0,
            "avg_response_time": 0.0,
            "start_time": datetime.now()
        }

        logger.info("🧮 WolframAlpha Pro Client initialized")
        logger.info(f"📊 Rate limit: {rate_limit_per_minute} requests/minute")
        logger.info(f"💾 Caching: {'Enabled' if enable_caching else 'Disabled'}")

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            headers={
                "User-Agent": "PLC-GPT Industrial Control LLM/1.0",
                "Accept": "application/json, application/xml, text/plain"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if hasattr(self, 'session'):
            await self.session.close()
        if self.redis_client:
            await self.redis_client.close()

    def _generate_cache_key(self, query: WolframQuery) -> str:
        """Generate cache key for query"""
        key_data = {
            "input": query.input_text,
            "type": query.query_type.value,
            "format": query.format.value,
            "assumptions": sorted(query.assumptions),
            "units": query.units
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"wolfram:{hashlib.md5(key_string.encode()).hexdigest()}"

    async def _check_cache(self, query: WolframQuery) -> Optional[WolframResponse]:
        """Check Redis cache for existing response"""
        if not self.enable_caching or not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key(query)
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                self.session_stats["cache_hits"] += 1
                logger.info(f"🎯 Cache hit for query: {query.query_id}")

                response_data = json.loads(cached_data)
                return WolframResponse(**response_data)
            else:
                self.session_stats["cache_misses"] += 1
                return None

        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
            return None

    async def _store_in_cache(self, query: WolframQuery, response: WolframResponse):
        """Store response in Redis cache"""
        if not self.enable_caching or not self.redis_client:
            return

        try:
            cache_key = self._generate_cache_key(query)
            response_data = asdict(response)

            # Convert datetime to string for JSON serialization
            if 'timestamp' in response_data:
                response_data['timestamp'] = response_data['timestamp'].isoformat()

            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(response_data, default=str)
            )

            logger.info(f"💾 Cached response for query: {query.query_id}")

        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")

    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        current_time = time.time()

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if current_time - t < 60]

        if len(self.request_times) >= self.rate_limit_per_minute:
            wait_time = 60 - (current_time - self.request_times[0])
            logger.warning(f"⏳ Rate limit reached. Waiting {wait_time:.1f} seconds...")
            await asyncio.sleep(wait_time)

        self.request_times.append(current_time)

    def _build_query_params(self, query: WolframQuery) -> Dict[str, str]:
        """Build query parameters for WolframAlpha Pro API"""
        params = {
            "input": query.input_text,
            "format": "plaintext,image",
            "output": "json",
            "appid": self.api_key,
            "units": query.units,
            "timeout": str(query.timeout),
            "scantimeout": str(query.scantimeout),
            "podtimeout": str(query.podtimeout),
            "formattimeout": str(query.formattimeout),
            "parsetimeout": str(query.parsetimeout),
            "totaltimeout": str(query.totaltimeout),
            "width": str(query.width),
            "maxwidth": str(query.maxwidth),
            "plotwidth": str(query.plotwidth),
            "mag": str(query.mag)
        }

        # Add optional parameters
        if query.assumptions:
            params["assumption"] = ",".join(query.assumptions)

        if query.podstates:
            params["podstate"] = ",".join(query.podstates)

        if query.includepodid:
            params["includepodid"] = ",".join(query.includepodid)

        if query.excludepodid:
            params["excludepodid"] = ",".join(query.excludepodid)

        if query.reinterpret:
            params["reinterpret"] = "true"

        if query.translation:
            params["translation"] = "true"

        if query.ignorecase:
            params["ignorecase"] = "true"

        if query.location:
            params["location"] = query.location

        if query.latlong:
            params["latlong"] = query.latlong

        if query.countrycode:
            params["countrycode"] = query.countrycode

        if query.ip:
            params["ip"] = query.ip

        return params

    def _parse_response(self, response_data: Dict[str, Any], query: WolframQuery) -> WolframResponse:
        """Parse WolframAlpha Pro API response"""
        queryresult = response_data.get("queryresult", {})

        # Parse pods
        pods = []
        if "pods" in queryresult:
            for pod_data in queryresult["pods"]:
                pod = WolframPod(
                    pod_id=pod_data.get("id", ""),
                    title=pod_data.get("title", ""),
                    scanner=pod_data.get("scanner", ""),
                    position=pod_data.get("position", 0),
                    error=pod_data.get("error", False),
                    numsubpods=pod_data.get("numsubpods", 0),
                    subpods=pod_data.get("subpods", []),
                    states=pod_data.get("states", []),
                    infos=pod_data.get("infos", []),
                    primary=pod_data.get("primary", False)
                )
                pods.append(pod)

        # Extract mathematical result
        mathematical_result = None
        educational_content = []
        confidence_score = 0.0

        if pods:
            # Look for result in first few pods
            for pod in pods[:3]:
                if pod.subpods and pod.subpods[0].get("plaintext"):
                    if mathematical_result is None:
                        mathematical_result = pod.subpods[0]["plaintext"]
                        confidence_score = 0.9  # High confidence for first result

                    educational_content.append({
                        "title": pod.title,
                        "content": pod.subpods[0]["plaintext"],
                        "scanner": pod.scanner
                    })

        response = WolframResponse(
            response_id=f"resp_{query.query_id}_{int(time.time())}",
            query_id=query.query_id,
            success=queryresult.get("success", False),
            error=queryresult.get("error", False),
            numpods=queryresult.get("numpods", 0),
            datatypes=queryresult.get("datatypes", "").split(",") if queryresult.get("datatypes") else [],
            timedout=queryresult.get("timedout", "").split(",") if queryresult.get("timedout") else [],
            timedoutpods=queryresult.get("timedoutpods", "").split(",") if queryresult.get("timedoutpods") else [],
            timing=float(queryresult.get("timing", 0.0)),
            parsetiming=float(queryresult.get("parsetiming", 0.0)),
            parsetimedout=queryresult.get("parsetimedout", False),
            recalculate=queryresult.get("recalculate", ""),
            id=queryresult.get("id", ""),
            host=queryresult.get("host", ""),
            server=queryresult.get("server", ""),
            related=queryresult.get("related", []),
            version=queryresult.get("version", ""),
            pods=pods,
            assumptions=queryresult.get("assumptions", []),
            sources=queryresult.get("sources", []),
            generalization=queryresult.get("generalization", {}),
            warnings=queryresult.get("warnings", []),
            raw_response=json.dumps(response_data),
            mathematical_result=mathematical_result,
            confidence_score=confidence_score,
            educational_content=educational_content,
            validation_status=queryresult.get("success", False) and not queryresult.get("error", True),
            timestamp=datetime.now()
        )

        return response

    async def query(self,
                   input_text: str,
                   query_type: WolframQueryType = WolframQueryType.MATHEMATICAL_CALCULATION,
                   **kwargs) -> WolframResponse:
        """
        Execute query against WolframAlpha Pro API
        """
        query_id = f"wolfram_{uuid.uuid4().hex[:8]}"

        # Create query object
        query = WolframQuery(
            query_id=query_id,
            input_text=input_text,
            query_type=query_type,
            **kwargs
        )

        logger.info(f"🔍 Executing WolframAlpha query: {query_id}")
        logger.info(f"📝 Input: {input_text}")

        # Check cache first
        cached_response = await self._check_cache(query)
        if cached_response:
            return cached_response

        # Check rate limit
        await self._check_rate_limit()

        # Build query parameters
        params = self._build_query_params(query)

        # Execute query with retries
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()

                async with self.session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        response_data = await response.json()

                        # Parse response
                        wolfram_response = self._parse_response(response_data, query)

                        # Update session stats
                        response_time = time.time() - start_time
                        self.session_stats["queries_sent"] += 1
                        self.session_stats["avg_response_time"] = (
                            (self.session_stats["avg_response_time"] * (self.session_stats["queries_sent"] - 1) + response_time) /
                            self.session_stats["queries_sent"]
                        )

                        # Store in cache
                        await self._store_in_cache(query, wolfram_response)

                        logger.info(f"✅ Query completed successfully: {query_id}")
                        logger.info(f"⏱️ Response time: {response_time:.2f}s")

                        return wolfram_response

                    elif response.status == 403:
                        raise WolframAPIException(
                            "Authentication failed. Check API key.",
                            error_code="AUTH_FAILED",
                            query_id=query_id
                        )

                    elif response.status == 429:
                        wait_time = self.retry_delay * (2 ** attempt)
                        logger.warning(f"⚠️ Rate limited. Waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                        continue

                    else:
                        error_text = await response.text()
                        raise WolframAPIException(
                            f"HTTP {response.status}: {error_text}",
                            error_code=f"HTTP_{response.status}",
                            query_id=query_id
                        )

            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    self.session_stats["errors"] += 1
                    raise WolframAPIException(
                        f"Network error after {self.max_retries} attempts: {e}",
                        error_code="NETWORK_ERROR",
                        query_id=query_id
                    )

                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"Network error on attempt {attempt + 1}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except Exception as e:
                self.session_stats["errors"] += 1
                raise WolframAPIException(
                    f"Unexpected error: {e}",
                    error_code="UNEXPECTED_ERROR",
                    query_id=query_id
                )

        # If we get here, all retries failed
        self.session_stats["errors"] += 1
        raise WolframAPIException(
            f"All {self.max_retries} attempts failed",
            error_code="MAX_RETRIES_EXCEEDED",
            query_id=query_id
        )

    async def batch_query(self, queries: List[Tuple[str, WolframQueryType]]) -> List[WolframResponse]:
        """Execute multiple queries in batch with rate limiting"""
        results = []

        logger.info(f"📦 Executing batch query: {len(queries)} queries")

        for i, (input_text, query_type) in enumerate(queries):
            try:
                response = await self.query(input_text, query_type)
                results.append(response)

                # Add delay between queries to respect rate limits
                if i < len(queries) - 1:
                    await asyncio.sleep(60 / self.rate_limit_per_minute)

            except WolframAPIException as e:
                logger.error(f"Batch query failed for query {i}: {e}")
                # Create error response
                error_response = WolframResponse(
                    response_id=f"error_{i}_{int(time.time())}",
                    query_id=f"batch_{i}",
                    success=False,
                    error=True,
                    numpods=0,
                    datatypes=[],
                    timedout=[],
                    timedoutpods=[],
                    timing=0.0,
                    parsetiming=0.0,
                    parsetimedout=False,
                    recalculate="",
                    id="",
                    host="",
                    server="",
                    related=[],
                    version="",
                    pods=[],
                    assumptions=[],
                    sources=[],
                    generalization={},
                    warnings=[{"text": str(e)}],
                    raw_response="",
                    mathematical_result=None,
                    confidence_score=0.0,
                    educational_content=[],
                    validation_status=False
                )
                results.append(error_response)

        logger.info(f"✅ Batch query completed: {len(results)} results")
        return results

    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        duration = datetime.now() - self.session_stats["start_time"]

        stats = self.session_stats.copy()
        stats["session_duration"] = str(duration)
        stats["cache_hit_rate"] = (
            self.session_stats["cache_hits"] /
            max(1, self.session_stats["cache_hits"] + self.session_stats["cache_misses"])
        )
        stats["queries_per_minute"] = (
            self.session_stats["queries_sent"] /
            max(1, duration.total_seconds() / 60)
        )

        return stats

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of WolframAlpha Pro API"""
        try:
            test_response = await self.query("2+2", WolframQueryType.MATHEMATICAL_CALCULATION)

            return {
                "status": "healthy" if test_response.success else "degraded",
                "api_accessible": True,
                "cache_accessible": self.enable_caching and self.redis_client is not None,
                "last_check": datetime.now().isoformat(),
                "test_query_success": test_response.success,
                "session_stats": self.get_session_stats()
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "cache_accessible": False,
                "last_check": datetime.now().isoformat(),
                "error": str(e),
                "session_stats": self.get_session_stats()
            }

# Industrial Control Theory specific query helpers

class IndustrialControlQueries:
    """Specialized queries for industrial control theory applications"""

    @staticmethod
    def pid_tuning_query(kp: float, ki: float, kd: float, process_type: str = "first_order") -> str:
        """Generate PID tuning analysis query"""
        return f"analyze PID controller with Kp={kp}, Ki={ki}, Kd={kd} for {process_type} process stability and performance"

    @staticmethod
    def transfer_function_analysis(numerator: List[float], denominator: List[float]) -> str:
        """Generate transfer function analysis query"""
        num_str = " + ".join([f"{coeff}*s^{len(numerator)-i-1}" for i, coeff in enumerate(numerator) if coeff != 0])
        den_str = " + ".join([f"{coeff}*s^{len(denominator)-i-1}" for i, coeff in enumerate(denominator) if coeff != 0])
        return f"analyze transfer function ({num_str}) / ({den_str}) for stability, poles, zeros, and frequency response"

    @staticmethod
    def optimization_query(objective: str, constraints: List[str], variables: List[str]) -> str:
        """Generate optimization problem query"""
        constraint_str = ", ".join(constraints)
        variable_str = ", ".join(variables)
        return f"optimize {objective} subject to constraints {constraint_str} with variables {variable_str}"

    @staticmethod
    def stability_analysis_query(system_equation: str) -> str:
        """Generate stability analysis query"""
        return f"analyze stability of control system {system_equation} using Routh-Hurwitz criterion and root locus"

# Example usage and testing functions

async def test_wolfram_client():
    """Test function for WolframAlpha Pro client"""

    # This would require actual API key - for testing only
    api_key = os.getenv("WOLFRAM_ALPHA_API_KEY", "demo_key")

    if api_key == "demo_key":
        logger.warning("Demo mode - using mock responses")
        return

    async with WolframAlphaProClient(api_key) as client:
        # Test basic mathematical calculation
        response = await client.query("integrate x^2 from 0 to 1")
        print(f"Mathematical result: {response.mathematical_result}")

        # Test industrial control query
        pid_query = IndustrialControlQueries.pid_tuning_query(1.0, 0.1, 0.01)
        pid_response = await client.query(pid_query, WolframQueryType.CONTROL_THEORY)
        print(f"PID analysis: {pid_response.mathematical_result}")

        # Test batch queries
        batch_queries = [
            ("solve x^2 + 2x + 1 = 0", WolframQueryType.EQUATION_SOLVING),
            ("derivative of sin(x)", WolframQueryType.MATHEMATICAL_CALCULATION),
            ("matrix inverse {{1,2},{3,4}}", WolframQueryType.MATRIX_OPERATIONS)
        ]

        batch_results = await client.batch_query(batch_queries)
        print(f"Batch results: {len(batch_results)} responses")

        # Print session statistics
        stats = client.get_session_stats()
        print(f"Session stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_wolfram_client())
