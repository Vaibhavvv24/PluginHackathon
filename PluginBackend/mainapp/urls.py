from django.contrib import admin
from django.urls import path
from mainapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework.authtoken import views as auth_Token_Views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
    TokenVerifyView
)
 
urlpatterns = [
    path('', view=views.home),
    path('token/', view=views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api-token-auth', view=auth_Token_Views.obtain_auth_token),
    path('register-user/', view=views.user_Post, name='register_user'),
    path('user-get-delete/', view=views.user_Get_Delete, name='user_get_delete'),
    path('video-audio/', view=views.video_audio_CRUD, name='video_audio'),
    path('user-history/', view=views.user_history, name='user_history'),
    path('report/', view=views.get_Analysis, name='get_analysis'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)