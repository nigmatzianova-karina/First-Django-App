from django.contrib.auth.models import User
from django.db import models

def profile_avatar_dir_path(instance: "Profile", filename: str):
    return "profile/user_{pk}/avatar/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(null=True, blank=True, upload_to=profile_avatar_dir_path, default="uploads/avatars/default.jpg")

    def __str__(self):
        return self.user.name