# 📋 Current System Specification
# المواصفات الحالية لنظام Digital Castle S.P.C

**Version:** 1.0.0  
**Last Updated:** 2026-08-15  
**Status:** 🟢 Production Ready (In Progress)

---

## 1. نظرة عامة على النظام

### الغرض
نظام تشغيلي ذاتي الحكم (Autonomous Operating System) لشركة Digital Castle S.P.C يدير:
- 📝 توليد الوثائق والفواتير
- 🤖 تنسيق الوكلاء الذكيين (22 agent)
- 💬 واجهة Telegram للتحكم التنفيذي
- 📊 مراقبة الأداء والتكاليف
- 🔒 الأمان والمراجعة

### البيئة التشغيلية
```
Platform:    Railway (Python 3.10+)
Container:   Docker (python:3.10-slim)
API Keys:    3 نماذج (Claude + DeepSeek + Together)
Database:   PostgreSQL (تحت الإعداد)
VCS:        GitHub
Interface:  Telegram Bot
```

---

## 2. المعمارية الشاملة

```
┌─────────────────────────────────────────────────────────────┐
│                      TELEGRAM INTERFACE                      │
│           (User → Commands → bot_orchestrator.py)           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   AGENT ROUTER LAYER                        │
│  (agent_router.py - Route tasks to 3 LLM providers)        │
│                                                             │
│  ├─ PLANNER (Claude 3.5 Sonnet)                           │
│  ├─ DEVELOPER (DeepSeek)                                  │
│  └─ OPERATIONS (Together AI Llama 3.1)                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
    ┌──────┐ ┌──────┐ ┌──────────┐
    │ Spec │ │ Code │ │ Document │
    │ Kit  │ │ Gen  │ │ Engine   │
    └──────┘ └──────┘ └──────────┘
        │         │         │
        ▼         ▼         ▼
    ┌───────────────────────────────┐
    │    DATABASE LAYER             │
    │  (Models + Transactions)      │
    └───────────────────────────────┘
        │
        ▼
    ┌───────────────────────────────┐
    │    GITHUB INTEGRATION         │
    │  (Auto-commit + PR Preview)   │
    └───────────────────────────────┘
```

---

## 3. مكونات النظام الرئيسية

### 3.1 Telegram Bot (bot_orchestrator.py)
**المسؤوليات:**
- استقبال الأوامر من Admin
- توجيه الطلبات للـ agents المناسبة
- إرسال التقارير والنتائج مرة أخرى

**الأوامر المدعومة:**
```
/start                    → تحية الترحيب
/invoice [details]        → إنشاء فاتورة PDF
/ask [prompt]             → استشارة وكيل ذكي
/status                   → حالة النظام الحالية
/scan_security            → فحص أمان شامل
/finops_report            → تقرير التكاليف
```

**الأمان:**
- التحقق من Admin ID فقط
- لا طباعة مفاتيح في السجلات
- Timeout على كل طلب

---

### 3.2 Agent Router (agent_router.py)
**المسؤوليات:**
- إرسال الطلبات للنماذج المناسبة
- معالجة الأخطاء والـ retries
- إدارة التوقيت والموارد

**التوجيه الذكي:**
```
تحليل المتطلبات (Spec)     → Claude 3.5 Sonnet
كتابة الكود (Implementation) → DeepSeek
عمليات سريعة (Operations)   → Together AI
```

---

### 3.3 Document Engine (document_engine.py)
**المسؤوليات:**
- توليد HTML من Jinja2 templates
- تحويل HTML → PDF عبر Playwright
- دمج الأختام والتوقيعات المشفرة

