from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import Post, Like
from profiles.models import Profile
from .forms import PostModelForm, CommentModelForm
from django.views.generic import UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


@login_required
def post_comment_create_and_list_view(request):
    qs = Post.objects.all()
    profile = Profile.objects.get(user=request.user)

    # Initials
    p_form = PostModelForm()
    c_form = CommentModelForm()
    post_added = False

    # Getting the profile of the user that is currently loggedin
    profile = Profile.objects.get(user=request.user)

    if 'submit_p_form' in request.POST:
        p_form = PostModelForm(request.POST, request.FILES)
        if p_form.is_valid():
            instance = p_form.save(commit=False)
            instance.author = profile
            instance.save()
            p_form = PostModelForm()
            post_added = True

    if 'submit_c_form' in request.POST:
        c_form = CommentModelForm(request.POST)
        if c_form.is_valid():
            instance = c_form.save(commit=False)
            instance.user = profile
            instance.post = Post.objects.get(id=request.POST.get('post_id'))
            instance.save()
            c_form = CommentModelForm()

    context = {
        'qs': qs,
        'profile': profile,
        'p_form': p_form,
        'c_form': c_form,
        'post_added': post_added,
    }

    return render(request, 'posts/main.html', context)

# A view to like and unlike posts


@login_required
def like_unlike_post(request):
    # We first request a user that is logged in
    user = request.user

    # We cheeck if we are dealing with a post request
    if request.method == 'POST':
       # We grab the post id from the form
        post_id = request.POST.get('post_id')
        # We grab the post thru its id
        post_obj = Post.objects.get(id=post_id)
        # We grab the profile of that user
        profile = Profile.objects.get(user=user)

        # we check if a profile has liked this post
        if profile in post_obj.liked.all():
            # if so, remove this profile in the like of this post
            post_obj.liked.remove(profile)
        else:
            # if the profile hasn't liked the post we add it to the likes of this post
            post_obj.liked.add(profile)

        # Then We create the like
        # The "like" is an object and the "created" is a boolean value
        # meaning if created == TRUE the post didn't exist it was created
        like, created = Like.objects.get_or_create(
            # In our like table the user is a profile
            user=profile, post_id=post_id)

        if not created:
            if like.value == 'Like':
                like.value == 'Unlike'
            else:
                like.value == 'Like'
        else:
            like.value == 'Like'

            post_obj.save()
            like.save()
        # Creating a json response for likes and unlikes to prevent page reload
        data = {
            'value': like.value,
            'likes': post_obj.liked.all().count()
        }

        return JsonResponse(data, safe=False)
    return redirect('posts:main-post-view')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/confirm_del.html'
    success_url = reverse_lazy('posts:main-post-view')
    # success_url = '/posts'

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Post.objects.get(pk=pk)
        if not obj.author.user == self.request.user:
            messages.warning(
                self.request, 'You need to be the author of the post in order to delete it')
        return obj


class PostUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PostModelForm
    model = Post
    template_name = 'posts/update.html'
    success_url = reverse_lazy('posts:main-post-view')

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        if form.instance.author == profile:
            return super().form_valid(form)
        else:
            form.add_error(
                None, "You need to be the author of this post in order to update it")
            return super().form_invalid(form)
