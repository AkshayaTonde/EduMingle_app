from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=100, null=True)
    image = models.ImageField(default="default.jpg", upload_to='profile_pics')
    preferred_subjects = models.CharField(max_length=255, blank=True)
    study_type = models.CharField(max_length=50, choices=[('online', 'Online'), ('offline', 'Offline'), ('hybrid', 'Hybrid')], blank=True)
    user_bio = models.TextField(blank=True)

    

    def __str__(self):
        return f"{self.user.username} profile"

    # save method if the image is too big, Pillow for resizing

    # Alternatively, you can also resize the image before committing the form
    # Lots of ways to do it
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class QuizQuestion(models.Model):
    question_text = models.CharField(max_length=255)
    option_1 = models.CharField(max_length=100)
    option_2 = models.CharField(max_length=100)
    option_3 = models.CharField(max_length=100)
    option_4 = models.CharField(max_length=100)

    def __str__(self):
        return self.question_text

class QuizResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.question.question_text} - {self.selected_option}"
