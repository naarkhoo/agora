# Create your views here.
from datetime import date, timedelta
# from urlparse import urlparse

from django.shortcuts import render, redirect
from django.contrib.auth import login as lin, authenticate, logout as lg
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import HttpResponse
from agora.models import Karma, Post, Comment, CommentVotes, PostVotes

today = date.today()
posts_limit = today - timedelta(days=3)

def home(request):
    global today
    global posts_limit
    if date.today() != today:

        today = date.today()
        posts_limit = today - timedelta(days=3)
    posts = Post.objects.filter(timestamp__gte=posts_limit).order_by('upvotes')[:50]
    return render(request, 'posts.html', {"posts":posts, "today":today})

def login(request):
    if request.user.is_authenticated():
        return home(request)
    elif request.method == 'GET':
        c = {}
        c.update(csrf(request))
        return render(request, 'login.html', c)
    else:
        # This is done quite stupid
        print "a"
        username = request.POST['name']
        password = request.POST['pass']
        user = authenticate(username=username, password=password)
        lin(request, user)
        return redirect("/")


def logout(request):
    lg(request)

def register(request):
    username = request.POST['name']
    password = request.POST['pass']
    user = User.objects.create_user(username=username, password=password)
    user.save()
    lin(request, user)
    return redirect("/")

def comment(request):
    """Adds a comment to a post."""
    if request.user.is_authenticated:
        post_id = int(request.POST['post'])
        parent_id = int(request.POST['parent'])
        user_id = int(request.POST['user'])
        text = request.POST['text']
        if parent_id != 0:
            parent = Comment.objects.get(pk=parent_id)
            depth = parent.depth + 1
        else:
            depth = 0
        post = Post.objects.get(pk=post_id)
        user = User.objects.get(pk=user_id)
        cmt = Comment(post=post, user=user, depth=depth, text=text, parent=parent_id)
        cmt.save()
    return redirect("/post/%d" % post_id)

def upvote(request):
    if request.user.is_authenticated:
        tip = request.POST['type']
        obj = request.POST['id']
        if tip == "comment":
            comment = Comment.objects.get(pk=obj)
            if request.user != comment.user and CommentVotes.object.filter(user=request.user, comment=comment).count() == 0:
                comment.upvotes += 1
                comment.save()
        elif tip == "post":
            post = Post.objects.get(pk=obj)
            if request.user != post.user and PostVotes.object.filter(user=request.user, post=post).count() == 0:
                post.upvotes += 1
                post.save()
    return HttpResponse("")


def submit(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'submit.html')
        else:
            url = request.POST['url']
            title = request.POST['title']
            text = request.POST['text']
            p = Post(url=url, title=title, text=text,
                     user=User.objects.get(pk=request.user.id))
            p.save()
            return redirect("/post/%d" % p.id)
    else:
        return redirect("/")

def user(request, username):
    user = User.objects.get(username=username)
    karma = 0
    posts = user.post_set.all()
    if len(posts) > 0:
        karma = sum([x.upvotes*2 for x in posts])
    comments = user.comment_set.all()
    if len(comments) > 0:
        karma += sum([x.upvotes for x in comments])

    return render(request, "user.html", {"usr":user, "karma":karma,
                                         "posts_count": len(posts),
                                         "comments_count": len(comments)})

def post(request, post_id):
    p = Post.objects.get(pk=post_id)
    comments = sorted(p.comment_set.all().order_by("timestamp"), key=lambda x: x.parent)

    # Pretty shitty situation with top level comments
    # Since they all have parent=0 they will be incorrectly grouped
    # in the begining of the list
    nested_comments = {}
    all_comments = []
    for comment in comments:
        nested_comments.setdefault(comment, [])
        if comment.parent == 0:
            all_comments.append(comment)
        for cmt2 in comments:
            if cmt2.parent == comment.id:
                nested_comments[comment].append(cmt2)

    for parent, children in nested_comments.iteritems():
        children.reverse()
        for child in children:
            all_comments.insert(all_comments.index(parent)+1, child)
                
    c = {}
    c.update(csrf(request))
    c['post'] = p
    c['comments'] = all_comments
    return render(request, 'post.html', c)

def newcomments(request):
    comments = Comment.objects.order_by('-timestamp')[:50]
    return render(request, "comments.html", {"comments":comments})

def new(request):
    posts = Post.objects.order_by('-timestamp')[:50]
    return render(request, 'posts.html', {"posts": posts})
