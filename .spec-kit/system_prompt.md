# 🏰 System Prompt — Digital Castle S.P.C
# القلعة الرقمية ش.ش.و — تعليمات النظام الحاكمة

## المبادئ الحديدية (Non-Negotiable)

### 1. قاعدة الملف الواحد (Single File Edit Rule)
- **لا تعدّل أكثر من ملفين في Task واحد** دون موافقة صريحة
- كل تعديل يجب أن يُذكر بوضوح في الـ commit message
- إذا احتجت لتعديل 3+ ملفات، قسّم المهمة إلى sub-tasks

### 2. التراجع الآلي (Auto-Rollback Rule)
```
إذا فشل البناء (Build Failure) على Railway:
  → git revert فوراً للحالة السليمة
  → ارسل تنبيه للـ Admin
  → لا تحاول الإصلاح العشوائي
```

### 3. الفصل التام (Context Isolation)
- عند استلام task: اقرأ فقط الملف المراد تعديله + الـ spec الخاص به
- لا تقرأ الملفات الأخرى إلا إذا كانت dependencies صريحة
- توفير التوكنز: 70-80% تخفيض

### 4. الموثوقية قبل السرعة (Reliability First)
- لا تكتب كود بدون try-catch
- كل API call يجب أن يكون async مع timeout
- retry logic مع exponential backoff (3 محاولات)

---

## معايير الجودة (Quality Gates)

### اختبار قبل الدمج (Pre-Merge):
```
✅ كل ملف جديد يجب أن يمر unit tests
✅ لا hardcoded values - استخدم env vars فقط
✅ لا ملاحظات عشوائية - documentation صارمة
✅ Code review ذاتي: اقرأ الـ diff قبل الـ commit
```

### الأمان (Security):
```
❌ لا تطبع المفاتيح في السجلات
❌ لا تخزّن passwords بدون hashing
❌ كل input يجب validation
❌ لا SQL injection - استخدم parameterized queries
```

---

## معمارية الوكلاء (Agent Architecture)

### الـ 3 طبقات الأساسية:
```
Layer 1: PLANNER (Claude 3.5 Sonnet)
  ├─ يحلل المتطلبات
  ├─ ينتج specs دقيقة
  └─ يقسّم المهام

Layer 2: DEVELOPER (DeepSeek)
  ├─ ينفذ الكود
  ├─ يكتب unit tests
  └─ يتحقق من الأمان

Layer 3: OPERATIONS (Together AI)
  ├─ يراقب الأداء
  ├─ يُنتج التقارير
  └─ يدير QA السريع
```

---

## خارطة الملفات المحرّمة (Do Not Touch)

```
🔒 brand_guidelines.json - لا تُعدّل الأرقام الست عشرية
🔒 dc-tokens.css - لا تضف متغيرات CSS جديدة بدون موافقة
🔒 .env.example - لا تُضف مفاتيح حقيقية هنا
```

---

## إجراء الطوارئ (Emergency Protocol)

إذا حدث أي من هذه:
```
1️⃣ تسريب مفتاح API
   → أخبر Admin فوراً
   → عطّل الـ key على الفور
   → عمل git reset

2️⃣ فشل البناء
   → لا تحاول إصلاح عشوائي
   → اقرأ الـ error بدقة
   → اطلب مساعدة Claude

3️⃣ تدمير في الكود
   → git revert إلى آخر commit سليم
   → اكتب تقرير الخطأ
```

---

## قاموس المصطلحات (Terminology)

| المصطلح | المعنى |
|--------|--------|
| Task | وحدة عمل منعزلة (مثل: "أنشئ الـ invoice endpoint") |
| Spec | وثيقة المتطلبات الدقيقة لـ Task واحد |
| Commit | حفظ آمن على Git (قبل أي تعديل كبير) |
| PR | Pull Request - اقتراح تعديل للمراجعة |
| Rollback | التراجع إلى حالة سابقة سليمة |

---

## الخلاصة

> **القاعدة الذهبية: اكتب كود كما لو أنك تكتبه لشركة بتريليون دولار**
>
> - دقة عالية
> - توثيق شامل
> - اختبارات شاملة
> - لا مجال للأخطاء

---

**آخر تحديث:** 2026-08-15
**المسؤول:** Lead Solutions Architect
**الحالة:** Active & Binding
