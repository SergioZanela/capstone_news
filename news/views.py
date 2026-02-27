from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib import messages
from .forms import ArticleForm
from .models import (
    Article,
    JournalistSubscription,
    PublisherSubscription,
    )
from .services import send_article_approved_email_to_subscribers


def _is_editor(user) -> bool:
    """
    Return True if user is an editor.

    We support both:
    - role field: "Editor" (capitalized in your DB)
    - group name: "Editor"
    """
    role = (getattr(user, "role", "") or "").strip()
    return role == "Editor" or user.groups.filter(name="Editor").exists()


@login_required
def article_list(request):
    """
    Main page: show ONLY approved articles.
    """
    articles = Article.objects.filter(approved=True).order_by("-created_at")
    return render(request, "news/article_list.html", {"articles": articles})


@login_required
def article_detail(request, pk):
    """
    Detail page:
    - Approved articles can be viewed by anyone logged in
    - Unapproved articles can only be viewed by editors
    - Readers can subscribe to the article's journalist/publisher
    """
    article = get_object_or_404(Article, pk=pk)

    if not article.approved and not _is_editor(request.user):
        return HttpResponseForbidden("Not allowed.")

    is_reader = _is_reader(request.user)

    is_subscribed_to_journalist = False
    is_subscribed_to_publisher = False

    if is_reader:
        is_subscribed_to_journalist = JournalistSubscription.objects.filter(
            reader=request.user,
            journalist=article.author,
        ).exists()

        if article.publisher:
            is_subscribed_to_publisher = PublisherSubscription.objects.filter(
                reader=request.user,
                publisher=article.publisher,
            ).exists()

    context = {
        "article": article,
        "is_reader": is_reader,
        "is_subscribed_to_journalist": is_subscribed_to_journalist,
        "is_subscribed_to_publisher": is_subscribed_to_publisher,
    }
    return render(request, "news/article_detail.html", context)


@login_required
def approval_queue(request):
    """
    Editor-only page: show articles waiting for approval (approved=False).
    """
    if not _is_editor(request.user):
        return HttpResponseForbidden("Editors only.")

    articles = Article.objects.filter(approved=False).order_by("-created_at")
    return render(request, "news/approval_queue.html", {"articles": articles})


@login_required
def approve_article(request, pk):
    """
    Editor action: approve a pending article (POST only).
    """
    if not _is_editor(request.user):
        return HttpResponseForbidden("Editors only.")

    article = get_object_or_404(Article, pk=pk)

    if request.method == "POST":
        article.approved = True
        article.approved_at = timezone.now()
        article.approved_by = request.user
        article.save(update_fields=["approved", "approved_at", "approved_by"])

        # Notify subscribed readers after approval
        send_article_approved_email_to_subscribers(article)

        # Success message shown on next page load
        # (base.html already renders messages)
        messages.success(request, f'Article "{article.title}" was approved.')

        return redirect("approval_queue")

    return redirect("approval_queue")


@login_required
def reject_article(request, pk):
    """
    Editor action: reject an article (POST only).

    Simple approach: delete it.
    (Later we can change this to 'rejected' status instead of delete.)
    """
    if not _is_editor(request.user):
        return HttpResponseForbidden("Editors only.")

    article = get_object_or_404(Article, pk=pk)

    if request.method == "POST":
        article.delete()
        msg = (
            f'Article "{article.title}" was rejected and deleted.'
        )
        messages.success(request, msg)
        return redirect("approval_queue")

    return redirect("approval_queue")


def _is_journalist(user) -> bool:
    """
    Return True if user is a journalist.

    Your DB roles are capitalized (Journalist/Editor/Reader),
    so we compare against "Journalist".
    """
    role = (getattr(user, "role", "") or "").strip()
    return (
        role == "Journalist"
        or user.groups.filter(name="Journalist").exists()
    )


def _is_reader(user) -> bool:
    """
    Return True if user is a reader.

    Your DB roles are capitalized (Journalist/Editor/Reader),
    so we compare against "Reader".
    """
    role = (getattr(user, "role", "") or "").strip()
    return (
        role == "Reader"
        or user.groups.filter(name="Reader").exists()
    )


