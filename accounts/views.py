from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import CustomUserRegistrationForm


def register(request):
    """
    Public registration view for Reader / Journalist accounts.
    """
    if request.user.is_authenticated:
        return redirect("article_list")

    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        user = form.save()
        # Reader is approved immediately
        if user.role == "Reader":
            user.is_active = True
            user.save(update_fields=["is_active"])
            login(request, user)
            messages.success(
                request,
                "Account created successfully. You are now logged in."
            )
            return redirect("article_list")

        # Journalist / Editor require admin approval
        user.is_active = False
        user.save(update_fields=["is_active"])

        messages.info(
            request,
            "Your account request has been submitted and is pending "
            "admin approval. You will be able to log in once approved."
        )
        return redirect("login")
    else:
        form = CustomUserRegistrationForm()

    return render(request, "registration/register.html", {"form": form})
