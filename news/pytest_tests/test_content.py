import pytest
from django.urls import reverse
from news.forms import CommentForm
from news.models import News, Comment
from datetime import timedelta
from django.utils.timezone import now


@pytest.mark.django_db
def test_home_page_contains_max_10_news(client):
    """Проверяем, что на главной странице не более 10 новостей."""
    for i in range(12):
        News.objects.create(title=f"News {i}", text="Some content", date=now())
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) <= 10


@pytest.mark.django_db
def test_news_sorted_by_date(client):
    """Проверяем, что новости отсортированы от самой свежей к самой старой."""
    for i in range(3):
        News.objects.create(
            title=f"News {i}",
            text="Some content",
            date=now() - timedelta(days=i)
        )
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_sorted_chronologically(client, news, author):
    """Проверяем, что комментарии отсортированы по дате: старые в начале."""
    Comment.objects.create(news=news, author=author, text="Oldest comment",
                           created=now() - timedelta(days=2))
    Comment.objects.create(news=news, author=author, text="Newest comment",
                           created=now())
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    comments = response.context['news'].comment_set.all()
    dates = [comment.created for comment in comments]
    assert dates == sorted(dates)


@pytest.mark.django_db
def test_comment_form_visibility(client, news, author_client):
    """Проверяем видимость формы комментариев для разных пользователей."""
    url = reverse('news:detail', kwargs={'pk': news.pk})

    response = client.get(url)
    assert 'form' not in response.context

    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
