import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup'),
)
def test_pages_availability_for_anonymous_user(client, name):
    """Проверяем доступность страниц для анонимного пользователя."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, requires_auth',
    [
        ('news:detail', False),
        ('news:edit', True),
        ('news:delete', True),
    ],
)
def test_redirects_for_anonymous_user(client, name, requires_auth, news):
    """Проверяем редирект анонимного пользователя на страницу авторизации."""
    url = reverse(name, kwargs={'pk': news.pk})
    if requires_auth:
        expected_url = f"{reverse('users:login')}?next={url}"
        response = client.get(url)
        assertRedirects(response, expected_url)
    else:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_access_for_author_only(author_client, name, comment):
    """Проверяем доступность страниц редактирования\
          и удаления комментария для автора."""
    url = reverse(name, kwargs={'pk': comment.pk})
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_access_denied_for_non_author(not_author_client, name, comment):
    """Проверяем недоступность страниц редактирования\
          и удаления комментария для не автора."""
    url = reverse(name, kwargs={'pk': comment.pk})
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
