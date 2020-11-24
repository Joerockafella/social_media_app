from .models import Profile, Relationship 


# Getting the profile pic
def profile_pic(request):
    if request.user.is_authenticated:
        profile_obj = Profile.objects.get(user=request.user)
        pic = profile_obj.avatar
        return {'picture': pic}
    return {}


# Getting the invitation number
def invitations_received_no(request):
    if request.user.is_authenticated:
        # Getting the profile
        profile_obj = Profile.objects.get(user=request.user)
        # Here we get the count of invitation of this profile and the receiver is the profile
        qs_count = Relationship.objects.invitations_received(
            profile_obj).count()
        return {'invites_num': qs_count}
    return {}
