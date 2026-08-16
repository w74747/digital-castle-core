# 📡 مواصفات API - Digital Castle S.P.C

## معلومات عامة

**Base URL:** `https://your-app.railway.app` (أو `http://localhost:8000` في التطوير)

**Authentication:** غير مطلوبة حالياً (متحكم عليها من خلال Telegram Admin ID)

**Response Format:** JSON

**Rate Limiting:** غير محدود حالياً (سيتم تفعيله لاحقاً)

---

## Endpoints

### 1. صحة التطبيق

#### GET /
الحصول على حالة التطبيق والنظام

**Response:**
```json
{
  "status": "online",
  "company": "Digital Castle S.P.C",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**Status Codes:**
- `200 OK` - النظام يعمل بشكل طبيعي

---

### 2. استهلاك التوكنز

#### GET /api/tokens
الحصول على ملخص استهلاك التوكنز لجميع النماذج

**Response:**
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

**Status Codes:**
- `200 OK` - تم استرجاع البيانات بنجاح

---

### 3. دراسات الجدوى

#### POST /api/feasibility
إنشاء دراسة جدوى اقتصادية جديدة

**Request Body:**
```json
{
  "market_problem": "تطبيق توصيل طعام محلي",
  "target_audience": "سكان المدينة الأساسيون والعاملون"
}
```

**Response (Success):**
```json
{
  "success": true,
  "market_analysis": "تحليل مفصل لحجم السوق والفرص...",
  "feasibility_analysis": "دراسة اقتصادية شاملة...",
  "tokens_used": {
    "anthropic": 2500
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "وصف الخطأ هنا"
}
```

**Status Codes:**
- `200 OK` - تم إنشاء الدراسة بنجاح
- `400 Bad Request` - بيانات مفقودة أو غير صحيحة
- `500 Internal Server Error` - خطأ في الخادم

---

### 4. المواصفات الفنية

#### POST /api/specification
صياغة مواصفات تقنية جديدة لمشروع

**Request Body:**
```json
{
  "project_name": "متجر إلكتروني",
  "requirements": "نظام إدارة المخزون، بوابة دفع، لوحة تحكم المسؤول"
}
```

**Response (Success):**
```json
{
  "success": true,
  "specifications": "# المواصفات الفنية\n\n## النظرة العامة\n...",
  "tokens_used": {
    "anthropic": 3000
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "وصف الخطأ هنا"
}
```

**Status Codes:**
- `200 OK` - تم إنشاء المواصفات بنجاح
- `400 Bad Request` - بيانات مفقودة
- `500 Internal Server Error` - خطأ في الخادم

---

### 5. Telegram Webhook

#### POST /webhook/telegram
استقبال أحداث Telegram (يتم الاتصال بها تلقائياً من Telegram)

**Request Body (مثال):**
```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "date": 1615000000,
    "chat": {
      "id": 123456789,
      "type": "private"
    },
    "from": {
      "id": 123456789,
      "first_name": "Admin"
    },
    "text": "/start"
  }
}
```

**Response:**
```json
{
  "ok": true
}
```

**Status Codes:**
- `200 OK` - تم استقبال الرسالة بنجاح
- `400 Bad Request` - صيغة الرسالة خاطئة

**ملاحظة:** هذا الـ endpoint لا يحتاج استدعاء يدوي - يتم استدعاؤه من قبل Telegram فقط

---

## أوامر Telegram المتاحة

### الأوامر الأساسية

| الأمر | الوصف | المثال |
|------|-------|--------|
| `/start` | عرض الترحيب والأوامر المتاحة | `/start` |
| `/status` | حالة النظام والموارد | `/status` |
| `/tokens` | ملخص استهلاك التوكنز | `/tokens` |
| `/help` | المساعدة الكاملة | `/help` |

### أوامر الجدوى والمشاريع

| الأمر | الوصف | المثال |
|------|-------|--------|
| `/feasibility` | معلومات عن دراسة الجدوى | `/feasibility` |
| `/start_feasibility` | بدء دراسة جدوى جديدة | `/start_feasibility تطبيق توصيل \| سكان المدينة` |

### أوامر المواصفات

| الأمر | الوصف | المثال |
|------|-------|--------|
| `/spec` | معلومات عن المواصفات | `/spec` |
| `/start_spec` | صياغة مواصفات جديدة | `/start_spec متجر \| نظام دفع ومخزون` |

### أوامر الكود والجودة

| الأمر | الوصف |
|------|-------|
| `/code` | معلومات عن كتابة الكود |
| `/qa` | معلومات عن فحص الجودة |

---

## معالجة الأخطاء

### أنواع الأخطاء

#### 1. خطأ المفتاح API غير صحيح
```json
{
  "success": false,
  "provider": "anthropic",
  "error": "Unauthorized",
  "status_code": 401
}
```

#### 2. خطأ في الاتصال
```json
{
  "success": false,
  "provider": "deepseek",
  "error": "Connection timeout"
}
```

#### 3. خطأ في صيغة الطلب
```json
{
  "success": false,
  "error": "Missing required field: market_problem"
}
```

### رموز الأخطاء الشائعة

| Code | الرسالة | السبب | الحل |
|------|---------|--------|------|
| 400 | Bad Request | بيانات مفقودة أو غير صحيحة | تحقق من صيغة الطلب |
| 401 | Unauthorized | مفتاح API غير صحيح | تحقق من المفاتيح |
| 429 | Too Many Requests | عدد الطلبات زائد | انتظر قليلاً وحاول مجدداً |
| 500 | Internal Server Error | خطأ في الخادم | راجع السجلات |
| 503 | Service Unavailable | الخدمة معطلة | حاول لاحقاً |

---

## أمثلة الاستخدام

### مثال 1: استدعاء API دراسة الجدوى (cURL)

```bash
curl -X POST https://your-app.railway.app/api/feasibility \
  -H "Content-Type: application/json" \
  -d '{
    "market_problem": "تطبيق توصيل طعام",
    "target_audience": "سكان المدينة"
  }'
