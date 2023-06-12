from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)

    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default='user.png')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Topic(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class Room(models.Model):
    host = models.ForeignKey(User, null=True, on_delete=models.SET_NULL,)
    topic = models.ForeignKey(Topic, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name
    

    class Meta:
        ordering = ['-updated', '-created']


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.body[0:20]
    

    class Meta:
        ordering = ['-updated', '-created']