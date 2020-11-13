from django.db import models
# So we can use the User in the field
from django.contrib.auth.models import User
from .utils import get_random_code
from django.template.defaultfilters import slugify

# Create your models here.


class Profile(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    # CASCADE means when user gets deleted profile get deleted too
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="no bio", max_length=100)
    email = models.EmailField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(default='avatar.png', upload_to='')
    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    # The slug field will help generate a user name from first and last name
    slug = models.SlugField(unique=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}-{self.created.strftime('%d-%m-%Y')}"

    # To grab all the friends from the "ManyToManyField"
    def get_friends(self):
        return self.friends.all()

    # To get the number of friends
    def get_friends_no(self):
        return self.friends.all().count()

    # To help the slug field create the username
    # Fist to check if the first name and the last name exist
    # bcoz if they exist we create the slug out of them
    # else we store in the slug field the user

    def save(self, *args, **kwargs):
        ex = False
        if self.first_name and self.last_name:  # if they exist we slug them below
            to_slug = slugify(str(self.first_name) + " " + str(self.last_name))
            # making sure that the to_slug (first and last name) exist or not in the database
            ex = Profile.objects.filter(slug=to_slug).exists()
            # if they exist then we create a new one with an addition of the random code
            # While means we do it as long as the slug exist
            while ex:
                to_slug = slugify(to_slug + " " + str(get_random_code()))
                ex = Profile.objects.filter(slug=to_slug).exists()
            # And if it doesnt exist then the slug equals user
        else:
            to_slug = str(self.user)
        self.slug = to_slug
        super().save(*args, **kwargs)


STATUS_CHOICES = (
    ('send', 'send'),
    ('accepted', 'accepted')
)


class Relationship(models.Model):
    # When a profile gets deleted the relationship gets deleted too
    sender = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"
