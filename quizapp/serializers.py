from rest_framework import views, serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import User

class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    dob = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    mobile_number = serializers.CharField(max_length=20)  # Add mobile_number field
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value
    def validate_mobile_number(self, value):
        if not User.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError('This mobile number is not registered.')
        return value
    def create(self, validated_data):
        mobile_number = validated_data['mobile_number']
        try:
            user = User.objects.get(username=str(mobile_number))
            user.email = validated_data['email']
            user.first_name = validated_data['first_name']
            user.last_name = validated_data['last_name']
            user.dob = validated_data['dob']
            user.set_password(validated_data['password'])
            user.save()
        except User.DoesNotExist:
            raise serializers.ValidationError('This mobile number is not registered.')
        return user
