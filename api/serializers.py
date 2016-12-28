from rest_framework import serializers
from api.models import Session, Song, SessionSong

class SongSerializer(serializers.ModelSerializer):

    class Meta:
        model = Song
        fields = ('title', 'apple_id')

class SessionSongSerializer(serializers.ModelSerializer):

    song = SongSerializer(many=False, read_only=True) 
    
    class Meta:
        model = SessionSong
        fields = ('add_time', 'song',)

class SessionSerializer(serializers.ModelSerializer):

    tracks = SessionSongSerializer(many=True, read_only=True) 

    class Meta:
        model = Session
        fields = ('user_name', 'identifier', 'tracks')

class SessionNameSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Session
        fields = ('user_name', 'identifier')
