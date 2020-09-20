from django.contrib.auth.models import AbstractUser
from django.db import models
import time

class User(AbstractUser):
    pass
    def __str__(self):
        return f"User ID: {self.id} Name: {self.username}"

class Post(models.Model):
    post = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def serialize(self):
        return {
            "id": self.id,
            "post": self.post,
            "created_at": self.created_at,
            "user": self.user_id.username,
            "user_id": self.user_id.id
        }

class Like(models.Model):
    like = models.BooleanField(default=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Like ID:{self.id}. Like Status: {self.like} From User ID: {self.user}"

#Check how to do a following, unfollowing model, confirmed a follower and following models are required. 

