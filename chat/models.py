from django.db import models
from users import models as usersmodels

# Create your models here.


"""class Message(models.Model):
    username = models.CharField(max_length=50)
    room = models.CharField(max_length=50)
    message_content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    profile_pic = models.ImageField()

    class Meta:
        ordering = ('date_added', )

    def __str__(self):
        return f"{self.username}: {self.message_content}"   """


# models.py

from django.db import models
from django.contrib.auth.models import User

from django.utils.text import slugify

class Room(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null= True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)  # Link to Room
    content = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp', )

    def __str__(self):
        return f"{self.user.username}: {self.content[:50] if self.content else 'File message'}"


"""class Room(models.Model):
    name = models.CharField(max_length=50)
    # for url
    slug = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.name) """


class Connectionrequests(models.Model):
    sender = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='received_requests')
    is_approved = models.BooleanField(default=False)
    chatroomname = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.sender} to {self.receiver} - Approved: {self.is_approved}"

