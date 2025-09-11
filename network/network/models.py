from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def followers_count(self):
        return Follow.objects.filter(following=self).count()

    def following_count(self):
        return Follow.objects.filter(follower=self).count()
    
    def is_following(self, user):
        return Follow.objects.filter(follower=self, following=user).exists()

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(max_length=280)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self): 
        return f"{self.user.username}: {self.content[:50]}"
    
    def like_count(self):
        return self.likes.count()
    
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"