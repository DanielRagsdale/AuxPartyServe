from django.contrib import admin
from .models import Session, SessionSong, Song, SongRequest

# Register your models here.
admin.site.register(Session)
admin.site.register(SessionSong)
admin.site.register(Song)
admin.site.register(SongRequest)
