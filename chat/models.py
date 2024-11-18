from django.db import models
from users import models as usersmodels

# Create your models here.


class Message(models.Model):
    username = models.CharField(max_length=50)
    room = models.CharField(max_length=50)
    message_content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    profile_pic = models.ImageField()

    class Meta:
        ordering = ('date_added', )

    def __str__(self):
        return f"{self.username}: {self.message_content}"


class Room(models.Model):
    name = models.CharField(max_length=50)
    # for url
    slug = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.name)


class Connectionrequests(models.Model):
    sender = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='received_requests')
    is_approved = models.BooleanField(default=False)
    chatroomname = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.sender} to {self.receiver} - Approved: {self.is_approved}"

