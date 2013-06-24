# Create your views here.
from datetime import date, timedelta
from urlparse import urlparse
# from urlparse import urlparse

from django.shortcuts import render, redirect
from django.contrib.auth import login as lin, authenticate, logout as lg
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import HttpResponse
from agora.models import Karma, Post, Comment, CommentVotes, PostVotes

today = date.today()
posts_limit = today - timedelta(days=3)

def main(request):
    return render(request, "faq.html")
