from django.shortcuts import render
from .models import Profile
from .forms import ProfileModelForm

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
