import pytest
from django.test import Client
from news.models import Comment, News
from django.contrib.auth.models import User


@pytest.fixture
def author(django_user_model):
    """Фикстура для автора."""
    return django_user_model.objects.create(username="test_author",
                                            password="test_password")


@pytest.fixture
def not_author(django_user_model):
    """Фикстура для не автора."""
    return django_user_model.objects.create(username='not_author',
                                            password='password')


@pytest.fixture
def author_client(author):
    """Клиент автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Клиент для не автора."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Новости."""
    return News.objects.create(title="Test News", text="Some content")


@pytest.fixture
def comment(author, news):
    """Комменты."""
    return Comment.objects.create(news=news, author=author,
                                  text="Test Comment")
