from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Song, Session, SessionSong, SongRequest, SongCandidate
from .serializers import SessionSerializer, SessionSongSerializer
from .tasks import gen_candidate_songs, create_request_from_apple 

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello World</h1>")

class SessionSongList(APIView):

    def get(self, request, identifier):
        
        session = Session.objects.get(identifier=identifier)
       
        if SessionSong.objects.filter(session=session).count() < int(request.GET.get('count')) - 1:
            # Start asynchronously generating candidate songs
            gen_candidate_songs.delay(identifier)
        
        if SessionSong.objects.filter(session=session).count() < int(request.GET.get('count')):
            print('Less Than')
            finalizeCandidates(identifier, 1)
            # Add new songs until the playlist length is equal to count
    
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
    candidates = SongCandidate.objects.filter(session=Session.objects.get(identifier=identifier))

    print(candidates)

    for r in candidates:
        addRequest(r)
        r.delete()

def addRequest(request):
    session_song = SessionSong()

    session_song.session = request.session
    session_song.song = request.song

    session_song.save()








