from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class CustomUserRegistrationForm(UserCreationForm):
    """
    Registration form for public account creation.

    Allow Reader and Journalist self-registration.
    Editor accounts should be created/admin-assigned manually.
    """

    ROLE_CHOICES = (
        ("Reader", "Reader"),
        ("Journalist", "Journalist"),
        ("Editor", "Editor")
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email", "role", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Bootstrap styling
        for name, field in self.fields.items():
            if name == "role":
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"

        # Optional nicer labels
        self.fields["email"].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user
