from rest_framework import views, serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import User

class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    dob=serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    
    def validate_email(self, value):
        # Check if the email is already in use
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value

    def validate_mobile_number(self, value):
        # Check if the mobile number is already in use
        if User.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError('This mobile number is already registered.')
        return value
    
    def update(self, instance, validated_data):
        # Update the user instance with the validated data
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('first_name', instance.first_name)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.dob = validated_data.get('dob', instance.dob)
        instance.save()
        return instance
    
    def create(self, validated_data):
        # Create a new user object with the validated data
        user = User.objects.create(
            email = validated_data['email'],
            username = validated_data['first_name'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            dob = validated_data['dob']
        )
        # Set the user's password
        user.set_password(validated_data['password'])
        user.save()
        return user