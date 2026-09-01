from django.urls import path
from . import views


urlpatterns = [
    path('projects/<int:project_id>/keys/',
         views.APIKeyListCreateView.as_view(),
         name='api-key-list-create'),
         
    path('projects/<int:project_id>/keys/<int:id>/',
         views.APIKeyDetailView.as_view(),
         name='api-key-detail'),
         
    path('projects/<int:project_id>/keys/<int:id>/regenerate/',
         views.APIKeyRegenerateView.as_view(),
         name='api-key-regenerate'),
]