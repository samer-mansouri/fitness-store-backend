from django.urls import path
from .views import UserRegisterView, UserLoginView, UserLogoutView
from rest_framework_simplejwt import views as jwt_views

app_name = 'users'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]