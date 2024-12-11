from rest_framework import serializers
from .models import VideoAudio, User, Report
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add the user's email to the response
        data['email'] = self.user.email
        
        return data

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
        depth = 2