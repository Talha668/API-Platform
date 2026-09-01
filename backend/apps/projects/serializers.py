from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    api_keys_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'owner', 'owner_email',
            'is_active', 'api_keys_count',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at', 'api_keys_count')
    
    def validate_name(self, value):
        """
        Validate that the project name is not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Project name cannot be empty.")
        return value.strip()


class ProjectCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new project.
    """
    class Meta:
        model = Project
        fields = ('name', 'description')
    
    def validate_name(self, value):
        """
        Validate that the project name is not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Project name cannot be empty.")
        return value.strip()
    
    def create(self, validated_data):
        """
        Create a new project with the current user as owner.
        """
        request = self.context.get('request')
        user = request.user
        
        project = Project.objects.create(
            owner=user,
            name=validated_data['name'],
            description=validated_data.get('description', '')
        )
        
        return project


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a project.
    """
    class Meta:
        model = Project
        fields = ('name', 'description', 'is_active')
    
    def validate_name(self, value):
        """
        Validate that the project name is not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Project name cannot be empty.")
        return value.strip()