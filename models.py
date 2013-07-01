from django.db import models
from django.contrib.auth.models import User

class BaseItem(models.Model):
    """Abstract class holding common fields."""
    # Amount of upvotes
    upvotes = models.IntegerField(db_index=True, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    class Meta:
        abstract = True

class Post(BaseItem):
    title = models.TextField(db_index=True)
    url = models.URLField(default='')
    # XXX Should this or shouldn't be indexed.
    text = models.TextField(default='', db_index=True)

class Question(BaseItem):
    title = models.TextField(db_index=True)
    # XXX Should this or shouldn't be indexed.
    text = models.TextField(default='', db_index=True)

class Comment(BaseItem):
    post = models.ForeignKey(Post, db_index=True)
    text = models.TextField(default='')
    depth = models.IntegerField(default=0)
    parent = models.IntegerField(default=0, db_index=True)

class Karma(BaseItem):
    # This is the most complex item as it implements users karma
    # How many posts/comments he did daily, in average.
    activity = models.FloatField(default=0.0)

class CommentVotes(models.Model):
    user = models.ForeignKey(User)
    comment = models.ForeignKey(Comment)
    is_positive = models.BooleanField(default=True)

class PostVotes(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    is_positive = models.BooleanField(default=True)
