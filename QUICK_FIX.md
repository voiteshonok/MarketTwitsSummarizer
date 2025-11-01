# Quick Fix for "database is locked" Error

## 🚨 Problem
```
sqlite3.OperationalError: database is locked
```

## ✅ Solution: Use StringSession

### 1️⃣ Generate Session String
```bash
python generate_session_string.py
```

### 2️⃣ Add to .env
```env
TELEGRAM_SESSION_STRING=1BJWap1wBu0xLwi4icwCC_RCJDRnHtRYVXd-vOD67ur...
```

### 3️⃣ Restart Application
```bash
# Local
python main.py

# Docker
docker-compose restart app
```

## ✨ Done!
No more SQLite locking issues. Multiple processes can now work simultaneously.
