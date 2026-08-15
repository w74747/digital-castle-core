# 📋 Task Backlog — Digital Castle S.P.C
# قائمة المهام المقسمة والمولودة

**تاريخ الإنشاء:** 2026-08-15  
**الحالة:** 🟢 Active  
**المسؤول:** Lead Architect + Development Team

---

## 📌 طريقة القراءة

```
[PHASE] [PRIORITY] TASK-###: Task Name
├─ Assigned to: [Model Name]
├─ Estimated Time: [X hours]
├─ Dependencies: [Task IDs]
├─ Spec File: [path]
└─ Acceptance Criteria: [✓ list]
```

---

# ⚙️ PHASE 1: Foundation (أيام 1-3)

## PRIORITY-1 (Critical Path)

### [P1] TASK-101: Database Schema + Models
**Assigned to:** DeepSeek  
**Time:** 2 hours  
**Dependencies:** None  
**Spec:** `.spec-kit/specs/task-101-database.md`

```python
# Deliverables:
✓ PostgreSQL connection pool
✓ SQLAlchemy ORM models
✓ Alembic migrations setup
✓ Models: User, Task, Invoice, Log, Session

Files to Create:
  - app/models/__init__.py
  - app/models/base.py (declarative base)
  - app/models/user.py
  - app/models/task.py
  - app/models/invoice.py
  - app/models/log.py
  - app/database.py (connection)
  - alembic/env.py
  - alembic/versions/001_initial.py

Acceptance:
  ✓ Migration runs without errors
  ✓ Tables created in PostgreSQL
  ✓ Relationships defined correctly
  ✓ Unit tests pass (migrations test)
```

---

### [P1] TASK-102: Enhanced Agent Router (Retry + Fallback)
**Assigned to:** DeepSeek  
**Time:** 3 hours  
**Dependencies:** None  
**Spec:** `.spec-kit/specs/task-102-agent-router.md`

```python
# Improvements:
✓ Retry logic with exponential backoff (3 attempts)
✓ Fallback strategy (Claude → DeepSeek → Together)
✓ Timeout handling (adaptive)
✓ Error logging with context
✓ Rate limiting per model
✓ Token counting and billing

Files to Modify:
  - agent_router.py (completely refactored)

New Functions:
  async def call_with_retry(
      model: str,
      prompt: str,
      system: str = "",
      max_retries: int = 3
  ) -> str

  async def call_with_fallback(
      prompt: str,
      system: str = "",
      primary: str = "claude",
      fallback: list = ["deepseek", "together"]
  ) -> str

Acceptance:
  ✓ Retry logic tested with mock failures
  ✓ Fallback switches models correctly
  ✓ Timeouts respected
  ✓ Errors logged with full context
  ✓ No hardcoded values
```

---

### [P1] TASK-103: Secure Bot Orchestrator (Validation + Auth)
**Assigned to:** DeepSeek  
**Time:** 2.5 hours  
**Dependencies:** TASK-102  
**Spec:** `.spec-kit/specs/task-103-bot-orchestrator.md`

```python
# Enhancements:
✓ Input validation (Pydantic models)
✓ Authentication middleware
✓ Rate limiting per user
✓ Command permissions
✓ Session management
✓ Audit logging

Files to Modify:
  - bot_orchestrator.py (completely refactored)

New Models:
  class UserCommand(BaseModel)
  class CommandResponse(BaseModel)
  class Session(BaseModel)

New Features:
  - @admin_only decorator
  - @rate_limit decorator
  - validate_telegram_update()
  - create_audit_log()

Acceptance:
  ✓ Only admin can execute commands
  ✓ Rate limit blocks 11th request
  ✓ Invalid input rejected with 400
  ✓ All commands logged
  ✓ Session token validated
```

---

### [P1] TASK-104: Error Handling Framework
**Assigned to:** DeepSeek  
**Time:** 2 hours  
**Dependencies:** TASK-102, TASK-103  
**Spec:** `.spec-kit/specs/task-104-error-handling.md`

```python
# Deliverables:
✓ Custom exception classes
✓ Global exception handler
✓ Error recovery strategies
✓ Structured error logging

Files to Create:
  - app/exceptions.py

Classes:
  class DigitalCastleException(Exception)
  class ConfigError(DigitalCastleException)
  class APIError(DigitalCastleException)
  class ValidationError(DigitalCastleException)
  class ResourceNotFound(DigitalCastleException)
  class RateLimitExceeded(DigitalCastleException)

Global Handler:
  async def global_exception_handler(exc, request)
    - Log with context
    - Return 500 with safe message
    - Avoid stack trace exposure

Acceptance:
  ✓ All exception types raised correctly
  ✓ No sensitive data in error messages
  ✓ 100% of exceptions logged
  ✓ Retry triggered for transient errors
```

---

### [P1] TASK-105: Centralized Logging System
**Assigned to:** DeepSeek  
**Time:** 1.5 hours  
**Dependencies:** TASK-104  
**Spec:** `.spec-kit/specs/task-105-logging.md`

