import json
import os
from unittest.mock import patch

import pytest

from app import (
    SentimentAnalyzer,
    ReviewRepository,
    ReviewService,
    app,
)


@pytest.fixture
def test_db(tmp_path):
    """Фикстура для тестовой базы данных."""

    db_path = tmp_path / "test_reviews.db"
    yield str(db_path)
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def repo(test_db):
    """Фикстура для тестового репозитория."""

    return ReviewRepository(test_db)


@pytest.fixture
def analyzer():
    """Фикстура для анализатора."""

    return SentimentAnalyzer()


@pytest.fixture
def service(repo, analyzer):
    """Фикстура для сервиса."""

    return ReviewService(repo, analyzer)


@pytest.fixture
def client():
    """Фикстура для тестового клиента Flask."""

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestSentimentAnalyzer:
    def test_analyze_positive(self, analyzer):
        assert analyzer.analyze("Это отличный продукт!") == "positive"
        assert analyzer.analyze("Мне очень нравится") == "positive"
        assert analyzer.analyze("Восхитительное качество") == "positive"

    def test_analyze_negative(self, analyzer):
        assert analyzer.analyze("Это ужасный продукт!") == "negative"
        assert analyzer.analyze("Мне очень не нравится") == "negative"
        assert analyzer.analyze("Отвратительное качество") == "negative"

    def test_analyze_neutral(self, analyzer):
        assert analyzer.analyze("Это обычный продукт") == "neutral"
        assert analyzer.analyze("") == "neutral"
        assert analyzer.analyze("123") == "neutral"

    def test_analyze_invalid_input(self, analyzer):
        with pytest.raises(ValueError):
            analyzer.analyze(None)
        with pytest.raises(ValueError):
            analyzer.analyze(123)


class TestReviewRepository:
    def test_create_review(self, repo):
        review = repo.create("Тестовый отзыв", "neutral")
        assert review["id"] == 1
        assert review["text"] == "Тестовый отзыв"
        assert review["sentiment"] == "neutral"
        assert isinstance(review["created_at"], str)

    def test_find_all(self, repo):
        repo.create("Позитивный", "positive")
        repo.create("Негативный", "negative")

        reviews = repo.find_all()
        assert len(reviews) == 2

        positive = repo.find_all("positive")
        assert len(positive) == 1
        assert positive[0]["sentiment"] == "positive"

    def test_delete_review(self, repo):
        review = repo.create("Тестовый отзыв", "neutral")
        assert repo.delete(review["id"]) is True
        assert repo.delete(999) is False


class TestReviewService:
    def test_create_review(self, service):
        with patch.object(service.analyzer, 'analyze', return_value='positive'):
            review = service.create_review("Хороший продукт")
            assert review["sentiment"] == "positive"
            assert review["text"] == "Хороший продукт"

    def test_create_review_empty_text(self, service):
        with pytest.raises(ValueError):
            service.create_review("")
        with pytest.raises(ValueError):
            service.create_review(None)

    def test_get_reviews(self, service):
        service.create_review("Позитивный отзыв")
        service.create_review("Негативный отзыв")

        reviews = service.get_reviews()
        assert len(reviews) == 2

        positive = service.get_reviews("positive")
        assert len(positive) >= 0

    def test_delete_review(self, service):
        review = service.create_review("Тестовый отзыв")
        assert service.delete_review(review["id"]) is True
        assert service.delete_review(999) is False


class TestFlaskEndpoints:
    def test_add_review_success(self, client):
        response = client.post(
            "/reviews",
            data=json.dumps({"text": "Отличный продукт!"}),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert "id" in data
        assert data["text"] == "Отличный продукт!"

    def test_add_review_invalid_content_type(self, client):
        response = client.post(
            "/reviews",
            data={"text": "Отличный продукт!"}
        )
        assert response.status_code == 400

    def test_add_review_missing_text(self, client):
        response = client.post(
            "/reviews",
            data=json.dumps({"wrong_field": "value"}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_get_reviews(self, client):
        client.post(
            "/reviews",
            data=json.dumps({"text": "Тестовый отзыв"}),
            content_type='application/json'
        )

        response = client.get("/reviews")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_reviews_filtered(self, client):
        response = client.get("/reviews?sentiment=positive")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_delete_review(self, client):
        create_response = client.post(
            "/reviews",
            data=json.dumps({"text": "Отзыв для удаления"}),
            content_type='application/json'
        )
        review_id = json.loads(create_response.data)["id"]

        delete_response = client.delete(f"/reviews/{review_id}")
        assert delete_response.status_code == 200

        delete_response = client.delete("/reviews/999999")
        assert delete_response.status_code == 404

    def test_delete_review_invalid_id(self, client):
        response = client.delete("/reviews/not_a_number")
        assert response.status_code == 404
