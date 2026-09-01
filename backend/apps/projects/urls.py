from django.urls import path
from . import views


urlpatterns = [
    # CRUD endpoints
    path('', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:id>/', views.ProjectDetailView.as_view(), name='project-detail'),

    # Usage and analytics endpoints
    path('<int:id>/usage/', views.ProjectUsageView.as_view(), name='project-usage'),
    path('<int:id>/rate-limit/', views.ProjectRateLimitView.as_view(), name='project-rate-limit'),
]