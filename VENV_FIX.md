# ⚠️ Virtual Environment Fix

## المشكلة:
```
ModuleNotFoundError: No module named 'django'
```

## السبب:
- نشّطت `.venv` لكن Django مثبت في `venv`
- البيئتان الافتراضيتان مختلفتان

---

## ✅ الحل:

### الطريقة 1: استخدم `venv` الصحيحة (الأسهل):

```bash
# أوقف البيئة الحالية
deactivate

# نشّط البيئة الصحيحة
source venv/bin/activate

# شغّل السيرفر
python manage.py runserver
```

---

### الطريقة 2: ثبّت Django في `.venv`:

```bash
# البقاء في .venv
.venv/bin/pip install -r requirements.txt

# ثم شغّل السيرفر
python manage.py runserver
```

---

## 🎯 الخطوات:

### 1. اكتب في Terminal:
```bash
deactivate
```

### 2. نشّط `venv`:
```bash
source venv/bin/activate
```

### 3. شغّل السيرفر:
```bash
python manage.py runserver
```

---

## ✅ التحقق:

بعد تنشيط `venv` الصحيحة، يجب أن ترى:
```bash
(venv) [zakee@zakee-latitude7420 origin app real estate]$
```

**لاحظ:** `(venv)` وليس `(.venv)`

---

## 📝 للمستقبل:

دائماً استخدم:
```bash
source venv/bin/activate
```

**وليس** `.venv`

---

## 🔍 الفرق:

```
venv/     ✅ فيها Django وجميع المكتبات
.venv/    ❌ فارغة أو بدون Django
```
