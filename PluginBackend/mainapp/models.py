from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import os
class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, username, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, username, password, **other_fields)
    def create_user(self, email, username, password, **other_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))
        
        other_fields.setdefault('is_active', True)
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **other_fields)
        # password = make_password(password=password)
        user.set_password(password)
        user.save()
        return user
    
class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, unique=True)
    id = models.AutoField(primary_key=True)

    objects = CustomAccountManager()

    # USERNAME_FIELD = 'username'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

class VideoAudio(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='media/videos/')
    audio_file = models.FileField(upload_to='media/audios/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Ensure video and audio file extensions are correct
        if self.video_file:
            # Get the file name and extension of the video
            video_filename, video_extension = os.path.splitext(self.video_file.name)
            # If the extension is not .mp4, change it to .mp4
            if video_extension.lower() != '.mp4':
                self.video_file.name = f"{slugify(self.title)}.mp4"  # Set to .mp4 extension

        if self.audio_file:
            # Get the file name and extension of the audio
            audio_filename, audio_extension = os.path.splitext(self.audio_file.name)
            # If the extension is not .mp3, change it to .mp3
            if audio_extension.lower() != '.mp3':
                self.audio_file.name = f"{slugify(self.title)}.mp3"  # Set to .mp3 extension

        # Call the original save method
        super().save(*args, **kwargs)

class Report(models.Model):
    id = models.AutoField(primary_key=True)
    report = models.JSONField(default=dict)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    video_audio = models.ForeignKey(to=VideoAudio, on_delete=models.CASCADE)