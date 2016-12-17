from __future__ import unicode_literals

from django.db import models
import datetime

# Create your models here.
class Song(models.Model):
    title = models.CharField(max_length=250)
    artist = models.CharField(max_length=250)

    apple_id = models.CharField(max_length=250)

    def __str__(self):
        return self.title

class Session(models.Model):
    create_date = models.DateTimeField() 
    identifier = models.CharField(unique=True, max_length=5)

    def __str__(self):
        return self.identifier
        
class SessionSong(models.Model):
    session = models.ForeignKey(Session, related_name='tracks', on_delete=models.CASCADE)
    song = models.ForeignKey(Song, related_name='song_serial', on_delete=models.CASCADE)

    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['add_time']

    def __str__(self):
        return self.song.title + self.session.identifier

class SongRequest(models.Model):
    session = models.ForeignKey(Session, related_name='song_requests', on_delete=models.CASCADE)
    song = models.ForeignKey(Song, related_name='requested_songs', on_delete=models.CASCADE)
    hype_value = models.FloatField(default=0.5) 

    is_fulfilled = models.BooleanField(default=False)

    request_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.song.title + self.session.identifier

class SongCandidate(models.Model):
    session = models.ForeignKey(Session, related_name='candidate_session', on_delete=models.CASCADE)
    song = models.ForeignKey(Song, related_name='candidate_songs', on_delete=models.CASCADE)

    def __str__(self):
        return self.song.title + self.session.identifier