```python
# Deliverables:
✓ Structured JSON logging
✓ Log rotation
✓ Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
✓ Request/response logging
✓ Performance metrics

Files to Create:
  - app/logging_config.py

Configuration:
  - Format: JSON (not plain text)
  - Output: /var/log/digital-castle/
  - Rotation: Daily + 30 days retention
  - Sensitive: Hide API keys, passwords

Usage:
  from app.logging_config import get_logger
  logger = get_logger(__name__)
  logger.info("Event", extra={"user_id": 123})

Acceptance:
  ✓ Logs rotate daily
  ✓ No API keys in logs
  ✓ JSON format valid
  ✓ Performance < 5ms per log call
```

---

## PRIORITY-2 (High Priority)

### [P2] TASK-106: Unit Tests Suite (Foundation)
**Assigned to:** DeepSeek  
**Time:** 3 hours  
**Dependencies:** TASK-101, TASK-102, TASK-103  
**Spec:** `.spec-kit/specs/task-106-unit-tests.md`

```python
# Test Coverage:
✓ agent_router.py: 100% coverage
✓ bot_orchestrator.py: 100% coverage
✓ document_engine.py: 95% coverage
✓ security.py: 100% coverage
✓ models.py: 95% coverage

Files to Create:
  - tests/__init__.py
  - tests/conftest.py (pytest fixtures)
  - tests/test_agent_router.py
  - tests/test_bot_orchestrator.py
  - tests/test_document_engine.py
  - tests/test_security.py
  - tests/test_models.py

Test Types:
  - Unit tests (functions in isolation)
  - Mock API calls
  - Test database transactions
  - Test error conditions

Acceptance:
  ✓ pytest runs: 100% pass
  ✓ Coverage > 90%
  ✓ All edge cases tested
  ✓ No external API calls in tests (mocked)
```

---

### [P2] TASK-107: GitHub Actions Workflows
**Assigned to:** Together  
**Time:** 1.5 hours  
**Dependencies:** TASK-106  
**Spec:** `.spec-kit/specs/task-107-github-actions.md`

```yaml
# Workflows to Create:

1. test-on-push.yml
   - Trigger: on every push
   - Steps:
     ✓ Set up Python 3.10
     ✓ Install dependencies
     ✓ Run pytest
     ✓ Calculate coverage
     ✓ Comment on PR

2. security-scan.yml
   - Trigger: on every push
   - Steps:
     ✓ bandit (code security)
     ✓ safety (dependencies)
     ✓ semgrep (patterns)
     ✓ Report findings

3. deploy-to-railway.yml
   - Trigger: on main branch push
   - Steps:
     ✓ Build Docker image
     ✓ Push to Railway
     ✓ Run migrations
     ✓ Health check
     ✓ Notify Admin

Files to Create:
  - .github/workflows/test-on-push.yml
  - .github/workflows/security-scan.yml
  - .github/workflows/deploy-to-railway.yml

Acceptance:
  ✓ All workflows run without errors
  ✓ Tests pass on every commit
  ✓ Security scan finds no critical issues
  ✓ Railway deployment successful
```

---

### [P2] TASK-108: Docker + Railway Configuration
**Assigned to:** Together  
**Time:** 1 hour  
**Dependencies:** None  
**Spec:** `.spec-kit/specs/task-108-docker-railway.md`

```dockerfile
# Dockerfile improvements:
✓ Multi-stage build
✓ Security best practices
✓ Health check
✓ Proper signal handling

railway.toml:
✓ Environment variables configured
✓ Volume mounts for logs
✓ Crash recovery settings
✓ Resource limits

Acceptance:
  ✓ Docker image builds
  ✓ Container runs without errors
  ✓ Health check passes
  ✓ Railway auto-redeploy works
```

---

### [P2] TASK-109: Brand Token Validation
**Assigned to:** Claude  
**Time:** 1 hour  
**Dependencies:** None  
**Spec:** `.spec-kit/specs/task-109-brand-validation.md`

```python
# Deliverables:
✓ Brand token validator
✓ CSS variable checker
✓ Color contrast validator
✓ Font availability checker

Files to Create:
  - app/brand_validator.py

Functions:
  def validate_all_tokens() -> ValidationReport
  def check_color_contrast(foreground, background) -> bool
  def validate_css_variables() -> list[str]  # warnings

Acceptance:
  ✓ All brand tokens present
  ✓ All colors meet WCAG AA
  ✓ All fonts available
  ✓ No unauthorized modifications
```

---

# 🔌 PHASE 2: Integration (أيام 4-6)

### [P1] TASK-201: GitHub Integration (Auto-commit + PR)
**Assigned to:** DeepSeek  
**Time:** 3 hours  
**Dependencies:** TASK-102, TASK-103  
**Spec:** `.spec-kit/specs/task-201-github-integration.md`

```python
# Features:
✓ Auto-create feature branches
✓ Auto-commit code changes
✓ Auto-create pull requests
✓ Auto-merge on success
✓ Auto-push to main
✓ Railway auto-deploy trigger

Files to Create:
  - app/github_manager.py

Classes:
  class GitHubManager:
    async def create_branch(feature_name: str)
    async def commit_changes(files: dict, message: str)
    async def create_pull_request(title: str, body: str)
    async def merge_pull_request(pr_number: int)
    async def push_to_main()

Acceptance:
  ✓ Branches created automatically
  ✓ Commits signed with GPG
  ✓ PRs have proper titles/descriptions
  ✓ Auto-merge only on test pass
```

