from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Song, Session, SessionSong, SongRequest
from .serializers import SessionSerializer, SessionSongSerializer

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello World</h1>")

class SessionSongList(APIView):

    def get(self, request, identifier):
        songs = Session.objects.get(identifier=identifier)
        serializer = SessionSerializer(songs)
        return Response(serializer.data)

    def post(self, request, identifier):
        print(request.data)
        print(type(request.data))
        print(request.data.get("add_time")) 

        session_song = SessionSong()
        session_song.session = Session.objects.get(identifier=identifier)
        session_song.song = Song.objects.get(apple_id=request.data.get('apple_id'))
        
        session_song.save()

        song_request = SongRequest()
        song_request.session = Session.objects.get(identifier=identifier)
        song_request.song = Song.objects.get(apple_id=request.data.get('apple_id'))
        
        song_request.save()

        return Response("success", status=status.HTTP_201_CREATED)
