import pytest
from http import HTTPStatus
from django.urls import reverse
from news.models import Comment
from news.forms import WARNING
from pytest_django.asserts import assertRedirects, assertFormError


@pytest.mark.django_db
def test_anonymous_user_cannot_add_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    form_data = {'text': 'Anonymous comment'}
    response = client.post(url, form_data)
    expected_url = f"{reverse('users:login')}?next={url}"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authorized_user_can_add_comment(author_client, news):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    form_data = {'text': 'Authorized comment'}
    response = author_client.post(url, form_data)
    assertRedirects(response, f"{url}#comments")
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news


@pytest.mark.django_db
def test_comment_with_prohibited_words(author_client, news):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    form_data = {'text': 'This contains редиска, a bad word.'}
    response = author_client.post(url, form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    form_data = {'text': 'Edited comment'}
    response = author_client.post(url, form_data)
    assertRedirects(response,
                    f"{reverse('news:detail',
                               kwargs={'pk': comment.news.pk})}#comments")
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.post(url)
    assertRedirects(response,
                    f"{reverse('news:detail',
                               kwargs={'pk': comment.news.pk})}#comments")
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cannot_edit_others_comment(not_author_client, comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    form_data = {'text': 'Attempted edit'}
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']


@pytest.mark.django_db
def test_user_cannot_delete_others_comment(not_author_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
