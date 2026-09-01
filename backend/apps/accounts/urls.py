from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', views.RefreshTokenView.as_view(), name='token_refresh'),
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
]