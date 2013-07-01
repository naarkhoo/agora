# -*- coding: utf-8 -*-
# Create your views here.
from datetime import date, timedelta, datetime
from urlparse import urlparse
import re
# from urlparse import urlparse

from django.shortcuts import render, redirect
from django.contrib.auth import login as lin, authenticate, logout as lg
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.humanize.templatetags.humanize import naturaltime

from notifications import notify
from notifications.models import Notification
from agora.models import Karma, Post, Comment, CommentVotes, PostVotes

today = date.today()
posts_limit = today - timedelta(days=3)


def set_language(view):
    def wrapped(*args, **kwargs):
        args[0].session['django_language'] = 'ar'
        return view(*args, **kwargs)
    return wrapped

def check_url(url):
    """
    Checks if url has http in front of it, and if not adds it.
    """
    if urlparse(url).scheme == '':
        return 'http://' + url
    else:
        return url

@set_language
def home(request):
    global today
    global posts_limit
    if date.today() != today:

        today = date.today()
        posts_limit = today - timedelta(days=3)
    posts = Post.objects.filter(timestamp__gte=posts_limit).order_by('upvotes')[:50]

    for i in range(1, len(posts) + 1):
        setattr(posts[i-1], "number", i)
    return render(request, 'posts.html', {"posts":posts, "today":today })

@set_language
def faq(request):
    return render(request, 'faq.html')

@set_language
def guidelines(request):
    return render(request, 'guidelines.html')

@set_language
def featreq(request):
    return post(request, 2)

@set_language
def login(request):
    if request.user.is_authenticated():
        return home(request)
    elif request.method == 'GET':
        c = {}
        c.update(csrf(request))
        return render(request, 'login.html', c)
    else:
        # This is done quite stupid
        username = request.POST['name']
        password = request.POST['pass']
        user = authenticate(username=username, password=password)
        lin(request, user)
        return redirect("/")


@set_language
def logout(request):
    lg(request)
    return redirect("/")

def register(request):
    username = request.POST['name']
    password = request.POST['pass']
    user = User.objects.create_user(username=username, password=password)
    user.save()
    user = authenticate(username=username, password=password)
    lin(request, user)
    return redirect("/")

@login_required
def comment(request):
    """Adds a comment to a post."""
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

    # Lets see if user called someone
    called = [x[1:] for x in re.findall(r"@[\w\.\+\-\_\@]{1,30}",text,re.L|re.U)]
    if len(called) > 0:
        try:
            called = User.objects.get(username__in=called)
            if isinstance(called, User):
                notify.send(cmt.user, recipient=called, verb=u'called you',
                            action_object=cmt, target=post)
            else:
                for u in called:
                    notify.send(cmt.user, recipient=u, verb=u'called you',
                                action_object=cmt, target=post)
        except ObjectDoesNotExist:
            pass

    # Lets notify OP and commenters
    notified = set()  # A set of those who should be informed
    obj = cmt
    while obj.parent != 0:
        parent = Comment.objects.get(pk=obj.parent)
        obj = parent
        notified.add(obj.user)
    if cmt.user in notified:
        notified.remove(cmt.user)
    for user in notified:
        notify.send(cmt.user, recipient=user, verb=u'also commented',
                    action_object=cmt, target=post)

    if post.user not in notified and post.user != cmt.user:
        notify.send(cmt.user, recipient=post.user, verb=u'commented',
                    action_object=cmt, target=post)


    return redirect("/post/%d" % post_id)

@login_required
def upvote(request):
    tip = request.POST['type']
    obj = request.POST['id']
    if tip == "comment":
        comment = Comment.objects.get(pk=obj)
        if request.user != comment.user and CommentVotes.objects.filter(user=request.user, comment=comment).count() == 0:
            comment.upvotes += 1
            comment.save()
            CommentVotes(user=request.user, comment=comment).save()
        result = str(comment.upvotes)
    elif tip == "post":
        post = Post.objects.get(pk=obj)
        if request.user != post.user and PostVotes.objects.filter(user=request.user, post=post).count() == 0:
            post.upvotes += 1
            post.save()
            PostVotes(user=request.user, post=post).save()
        result = str(post.upvotes)
    return HttpResponse(result)

@login_required
def downvote(request):
    tip = request.POST['type']
    obj = request.POST['id']
    if tip == "comment":
        comment = Comment.objects.get(pk=obj)
        if request.user != comment.user and CommentVotes.objects.filter(user=request.user, comment=comment).count() == 0:
            comment.upvotes -= 1
            comment.save()
            CommentVotes(user=request.user, comment=comment, isPositive=False).save()
        result = str(comment.upvotes)
    elif tip == "post":
        post = Post.objects.get(pk=obj)
        if request.user != post.user and PostVotes.objects.filter(user=request.user, post=post).count() == 0:
            post.upvotes -= 1
            post.save()
            PostVotes(user=request.user, post=post, isPositive=False).save()
        result = str(post.upvotes)
    return HttpResponse(result)

