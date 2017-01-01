from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'api'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    
    url(r'host/close/(?P<identifier>[\w]+)', views.HostClose.as_view()),
    url(r'host/create$', views.SessionCreate.as_view()),
    url(r'host/data/(?P<identifier>[\w]+)', views.SessionSongList.as_view()),
   
    url(r'client/name/(?P<identifier>[\w]+)', views.getName, name='get_name'),
    url(r'client/request/(?P<identifier>[\w]+)', views.ClientRequest.as_view()),

    url(r'neutral/nowplaying/(?P<identifier>[\w]+)', views.NeutralPlaying.as_view()),

]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
