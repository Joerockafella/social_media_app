from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Relationship


# Basically this creates a profile as soon as a user gets created
@receiver(post_save, sender=User)
def post_save_create_profile(sender, instance, created, **Kwargs):
    # print('sender', sender)
    # print ('instance', instance)
    if created:
        Profile.objects.create(user=instance)


# Defining Friendship with the relationship model
@receiver(post_save, sender=Relationship)
def post_save_add_to_friends(sender, instance, created, **Kwargs):
    sender_ = instance.sender
    receiver_ = instance.receiver
    if instance.status == 'accepted':
        sender_.friends.add(receiver_.user)
        receiver_.friends.add(sender_.user)
        sender_.save()
        receiver_.save()


@receiver(pre_delete, sender=Relationship)
def pre_delete_remove_from_friends(sender, instance, **Kwargs):
    sender = instance.sender
    receiver = instance.receiver
    sender.friends.remove(receiver.user)
    receiver.friends.remove(sender.user)
    sender.save()
    receiver.save()
