from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Song, Session, SessionSong, SongRequest, SongCandidate
from .serializers import SessionSerializer, SessionSongSerializer
from .tasks import gen_candidate_songs, create_request_from_apple 

import operator

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello World</h1>")

class SessionSongList(APIView):

    def get(self, request, identifier):
        session = Session.objects.get(identifier=identifier)

        requested_count = int(request.GET.get('count'))
        true_count = SessionSong.objects.filter(session=session).count()

        # Start asynchronously generating candidate songs
        if true_count < requested_count - 1:
            gen_candidate_songs.delay(identifier)
        
        # Add new songs until the playlist length is equal to count
        if true_count < requested_count:
            print(requested_count - true_count)
            finalizeCandidates(identifier, requested_count - true_count)
            session = Session.objects.get(identifier=identifier)

        serializer = SessionSerializer(session)

        return Response(serializer.data)

    def post(self, request, identifier):
        apple_id = request.data.get('apple_id')

        song = Song.objects.filter(apple_id=apple_id).first()

        if song is None:
            # Add a song from an itunes lookup
            create_request_from_apple.delay(apple_id, identifier)
            print('song is not found')

            return Response("delayed creation", status=status.HTTP_201_CREATED)
        
        # Add a SongRequest object to later be considered by the AI

        song_request = SongRequest()
        song_request.session = Session.objects.get(identifier=identifier)
        song_request.song = song 
        
        song_request.save()
        
        # Depending upon some set of parameters, flag a song for re-analysis

        return Response("success", status=status.HTTP_201_CREATED)

def finalizeCandidates(identifier, needed_count):
    session = Session.objects.get(identifier=identifier)
    
    candidates = SongCandidate.objects.filter(session=session)

    grouped_candidates = {} 

    for r in candidates:
        if r.song not in grouped_candidates:
            grouped_candidates[r.song] = 1
        else:
            grouped_candidates[r.song] += 1 
        
    for i in range(needed_count):
        if grouped_candidates:
            max_request = max(grouped_candidates.iteritems(), key=operator.itemgetter(1))[0]

            addRequest(max_request, session)

            SongCandidate.objects.filter(session=session, song=max_request).delete() 

def addRequest(song, session):
    session_song = SessionSong()

    session_song.session = session
    session_song.song = song

    session_song.save()
