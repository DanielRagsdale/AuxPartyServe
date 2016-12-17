from django.contrib import admin
from .models import Session, SessionSong, Song, SongRequest, SongCandidate

# Register your models here.
admin.site.register(Session)
admin.site.register(SessionSong)
admin.site.register(Song)
admin.site.register(SongRequest)
admin.site.register(SongCandidate)
