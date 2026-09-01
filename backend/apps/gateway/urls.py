from django.urls import path, re_path
from . import views





urlpatterns = [
    # Internal APIs
    path('apis/', views.APIDefinitionListView.as_view(), name='api-definitions'),
    
    # Project API management
    path('projects/<int:project_id>/apis/',
         views.ProjectEnabledAPIsView.as_view(),
         name='project-enabled-apis'),
    
    path('projects/<int:project_id>/apis/enable/',
         views.ProjectAPIEnableView.as_view(),
         name='project-api-enable'),
    
    path('projects/<int:project_id>/apis/<slug:api_slug>/disable/',
         views.ProjectAPIDisableView.as_view(),
         name='project-api-disable'),
]

# External APIs 
external_urlpatterns = [
    # Weather APIs
    path('external/v1/weather', WeatherCurrentView.as_view(), name='weather-current'),
    path('external/v1/weather/forecast', WeatherForecastView.as_view(), name='weather-forecast'),

    # Task APIs
    path('external/v1/tasks', TaskListView.as_view(), name='tasks-list'),
    re_path(r'^external/v1/tasks/(?P<id>\d+)$', TaskDetailView.as_view(), name='task-detail'),

    # Currency APIs
    path('external/v1/currencies', CurrencyListView.as_view(), name='currencies-list'),
    path('external/v1/exchange-rates', ExchangeRateView.as_view(), name='exchange-rates'),
]


# Combine urlspatterns
urlpatterns += external_urlpatterns