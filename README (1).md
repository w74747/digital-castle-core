# 🏰 Digital Castle S.P.C

**شركة القلعة الرقمية ش.ش.و** - منظومة برمجية وحاضنة مشاريع رقمية ذاتية التشغيل بالكامل

## 📋 نظرة عامة

منظومة مؤتمتة بالكامل تجمع بين:
- **22 وكيل ذكاء اصطناعي متخصص** موزعة على 4 قطاعات تشغيلية
- **نماذج هجينة** (Claude, DeepSeek, Together AI) لتحسين الكفاءة والتكاليف
- **واجهة Telegram** للتحكم الفوري
- **GitHub** كمستودع موحد
- **Railway** كبيئة سحابية موثوقة

## 🛠️ البنية التقنية

### المكونات الرئيسية

```
holding-company-engine/
├── app.py                  # التطبيق الرئيسي (FastAPI)
├── agent_router.py         # موزع المهام الذكي
├── document_engine.py      # محرك المستندات الرسمية
├── config.py               # الإعدادات والمتغيرات
├── requirements.txt        # المكتبات
├── Dockerfile              # للاستضافة على Railway
└── assets/                 # الشعار والتوقيع والختم
```

### النماذج المستخدمة

| النموذج | الدور | المهام |
|---------|------|--------|
| **Claude 3.5 Sonnet** | التخطيط المعماري | دراسات الجدوى، المواصفات، التحليل الاستراتيجي |
| **DeepSeek V3** | المبرمج الرئيسي | كتابة الكود، الأمان، Migrations |
| **Together AI (Llama 3)** | المهام السريعة | QA، المحتوى، المراقبة، التقارير |

## 🚀 البدء السريع

### 1. الإعداد المحلي (للاختبار)

```bash
# استنساخ المستودع
git clone https://github.com/yourusername/digital-castle.git
cd digital-castle

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# تثبيت المكتبات
pip install -r requirements.txt

# إنشاء ملف .env
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_ADMIN_ID=your_id_here
ANTHROPIC_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
TOGETHER_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
DATABASE_URL=sqlite:///digital_castle.db
PORT=8000
EOF

# تشغيل التطبيق
python app.py
```

### 2. النشر على Railway

```bash
# تسجيل الدخول إلى Railway
railway login

# إنشاء مشروع جديد
railway init

# تعيين المتغيرات على Railway
railway variables set TELEGRAM_BOT_TOKEN=...
railway variables set TELEGRAM_ADMIN_ID=...
railway variables set ANTHROPIC_API_KEY=...
railway variables set DEEPSEEK_API_KEY=...
railway variables set TOGETHER_API_KEY=...
railway variables set GITHUB_TOKEN=...

# نشر التطبيق
railway up
```

## 📊 الوكلاء المتخصصين

### 1. قطاع الجدوى والمشاريع (3 وكلاء)
- **صائد الفرص** - اكتشاف المشاكل والترندات
- **مستشار الجدوى** - تحليل اقتصادي وحساب الأرباح
- **مدير المشروع** - تخطيط التنفيذ

### 2. قطاع الهندسة والتطوير (10 وكلاء)
- **مهندس معماري** - صياغة المواصفات
- **مصمم واجهات** - تصميم UX/UI
- **مبرمج رئيسي** - كتابة الكود
- **خبير التوثيق** - توثيق المشاريع
- **مهندس قواعد البيانات** - إدارة البيانات
- **خبير الأمان** - فحص الثغرات
- **فريق الجودة** - الاختبارات والتقييم
- **متخصص النسخ الاحتياطي** - حماية البيانات
- **خبير SEO** - تحسين محركات البحث
- **مستشار المصادر المفتوحة** - استكشاف الأدوات

### 3. قطاع التسويق والإنتاج (5 وكلاء)
- **مدير التسويق الاستراتيجي** - خطط الإطلاق
- **كاتب المحتوى** - نصوص وإعلانات
- **مصمم موشن** - بنرات وفيديوهات
- **مدير الحملات** - جدولة النشر
- **حارس الهوية** - التحقق من المعايير

