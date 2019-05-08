from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UserChangeForm,
    ReadOnlyPasswordHashField,
    )

from panpub import references as refs
from panpub.models import (
    Collective,
    Content,
    Platform,
    fontawesome_choices,
    )
from panpub.utils import worktype_inputtype

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox


class LoginForm(AuthenticationForm):
    captcha = ReCaptchaField(label="",
                             widget=ReCaptchaV2Checkbox(attrs={'data-theme': 'dark',}),
                             )


class ContactForm(forms.Form):
    identity = forms.CharField(max_length=100)
    email = forms.EmailField(min_length=5, max_length=100)
    message = forms.CharField(max_length=400, widget=forms.Textarea(attrs={'rows': 2}))
    captcha = ReCaptchaField(label="",
                             widget=ReCaptchaV2Checkbox(attrs={'data-theme': 'dark'}),
                             )


class HiddenPasswordHashField(ReadOnlyPasswordHashField):
    """HiddenInput for the ReadOnlyPasswordHashField of UserChangeForm"""
    widget = forms.HiddenInput


class ProfileEdit(UserChangeForm):
    fa_icon = forms.ChoiceField(choices=fontawesome_choices())
    password = HiddenPasswordHashField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class CrafterDeploy(UserCreationForm):
    fa_icon = forms.ChoiceField(choices=fontawesome_choices())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class CollectiveDeploy(forms.ModelForm):
    class Meta:
        model = Collective
        fields = ['name', ]


class CollectiveEdit(forms.ModelForm):
    class Meta:
        model = Collective
        fields = ['name', 'members', 'manifeste']


class PlatformDeploy(forms.ModelForm):
    class Meta:
        model = Platform
        fields = ['contact_email', 'main_color', 'use_portal']


class ContentUpload(forms.ModelForm):
    input_type = forms.ChoiceField()
    document = forms.FileField()

    class Meta:
        model = Content
        exclude = ['id', 'ready', 'claims', 'is_exhibit']
        widgets = {
            'description': forms.Textarea(attrs={"rows": 3}),
        }


    def __init__(self, *args, **kwargs):
        super(ContentUpload, self).__init__(*args, **kwargs)
        if 'worktype' in self.data:
            try:
                worktype = str(self.data.get('worktype'))
                self.fields['input_type'].choices = worktype_inputtype(worktype)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['input_type'].choices = worktype_inputtype(self.worktype)


class TextExport(forms.Form):
    format = forms.ChoiceField(choices=[(k, k) for k in refs.text_pubformats])


class ImageExport(forms.Form):
    format = forms.ChoiceField(choices=[(k, k) for k in refs.image_pubformats])


class CorpusExport(forms.Form):
    format = forms.ChoiceField(choices=[(k, k) for k in refs.corpus_pubformats])


class AudioExport(forms.Form):
    format = forms.ChoiceField(choices=[(k, k) for k in refs.audio_pubformats])
