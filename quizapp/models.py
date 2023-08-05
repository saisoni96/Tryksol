from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    mobile_number = models.CharField(max_length=225, null=True)
    otp = models.CharField(max_length=20, null=True)
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
    quiz_title = models.CharField(max_length=255)
    quiz_description = models.TextField()
    quiz_date = models.DateField()
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
    option_text = models.CharField(max_length=100)
    is_correct_option = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.option_text
class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    date_completed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Result ID: {self.result_id} - User: {self.user.username}"

# class Category(models.Model):
#     name = models.CharField(max_length=255, default=None)
#     created_at = models.DateTimeField(auto_now_add=True, blank=True)
#     updated_at = models.DateTimeField(auto_now=True, blank=True)

#     def __str__(self):
#         return self.name

# class Questions(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     option1 = models.CharField(max_length=100)
#     option2 = models.CharField(max_length=100)
#     option3 = models.CharField(max_length=100)
#     option4 = models.CharField(max_length=100)
#     correct_option = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True, blank=True)
#     updated_at = models.DateTimeField(auto_now=True, blank=True)
    
#     class Meta:
#         verbose_name = "Question"
#         verbose_name_plural = "Questions"
#     def __str__(self):
#         return self.title

# class QuizSession(models.Model):
#     quiz_room_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     started_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Quiz Room ID: {self.quiz_room_id} - User: {self.user.username}"

# class Result(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     quiz_room_id =models.ForeignKey(QuizSession, on_delete=models.CASCADE)
#     score = models.IntegerField(null=True)
#     number_of_correct_answers = models.IntegerField(null=True)
#     number_of_wrong_answers = models.IntegerField(null=True)
#     date_completed = models.DateTimeField(auto_now=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True, blank=True)
#     updated_at = models.DateTimeField(auto_now=True, blank=True)

#     def __str__(self):
#         return f"Quiz Room ID: {self.quiz_room_id} - User: {self.user.username}"