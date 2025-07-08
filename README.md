# Отзывы с анализом тональности

## Установка и запуск

```bash
pip install flask
```
```bash
python app.py
```

## Запуск тестов

```bash
pip install pytest
```

```bash
pytest -v
```

## Примеры запросов

### Добавление отзыва Windows

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"text\":\"Отличный продукт!\"}" http://127.0.0.1:5000/reviews
```

### Добавление отзыва Linux/OS

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text":"Отличный продукт!"}' http://127.0.0.1:5000/reviews
```

### Получить все отзывы:

```bash
curl "http://localhost:5000/reviews"
```

```json

[
  {
    "created_at": "2025-07-08T14:22:30.462018",
    "идентификатор": 3,
    "настроение": "положительное",
    "text": "Отличный продукт!"
  },
  {
    "created_at": "2025-07-08T14:23:40.810185",
    "идентификатор": 4,
    "настроение": "положительное",
    "text": "Отличный продукт!"
  },
  {
    "created_at": "2025-07-08T14:23:40.819185",
    "идентификатор": 5,
    "настроение": "нейтральное",
    "text": "Тестовый отзыв"
  }
]
```

### Получить негативные отзывы:

```bash
curl "http://localhost:5000/reviews?sentiment=negative"

```

```json
[
  {
    "id": 2,
    "text": "Это ужасный продукт",
    "sentiment": "negative",
    "created_at": "2023-10-20T12:35:10.123456"
  }
]
```

### Получить позитивные отзывы:

```bash
curl "http://localhost:5000/reviews?sentiment=positive"
```

```json
[
  {
    "id": 2,
    "text": "Это прекрасный продукт",
    "sentiment": "positive",
    "created_at": "2023-10-20T12:35:10.123456"
  }
]
```

### Получить нейтральные отзывы:

```bash
curl "http://localhost:5000/reviews?sentiment=neutral"
```

```json
[
  {
    "id": 2,
    "text": "Это нормальный продукт",
    "sentiment": "neutral",
    "created_at": "2023-10-20T12:35:10.123456"
  }
]
```

### Удаление отзыва

```bash
curl -X DELETE "http://localhost:5000/reviews/4"
```

```json
[
  {
    "deleted_id": 4,
    "message": "Review with ID 4 deleted successfully"
  }
]
```
