# ⚡ البدء السريع - 5 دقائق فقط

## الخطوة 1️⃣: تجهيز المفاتيح (2 دقيقة)

احصل على هذه المفاتيح الآن:

```
1. TELEGRAM_BOT_TOKEN
   → أرسل رسالة لـ @BotFather في Telegram
   → اكتب: /newbot
   → اتبع الخطوات
   → ستحصل على الرمز

2. TELEGRAM_ADMIN_ID (معرفك في Telegram)
   → أرسل رسالة لـ @userinfobot
   → سيعطيك رقم معرفك

3. ANTHROPIC_API_KEY
   → اذهب إلى https://console.anthropic.com
   → قم بالتسجيل/تسجيل الدخول
   → اختر API Keys
   → انسخ المفتاح

4. DEEPSEEK_API_KEY
   → اذهب إلى https://platform.deepseek.com
   → انشئ حساب
   → اختر API
   → انسخ المفتاح

5. TOGETHER_API_KEY
   → اذهب إلى https://www.together.ai
   → انشئ حساب
   → اختر API
   → انسخ المفتاح

6. GITHUB_TOKEN
   → اذهب إلى https://github.com/settings/tokens
   → انقر "Generate new token"
   → حدد الصلاحيات
   → انسخ الرمز
```

## الخطوة 2️⃣: الإعداد المحلي (2 دقيقة)

```bash
# انسخ المشروع (أو انزل الملفات)
git clone https://github.com/your/digital-castle.git
cd digital-castle

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# تثبيت المكتبات
pip install -r requirements.txt

# إنشاء ملف الإعدادات
cp .env.example .env

# فتح .env وأضف المفاتيح
# استخدم محرر نص: VS Code, Sublime, Notepad++
# أضف القيم الستة أعلاه
```

## الخطوة 3️⃣: الاختبار المحلي (1 دقيقة)

```bash
# تشغيل التطبيق
python app.py

# ستظهر رسالة:
# ✅ All Systems Ready
# 🚀 Digital Castle S.P.C - Starting Up
```

**الآن اختبر البوت:**
```
افتح Telegram → ابحث عن البوت الذي أنشأته
أرسل: /start
يجب أن ترى ردود الآن ✅
```

## الخطوة 4️⃣: النشر على Railway (نقرة واحدة تقريباً!)

### الخيار A: عبر موقع Railway (الأسهل)

```
1. اذهب إلى https://railway.app
2. سجل الدخول بحساب GitHub
3. انقر "New Project"
4. اختر "Deploy from GitHub repo"
5. اختر مستودع digital-castle
6. اتبع الخطوات
7. أضف المتغيرات الستة من الخطوة 1️⃣
8. انقر Deploy
```

### الخيار B: عبر Terminal (5 دقائق)

```bash
# تثبيت Railway CLI
npm install -g @railway/cli

# تسجيل الدخول
railway login

# إنشاء مشروع
railway init

# إضافة المتغيرات
railway variables set TELEGRAM_BOT_TOKEN=...
railway variables set TELEGRAM_ADMIN_ID=...
railway variables set ANTHROPIC_API_KEY=...
railway variables set DEEPSEEK_API_KEY=...
railway variables set TOGETHER_API_KEY=...
railway variables set GITHUB_TOKEN=...

# النشر
railway up

# انسخ URL التطبيق الذي سيظهر
```

## الخطوة 5️⃣: تفعيل Telegram Webhook (30 ثانية)

```bash
# استبدل:
# - TOKEN: بـ TELEGRAM_BOT_TOKEN
# - https://your-app.railway.app: بـ URL التطبيق من الخطوة 4️⃣

curl -X POST https://api.telegram.org/botTOKEN/setWebhook \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.railway.app/webhook/telegram"
  }'

# ستحصل على رد:
# {"ok":true,"result":true}
```

## ✅ نهاية التشغيل!

الآن البوت يعمل على السحابة! 🚀

```
اختبر الأوامر:
/start      → عرض المرحبة
/status     → حالة النظام
/tokens     → استهلاك التوكنز
/help       → المساعدة الكاملة
```

---

## 🎯 إذا حدثت مشكلة

### البوت لا يرد؟
```
1. تحقق من المفاتيح صحيحة
2. تحقق من الـ webhook تم تفعيله
3. اختبر: curl https://your-app.railway.app/
4. انظر السجلات في Railway Dashboard
```

### الـ API لا تعمل؟
```
1. تحقق من المفاتيح مرة أخرى
2. حاول /status في Telegram
3. اقرأ logs/digital_castle.log محلياً
```

### خطأ في النشر على Railway؟
```
1. تأكد من وجود جميع الملفات
2. تأكد من requirements.txt صحيح
3. تأكد من Dockerfile موجود
4. اعرض السجلات في Railway
```

---

## 📚 المزيد من المعلومات

- 📖 [README.md](./README.md) - الدليل الشامل
- 🔧 [API_SPECIFICATION.md](./API_SPECIFICATION.md) - مواصفات API
- ✅ [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - قائمة التحقق
- 📊 [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - ملخص شامل

---

## 🎉 مبروك! أنت الآن في الطريق الصحيح!

النظام يعمل بكامل طاقته مع:
- ✅ 3 نماذج ذكية متكاملة
- ✅ Telegram Bot متقدم
- ✅ قاعدة بيانات كاملة
- ✅ إدارة توكنز تلقائية
- ✅ توليد مستندات احترافية

**الوقت المتبقي:** استمتع! 🚀

---

**آخر تحديث:** 2024-01-15
**المدة:** ⏱️ 5 دقائق فقط
**الحالة:** ✅ جاهز للعمل الفوري
