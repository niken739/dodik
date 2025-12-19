# Backend (Lab 6)

Коротка інструкція для запуску серверної частини лабораторної роботи №6.

Встановлення залежностей:

```bash
python -m pip install -r backend/requirements.txt
```

Запуск сервера:

```bash
python backend/run.py
```

Роути:
- `GET /health_check` - перевірка здоров'я сервісу
- `POST /api/auth/registration` - реєстрація (JSON: {"login": "..", "password": ".."})
- `POST /api/auth/login` - логін (JSON: {"login": "..", "password": ".."})

Тестування: використайте Postman або curl для відправки запитів на відповідні ендпоінти.
