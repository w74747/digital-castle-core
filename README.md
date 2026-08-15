# 🏰 Digital Castle S.P.C
# القلعة الرقمية ش.ش.و

**Autonomous AI-Powered Business Operating System**  
**نظام التشغيل الذاتي المدار بالذكاء الاصطناعي**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-green.svg)]()

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Development](#development)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

Digital Castle S.P.C is an **autonomous software engineering and business management system** that:

1. **Manages AI Agents** — 22 specialized agents for different business functions
2. **Generates Documents** — Invoices, proposals, reports with cryptographic seals
3. **Integrates with GitHub** — Auto-creates branches, commits, and deploys
4. **Deploys to Railway** — Containerized, production-ready infrastructure
5. **Controls via Telegram** — Real-time admin commands and reporting
6. **Hybrid LLM Strategy** — 3 AI models (Claude, DeepSeek, Together) optimized for cost and speed

### Key Numbers:
- **3 AI Models** — Claude, DeepSeek, Together
- **22 Agents** — Market Scout, Developer, QA Engineer, CFO, etc.
- **75-80% Cost Reduction** — vs. single-model approach
- **Production Ready** — Deployed on Railway with auto-scaling

---

## ✨ Features

### 🤖 AI Agent Orchestration
- Multi-agent system with specialized roles
- Automatic task routing and dependency management
- Fallback strategies and retry logic (3 attempts with exponential backoff)
- Token-efficient context isolation

### 📄 Document Generation
- Invoice generation with QR codes and security seals
- Custom PDF templates with Jinja2
- Cryptographic watermarking (SHA-256)
- Sequence number management (INV-2026-0001 format)

### 🔐 Security & Compliance
- Sensitive data filtering in logs
- Input validation with Pydantic
- Rate limiting per user
- Session encryption
- Audit logging for all operations

### 📊 Monitoring & Alerts
- Structured JSON logging
- Performance metrics tracking
- Cost tracking per AI model
- Real-time alerts via Telegram
- Health checks and auto-recovery

### 🔗 GitHub Integration
- Automatic branch creation
- Auto-commit with GPG signing
- Pull request automation
- Pre-merge testing
- Auto-deploy to Railway

### 💬 Telegram Interface
- Real-time command execution
- Admin-only operations
- Progress tracking
- Error notifications
- Cost reports

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           TELEGRAM INTERFACE                    │
│     (Admin Commands → Orchestrator)             │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         AGENT ROUTER LAYER                      │
│  (Route to Claude, DeepSeek, or Together)      │
└────────────────┬────────────────────────────────┘
                 │
         ┌───────┼───────┐
         ▼       ▼       ▼
    ┌────────┐┌────────┐┌──────────┐
    │ CLAUDE ││DEEPSEEK││ TOGETHER │
    └────────┘└────────┘└──────────┘
         │       │       │
         └───────┼───────┘
                 ▼
    ┌─────────────────────────────┐
    │  BUSINESS LOGIC LAYER       │
    │  (Specs, Tasks, Documents)  │
    └────────────┬────────────────┘
                 │
         ┌───────┼───────┐
         ▼       ▼       ▼
    ┌────────┐┌────────┐┌──────────┐
    │Database││GitHub  ││ Railway  │
    └────────┘└────────┘└──────────┘
```

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Runtime** | Python | 3.10+ |
| **Bot Framework** | python-telegram-bot | 21.10 |
| **HTTP Client** | httpx | 0.28.1 |
| **Database** | PostgreSQL + SQLAlchemy | 2.0+ |
| **PDF Generation** | Playwright | 1.49.1 |
| **Templating** | Jinja2 | 3.1.4 |
| **Container** | Docker | Latest |
| **Deployment** | Railway | Latest |
| **Testing** | pytest | 8.2.2 |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- PostgreSQL 12+
- Docker & Docker Compose (optional)
- Git
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### 1. Clone Repository
```bash
git clone https://github.com/your-org/digital-castle-core.git
cd digital-castle-core
```

### 2. Set Up Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
nano .env

# Required values:
# - TELEGRAM_BOT_TOKEN
# - ANTHROPIC_API_KEY
# - DEEPSEEK_API_KEY
# - TOGETHER_API_KEY
# - DATABASE_URL
```

### 3. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download Playwright browsers (for PDF generation)
playwright install chromium
```

### 4. Set Up Database
```bash
# Create database (if not exists)
createdb digital_castle

# Run migrations
alembic upgrade head
```

### 5. Run Application
```bash
# Development
python bot_orchestrator.py

# Production (with gunicorn)
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### 6. Test
```bash
# Run tests
pytest tests/ -v --cov=app

# Run specific test
pytest tests/test_agent_router.py -v
```

---

## ⚙️ Configuration

### Environment Variables

**Essential:**
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_ADMIN_ID=123456789
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
TOGETHER_API_KEY=...
```

**Database:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/digital_castle
```

**Application:**
```env
APP_ENV=production
DEBUG=False
PORT=8000
LOG_LEVEL=INFO
```

See `.env.example` for all available options.

### Brand Configuration

Edit `brand_settings.py` to customize:
- Company name (English & Arabic)
- Colors and typography
- Tax rates
- Contact information

---

## 📦 Deployment

### Docker (Local)
```bash
# Build image
docker build -t digital-castle:latest .

# Run container
docker run -p 8000:8000 \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e DATABASE_URL=postgresql://... \
  digital-castle:latest
```

### Railway

1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Railway automatically deploys on push to `main`
4. Check logs: `railway logs`

### Docker Compose
```bash
docker-compose up -d
```

---

## 🧪 Development

### Project Structure
```
digital-castle-core/
├── .spec-kit/                 # Specifications and task backlog
│   ├── system_prompt.md
│   ├── current_spec.md
│   └── task_backlog.md
├── app/
│   ├── __init__.py
│   ├── agent_router.py       # LLM routing logic
│   ├── bot_orchestrator.py   # Telegram bot
│   ├── document_engine.py    # PDF generation
│   ├── security.py           # Encryption & watermarking
│   ├── exceptions.py         # Custom exceptions
│   ├── logging_config.py     # Logging setup
│   ├── models/               # Database models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── invoice.py
│   │   └── log.py
│   └── github_manager.py     # GitHub integration
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agent_router.py
│   ├── test_bot_orchestrator.py
│   └── test_document_engine.py
├── config/
│   ├── brand_settings.py
│   └── invoice_template.html
├── .github/workflows/        # GitHub Actions
│   ├── test-on-push.yml
│   ├── security-scan.yml
│   └── deploy-to-railway.yml
├── requirements.txt
├── Dockerfile
├── Procfile
├── .gitignore
├── .env.example
└── README.md
```

### Running Tests
```bash
# All tests
pytest -v

# With coverage
pytest --cov=app tests/

# Specific test file
pytest tests/test_agent_router.py -v

# Watch mode (requires pytest-watch)
ptw
```

### Code Quality
```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint
flake8 app/ tests/
pylint app/

# Type checking
mypy app/

# Security check
bandit -r app/
```

### Logging
Structured JSON logs are stored in `logs/` directory:
- `digital-castle.log` — All logs
- `errors.log` — Errors only
- `agents.log` — Agent-specific logs
- `performance.log` — Performance metrics

---

## 📚 API Documentation

### Telegram Commands

| Command | Description | Permissions |
|---------|-------------|------------|
| `/start` | Initialize bot | Admin |
| `/invoice` | Create invoice | Admin |
| `/ask [prompt]` | Query AI agents | Admin |
| `/status` | System status | Admin |
| `/scan_security` | Security audit | Admin |
| `/finops_report` | Cost breakdown | Admin |
| `/help` | Show help | All |

### Example: Create Invoice via Telegram
```
/invoice client:"Acme Corp" total:"1000 OMR" items:"Consulting, Development"
```

### REST API (via FastAPI)

**Base URL:** `https://your-domain.railway.app/api/v1`

#### Create Invoice
```bash
POST /api/v1/invoices
Content-Type: application/json

{
  "client_name": "Acme Corp",
  "client_contact": "info@acme.com",
  "items": [
    {
      "description": "Software Development",
      "quantity": 1,
      "unit_price": 1000
    }
  ]
}

Response:
{
  "invoice_number": "DC-INV-2026-0001",
  "pdf_url": "...",
  "created_at": "2026-08-15T10:30:00Z"
}
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**Code Style:**
- Follow [PEP 8](https://pep8.org/)
- Use type hints for all functions
- Write docstrings for all classes and functions
- Keep functions under 50 lines when possible

**Testing:**
- Aim for 90%+ code coverage
- Write tests before implementing features
- Mock external API calls

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/your-org/digital-castle-core/issues)
- **Documentation:** [Wiki](https://github.com/your-org/digital-castle-core/wiki)
- **Email:** info@DigitalCastle.io

---

## 🏆 Acknowledgments

Built with ❤️ by the Digital Castle team.

- **Claude 3.5 Sonnet** — Architecture & Planning
- **DeepSeek** — Code Generation & Implementation
- **Together AI** — Fast Operations & Reporting

---

**Version:** 1.0.0  
**Last Updated:** 2026-08-15  
**Status:** 🟢 Production Ready