### 4. قطاع الإدارة والمالية (4 وكلاء)
- **مدير مالي** - التقارير المالية
- **مراقب الأرصدة** - استهلاك التوكنز
- **محاسب التكاليف** - حسابات الربح
- **مستشار الاستثمار** - توصيات التوسع

### 5. قطاع الحوكمة (1 وكيل)
- **المدرب التنفيذي** - مراقبة الأداء وتحسين الكفاءة

## 💬 الأوامر المتاحة في Telegram

```
/start              - البدء والمساعدة
/status             - حالة النظام والموارد
/tokens             - ملخص استهلاك التوكنز
/feasibility        - طلب دراسة جدوى
/spec               - صياغة مواصفات
/code               - كتابة كود
/qa                 - فحص جودة
/help               - المساعدة الكاملة
```

## 📈 مؤشرات الأداء

```json
{
  "anthropic": {
    "used": 12500,
    "limit": 500000,
    "remaining": 487500,
    "percentage": 2.5
  },
  "deepseek": {
    "used": 8300,
    "limit": 300000,
    "remaining": 291700,
    "percentage": 2.8
  },
  "together": {
    "used": 5600,
    "limit": 200000,
    "remaining": 194400,
    "percentage": 2.8
  }
}
```

## 🔐 متغيرات البيئة المطلوبة

```env
# Telegram
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_ADMIN_ID=xxx

# APIs
ANTHROPIC_API_KEY=xxx
DEEPSEEK_API_KEY=xxx
TOGETHER_API_KEY=xxx

# GitHub
GITHUB_TOKEN=xxx

# Database
DATABASE_URL=postgresql://...

# Server
PORT=8000
WEBHOOK_URL=https://your-domain.com
```

## 🏗️ هيكل المشروع

- **spec-kit/**: المواصفات والمتطلبات
- **docs/**: التوثيق والأدلة
- **agents/**: ملفات الوكلاء المتخصصين
- **assets/**: الشعار والعلامات التجارية
- **brand-kit/**: معايير الهوية البصرية
- **templates/**: قوالب المستندات

## 📝 المستندات المولدة

النظام يقوم بتوليد تلقائياً:
- ✅ الفواتير الرسمية
- ✅ العروض التقنية والمالية
- ✅ دراسات الجدوى الاقتصادية
- ✅ المواصفات الفنية
- ✅ جداول المهام

جميع المستندات تحمل هوية وختم شركة Digital Castle S.P.C

## 🔄 دورة العمل (Workflow)

```
1. تحديد الفرصة → Market Scout
2. دراسة الجدوى → Feasibility Consultant  
3. صياغة المواصفات → System Architect
4. كتابة الكود → Core Developer
5. فحص الجودة → QA Agent
6. توليد المستندات → Document Engine
7. الإطلاق → Deployment
8. المراقبة → Monitoring Agents
```

## 🎯 الأهداف الرئيسية

- ✅ بناء وإطلاق مشاريع بسرعة واحترافية
- ✅ تحسين جودة المنتجات عبر Spec-Driven Development
- ✅ تقليل التكاليف عبر النماذج الهجينة
- ✅ الالتزام الكامل بهوية الشركة
- ✅ أتمتة جميع العمليات الممكنة

## 📞 الدعم والمساعدة

للحصول على الدعم:
1. تحقق من السجلات: `logs/digital_castle.log`
2. استخدم `/help` في Telegram
3. راجع التوثيق الكاملة
4. تواصل مع فريق الدعم

## 📄 الترخيص

جميع الحقوق محفوظة لشركة Digital Castle S.P.C © 2024

---

**آخر تحديث:** 2024-01-15  
**الإصدار:** 1.0.0  
**الحالة:** 🟢 إنتاجي
