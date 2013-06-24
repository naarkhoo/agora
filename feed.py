from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from agora.models import Post
from agora.views import post

class LatestEntriesFeed(Feed):
    title = "Hack news feed"
    link = "/new/"
    description = "Updates on changes and additions to hack news"

    def items(self):
        return Post.objects.order_by('-timestamp')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.text

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        # return reverse(post, args=[item.pk])
        return "http://23.21.240.209:3000/post/%d" % item.pk

    def link(self):
        return "http://23.21.240.209:3000"
