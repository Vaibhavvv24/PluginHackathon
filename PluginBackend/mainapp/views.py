from django.shortcuts import render
from mainapp.models import User, Report, VideoAudio
from mainapp.serializers import UserSerializer, ReportSerializer, VideoAudioSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpRequest
from ML_Models.speech_to_text import process_audio
# from ML_Models.Grammer import process_text_file
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
    TokenVerifyView
)
from mainapp.serializers import CustomTokenObtainPairSerializer
import sys
import os
from gramformer import Gramformer
import re

# # Add the ML_Models directory to the Python path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ML_Models')))
from ML_Models.speech_to_text import process_audio

gf = Gramformer(models=1, use_gpu=False)

def correct_sentence_with_error_count(sentence):
    """
    Correct a sentence and count the errors.

    Args:
        gf (Gramformer): Initialized Gramformer model.
        sentence (str): Original sentence to correct.

    Returns:
        tuple: (corrected_sentence, error_count, error_details)
    """
    corrections = list(gf.correct(sentence))
    corrected_sentence = corrections[0] if corrections else sentence
    # error_count, error_details = count_errors(sentence, corrected_sentence)
    
    # return corrected_sentence, error_count, error_details
    return corrected_sentence

def process_text_file(incorrect:list[str]):
    """
    Process a text file, calculate grammar errors, and save the corrected output.

    Args:
        file_path (str): Path to the input text file.
        output_path (str): Path to save the corrected output file.

    Returns:
        dict: A dictionary with error count, total sentences, and grammar score.
    """
    # if not os.path.exists(file_path):
    #     raise FileNotFoundError(f"File '{file_path}' does not exist.")

    # with open(file_path, "r", encoding="utf-8") as file:
    #     lines = file.readlines()

    corrected_sentences = []
    total_sentences = 0
    total_errors = 0
    all_error_details = []

    # Process each sentence
    for line in incorrect:
        # Split on punctuation (periods, exclamation marks, question marks) and new lines
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|\n)', line.strip())
        for sentence in sentences:
            if sentence.strip():  # Ignore empty sentences
                total_sentences += 1
                corrected= correct_sentence_with_error_count(sentence.strip())
                corrected_sentences.append(corrected)
                # total_errors += errors
                # all_error_details.extend(error_details)

    # # Save corrected sentences to output file
    # with open(output_path, "w", encoding="utf-8") as file:
    #     file.write("\n".join(corrected_sentences))

    # Return the results
    return {
        "total_sentences": total_sentences,
        "total_errors": total_errors,
        "grammar_score": total_errors,  # Number of errors as grammar score
        # "output_file": output_path,
        "error_details": all_error_details,
        "corrected_sentences": corrected_sentences
    }

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
                'message': f"User with email = {request.POST.get('user_email')} does not exist."
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
        
@api_view(['GET'])
def get_Analysis(request: HttpRequest) -> Response:
    """
    To get the detailed report.
    """
    if request.method == 'GET':
        """
        id: query url param
        """
        try:
            video_audio = VideoAudio.objects.get(id=request.GET.get('id'))
            text_of_speech = process_audio(video_audio.audio_file.path)
            text_of_speech_refined = text_of_speech.strip().split('.')
            print(text_of_speech_refined)
            grammar_Maal = process_text_file(text_of_speech_refined)
            return Response({
                'grammer_Maal': grammar_Maal
            })
        except VideoAudio.DoesNotExist:
            return Response({
                'message': f"Video audio with ID = {request.GET.get('id')} does not exist."
            })
    else:
        return Response({
            'message': f'Expected GET request but got {request.method}.'
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
                'message': f"User with email = {request.GET.get('user_email')} does not exist."
            })

def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>HOME</h1>")