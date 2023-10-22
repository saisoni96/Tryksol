from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    mobile_number = models.CharField(max_length=225, null=True)
    otp = models.CharField(max_length=20, null=True, unique=True)
    otp_verified = models.BooleanField(default=False)
    dob = models.DateField(null=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    category_name = models.CharField(max_length=255,null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name

class Quiz(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quiz_title = models.CharField(max_length=500)
    quiz_description = models.TextField()
    timer = models.PositiveIntegerField(default=0)
    num_questions = models.PositiveIntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.quiz_title
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text
    
class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_text = models.CharField(max_length=500)
    is_correct_option = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.option_text
    
class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    quiz_data = models.JSONField(blank=True, default=dict)
    score = models.IntegerField(default=0)
    date_completed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Result ID: {self.id} - User: {self.user.username}"
