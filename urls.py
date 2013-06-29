from django.conf.urls import patterns, include, url
from agora.feed import LatestEntriesFeed

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'agora.views.home', name='home'),
    url(r"^newcomments", "agora.views.newcomments", name="newcomments"),
    url(r"^new", "agora.views.new", name="new"),
    url(r"^post/(?P<post_id>\d+)", "agora.views.post", name="post"),
    url(r"^user/(?P<username>\w+)", "agora.views.user", name="user"),
    url(r"^login", "agora.views.login", name="login"),
    url(r"^register", "agora.views.register", name="register"),
    url(r"^submit", "agora.views.submit", name="submit"),
    url(r"^comment", "agora.views.comment", name="comment"),
    url(r"^upvote", "agora.views.upvote", name="upvote"),
    url(r"^downvote", "agora.views.downvote", name="downvote"),

    url(r"^faq", "agora.views.faq", name="faq"),
    url(r"^featreq", "agora.views.featreq", name="featreq"),
    url(r"^guidelines", "agora.views.guidelines", name="guidelines"),
    url(r"^rss", LatestEntriesFeed()),
    url(r"^lists", "agora.lists.main", name="lists"),
    url(r"^notifications/read-all", "agora.views.read_all"),

    # Examples:
    # url(r'^$', 'haknews.views.home', name='home'),
    # url(r'^haknews/', include('haknews.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
