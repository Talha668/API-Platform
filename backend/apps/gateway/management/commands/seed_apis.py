from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.gateway.models import APICategory, APIDefinition


class Command(BaseCommand):
    help = 'Seed the database with predefined APIs'

    def handle(self, *args, **options):
        self.stdout.write('Seeding APIs...')
        
        # Create categories
        categories = {
            'weather': APICategory.objects.create(
                name='Weather',
                slug='weather',
                description='Weather data and forecasts',
                icon='🌤️'
            ),
            'tasks': APICategory.objects.create(
                name='Tasks Management',
                slug='tasks',
                description='Manage tasks and to-dos',
                icon='📋'
            ),
            'currency': APICategory.objects.create(
                name='Currency & Exchange',
                slug='currency',
                description='Currency conversion and exchange rates',
                icon='💰'
            ),
        }
        
        # Define API definitions
        apis = [
            # Weather APIs
            {
                'name': 'Current Weather',
                'slug': 'weather-current',
                'description': 'Get current weather conditions for a location',
                'path': '/v1/weather',
                'method': 'GET',
                'category': categories['weather'],
                'default_rate_limit': 100,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'location': {'type': 'string'},
                        'temperature': {'type': 'number'},
                        'condition': {'type': 'string'},
                        'humidity': {'type': 'number'},
                        'wind_speed': {'type': 'number'},
                        'timestamp': {'type': 'string'}
                    }
                },
                'mock_data': {
                    'location': 'San Francisco, CA',
                    'temperature': 22.5,
                    'condition': 'Partly Cloudy',
                    'humidity': 65,
                    'wind_speed': 12,
                    'timestamp': '2024-01-15T14:30:00Z'
                }
            },
            {
                'name': 'Weather Forecast',
                'slug': 'weather-forecast',
                'description': 'Get 5-day weather forecast',
                'path': '/v1/weather/forecast',
                'method': 'GET',
                'category': categories['weather'],
                'default_rate_limit': 50,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'location': {'type': 'string'},
                        'forecast': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'date': {'type': 'string'},
                                    'high': {'type': 'number'},
                                    'low': {'type': 'number'},
                                    'condition': {'type': 'string'}
                                }
                            }
                        }
                    }
                },
                'mock_data': {
                    'location': 'San Francisco, CA',
                    'forecast': [
                        {'date': '2024-01-16', 'high': 23, 'low': 15, 'condition': 'Sunny'},
                        {'date': '2024-01-17', 'high': 20, 'low': 14, 'condition': 'Partly Cloudy'},
                        {'date': '2024-01-18', 'high': 18, 'low': 12, 'condition': 'Rain'},
                        {'date': '2024-01-19', 'high': 21, 'low': 13, 'condition': 'Cloudy'},
                        {'date': '2024-01-20', 'high': 25, 'low': 16, 'condition': 'Sunny'},
                    ]
                }
            },
            
            # Tasks APIs
            {
                'name': 'List Tasks',
                'slug': 'tasks-list',
                'description': 'List all tasks with optional filtering',
                'path': '/v1/tasks',
                'method': 'GET',
                'category': categories['tasks'],
                'default_rate_limit': 200,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'count': {'type': 'integer'},
                        'results': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'title': {'type': 'string'},
                                    'description': {'type': 'string'},
                                    'status': {'type': 'string', 'enum': ['pending', 'in_progress', 'completed']},
                                    'priority': {'type': 'string', 'enum': ['low', 'medium', 'high']},
                                    'due_date': {'type': 'string'},
                                    'created_at': {'type': 'string'}
                                }
                            }
                        }
                    }
                },
                'mock_data': {
                    'count': 3,
                    'results': [
                        {
                            'id': 1,
                            'title': 'Complete project documentation',
                            'description': 'Write comprehensive API documentation',
                            'status': 'pending',
                            'priority': 'high',
                            'due_date': '2024-01-20',
                            'created_at': '2024-01-10T10:00:00Z'
                        },
                        {
                            'id': 2,
                            'title': 'Review pull requests',
                            'description': 'Review and merge pending PRs',
                            'status': 'in_progress',
                            'priority': 'medium',
                            'due_date': '2024-01-17',
                            'created_at': '2024-01-12T14:30:00Z'
                        },
                        {
                            'id': 3,
                            'title': 'Deploy to production',
                            'description': 'Deploy the latest version to production',
                            'status': 'pending',
                            'priority': 'high',
                            'due_date': '2024-01-25',
                            'created_at': '2024-01-14T09:15:00Z'
                        }
                    ]
                }
            },
            {
                'name': 'Create Task',
                'slug': 'tasks-create',
                'description': 'Create a new task',
                'path': '/v1/tasks',
                'method': 'POST',
                'category': categories['tasks'],
                'default_rate_limit': 50,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'title': {'type': 'string'},
                        'description': {'type': 'string'},
                        'status': {'type': 'string'},
                        'created_at': {'type': 'string'}
                    }
                },
                'mock_data': {
                    'id': 4,
                    'title': 'New task created',
                    'description': 'This task was created via the API',
                    'status': 'pending',
                    'created_at': '2024-01-15T15:30:00Z'
                }
            },
            {
                'name': 'Get Task',
                'slug': 'tasks-detail',
                'description': 'Get details of a specific task',
                'path': '/v1/tasks/{id}',
                'method': 'GET',
                'category': categories['tasks'],
                'default_rate_limit': 100,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'title': {'type': 'string'},
                        'description': {'type': 'string'},
                        'status': {'type': 'string'},
                        'priority': {'type': 'string'},
                        'due_date': {'type': 'string'},
                        'created_at': {'type': 'string'},
                        'updated_at': {'type': 'string'}
                    }
                },
                'mock_data': {
                    'id': 1,
                    'title': 'Complete project documentation',
                    'description': 'Write comprehensive API documentation',
                    'status': 'pending',
                    'priority': 'high',
                    'due_date': '2024-01-20',
                    'created_at': '2024-01-10T10:00:00Z',
                    'updated_at': '2024-01-10T10:00:00Z'
                }
            },
            {
                'name': 'Update Task',
                'slug': 'tasks-update',
                'description': 'Update an existing task',
                'path': '/v1/tasks/{id}',
                'method': 'PUT',
                'category': categories['tasks'],
                'default_rate_limit': 50,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'title': {'type': 'string'},
                        'status': {'type': 'string'},
                        'updated_at': {'type': 'string'}
                    }
                },
                'mock_data': {
                    'id': 1,
                    'title': 'Updated task title',
                    'status': 'in_progress',
                    'updated_at': '2024-01-15T16:00:00Z'
                }
            },
            {
                'name': 'Delete Task',
                'slug': 'tasks-delete',
                'description': 'Delete a specific task',
                'path': '/v1/tasks/{id}',
                'method': 'DELETE',
                'category': categories['tasks'],
                'default_rate_limit': 30,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'deleted_id': {'type': 'integer'}
                    }
                },
                'mock_data': {
                    'message': 'Task deleted successfully',
                    'deleted_id': 1
                }
            },
            
            # Currency APIs
            {
                'name': 'List Currencies',
                'slug': 'currencies-list',
                'description': 'Get list of all available currencies',
                'path': '/v1/currencies',
                'method': 'GET',
                'category': categories['currency'],
                'default_rate_limit': 150,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'count': {'type': 'integer'},
                        'results': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'code': {'type': 'string'},
                                    'name': {'type': 'string'},
                                    'symbol': {'type': 'string'}
                                }
                            }
                        }
                    }
                },
                'mock_data': {
                    'count': 5,
                    'results': [
                        {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
                        {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
                        {'code': 'GBP', 'name': 'British Pound', 'symbol': '£'},
                        {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥'},
                        {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹'}
                    ]
                }
            },
            {
                'name': 'Exchange Rates',
                'slug': 'exchange-rates',
                'description': 'Get current exchange rates',
                'path': '/v1/exchange-rates',
                'method': 'GET',
                'category': categories['currency'],
                'default_rate_limit': 100,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'base': {'type': 'string'},
                        'timestamp': {'type': 'string'},
                        'rates': {
                            'type': 'object',
                            'additionalProperties': {'type': 'number'}
                        }
                    }
                },
                'mock_data': {
                    'base': 'USD',
                    'timestamp': '2024-01-15T12:00:00Z',
                    'rates': {
                        'EUR': 0.92,
                        'GBP': 0.79,
                        'JPY': 148.50,
                        'INR': 83.12,
                        'CAD': 1.35,
                        'AUD': 1.52,
                        'CHF': 0.87,
                        'CNY': 7.18
                    }
                }
            },
        ]
        
        # Create API definitions
        for api_data in apis:
            APIDefinition.objects.get_or_create(
                slug=api_data['slug'],
                defaults=api_data
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {len(apis)} APIs!')
        )