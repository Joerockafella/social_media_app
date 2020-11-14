from django.db import models
from django.core.validators import FileExtensionValidator
from profiles.models import Profile

# Create your models here.


class Post(models.Model):
    content = models.TextField()
    image = models.ImageField(upload_to='posts', validators=[
                              FileExtensionValidator(['png', 'jpg', 'jpeg'])], blank=True)
    # To Keep track of profiles that like a post
    liked = models.ManyToManyField(Profile, blank=True, related_name='Likes')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='posts')

    def __str__(self):
        return str(self.content[:20])  # Limiting the content to 20 chars

    # Grab the number of likes for one particular post object and count them
    def num_likes(self):
        return self.liked.all().count()

    # TODO: Grab the number of comments here
    # This is a "Reverse Relationship" because we don't have a related name,
    #  so we use it with a "modelName_set" like below
    def num_comments(self):
        return self.comment_set.all().count()

    class Meta:
        ordering = ('-created',)


class Comment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    body = models.TextField(max_length=300)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)


# This is for value field for choices
LIKE_CHOICES = (
    # In this tuple the left value is for database purposes
    # and the right value is for human readable name
    ('Like', 'Like'),
    ('Unlike', 'Unlike'),
)

# The purpose of this is to hava a track of the like
# To know when a particular user give a like to what post


class Like(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, max_length=8)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}-{self.post}-{self.value}"
