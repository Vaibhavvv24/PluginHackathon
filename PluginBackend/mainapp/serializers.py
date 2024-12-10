from rest_framework import serializers
from .models import VideoAudio, User, UserHistory, Report

class VideoAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoAudio
        fields = '__all__'
        depth = 1

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
        depth = 1

class UserHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHistory
        fields = '__all__'
        depth = 2