@login_required
def read_all(request):
    request.user.notifications.unread().mark_all_as_read()
    return HttpResponse("Success")

@set_language
@login_required
def submit(request):
    if request.method == 'GET':
        return render(request, 'submit.html')
    else:
        url = request.POST['url']
        url = check_url(url)
        title = request.POST['title']
        text = request.POST['text']
        p = Post(url=url, title=title, text=text,
                 user=User.objects.get(pk=request.user.id))
        p.save()
        return redirect("/post/%d" % p.id)

@set_language
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

@set_language
def post(request, post_id):
    p = Post.objects.get(pk=post_id)
    comments = sorted(p.comment_set.all().order_by("timestamp"), key=lambda x: x.parent)
    # If user came here because of notification, lets mark it as read
    note = request.GET.get('note')
    if note:
        try:
            notification = Notification.objects.get(pk=int(note))
            if request.user.is_authenticated and \
               notification.recipient == request.user:
                notification.mark_as_read()
        except:
            pass

    # Pretty shitty situation with top level comments
    # Since they all have parent=0 they will be incorrectly grouped
    # in the begining of the list
    nested_comments = {}
    all_comments = []
    top_comment_number = 1
    for comment in comments:
        nested_comments.setdefault(comment, [])
        if comment.parent == 0:
            setattr(comment, "number", top_comment_number)
            top_comment_number += 1
            all_comments.append(comment)
        for cmt2 in comments:
            if cmt2.parent == comment.id:
                nested_comments[comment].append(cmt2)

    for parent, children in nested_comments.iteritems():
        children.reverse()
        for child in children:
            all_comments.insert(all_comments.index(parent)+1, child)

    # Lets humanize the dates
    today = datetime.today()
    if today - p.timestamp.replace(tzinfo=None) < timedelta(days=1):
        p.timestamp = naturaltime(p.timestamp)
        p.timestamp = convert_time_to_arabic(p.timestamp)
        # If it was in one day, so did its comments
        for comment in all_comments:
            comment.timestamp = naturaltime(comment.timestamp)
            comment.timestamp = convert_time_to_arabic(comment.timestamp)
    else:
        for comment in all_comments:
            if today - comment.timestamp.replace(tzinfo=None) < timedelta(days=1):
                comment.timestamp = naturaltime(comment.timestamp)
                comment.timestamp = convert_time_to_arabic(comment.timestamp)

    commenters = set()
    for comment in comments:
        commenters.add(comment.user)

    c = {}
    c.update(csrf(request))
    c['post'] = p
    c['comments'] = all_comments
    c['commenters'] = commenters
    return render(request, 'post.html', c)

def convert_time_to_arabic(time):
    # INCEPTION! Need to update the humanization translation I guess
    return time.replace("minutes\ ago", u"دقیقه پیش")\
            .replace("an\ hour\ ago", u"یک ساعت پیش")\
            .replace("hours\ ago", u"ساعت قبل")\
            .replace("a\ minute\ from\ now", u"یک دقیقه از هم اکنون")\
            .replace("minutes\ from\ now", u"دقیقه از هم اکنون")\
            .replace("an\ hour\ from\ now", u"یک ساعت از هم اکنون")\
            .replace("hours\ from\ now", u"ساعت از هم اکنون")\
            .replace("a\ minute\ ago", u"یک دقیقه پیش")\
            .replace("seconds\ ago", u"ثانیه پیش")\
            .replace("now",u"اکنون")
    # return re.sub("minutes\ ago", u"دقیقه پیش",\
    #         re.sub("an\ hour\ ago", u"یک ساعت پیش",\
    #         re.sub("hours\ ago", u"ساعت قبل",\
    #         re.sub("a\ minute\ from\ now", u"یک دقیقه از هم اکنون",\
    #         re.sub("minutes\ from\ now", u"دقیقه از هم اکنون",\
    #         re.sub("an\ hour\ from\ now", u"یک ساعت از هم اکنون",\
    #         re.sub("hours\ from\ now", u"ساعت از هم اکنون",\
    #         re.sub("a\ minute\ ago", u"یک دقیقه پیش",\
    #               re.sub("seconds\ ago", u"ثانیه پیش",\
    #                     re.sub("now",u"اکنون",time))))))))))

@set_language
def newcomments(request):
    comments = Comment.objects.order_by('-timestamp')[:50]
    return render(request, "comments.html", {"comments":comments})

@set_language
def new(request):
    posts = Post.objects.order_by('-timestamp')[:50]
    for i in range(1, len(posts) + 1):
        setattr(posts[i-1], "number", i)
    return render(request, 'posts.html', {"posts": posts})
