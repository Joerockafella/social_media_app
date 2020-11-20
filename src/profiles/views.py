from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Relationship, ProfileManager
from .forms import ProfileModelForm
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.db.models import Q

# Create your views here.


def my_profile_view(request):
    # Requesting the user field
    profile = Profile.objects.get(user=request.user)
    # Update the profile with the instance, then request POST and then request Files for the Avatar
    form = ProfileModelForm(request.POST or None,
                            request.FILES or None, instance=profile)
    confirm = False
    # This form helps to update the profile
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            confirm = True
    context = {
        'profile': profile,
        'form': form,
        'confirm': confirm,
    }

    return render(request, 'profiles/myprofile.html', context)


def invites_received_view(request):
    profile = Profile.objects.get(user=request.user)
    qs = Relationship.objects.invitations_received(profile)
    # This helps to only get the sender
    results = list(map(lambda x: x.sender, qs))
    is_empty = False
    if len(results) == 0:
        is_empty = True
    context = {
        'qs': results,
        'is_empty': is_empty,
    }

    return render(request, 'profiles/my_invites.html', context)


# Accepting invitations
def accept_invitation(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        if rel.status == 'send':
            rel.status = 'accepted'
            rel.save()
    return redirect('profiles:my-invites-view')


# Rejecting invitations
def reject_invitation(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()
    return redirect('profiles:my-invites-view')


def invite_profiles_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles_to_invite(user)

    context = {
        'qs': qs,
    }

    return render(request, 'profiles/to_invite_list.html', context)


# def profiles_list_view(request):
#     user = request.user
#     qs = Profile.objects.get_all_profiles(user)

#     context = {
#         'qs': qs,
#     }

#     return render(request, 'profiles/profile_list.html', context)


class ProfileListView(ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'
    # This below can be used instead of "object_list" in the template
    context_object_name = 'qs'

    # Method 1 to get the list view
    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs

    # Method 2
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        # Relationship receiver (where we invited other users to friends) so we are the sender
        rel_r = Relationship.objects.filter(sender=profile)
        # Relationship that were sent by other users to our profile, so we are the reciever
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)
        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['is_empty'] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True

        return context


# Sending invitations
def send_invitation(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        # Relationship where receiver or sender wants to send friend request
        rel = Relationship.objects.create(
            sender=sender, receiver=receiver, status='send')

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')


# Removing a friend
def remove_from_friends(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        # Relationship to delete when received or sent friend request
        rel = Relationship.objects.get((Q(sender=sender) & Q(receiver=receiver)) | (
            Q(sender=receiver) & Q(receiver=sender)))

        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')
