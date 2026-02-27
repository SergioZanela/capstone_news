from django.urls import path
from . import views

urlpatterns = [
    # Main UI page (list of articles)
    path(
        "",
        views.article_list,
        name="article_list"
    ),

    # Article creation page
    path(
        "articles/new/",
        views.create_article,
        name="article_create"
    ),

    # Article detail page
    path(
        "articles/<int:pk>/",
        views.article_detail,
        name="article_detail"
    ),
    path(
        "articles/<int:pk>/subscribe/journalist/",
        views.subscribe_journalist_from_article,
        name="subscribe_journalist_from_article",
    ),
    path(
        "articles/<int:pk>/subscribe/publisher/",
        views.subscribe_publisher_from_article,
        name="subscribe_publisher_from_article",
    ),
    path(
        "articles/<int:pk>/unsubscribe/journalist/",
        views.unsubscribe_journalist_from_article,
        name="unsubscribe_journalist_from_article",
    ),
    path(
        "articles/<int:pk>/unsubscribe/publisher/",
        views.unsubscribe_publisher_from_article,
        name="unsubscribe_publisher_from_article",
    ),

    # Editor approval queue (pending/unapproved articles)
    path(
        "queue/",
        views.approval_queue,
        name="approval_queue"
    ),

    # Actions for editors
    path(
        "queue/<int:pk>/approve/",
        views.approve_article,
        name="approve_article",
    ),
    path(
        "queue/<int:pk>/reject/",
        views.reject_article,
        name="reject_article",
    ),
]
