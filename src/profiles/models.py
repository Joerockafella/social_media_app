from django.db import models
# So we can use the User in the field
from django.contrib.auth.models import User
from .utils import get_random_code
from django.template.defaultfilters import slugify
from django.db.models import Q


class ProfileManager(models.Manager):

    # Getting all the profiles that are available for us to invite
    # excluding the ones that we are already in relationship with
    def get_all_profiles_to_invite(self, sender):
        profiles = Profile.objects.all().exclude(user=sender)
        profile = Profile.objects.get(user=sender)
        qs = Relationship.objects.filter(
            Q(sender=profile) | Q(receiver=profile))
        print(qs)
        print("##########")

        accepted = set([])
        for rel in qs:
            if rel.status == 'accepted':
                accepted.add(rel.receiver)
                accepted.add(rel.sender)
            print(accepted)

            available = [
                profile for profile in profiles if profile not in accepted]
            print(available)
            print("##########")
            return available

     # Getting all the profiles excluding our own(sender)
    def get_all_profiles(self, me):
        profiles = Profile.objects.all().exclude(user=me)
        return profiles


class Profile(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    # CASCADE means when user gets deleted profile get deleted too
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="no bio", max_length=100)
    email = models.EmailField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(default='avatar.png', upload_to='')
    friends = models.ManyToManyField(
        User, blank=True, related_name='friends')
    # The slug field will help generate a user name from first and last name
    slug = models.SlugField(unique=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ProfileManager()

    # To grab all the friends from the "ManyToManyField"
    def get_friends(self):
        return self.friends.all()

    # To get the number of friends
    def get_friends_no(self):
        return self.friends.all().count()

    # To get the number of posts
    def get_posts_no(self):
        return self.posts.all().count()

    # To get all the posts of from the author
    def get_all_authors_posts(self):
        return self.posts.all()

    # To get all the given likes we use again the "Resvese Relationship"
    # because we don't have a related name
    def get_likes_given_no(self):
        likes = self.like_set.all()
        total_liked = 0
        # Loop through the likes
        for item in likes:
            # To check if this item has a value of like
            if item.value == 'Like':
                total_liked += 1
        return total_liked

    def get_likes_received_no(self):
        # On this field we don't use the "Reverse Relationship" but we use "forward relationship",
        # because in the models.py of posts app there is a the author field that has a 'related_name="posts"'
        # then we get all the posts
        posts = self.posts.all()
        total_liked = 0
        for item in posts:
            # Here we get all the liked posts ref "liked" field in posts.models.py
            total_liked = item.liked.all().count()
        return total_liked

    def __str__(self):
        return f"{self.user.username}-{self.created.strftime('%d-%m-%Y')}"

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


class RelationshipManager(models.Manager):
    # This will give us all the invitaions that we received from diffrent users
    # The receiver is ourselves (in Relationship table)
    def invitations_received(self, receiver):
        qs = Relationship.objects.filter(receiver=receiver, status='send')
        return qs


class Relationship(models.Model):
    # When a profile gets deleted the relationship gets deleted too
    sender = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = RelationshipManager()

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"
