# Productionization Guide - Moving from Tutorial to Production

Comprehensive guide for transforming the tutorial code into a production-ready AI agent system.

---

## Table of Contents
1. [Production Readiness Checklist](#production-readiness-checklist)
2. [Architecture Enhancements](#architecture-enhancements)
3. [Code Refactoring](#code-refactoring)
4. [API Layer Implementation](#api-layer-implementation)
5. [Error Handling & Logging](#error-handling--logging)
6. [Security & Secrets Management](#security--secrets-management)
7. [Monitoring & Observability](#monitoring--observability)
8. [Deployment Strategies](#deployment-strategies)
9. [Scaling Considerations](#scaling-considerations)
10. [Cost Optimization](#cost-optimization)

---

## Production Readiness Checklist

### Phase 1: Code Quality (Week 1)
- [ ] Restructure monolithic files into modules
- [ ] Add comprehensive error handling
- [ ] Implement structured logging
- [ ] Add type hints throughout
- [ ] Create unit tests (80%+ coverage)
- [ ] Add integration tests
- [ ] Setup linting (pylint, flake8, black)
- [ ] Add pre-commit hooks

### Phase 2: Infrastructure (Week 2)
- [ ] Wrap agents in FastAPI endpoints
- [ ] Add request validation
- [ ] Implement rate limiting
- [ ] Setup Redis caching
- [ ] Migrate SQLite to PostgreSQL
- [ ] Add health check endpoints
- [ ] Implement API versioning
- [ ] Setup CORS policies

### Phase 3: Security (Week 2-3)
- [ ] Use secrets manager (AWS Secrets Manager, Azure Key Vault)
- [ ] Implement API key authentication
- [ ] Add input sanitization
- [ ] Setup HTTPS/TLS
- [ ] Implement rate limiting per user
- [ ] Add audit logging
- [ ] Setup security scanning (Snyk, Dependabot)

### Phase 4: Observability (Week 3)
- [ ] Add Prometheus metrics
- [ ] Setup Grafana dashboards
- [ ] Implement distributed tracing (Jaeger, OpenTelemetry)
- [ ] Add structured logging (JSON format)
- [ ] Setup log aggregation (ELK, CloudWatch)
- [ ] Configure alerting (PagerDuty, Slack)
- [ ] Add performance profiling

### Phase 5: Deployment (Week 4)
- [ ] Containerize with Docker
- [ ] Create Kubernetes manifests
- [ ] Setup CI/CD pipeline (GitHub Actions, Jenkins)
- [ ] Implement blue-green deployment
- [ ] Add smoke tests for deployment
- [ ] Setup rollback procedures
- [ ] Document deployment process

---

## Architecture Enhancements

### Current Tutorial Architecture
```
agent.py → OpenAI API → SQLite
```

### Production Architecture
```
┌──────────────────┐
│  Load Balancer   │ (AWS ALB, Nginx)
└────────┬─────────┘
         │
    ┌────┴────┐
    │  Nginx  │ (Reverse proxy, SSL termination)
    └────┬────┘
         │
┌────────┴─────────┐
│   FastAPI App    │ (API layer)
│   (Gunicorn +    │
│    Uvicorn)      │
└────────┬─────────┘
         │
    ┌────┴────────────────┐
    │                     │
┌───▼─────┐        ┌─────▼────┐
│ Redis   │        │ Agent    │
│ Cache   │        │ Service  │
└─────────┘        └─────┬────┘
                         │
                    ┌────┴────────────┐
                    │                 │
            ┌───────▼───────┐  ┌─────▼──────┐
            │ OpenAI API    │  │ PostgreSQL │
            │ (GPT-4/5)     │  │ Sessions   │
            └───────────────┘  └────────────┘
                    │
            ┌───────┴────────┐
            │                │
    ┌───────▼───────┐ ┌─────▼──────┐
    │ Prometheus    │ │ Jaeger     │
    │ Metrics       │ │ Tracing    │
    └───────────────┘ └────────────┘
```

---

## Code Refactoring

### Step 1: Modularize Codebase

#### Proposed Structure
```
production_agents/
├── src/
│   ├── __init__.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py               # Base configurations
│   │   ├── travel_orchestrator.py
│   │   ├── planner.py
│   │   ├── budget.py
│   │   └── guide.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── web_search.py
│   │   └── custom_tools.py
│   │
│   ├── guardrails/
│   │   ├── __init__.py
│   │   ├── budget_validator.py
│   │   └── content_safety.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py            # Pydantic models
│   │   └── enums.py              # Enumerations
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent_service.py      # Business logic
│   │   └── session_service.py    # Session management
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── agents.py         # Agent endpoints
│   │   │   └── health.py         # Health checks
│   │   ├── dependencies.py       # Dependency injection
│   │   └── middleware.py         # Custom middleware
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration management
│   │   ├── logging.py            # Logging setup
│   │   ├── exceptions.py         # Custom exceptions
│   │   └── security.py           # Security utilities
│   │
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py
│       └── validators.py
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── config/
│   ├── development.yaml
│   ├── staging.yaml
│   └── production.yaml
│
├── deployment/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── kubernetes/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   └── helm/
│       └── chart/
│
├── scripts/
│   ├── setup.sh
│   ├── migrate.py
│   └── seed_data.py
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── .env.example
├── pyproject.toml
├── setup.py
└── README.md
```

### Step 2: Extract Agent Configurations

**Before (Monolithic)**:
```python
# All in one file
agent = Agent(
    name="Travel Agent",
    model="gpt-5",
    instructions="Long string...",
    ...
)
```

**After (Modular)**:
```python
# src/agents/base.py
from agents import Agent, ModelSettings
from src.models.schemas import TravelOutput

class AgentFactory:
    @staticmethod
    def create_travel_agent() -> Agent:
        return Agent(
            name="Travel Agent",
            model="gpt-5",
            instructions=AgentFactory._get_travel_instructions(),
            output_type=TravelOutput,
            model_settings=ModelSettings(
                reasoning={"effort": "medium"},
                extra_body={"text": {"verbosity": "low"}}
            ),
            tools=AgentFactory._get_travel_tools(),
            input_guardrails=AgentFactory._get_guardrails()
        )
    
    @staticmethod
    def _get_travel_instructions() -> str:
        # Load from file or config
        return open("config/instructions/travel_agent.txt").read()
```

### Step 3: Implement Error Handling

```python
# src/core/exceptions.py
class AgentException(Exception):
    """Base exception for all agent errors"""
    pass

class GuardrailException(AgentException):
    """Raised when guardrail blocks request"""
    pass

class OutputValidationException(AgentException):
    """Raised when output doesn't match schema"""
    pass

class ExternalAPIException(AgentException):
    """Raised when external API fails"""
    pass

# src/services/agent_service.py
import logging
from typing import Optional
from src.core.exceptions import *

logger = logging.getLogger(__name__)

class AgentService:
    async def run_agent(
        self, 
        agent_type: str, 
        prompt: str, 
        session_id: Optional[str] = None
    ) -> dict:
        try:
            agent = self.agent_factory.create(agent_type)
            session = self._get_session(session_id) if session_id else None
            
            result = await Runner.run(agent, prompt, session=session)
            
            logger.info(
                "Agent execution successful",
                extra={
                    "agent_type": agent_type,
                    "session_id": session_id,
                    "prompt_length": len(prompt)
                }
            )
            
            return {"status": "success", "data": result.final_output}
            
        except InputGuardrailTripwireTriggered as e:
            logger.warning("Guardrail triggered", extra={"reason": str(e)})
            raise GuardrailException(f"Request blocked by guardrail: {e}")
            
        except ValidationError as e:
            logger.error("Output validation failed", extra={"error": str(e)})
            raise OutputValidationException(f"Invalid output structure: {e}")
            
        except Exception as e:
            logger.exception("Unexpected agent error")
            raise AgentException(f"Agent execution failed: {e}")
```

---

## API Layer Implementation

### FastAPI Wrapper

```python
# src/api/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from src.api.routes import agents, health
from src.core.logging import setup_logging
from src.core.config import settings

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Travel Agent API",
    version="1.0.0",
    description="Production AI Travel Planning System"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(health.router, prefix="/health", tags=["health"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Travel Agent API", extra={"version": "1.0.0"})

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Travel Agent API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Agent Endpoints

```python
# src/api/routes/agents.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import logging

from src.services.agent_service import AgentService
from src.core.exceptions import GuardrailException, OutputValidationException
from src.api.dependencies import get_agent_service, rate_limit

router = APIRouter()
logger = logging.getLogger(__name__)

# Request models
class AgentRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=2000)
    session_id: Optional[str] = None
    agent_type: str = Field(default="travel", pattern="^(travel|planner|budget|guide)$")

class AgentResponse(BaseModel):
    status: str
    data: dict
    session_id: Optional[str] = None

# Endpoints
@router.post("/run", response_model=AgentResponse, dependencies=[Depends(rate_limit)])
async def run_agent(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    service: AgentService = Depends(get_agent_service)
):
    """
    Execute an AI agent with given prompt.
    
    - **prompt**: User request (10-2000 characters)
    - **session_id**: Optional session ID for conversation context
    - **agent_type**: Type of agent (travel, planner, budget, guide)
    """
    try:
        result = await service.run_agent(
            agent_type=request.agent_type,
            prompt=request.prompt,
            session_id=request.session_id
        )
        
        # Log async (non-blocking)
        background_tasks.add_task(
            log_agent_execution,
            request.agent_type,
            request.session_id,
            "success"
        )
        
        return AgentResponse(
            status="success",
            data=result["data"],
            session_id=request.session_id
        )
        
    except GuardrailException as e:
        logger.warning("Guardrail triggered", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
        
    except OutputValidationException as e:
        logger.error("Output validation failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Agent output invalid")
        
    except Exception as e:
        logger.exception("Agent execution failed")
        raise HTTPException(status_code=500, detail="Internal server error")

async def log_agent_execution(agent_type: str, session_id: str, status: str):
    """Background task for logging"""
    logger.info(
        "Agent execution completed",
        extra={
            "agent_type": agent_type,
            "session_id": session_id,
            "status": status
        }
    )
```

### Health Check Endpoint

```python
# src/api/routes/health.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class HealthResponse(BaseModel):
    status: str
    version: str
    dependencies: dict

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    """
    # Check dependencies
    dependencies_status = {
        "openai_api": await check_openai_api(),
        "database": await check_database(),
        "redis": await check_redis()
    }
    
    overall_status = "healthy" if all(dependencies_status.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        dependencies=dependencies_status
    )

async def check_openai_api() -> bool:
    """Check OpenAI API connectivity"""
    try:
        # Lightweight API check
        return True
    except:
        return False

async def check_database() -> bool:
    """Check database connectivity"""
    try:
        # Query database
        return True
    except:
        return False

async def check_redis() -> bool:
    """Check Redis connectivity"""
    try:
        # Ping Redis
        return True
    except:
        return False
```

---

## Error Handling & Logging

### Structured Logging Setup

```python
# src/core/logging.py
import logging
import sys
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

def setup_logging(log_level: str = "INFO"):
    """
    Configure structured JSON logging.
    """
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Remove existing handlers
    logger.handlers = [handler]

# Usage in application
import logging
logger = logging.getLogger(__name__)

logger.info(
    "Agent executed successfully",
    extra={
        "agent_type": "travel",
        "session_id": "user_123",
        "execution_time_ms": 1234,
        "token_count": 567
    }
)
```

### Retry Logic with Exponential Backoff

```python
# src/utils/retry.py
import asyncio
import logging
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)

def async_retry(max_attempts: int = 3, backoff_factor: float = 2.0):
    """
    Decorator for async functions with exponential backoff retry.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts",
                            extra={"error": str(e)}
                        )
                        raise
                    
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        f"Function {func.__name__} failed, retrying in {wait_time}s",
                        extra={"attempt": attempt + 1, "error": str(e)}
                    )
                    await asyncio.sleep(wait_time)
        return wrapper
    return decorator

# Usage
@async_retry(max_attempts=3, backoff_factor=2.0)
async def call_openai_api(prompt: str):
    return await Runner.run(agent, prompt)
```

---

## Security & Secrets Management

### AWS Secrets Manager Integration

```python
# src/core/security.py
import boto3
import json
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class SecretsManager:
    """AWS Secrets Manager integration"""
    
    def __init__(self, region_name: str = "us-east-1"):
        self.client = boto3.client('secretsmanager', region_name=region_name)
    
    @lru_cache(maxsize=10)
    def get_secret(self, secret_name: str) -> dict:
        """
        Retrieve secret from AWS Secrets Manager.
        Cached to avoid repeated API calls.
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return json.loads(response['SecretString'])
        except Exception as e:
            logger.exception(f"Failed to retrieve secret: {secret_name}")
            raise

# src/core/config.py
from pydantic import BaseSettings
from src.core.security import SecretsManager

class Settings(BaseSettings):
    """Application settings with secrets from AWS"""
    
    ENVIRONMENT: str = "production"
    SECRET_NAME: str = "travel-agent-secrets"
    
    @property
    def openai_api_key(self) -> str:
        secrets = SecretsManager().get_secret(self.SECRET_NAME)
        return secrets['OPENAI_API_KEY']
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### API Key Authentication

```python
# src/api/dependencies.py
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from src.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verify API key from request header.
    """
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return api_key

# Usage in routes
@router.post("/run", dependencies=[Depends(verify_api_key)])
async def run_agent(...):
    ...
```

### Rate Limiting

```python
# src/api/middleware.py
from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# In main.py
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In routes
@router.post("/run")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def run_agent(request: Request, ...):
    ...
```

---

## Monitoring & Observability

### Prometheus Metrics

```python
# src/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
agent_requests_total = Counter(
    'agent_requests_total',
    'Total agent requests',
    ['agent_type', 'status']
)

agent_execution_duration = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration',
    ['agent_type']
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active sessions'
)

# Usage
async def run_agent_with_metrics(agent_type: str, prompt: str):
    start_time = time.time()
    
    try:
        result = await run_agent(agent_type, prompt)
        agent_requests_total.labels(agent_type=agent_type, status='success').inc()
        return result
    except Exception as e:
        agent_requests_total.labels(agent_type=agent_type, status='error').inc()
        raise
    finally:
        duration = time.time() - start_time
        agent_execution_duration.labels(agent_type=agent_type).observe(duration)
```

### OpenTelemetry Tracing

```python
# src/core/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_tracing():
    """Configure OpenTelemetry with Jaeger"""
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831
    )
    
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    trace.set_tracer_provider(provider)

# Usage
tracer = trace.get_tracer(__name__)

async def run_agent_with_tracing(prompt: str):
    with tracer.start_as_current_span("agent_execution") as span:
        span.set_attribute("prompt_length", len(prompt))
        result = await run_agent(prompt)
        span.set_attribute("tokens_used", result.token_count)
        return result
```

---

## Deployment Strategies

### Docker Containerization

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/production.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["gunicorn", "src.api.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### Kubernetes Deployment

```yaml
# deployment/kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: travel-agent-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: travel-agent-api
  template:
    metadata:
      labels:
        app: travel-agent-api
    spec:
      containers:
      - name: api
        image: travel-agent-api:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secrets
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/cd.yml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements/development.txt
          pytest tests/
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t travel-agent-api:${{ github.sha }} .
      - name: Push to registry
        run: docker push travel-agent-api:${{ github.sha }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/travel-agent-api \\
            api=travel-agent-api:${{ github.sha }}
```

---

## Cost Optimization

### Token Usage Tracking

```python
# src/services/cost_tracking.py
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class CostTracker:
    """Track OpenAI API costs"""
    
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
        "gpt-5": {"input": 0.05, "output": 0.10}
    }
    
    @staticmethod
    def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for API call"""
        pricing = CostTracker.PRICING.get(model, CostTracker.PRICING["gpt-4"])
        
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        logger.info(
            "API cost calculated",
            extra={
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": total_cost
            }
        )
        
        return total_cost
```

### Caching Strategy

```python
# src/services/cache_service.py
import redis
import json
import hashlib
from typing import Optional

class CacheService:
    """Redis caching for agent responses"""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.ttl = 3600  # 1 hour
    
    def get_cache_key(self, agent_type: str, prompt: str) -> str:
        """Generate cache key from agent type and prompt"""
        content = f"{agent_type}:{prompt}"
        return f"agent_cache:{hashlib.sha256(content.encode()).hexdigest()}"
    
    def get(self, agent_type: str, prompt: str) -> Optional[dict]:
        """Retrieve cached response"""
        key = self.get_cache_key(agent_type, prompt)
        cached = self.redis.get(key)
        
        if cached:
            return json.loads(cached)
        return None
    
    def set(self, agent_type: str, prompt: str, response: dict):
        """Cache response"""
        key = self.get_cache_key(agent_type, prompt)
        self.redis.setex(key, self.ttl, json.dumps(response))
```

---

## Production Checklist Summary

✅ **Code Quality**: Modular, tested, typed  
✅ **API Layer**: FastAPI with validation  
✅ **Security**: Secrets manager, auth, HTTPS  
✅ **Monitoring**: Metrics, logs, tracing  
✅ **Deployment**: Docker, K8s, CI/CD  
✅ **Scalability**: Load balancing, caching  
✅ **Cost**: Usage tracking, optimization  

---

## Next Steps

- **Testing**: [11_TESTING_STRATEGY.md](./11_TESTING_STRATEGY.md)
- **Troubleshooting**: [13_TROUBLESHOOTING.md](./13_TROUBLESHOOTING.md)
- **Extending**: [14_EXTENDING_THE_PROJECT.md](./14_EXTENDING_THE_PROJECT.md)

---

**Document Version**: 1.0.0  
**Last Updated**: December 29, 2025  
**Target Audience**: DevOps, Production Engineers, Team Leads