```

### مثال 2: الحصول على ملخص التوكنز (cURL)

```bash
curl https://your-app.railway.app/api/tokens
```

### مثال 3: استدعاء API في Python

```python
import requests
import json

url = "https://your-app.railway.app/api/feasibility"
payload = {
    "market_problem": "تطبيق توصيل طعام",
    "target_audience": "سكان المدينة"
}

response = requests.post(url, json=payload)
data = response.json()

if data['success']:
    print(data['market_analysis'])
else:
    print(f"Error: {data['error']}")
```

### مثال 4: استدعاء API في JavaScript

```javascript
const url = "https://your-app.railway.app/api/specification";
const payload = {
    project_name: "متجر إلكتروني",
    requirements: "نظام دفع ومخزون"
};

fetch(url, {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log(data.specifications);
    } else {
        console.error("Error:", data.error);
    }
});
```

---

## معايير الاستجابة

### وقت الاستجابة المتوقع

| نوع المهمة | الوقت المتوقع | الحد الأقصى |
|-----------|-------------|----------|
| حالة النظام | < 100ms | 200ms |
| ملخص التوكنز | < 200ms | 500ms |
| دراسة الجدوى | 30-60s | 120s |
| المواصفات | 45-90s | 180s |
| الكود | 60-120s | 240s |

### حجم الاستجابة

| نوع الاستجابة | الحد الأقصى |
|-----------|----------|
| رسائل بسيطة | 10 KB |
| المحتوى الكامل | 10 MB |

---

## المصادقة والأمان

### مستويات الوصول الحالية

- **المسؤول:** جميع الأوامر والعمليات (التحقق عبر TELEGRAM_ADMIN_ID)
- **المستخدمون العاديون:** رفض الوصول

### خطة المصادقة المستقبلية

- تفعيل نظام API Keys
- إدارة الأدوار والأذونات
- تشفير البيانات الحساسة

---

## قدود الاستخدام (Rate Limits)

حالياً لا توجد حدود للاستخدام، لكن سيتم تفعيلها:

```
الحدود المخطط لها:
- 100 طلب / دقيقة للمستخدم
- 10 طلبات متزامنة كحد أقصى
- 1GB / شهر نقل البيانات
```

---

## التحديثات والإصدارات

### Version 1.0.0 (Current)
- ✅ وظائف الجدوى الأساسية
- ✅ المواصفات الفنية
- ✅ Telegram Bot Integration
- ✅ Token Usage Tracking

### Version 1.1.0 (Planned)
- API Keys Authentication
- Role-Based Access Control
- Advanced Rate Limiting
- Data Export Feature

---

## دعم المطورين

### الموارد المتاحة
- 📖 [Postman Collection](https://www.postman.com) - قم بنسخ الطلبات
- 🧪 [Sandbox Environment](http://localhost:8000) - للاختبار المحلي
- 📋 [API Changelog](./CHANGELOG.md) - سجل التغييرات

### كيفية الإبلاغ عن المشاكل
1. تحقق من السجلات في `/logs`
2. احفظ معرف الطلب (Request ID)
3. وصف المشكلة بالتفصيل
4. أرسل التقرير إلى الدعم

---

**آخر تحديث:** 2024-01-15
**الحالة:** ✅ تم التحديث
