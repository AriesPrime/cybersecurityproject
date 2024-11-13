from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from django.db.models import Q
from django.db import connection
from .forms import CommentForm, PostForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt


def signup(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')

    return render(request, 'signup.html', {'form': form})


def signin(request):
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('home')

    return render(request, 'signin.html', {'form': form})


def signout(request):
    logout(request)
    return redirect('home')


def home(request):
    search_query = request.GET.get('search', '')
    if search_query:
        posts = Post.objects.filter(
            Q(id__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    else:
        posts = Post.objects.all().order_by('-created_at')[:50]

    return render(request, 'home.html', {'posts': posts, 'search_query': search_query})

def create_post(request):

    # Cryptographic Failures (A02:2021): data submitted by user is visible in URL
    # Fix:
    # Switch the 'GET' method to a 'POST' request to transfer data
    # form = PostForm(request.POST)

    form = PostForm(request.GET)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('post_detail', post_id=post.id)

    return render(request, 'create_post.html', {'form': form})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user.username
        comment.save()
        return redirect('post_detail', post_id=post.id)
    return render(request, 'post_detail.html', {'post': post, 'comments': comments, 'form': form})


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Broken Access Control (A01:2021): any user can edit any post
    # Fix: 
    # Check if the user is the author of the post
    # if post.author != request.user:
    #    return HttpResponseForbidden("You are not allowed to edit this post.")

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post_detail', post_id=post.id)
    return render(request, 'edit_post.html', {'form': form, 'post': post})


def search_posts(request):
    query = request.GET.get('q')
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM main_post WHERE title LIKE %s", [f'%{query}%'])
    posts = cursor.fetchall()

    return render(request, 'search_results.html', {'posts': posts})


# Cross-Site Request Forgery (CSRF): app is vulnerable to CSRF attacks
@csrf_exempt
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        Comment.objects.create(
            post=post, author=request.user, content=request.POST.get('content'))
        return redirect('post_detail', post_id=post.id)
    return render(request, 'add_comment.html', {'post': post})

# Fix:
# Remove @csrf_exempt and use CSRF protection on the form
# in the HTML template (e.g., {% csrf_token %} in forms)


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Broken Access Control (A01:2021): any user can delete any post
    # Fix:
    # Ensure only the post author can delete the post
    # if post.author != request.user.username:
    #     return HttpResponseForbidden("You are not allowed to delete this post.")
    post.delete()

    return redirect('home')


def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Broken Access Control (A01:2021): any user can delete any comment
    # Fix:
    # Ensure only the comment author can delete the comment
    # if comment.author != request.user.username:
    #     return HttpResponseForbidden("You are not allowed to delete this comment.")
    comment.delete()

    return redirect('post_detail', post_id=comment.post.id)