**المستندات المدعومة:**
- 📄 Invoices (DC-INV-YYYY-####)
- 📋 Proposals (DC-PRO-YYYY-####)
- 📊 Reports (DC-REP-YYYY-####)

---

### 3.4 Security Layer (security.py)
**المسؤوليات:**
- توليد أكواد أمان مشفرة (SHA-256)
- توليد QR codes للتحقق
- دمج الختم والتوقيع في الصور

**التقنيات:**
```
Encryption:   SHA-256 (document_number + amount + date + SECRET_KEY)
QR:          qrcode library (version auto, error correction M)
Watermark:   PIL (rotation + transparency + center alignment)
```

---

### 3.5 Sequence Manager (sequence_manager.py)
**المسؤوليات:**
- توليد أرقام فريدة تسلسلية
- حفظ الحالة في JSON

**الصيغة:**
```
INV-2026-0001  (Invoice)
PRO-2026-0001  (Proposal)
REP-2026-0001  (Report)
```

---

## 4. معايير الجودة (Quality Standards)

### 4.1 الموثوقية
- ✅ Retry logic مع exponential backoff (3 محاولات)
- ✅ Timeout adaptive (60-120 ثانية)
- ✅ Fallback إلى نموذج بديل عند الفشل
- ✅ Error logging مع stack traces

### 4.2 الأمان
- ✅ Input validation على كل endpoint
- ✅ Rate limiting (10 requests/minute per user)
- ✅ Session encryption
- ✅ مفاتيح من متغيرات البيئة فقط
- ✅ No credentials في Git

### 4.3 الأداء
- ✅ Async/await على كل I/O
- ✅ Connection pooling للـ database
- ✅ Caching للـ specs والـ tokens
- ✅ Response time < 5 seconds للـ 80% من الطلبات

### 4.4 الاختبارات
- ✅ Unit tests (90% code coverage)
- ✅ Integration tests
- ✅ Load testing (100 concurrent users)
- ✅ Security testing (OWASP Top 10)

---

## 5. النماذج الثلاثة (Hybrid LLM Strategy)

| النموذج | المهام | التكلفة | الحد الأقصى للـ Tokens |
|---------|--------|---------|----------------------|
| Claude 3.5 Sonnet | Specs + Architecture | $3/MTok | 4,096 out |
| DeepSeek V3 | Code Generation | $0.14/MTok | 4,096 out |
| Together Llama 3.1 | Operations + Reports | $0.90/MTok | 4,096 out |

**استراتيجية التوفير:**
```
- استخدم Together لـ 60% من المهام (الأسرع والأرخص)
- استخدم DeepSeek لـ 30% من المهام (البرمجة المعقدة)
- احفظ Claude لـ 10% فقط (القرارات المعمارية)

Expected Cost Reduction: 75-80%
```

---

## 6. نقاط التكامل (Integration Points)

### GitHub Integration
```
Workflow:
  1. Admin يرسل أمر عبر Telegram
  2. Bot يُنشئ فرع جديد (feat/feature-name)
  3. DeepSeek يكتب الكود
  4. Unit tests تُشغّل تلقائياً
  5. إذا passed: PR ينشأ تلقائياً
  6. إذا approved: merge إلى main
  7. Railway يُعيد بناء تلقائياً
```

### Railway Deployment
```
Environment Variables:
  ✅ TELEGRAM_BOT_TOKEN
  ✅ TELEGRAM_ADMIN_ID
  ✅ ANTHROPIC_API_KEY
  ✅ DEEPSEEK_API_KEY
  ✅ TOGETHER_API_KEY
  ✅ GITHUB_TOKEN
  ✅ DATABASE_URL
  ✅ APP_ENV=production
  ✅ DEBUG=False
  ✅ PORT=8000
```

---

## 7. حالة التطوير الراهنة

### ✅ مكتملة
- [x] Telegram Bot أساسي
- [x] Agent Router (3 نماذج)
- [x] Document Engine
- [x] Brand Identity
- [x] Security Layer

### 🟡 قيد العمل
- [ ] Database Layer (PostgreSQL)
- [ ] GitHub Actions Workflows
- [ ] Comprehensive Tests
- [ ] Logging Centralized
- [ ] Monitoring + Alerts

### ⏳ مخطط لاحقاً
- [ ] Web Dashboard
- [ ] API Gateway
- [ ] 22-Agent System
- [ ] Analytics Engine
- [ ] Cost Optimization

---

## 8. متطلبات الإطلاق (Launch Checklist)

قبل الإطلاق للـ Production:

```
Infrastructure:
  [ ] Database مهيأة وآمنة
  [ ] GitHub Actions workflows تعمل
  [ ] Railway monitoring فعّال
  [ ] Backup automation شغّال
  
Code Quality:
  [ ] 90%+ unit test coverage
  [ ] Security scan نجح
  [ ] Load test passed (100 users)
  [ ] Documentation شاملة
  
Operations:
  [ ] Alert system موصول
  [ ] Logging centralized
  [ ] Cost tracking نشط
  [ ] Incident response plan جاهز
```

---

**Next Step:** انظر `task_backlog.md` للمهام المقسمة والمولودة.
