from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from .models import Song, Session, SessionSong, SongRequest, SongCandidate
from .serializers import SessionSerializer, SessionSongSerializer, SessionNameSerializer
from .tasks import gen_candidate_songs, create_request_from_apple 

import operator
import string
import random

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello World</h1>")

def getName(request, identifier):
    identifier = identifier.upper()
    
    session = Session.objects.filter(identifier=identifier).first()

    if session is None:
        return HttpResponse("{ \"does_exist\":false } ")

    json = JSONRenderer().render({"does_exist":True, "user_name":session.user_name, "identifier":identifier })

    return HttpResponse(json) 

class NeutralPlaying(APIView):

    def get(self, request, identifier):
        session = Session.objects.get(identifier=identifier)
        song = session.now_playing

        return Response({"apple_id":song.apple_id, "is_closed":session.is_closed})

    def post(self, request, identifier):
        identifier = identifier.upper()

        session = Session.objects.get(identifier=identifier)

        now_playing = Song.objects.get(apple_id=request.data.get("apple_id"))
        session.now_playing = now_playing

        session.save()

        return Response("playing song set")

class ClientRequest(APIView):
    
    def get(self, request, identifier):
        return Response("POST to request song")

    def post(self, request, identifier):
        identifier = identifier.upper()

        apple_id = request.data.get('apple_id')
        session = Session.objects.get(identifier=identifier)
        song = Song.objects.filter(apple_id=apple_id).first()

        if session.is_closed:
            return Response("Session is Closed", status=status.HTTP_200_OK)

        if song is None:
            # Add a song from an itunes lookup
            create_request_from_apple.delay(apple_id, identifier)
            print('song is not found')

            return Response("delayed creation", status=status.HTTP_201_CREATED)
        
        # Add a SongRequest object to later be considered by the AI

        song_request = SongRequest()
        song_request.session = session 
        song_request.song = song 
        
        song_request.save()
        
        # Depending upon some set of parameters, flag a song for re-analysis

        return Response("success", status=status.HTTP_201_CREATED)


class HostClose(APIView):
    
    def get(self, request, identifier):
        identifier = identifier.upper()
        session = Session.objects.get(identifier=identifier)

        if session.is_closed:
            return Response({'status':'closed'})
        else:
            return Response({'status':'open'})

    def post(self, request, identifier):
        identifier = identifier.upper()
        session = Session.objects.get(identifier=identifier)


        if request.data.get('key') == toKey(identifier):
            session.is_closed = True
            session.save()
        else:
            return Response("You do not have permission to close this session", status=status.HTTP_403_FORBIDDEN)

        return Response("Feature closed")

class SessionCreate(APIView):
    
    def get(self, request):
        
        return Response("No data to show. Submit a post request to create a session")

    def post(self, request):
        # Create a session with user_name and unique identifier 
        user_name = request.data.get('user_name')
        
        identifier = False
        while not identifier:
            identifier =  tryCreateSession(user_name)

        return Response({
            'identifier': identifier,
            'key': toKey(identifier)})

class SessionSongList(APIView):

    def get(self, request, identifier):
        identifier = identifier.upper()
        
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
        return Response("GET to receive playlist")

# Helper functions

def toKey(identifier):
    key = ''
    for c in identifier:
        key += str(ord(c))
    
    return key

def generateID(size=5, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

def tryCreateSession(user_name):
    identifier = generateID()
    
    try:
        sess = Session()
        sess.identifier = identifier 
        sess.user_name = user_name
        sess.save()
    except IntegrityError:
        return False

    return identifier

def finalizeCandidates(identifier, needed_count):
    session = Session.objects.get(identifier=identifier)
    
    candidates = SongCandidate.objects.filter(session=session)

    grouped_candidates = {} 

    for r in candidates:
        if r.song not in grouped_candidates:
            grouped_candidates[r.song] = 1
        else:
            grouped_candidates[r.song] += 1 
       
    if grouped_candidates:
        max_request = max(grouped_candidates.iteritems(), key=operator.itemgetter(1))[0]

        addRequest(max_request, session)

        SongCandidate.objects.filter(session=session, song=max_request).delete() 

    if needed_count > 1:
        finalizeCandidates(identifier, needed_count - 1)

def addRequest(song, session):
    session_song = SessionSong()

    session_song.session = session
    session_song.song = song

    session_song.save()
