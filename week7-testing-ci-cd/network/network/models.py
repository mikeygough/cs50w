from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)


class Post(models.Model):

    body = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.author}, {self.body}"


class UserFollowing(models.Model):
    user_id = models.ForeignKey("User", related_name="following", on_delete=models.CASCADE)
    following_user_id = models.ForeignKey("User", related_name="followers", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    '''
    # to add
    UserFollowing.objects.create(user_id=user.id,
                                 following_user_id=follow.id)

    # to access
    user = User.objects.get(id=1)
    user.following.all()
    user.followers.all()
    '''


class UserLikes(models.Model):
    user_id = models.ForeignKey("User", related_name="user", on_delete=models.CASCADE)
    liked_post_id = models.ForeignKey("Post", related_name="likedpost", on_delete=models.CASCADE)