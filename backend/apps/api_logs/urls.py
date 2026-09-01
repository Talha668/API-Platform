from django.urls import path
from . import views



urlpatterns = [
    # Request logs
    path('projects/<int:project_id>/logs/',
         views.RequestLogListView.as_view(),
         name='request-logs'),
    
    # Analytics
    path('projects/<int:project_id>/analytics/',
         views.ProjectAnalyticsView.as_view(),
         name='project-analytics'),
    
    path('projects/<int:project_id>/apis/<slug:api_slug>/analytics/',
         views.APIAnalyticsView.as_view(),
         name='api-analytics'),
]