# Отзывы с анализом тональности

## Установка и запуск

```bash
pip install flask
```
```bash
python app.py
```
## Примеры запросов

### Добавление отзыва

```bash
curl -X POST -H "Content-Type: application/json" -d '{"message":"Hello World"}' http://localhost:5000/reviews
```

Ответ:

```json
    {
      "id": 1,
      "text": "Мне нравится этот продукт",
      "sentiment": "positive",
      "created_at": "2025-07-08T12:34:56.789123"
    }
```

### Получение негативных отзывов

```bash
curl "http://localhost:5000/reviews?sentiment=negative"
```

Ответ:

```json
[
  {
    "id": 3,
    "text": "Ужасный сервис",
    "sentiment": "negative",
    "created_at": "2025-07-08T12:35:10.123456"
  },
  {
    "id": 4,
    "text": "Не рекомендую этот продукт",
    "sentiment": "negative",
    "created_at": "2025-07-08T12:35:20.123456"
  }
]
```

### Получение положительных отзывов

```bash
curl "http://localhost:5000/reviews?sentiment=positive"
```

Ответ:

```json
[
  {
    "id": 1,
    "text": "Мне нравится этот продукт",
    "sentiment": "positive",
    "created_at": "2025-07-08T12:34:56.789123"
  },
  {
    "id": 2,
    "text": "Отличное качество!",
    "sentiment": "positive",
    "created_at": "2025-07-08T12:34:56.789456"
  }
]
```

```

### Получение нейтральных отзывов
```bash
curl "http://localhost:5000/reviews?sentiment=neutral"
```

Ответ:

```json
[
  {
    "id": 2,
    "text": "Это ужасный продукт",
    "sentiment": "neutral",
    "created_at": "2023-10-20T12:35:10.123456"
  }
]
```