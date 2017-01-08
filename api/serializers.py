from rest_framework import serializers
from api.models import Session, Song, SessionSong, Service

class SongSerializer(serializers.ModelSerializer):

    class Meta:
        model = Song
        fields = ('title', 'apple_id')

class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ('name',)

class SessionSongSerializer(serializers.ModelSerializer):

    song = SongSerializer(many=False, read_only=True) 
    
    class Meta:
        model = SessionSong
        fields = ('add_time', 'song',)

class SessionSerializer(serializers.ModelSerializer):

    tracks = SessionSongSerializer(many=True, read_only=True) 
    service_name = serializers.ReadOnlyField()

    class Meta:
        model = Session
        fields = ('user_name', 'identifier', 'service_name', 'tracks')

class SessionNameSerializer(serializers.ModelSerializer):
    
    does_exist = True

    class Meta:
        model = Session
        fields = ('user_name', 'identifier', 'does_exist')
