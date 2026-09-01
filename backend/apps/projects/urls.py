from django.urls import path
from . import views


urlpatterns = [
    path('', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:id>/', views.ProjectDetailView.as_view(), name='project-detail'),
]