from django.urls import path
from . import views


urlpatterns = [
    path('projects/<int:project_id>/rate-limit/',
         views.RateLimitStatusView.as_view(),
         name='rate-limit-status'),
         
    path('projects/<int:project_id>/rate-limit/reset/',
         views.RateLimitResetView.as_view(),
         name='rate-limit-reset'),
]