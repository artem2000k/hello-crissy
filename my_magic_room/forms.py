from django import forms
from django_quill.widgets import QuillWidget
from my_magic_room.models import memes, tales, stories, JournalPage, posts, krissy_blog
from pprint import pprint


class MemesAdminForm(forms.ModelForm):
    class Meta:
        model = memes
        fields = "__all__"
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].widget = QuillWidget(config_name="default")


class TalesAdminForm(forms.ModelForm):
    class Meta:
        model = tales
        fields = "__all__"
        # widgets = {}
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields["description"].widget = QuillWidget(config_name="default")


class StoriesAdminForm(forms.ModelForm):
    class Meta:
        model = stories
        fields = "__all__"
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].widget = QuillWidget(config_name="default")


class PostsAdminForm(forms.ModelForm):
    class Meta:
        model = posts
        fields = "__all__"
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CrissyBlogAdminForm(forms.ModelForm):
    class Meta:
        model = krissy_blog
        fields = "__all__"
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class JournalPageAdminForm(forms.ModelForm):
    class Meta:
        model = JournalPage
        fields = "__all__"
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].widget = QuillWidget(config_name="default")