@login_required
def create_article(request):
    """
    Journalists submit new articles here.

    Important:
    - author is always the logged-in user (set BEFORE validation)
    - approved is forced to False so editors must approve in /queue/
    """
    if not _is_journalist(request.user):
        return HttpResponseForbidden("Journalists only.")

    if request.method == "POST":
        # ✅ Create an Article instance with author set BEFORE form validation.
        # This prevents Article.clean() from raising an "author required" error
        # against a form that doesn't include an author field.
        article_instance = Article(author=request.user)

        form = ArticleForm(request.POST, instance=article_instance)
        if form.is_valid():
            article = form.save(commit=False)

            # Lock down editor-controlled fields
            article.approved = False
            article.approved_at = None
            article.approved_by = None

            article.save()

            messages.success(
                request,
                "Article submitted successfully and sent for editor approval.",
            )
            return redirect("article_list")
    else:
        form = ArticleForm()

    return render(request, "news/article_form.html", {"form": form})


@login_required
def subscribe_journalist_from_article(request, pk):
    """
    Reader-only action: subscribe to the article author's updates.
    POST only.
    """
    if request.method != "POST":
        return redirect("article_detail", pk=pk)

    if not _is_reader(request.user):
        return HttpResponseForbidden("Readers only.")

    article = get_object_or_404(Article, pk=pk)

    _, created = JournalistSubscription.objects.get_or_create(
        reader=request.user,
        journalist=article.author,
    )

    if created:
        messages.success(
            request,
            f"You are now subscribed to journalist {article.author.username}.",
        )
    else:
        messages.info(
            request,
            f"You are already subscribed to journalist "
            f"{article.author.username}.",
        )

    return redirect("article_detail", pk=pk)


@login_required
def subscribe_publisher_from_article(request, pk):
    """
    Reader-only action: subscribe to the article's publisher updates.
    POST only.
    """
    if request.method != "POST":
        return redirect("article_detail", pk=pk)

    if not _is_reader(request.user):
        return HttpResponseForbidden("Readers only.")

    article = get_object_or_404(Article, pk=pk)

    if not article.publisher:
        messages.warning(
            request,
            "This article has no publisher to subscribe to.",
        )
        return redirect("article_detail", pk=pk)

    _, created = PublisherSubscription.objects.get_or_create(
        reader=request.user,
        publisher=article.publisher,
    )

    if created:
        messages.success(
            request,
            f"You are now subscribed to publisher {article.publisher.name}.",
        )
    else:
        messages.info(
            request,
            f"You are already subscribed to publisher "
            f"{article.publisher.name}.",
        )

    return redirect("article_detail", pk=pk)


@login_required
def unsubscribe_journalist_from_article(request, pk):
    """
    Reader-only action: unsubscribe from the article author's updates.
    POST only.
    """
    if request.method != "POST":
        return redirect("article_detail", pk=pk)

    if not _is_reader(request.user):
        return HttpResponseForbidden("Readers only.")

    article = get_object_or_404(Article, pk=pk)

    deleted_count, _ = JournalistSubscription.objects.filter(
        reader=request.user,
        journalist=article.author,
    ).delete()

    if deleted_count:
        messages.success(
            request,
            f"You unsubscribed from journalist "
            f"{article.author.username}.",
        )
    else:
        messages.info(
            request,
            f"You were not subscribed to journalist "
            f"{article.author.username}.",
        )

    return redirect("article_detail", pk=pk)


@login_required
def unsubscribe_publisher_from_article(request, pk):
    """
    Reader-only action: unsubscribe from the article's publisher updates.
    POST only.
    """
    if request.method != "POST":
        return redirect("article_detail", pk=pk)

    if not _is_reader(request.user):
        return HttpResponseForbidden("Readers only.")

    article = get_object_or_404(Article, pk=pk)

    if not article.publisher:
        messages.warning(request, "This article has no publisher.")
        return redirect("article_detail", pk=pk)

    deleted_count, _ = PublisherSubscription.objects.filter(
        reader=request.user,
        publisher=article.publisher,
    ).delete()

    if deleted_count:
        messages.success(
            request,
            f"You unsubscribed from publisher "
            f"{article.publisher.name}.",
        )
    else:
        messages.info(
            request,
            f"You were not subscribed to publisher "
            f"{article.publisher.name}.",
        )

    return redirect("article_detail", pk=pk)
