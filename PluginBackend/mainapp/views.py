from django.shortcuts import render
from mainapp.models import User, Report, VideoAudio
from mainapp.serializers import UserSerializer, ReportSerializer, VideoAudioSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpRequest
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
    TokenVerifyView
)
from mainapp.serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def user_Post(request: HttpRequest) -> Response:
    """
    Request JSON body (form data):
    {
        "email": email,
        "username": username,
        "password": password
    }
    """
    if request.method == 'POST':
        data = request.data
        try:
            serializer = UserSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                    'error': serializer.errors
                })
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            serializer.save()
            return Response({
                'message': 'User created successfully.'
            })
        except Exception as e:
            return Response({
                'error': e
            })
    else:
        return Response({
            'message': f'Only POST request allowed but got {request.method}.'
        })

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_Get_Delete(request: HttpRequest) -> Response:
    if request.method == 'GET':
        """
        Query parameters:
        email
        """
        email = request.GET.get('email', None)
        if email is None:
            return Response({
                'message': 'Email is None.'
            })
        try:
            user = User.objects.get(email=email)
            user_serializer = UserSerializer(user)
            return Response({
                'user': user_serializer.data
            })
        except User.DoesNotExist:
            return Response({
                'message': f'User with email = {email} does not exist.'
            })
    elif request.method == 'DELETE':
        """
        Request JSON body:
        email
        """
        email = request.data.get('email')
        if email is None:
            return Response({
                'message': 'Email is None.'
            })
        try:
            user = User.objects.get(email=email)
            user.delete()
            return Response({
                'message': 'User deleted successfully.'
            })
        except User.DoesNotExist:
            return Response({
                'message': f'User with email = {email} does not exist.'
            })
        except Exception as e:
            return Response({
                'error': e
            })
    else:
        return Response({
            'message': f'Allowed request methods are GET AND DELETE but got {request.method}.'
        })

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def video_audio_CRUD(request: HttpRequest) -> Response:
    if request.method == 'POST':
        """
        form data:
        {
            title,
            video_file,
            audio_file,
            user_email
        }
        """
        try:
            user = User.objects.get(email=request.POST.get('user_email'))
            video_audio = VideoAudio.objects.create(
                title=request.POST.get('title'),
                video_file=request.FILES.get('video_file'),
                audio_file=request.FILES.get('audio_file'),
                user=user
            )
            serializer = VideoAudioSerializer(video_audio)
            return Response({
                'saved': serializer.data
            })
        except User.DoesNotExist:
            return Response({
                'message': f'User with email = {request.POST.get('user_email')} does not exist.'
            })
        except Exception as e:
            return Response({
                'error': f'{e}'
            })
    if request.method == 'GET':
        """
        It is a GET query parameter.
        id
        """
        try:
            id = request.GET.get('id')
            video_audio = VideoAudio.objects.get(id=id)
            serializer = VideoAudioSerializer(video_audio)
            return Response({
                'message': serializer.data
            })
        except VideoAudio.DoesNotExist:
            return Response({
                'message': f'Video audio with ID = {id} does not exist.'
            })
        except Exception as e:
            return Response({
                'error': f'{e}'
            })
    if request.method == 'PUT':
        """
        raw JSON data:
        {
            title,
            video_file,
            audio_file,
            video_audio_id
        }
        """
        try:
            video_audio = VideoAudio.objects.get('video_audio_id')
            video_audio.video_file = request.FILES.get('video_file')
            video_audio.audio_file = request.FILES.get('audio_file')
            video_audio.save()
            serializer = VideoAudioSerializer(video_audio)
            return Response({
                'updated': serializer.data
            })
        except User.DoesNotExist:
            return Response({
                'message': f'User with ID = {id} does not exist.'
            })
        except VideoAudio.DoesNotExist:
            return Response({
                'message': f'Video audo with ID = {id} does not exist.'
            })
        except Exception as e:
            return Response({
                'error': f'{e}'
            })
        
@api_view(['POST', 'GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_history(request: HttpRequest) -> Response:
    if request.method == 'GET':
        """
        GET query url parameter:
        user_email
        """
        try:
            user = User.objects.get(email=request.GET.get('user_email'))
            reports = Report.objects.get(user=user)
            report_serializer = ReportSerializer(reports, many=True)
            return Response({
                'reports': report_serializer.data
            })
        except User.DoesNotExist:
            return Response({
                'message': f'User with email = {request.GET.get('user_email')} does not exist.'
            })

def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>HOME</h1>")