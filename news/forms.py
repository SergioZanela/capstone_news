from django import forms

from .models import Article


class ArticleForm(forms.ModelForm):
    """
    Simple form for journalists to submit a new Article from the web UI.

    Notes:
    - We intentionally exclude author/approved fields.
      Those are set in the view to prevent user tampering.
    """

    class Meta:
        model = Article
        fields = ["title", "content", "publisher"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 8}
            ),
            "publisher": forms.Select(
                attrs={"class": "form-select"}
            ),
        }
