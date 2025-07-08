import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Union
from flask import Flask, request, jsonify

app = Flask(__name__)
DATABASE = "reviews.db"


class SentimentAnalyzer:
    """Анализатор тональности текста на основе ключевых слов."""

    POSITIVE_WORDS = {
        "хорош", "хорошо", "отличн", "прекрасн", "люблю",
        "нравится", "супер", "класс", "восхитительн", "лучш",
        "замечательн", "превосходн", "удобн", "рекомендую", "доволен",
        "великолепн", "безупречн", "идеальн", "прекрасно", "отлично"
    }
    NEGATIVE_WORDS = {
        "плох", "плохо", "ужасн", "ненавиж", "отвратительн",
        "кошмар", "разочарован", "неудобн", "худш", "недостаток",
        "проблем", "недостат", "недоволен", "некачествен", "ужасно",
        "недоволь", "отвратно", "отвратительно", "мерзост", "неприятн", "не нравится"
    }

    @classmethod
    def analyze(cls, text: str) -> str:
        if not isinstance(text, str):
            raise ValueError("Text must be a string")

        if not text.strip():
            return "neutral"

        text_lower = text.lower()

        # Проверка на отрицательные фразы с "не"
        negative_phrases = {"не нравится", "не люблю", "не хочу"}
        if any(phrase in text_lower for phrase in negative_phrases):
            return "negative"

        if any(word in text_lower for word in cls.POSITIVE_WORDS):
            return "positive"
        if any(word in text_lower for word in cls.NEGATIVE_WORDS):
            return "negative"
        return "neutral"


class ReviewRepository:
    """
    Репозиторий для работы с отзывами в SQLite.
    Инкапсулирует все операции с базой данных.
    """

    def __init__(self, db_path: str = DATABASE) -> None:
        """
        Инициализирует репозиторий.

        :param db_path: Путь к файлу БД (по умолчанию 'reviews.db')
        """

        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Создает таблицу отзывов при отсутствии."""

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    sentiment TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

    def create(self, text: str, sentiment: str) -> Dict[str, Union[str, int]]:
        """
        Создает новый отзыв в базе данных.

        :param text: Текст отзыва.
        :param sentiment: Тональность ('positive'/'negative'/'neutral').
        :return: Созданный отзыв с ID и временем создания.

        :raises sqlite3.Error: При ошибках работы с БД.
        """

        created_at = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reviews (text, sentiment, created_at) VALUES (?, ?, ?)",
                (text, sentiment, created_at)
            )
            return {
                "id": cursor.lastrowid,
                "text": text,
                "sentiment": sentiment,
                "created_at": created_at
            }

    def find_all(self, sentiment: Optional[str] = None) -> List[Dict[str, Union[str, int]]]:
        """
        Возвращает список отзывов с фильтрацией по тональности.

        :param sentiment: Опциональный фильтр ('positive'/'negative'/'neutral').
        :return: Список отзывов.

        :raises sqlite3.Error: При ошибках чтения.
        """

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM reviews"
            params = ()
            if sentiment:
                query += " WHERE sentiment = ?"
                params = (sentiment,)

            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def delete(self, review_id: int) -> bool:
        """
        Удаляет отзыв по ID.

        :param review_id: ID отзыва для удаления.
        :return: True если удалено, False если не найдено.

        :raises sqlite3.Error: При ошибках удаления.
        """

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))

            return cursor.rowcount > 0


class ReviewService:
    """
    Сервис для обработки бизнес-логики отзывов.
    Координирует работу репозитория и анализатора.
    """

    def __init__(self, repository: ReviewRepository, analyzer: SentimentAnalyzer) -> None:
        """
        Инициализирует сервис.

        :param repository: Экземпляр ReviewRepository
        :param analyzer: Экземпляр SentimentAnalyzer
        """

        self.repository = repository
        self.analyzer = analyzer

    def create_review(self, text: str) -> Dict[str, Union[str, int]]:
        """
        Создает отзыв с автоматическим анализом тональности.

        :param text: Текст отзыва
        :return: Созданный отзыв

        :raises ValueError: При пустом тексте
        :raises sqlite3.Error: При ошибках сохранения
        """

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string")

        sentiment = self.analyzer.analyze(text)

        return self.repository.create(text, sentiment)

    def get_reviews(self, sentiment: Optional[str] = None) -> List[Dict[str, Union[str, int]]]:
        """
        Возвращает отзывы с возможной фильтрацией.

        :param sentiment: Опциональный фильтр тональности.
        :return: Список отзывов.

        :raises sqlite3.Error: При ошибках чтения.
        """

        return self.repository.find_all(sentiment)

    def delete_review(self, review_id: int) -> bool:
        """
        Удаляет отзыв по ID.

        :param review_id: ID отзыва.
        :return: Статус удаления.

        :raises sqlite3.Error: При ошибках удаления.
        """

        return self.repository.delete(review_id)


repository = ReviewRepository()
analyzer = SentimentAnalyzer()
service = ReviewService(repository, analyzer)


@app.route("/reviews", methods=["POST"])
def add_review() -> Tuple[Dict, int]:
    """
    Обрабатывает POST-запрос для создания отзыва.

    :return: Кортеж (JSON-ответ, HTTP-статус).

    Пример запроса:
        POST /reviews
        Content-Type: application/json
        {"text": "Отличный продукт!"}
    """

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Field 'text' is required"}), 400

        review = service.create_review(data["text"])
        return jsonify(review), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@app.route("/reviews", methods=["GET"])
def get_reviews() -> Tuple[Dict, int]:
    """
    Обрабатывает GET-запрос для получения отзывов.

    :queryparam sentiment: Фильтр по тональности.
    :return: Кортеж (JSON-ответ, HTTP-статус).

    Пример запроса:
        GET /reviews?sentiment=negative
        GET /reviews?sentiment=positive
        GET /reviews?sentiment=neutral
    """

    sentiment = request.args.get("sentiment")
    try:
        reviews = service.get_reviews(sentiment)
        return jsonify(reviews), 200

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@app.route("/reviews/<int:review_id>", methods=["DELETE"])
def delete_review(review_id: int) -> Tuple[Dict, int]:
    """
    Обрабатывает DELETE-запрос для удаления отзыва.

    :param review_id: ID отзыва.

    :return: Кортеж (JSON-ответ, HTTP-статус).

    Пример запроса:
        DELETE /reviews/1
    """

    try:
        if not isinstance(review_id, int) or review_id <= 0:
            return jsonify({"error": "Review ID must be a positive integer"}), 400

        if service.delete_review(review_id):
            app.logger.info(f"Successfully deleted review ID {review_id}")
            return jsonify({
                "message": f"Review with ID {review_id} deleted successfully",
                "deleted_id": review_id
            }), 200

        app.logger.warning(f"Review ID {review_id} not found for deletion")
        return jsonify({
            "error": f"Review with ID {review_id} not found",
            "requested_id": review_id
        }), 404

    except sqlite3.Error as e:
        app.logger.error(f"Database error while deleting review {review_id}: {str(e)}")
        return jsonify({
            "error": "Database operation failed",
            "details": str(e)
        }), 500

    except Exception as e:
        app.logger.error(f"Unexpected error deleting review {review_id}: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
