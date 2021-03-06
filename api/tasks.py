from __future__ import absolute_import, unicode_literals
from celery import Celery, shared_task
from .models import Song, SongRequest, SongCandidate, Session, Service
import requests

@shared_task
def gen_candidate_songs(session_identifier):
    session = Session.objects.get(identifier=session_identifier)

    requested = SongRequest.objects.filter(session=session, is_fulfilled=False)

    # Add fallback candidates if there have been no song requests
    if requested is None:
        return False

    for r in requested:
        candidate = SongCandidate()

        candidate.session = session
        candidate.song = r.song
        candidate.save()

        r.is_fulfilled = True
        r.save()

    return True 

@shared_task
def create_request_from_spotify(spotify_id, session_identifier):
    r = requests.get('https://api.spotify.com/v1/tracks/' + spotify_id)

    session = Session.objects.get(identifier=session_identifier)
    service = Service.objects.get(name='spotify')

    song = Song()

    song.title = r.json().get('name')
    song.artist = r.json().get('artists')[0].get('name')

    song.play_id = spotify_id
    song.service = service

    song.save()

    song_request = SongRequest()
    song_request.session = session
    song_request.song = song

    song_request.save()

    return 0

@shared_task
def create_request_from_apple(apple_id, session_identifier):
    r = requests.get('https://itunes.apple.com/lookup', params={'id':apple_id})
   
    print(r.json())
    
    session = Session.objects.get(identifier=session_identifier)
    service = Service.objects.get(name='apple_music')

    song = Song()

    results = r.json().get('results')
    if len(results) > 0:
        song.title = results[0].get('trackName')
        song.artist = results[0].get('artistName')
    else:
        print('Song not found!!: ' + str(apple_id))
        return 1

    song.play_id = apple_id
    song.service = service

    song.save()

    song_request = SongRequest()
    song_request.session = session
    song_request.song = song
    
    song_request.save()

    return 0
