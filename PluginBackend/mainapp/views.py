from django.shortcuts import render
from mainapp.models import User, UserHistory, Report, VideoAudio
from mainapp.serializers import UserSerializer, UserHistorySerializer, ReportSerializer, VideoAudioSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse, HttpRequest

# Create your views here.

@api_view(['POST', 'GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def users(request: HttpRequest) -> Response:
    """"""

def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>HOME<\h1>")