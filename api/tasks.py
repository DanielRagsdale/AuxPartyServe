from __future__ import absolute_import, unicode_literals
from celery import Celery, shared_task
from .models import Song, SongRequest, SongCandidate, Session
import requests

@shared_task
def gen_candidate_songs(session_identifier):
    session = Session.objects.get(identifier=session_identifier)

    candidate = SongCandidate()

    first_requested = SongRequest.objects.filter(session=session, is_fulfilled=False).first()

    if first_requested is None:
        return False

    candidate.session = session
    candidate.song = first_requested.song
    candidate.save()

    first_requested.is_fulfilled = True
    first_requested.save()

    return True 
   
@shared_task
def create_request_from_apple(apple_id, session_identifier):
    r = requests.get('https://itunes.apple.com/lookup', params={'id':apple_id})
    
    session = Session.objects.get(identifier=session_identifier)

    song = Song()

    print(r.json())
    print('*************')

    results = r.json().get('results')
    if len(results) > 0:
        title = results[0].get('trackName')
        artist = results[0].get('artistName')
    else:
        print('Song not found!!: ' + str(apple_id))
        return 1

    song.title = title
    song.artist = artist
    song.apple_id = apple_id

    song.save()

    song_request = SongRequest()
    song_request.session = session
    song_request.song = song
    
    song_request.save()

    return 0