---

### [P2] TASK-202: Railway Monitoring + Alerts
**Assigned to:** Together  
**Time:** 2 hours  
**Dependencies:** None  
**Spec:** `.spec-kit/specs/task-202-monitoring.md`

```python
# Monitoring:
✓ CPU/Memory usage
✓ API response times
✓ Error rate tracking
✓ Cost tracking
✓ Auto-alerts on thresholds

Files to Create:
  - app/monitoring.py

Alerts:
  - CPU > 80%
  - Memory > 85%
  - Error rate > 5%
  - Response time > 5s
  - Cost > daily budget

Acceptance:
  ✓ Metrics collected
  ✓ Alerts sent to Admin Telegram
  ✓ Dashboard accessible
  ✓ Historical data stored
```

---

# 📚 PHASE 3: Advanced (أيام 7-10)

### [P1] TASK-301: Web Dashboard
**Assigned to:** Claude + DeepSeek  
**Time:** 4 hours  
**Dependencies:** TASK-201, TASK-202  
**Spec:** `.spec-kit/specs/task-301-dashboard.md`

```
Dashboard Features:
  ✓ System status (real-time)
  ✓ Recent invoices list
  ✓ Cost breakdown by model
  ✓ Tasks in progress
  ✓ Error logs
  ✓ Performance metrics
  ✓ Team activity feed

Tech: React + TypeScript + TailwindCSS
Auth: JWT tokens
Hosting: Railway or Vercel

Acceptance:
  ✓ Page loads < 2 seconds
  ✓ Real-time updates via WebSocket
  ✓ Mobile responsive
  ✓ Dark mode support
```

---

### [P1] TASK-302: API Gateway
**Assigned to:** DeepSeek  
**Time:** 3 hours  
**Dependencies:** TASK-103  
**Spec:** `.spec-kit/specs/task-302-api-gateway.md`

```
Endpoints:
  POST   /api/v1/invoices
  GET    /api/v1/invoices/{id}
  POST   /api/v1/tasks
  GET    /api/v1/tasks/{id}
  GET    /api/v1/status
  POST   /api/v1/agents/execute

Security:
  ✓ API key validation
  ✓ Rate limiting per key
  ✓ Request signing
  ✓ Response encryption (optional)

Tech: FastAPI + Uvicorn

Acceptance:
  ✓ All endpoints documented
  ✓ OpenAPI spec generated
  ✓ Rate limiting works
  ✓ Load test: 100 req/s
```

---

### [P2] TASK-303: 22-Agent System Architecture
**Assigned to:** Claude  
**Time:** 4 hours  
**Dependencies:** TASK-102  
**Spec:** `.spec-kit/specs/task-303-22-agents.md`

```
Agents:
1. Market Scout
2. Business Consultant
3. Project Manager
4. Architect
5. UI/UX Designer
6. Developer
7. Tech Writer
8. Database Admin
9. DevSecOps
10. QA Engineer
... (22 total)

Each Agent:
  ✓ Specialized system prompt
  ✓ Dedicated context
  ✓ Performance metrics
  ✓ Audit trail

Orchestration:
  ✓ Task routing
  ✓ Dependency management
  ✓ Parallel execution where possible
  ✓ Failure recovery

Acceptance:
  ✓ All 22 agents defined
  ✓ Each has tests
  ✓ Orchestration tested
```

---

# 🎯 Priority Matrix

```
Critical Path (Must do first):
  TASK-101 → TASK-102 → TASK-103 → TASK-104 → TASK-105 → TASK-106

Can Run in Parallel:
  TASK-107 ╱╲
  TASK-108  ╲╱ (after TASK-106)
  TASK-109

PHASE 2 Starts when PHASE 1 is 80% complete
PHASE 3 Starts when PHASE 2 is 80% complete
```

---

# 📊 Progress Tracking

| Task | Status | Owner | ETA | Notes |
|------|--------|-------|-----|-------|
| TASK-101 | ⏳ | DeepSeek | +2h | In Progress |
| TASK-102 | ⏳ | DeepSeek | +3h | Waiting |
| TASK-103 | ⏳ | DeepSeek | +2.5h | Waiting |
| TASK-104 | ⏳ | DeepSeek | +2h | Waiting |
| TASK-105 | ⏳ | DeepSeek | +1.5h | Waiting |
| TASK-106 | ⏳ | DeepSeek | +3h | Waiting |
| TASK-107 | ⏳ | Together | +1.5h | Waiting |
| TASK-108 | ⏳ | Together | +1h | Waiting |
| TASK-109 | ⏳ | Claude | +1h | Waiting |

**Total Phase 1 Time:** ~20 hours (split across 3 days with parallelization)

---

**Last Updated:** 2026-08-15 15:30 UTC  
**Next Review:** After TASK-106 completion
