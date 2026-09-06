from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
import json
from apps.gateway.models import APICategory, APIDefinition, ProjectAPIAssignment
from apps.projects.models import Project

class Command(BaseCommand):
    help = 'Seed gateway with additional API definitions and assignments'

    def handle(self, *args, **options):
        self.stdout.write('Seeding gateway data...')
        
        # Create additional API categories
        categories_data = [
            {
                'name': 'Weather',
                'slug': 'weather',
                'description': 'Weather data and forecasts',
                'icon': '🌤️'
            },
            {
                'name': 'Tasks Management',
                'slug': 'tasks',
                'description': 'Manage tasks and to-dos',
                'icon': '📋'
            },
            {
                'name': 'Currency & Exchange',
                'slug': 'currency',
                'description': 'Currency conversion and exchange rates',
                'icon': '💰'
            },
            {
                'name': 'User Management',
                'slug': 'users',
                'description': 'User authentication and profile management',
                'icon': '👤'
            },
            {
                'name': 'Content Management',
                'slug': 'content',
                'description': 'Content creation and management',
                'icon': '📝'
            },
            {
                'name': 'Analytics',
                'slug': 'analytics',
                'description': 'Usage analytics and reporting',
                'icon': '📊'
            },
        ]

        created_categories = []
        for cat_data in categories_data:
            category, created = APICategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            created_categories.append(category)
            if created:
                self.stdout.write(f'  Created category: {category.name}')

        # Additional API definitions
        apis_data = [
            # User APIs
            {
                'name': 'Create User',
                'slug': 'users-create',
                'description': 'Create a new user account',
                'path': '/v1/users',
                'method': 'POST',
                'category': 'users',
                'default_rate_limit': 50,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'email': {'type': 'string'},
                        'name': {'type': 'string'},
                        'created_at': {'type': 'string'}
                    }
                },
                'mock_data': {
                    'id': 1,
                    'email': 'newuser@example.com',
                    'name': 'New User',
                    'created_at': timezone.now().isoformat()
                }
            },
            {
                'name': 'Get User',
                'slug': 'users-get',
                'description': 'Get user details by ID',
                'path': '/v1/users/{id}',
                'method': 'GET',
                'category': 'users',
                'default_rate_limit': 100,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'email': {'type': 'string'},
                        'name': {'type': 'string'},
                        'created_at': {'type': 'string'},
                        'updated_at': {'type': 'string'}
                    }
                },
                'mock_data': {
                    'id': 1,
                    'email': 'john.doe@example.com',
                    'name': 'John Doe',
                    'created_at': timezone.now().isoformat(),
                    'updated_at': timezone.now().isoformat()
                }
            },
            {
                'name': 'Update User',
                'slug': 'users-update',
                'description': 'Update user details',
                'path': '/v1/users/{id}',
                'method': 'PUT',
                'category': 'users',
                'default_rate_limit': 50,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'email': {'type': 'string'},
                        'name': {'type': 'string'},
                        'updated_at': {'type': 'string'}
                    }
                },
                'mock_data': {
                    'id': 1,
                    'email': 'updated@example.com',
                    'name': 'Updated User',
                    'updated_at': timezone.now().isoformat()
                }
            },
            {
                'name': 'Delete User',
                'slug': 'users-delete',
                'description': 'Delete a user account',
                'path': '/v1/users/{id}',
                'method': 'DELETE',
                'category': 'users',
                'default_rate_limit': 30,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'deleted_id': {'type': 'integer'}
                    }
                },
                'mock_data': {
                    'message': 'User deleted successfully',
                    'deleted_id': 1
                }
            },
            
            # Content Management APIs
            {
                'name': 'List Articles',
                'slug': 'articles-list',
                'description': 'Get list of articles with optional filtering',
                'path': '/v1/articles',
                'method': 'GET',
                'category': 'content',
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
                                    'author': {'type': 'string'},
                                    'published_at': {'type': 'string'}
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
                            'title': 'Getting Started with APIs',
                            'author': 'Jane Smith',
                            'published_at': timezone.now().isoformat()
                        },
                        {
                            'id': 2,
                            'title': 'Advanced Rate Limiting Strategies',
                            'author': 'John Doe',
                            'published_at': timezone.now().isoformat()
                        },
                        {
                            'id': 3,
                            'title': 'Building Production-Ready APIs',
                            'author': 'Bob Wilson',
                            'published_at': timezone.now().isoformat()
                        }
                    ]
                }
            },
            {
                'name': 'Create Article',
                'slug': 'articles-create',
                'description': 'Create a new article',
                'path': '/v1/articles',
                'method': 'POST',
                'category': 'content',
                'default_rate_limit': 30,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'title': {'type': 'string'},
                        'content': {'type': 'string'},
                        'created_at': {'type': 'string'}
                    }
                },
                'mock_data': {
                    'id': 4,
                    'title': 'New Article Created',
                    'content': 'This is the content of the new article...',
                    'created_at': timezone.now().isoformat()
                }
            },
            
            # Analytics APIs
            {
                'name': 'Get Analytics',
                'slug': 'analytics-get',
                'description': 'Get usage analytics for your project',
                'path': '/v1/analytics',
                'method': 'GET',
                'category': 'analytics',
                'default_rate_limit': 50,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'total_requests': {'type': 'integer'},
                        'success_rate': {'type': 'number'},
                        'avg_response_time': {'type': 'number'},
                        'period': {'type': 'string'}
                    }
                },
                'mock_data': {
                    'total_requests': 25890,
                    'success_rate': 98.7,
                    'avg_response_time': 145,
                    'period': 'last_7_days'
                }
            },
        ]

        created_apis = []
        for api_data in apis_data:
            category_slug = api_data.pop('category')
            category = APICategory.objects.get(slug=category_slug)
            
            api, created = APIDefinition.objects.get_or_create(
                slug=api_data['slug'],
                defaults={
                    **api_data,
                    'category': category
                }
            )
            created_apis.append(api)
            if created:
                self.stdout.write(f'  Created API: {api.name} ({api.method} {api.path})')

        # Enable APIs for random projects
        projects = Project.objects.filter(is_active=True)
        enabled_count = 0
        
        for project in projects:
            # Enable 3-6 random APIs for each project
            num_apis = random.randint(3, min(6, len(created_apis)))
            selected_apis = random.sample(created_apis, num_apis)
            
            for api in selected_apis:
                # Random rate limit override
                rate_limit_override = None
                if random.random() > 0.5:
                    rate_limit_override = api.default_rate_limit * random.randint(2, 5)
                
                assignment, created = ProjectAPIAssignment.objects.get_or_create(
                    project=project,
                    api_definition=api,
                    defaults={
                        'is_enabled': True,
                        'rate_limit': rate_limit_override,
                        'enabled_at': timezone.now() - timedelta(days=random.randint(1, 60))
                    }
                )
                
                if created:
                    enabled_count += 1
                    self.stdout.write(f'  Enabled API: {api.name} for project {project.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_apis)} APIs and enabled {enabled_count} project assignments!')
        )