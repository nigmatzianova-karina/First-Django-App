from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError

class UserBioForm(forms.Form):
    name = forms.CharField(label="Full name", max_length=100)
    age = forms.IntegerField(label="Age", max_value=100, min_value=1)
    bio = forms.CharField(label="Biography", widget=forms.Textarea)


def validate_file_name(file: InMemoryUploadedFile) -> None:
    if file.name and "virus" in file.name:
        raise ValidationError("File name should not contain 'virus'")


class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[validate_file_name])
