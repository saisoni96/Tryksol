from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .utils import generate_otp
import ast
from .models import User,Category, Quiz, Question, Option, Result
from django.contrib.auth import authenticate, logout
from quizapp.serializers import UserRegisterSerializer
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

class SendOTPView(views.APIView):
    def post(self, request):
        try:
            mobile_number = request.data.get('mobile_number')
            otp = generate_otp()
            user, created = User.objects.get_or_create(mobile_number=mobile_number)
            user.otp = otp
            user.save()

            if not mobile_number:
                return Response({'error': 'Mobile number is required.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'OTP sent successfully.', 'otp': otp}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(views.APIView):
    def post(self, request):
        try:
            mobile_number = request.data.get('mobile_number')
            otp = request.data.get('otp')
            user = User.objects.get(mobile_number=mobile_number)

            if not (mobile_number and otp):
                return Response({'error': 'Mobile number and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

            if user.otp == otp:
                return Response({'message': 'OTP verification successful.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_401_UNAUTHORIZED)
        except ObjectDoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserRegisterView(views.APIView):
    def post(self, request):
        try:
            serializer = UserRegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Registration successful.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLoginView(views.APIView):
    def post(self, request):
        try:
            mobile_number = request.data.get('mobile_number')
            email = request.data.get('email')
            password = request.data.get('password')

            if not (mobile_number or email):
                return Response({'error': 'You must provide either a mobile number or an email.'}, status=status.HTTP_400_BAD_REQUEST)

            if not password:
                return Response({'error': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)

            user = None
            if mobile_number:
                user = User.objects.filter(mobile_number=mobile_number).first()
            elif email:
                user = User.objects.filter(email=email).first()

            if not user:
                return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
            authenticated_user = authenticate(request=request, username=user.username, password=password)

            if authenticated_user is None:
                return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

            token, created = Token.objects.get_or_create(user=authenticated_user)

            return Response({'access_token': token.key, 'message': 'Login successful.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResetPasswdView(views.APIView):
    def post(self, request):
        try:
            mobile_number = request.data.get('mobile_number')
            new_password = request.data.get('new_password')

            if not (mobile_number and new_password):
                return Response({'error': 'Mobile number and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(mobile_number=mobile_number).first()
            if not user:
                return Response({'error': 'User not found with the provided mobile number.'}, status=status.HTTP_404_NOT_FOUND)

            user.set_password(new_password)
            user.save()

            return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(views.APIView):
    def post(self, request):
        try:
            if request.user.is_authenticated:
                try:
                    token = Token.objects.get(user=request.user)
                    token.delete()
                except Token.DoesNotExist:
                    pass  # Token not found, user already logged out

            return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryListView(views.APIView):
    def get(self, request):
        try:
            categories = Category.objects.all()
            items = [{"categoryId":category.id,"categoryName":category.category_name,"categoryDescription":category.description} for category in categories]
            return Response(items, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class quizListView(views.APIView):
    def get(self, request, category_id):
        try:
            quiz = Quiz.objects.filter(category_id=category_id)
            items = [{"quizId": item.id, "quizName": item.quiz_title,"quizDescription":item.quiz_description} for item in quiz]
            return Response(items, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FetchNewQuiz(views.APIView):
    def get(self, request, quiz_id):
        try:
            all_questions = Question.objects.filter(quiz=quiz_id)
            selected_questions = all_questions.order_by('?')[:60]

            serialized_questions = []
            for question in selected_questions:
                options = Option.objects.filter(question=question)
                serialized_options = [{"optionId": option.id,"isCorrectOption":option.is_correct_option, "optionText": option.option_text} for option in options]

                serialized_question = {
                    'questionId': question.id,
                    'questionText': question.question_text,
                    'options': serialized_options,
                }
                serialized_questions.append(serialized_question)

            response_data = {
                'quizId': quiz_id,
                'questions': serialized_questions,
            }
            return Response(response_data)
        except Category.DoesNotExist:
            return Response({'message': 'Invalid categoryId'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SaveQuizResponse(views.APIView):
    def post(self, request):
        try:
            quiz_id = request.data.get('quizId')
            quiz_responses = request.data.get('quizResponses')
            try:
                quiz = Quiz.objects.get(id=quiz_id)
            except Quiz.DoesNotExist:
                return Response({'message': 'Invalid quizId'}, status=status.HTTP_400_BAD_REQUEST)
            result = Result.objects.create(
                user=request.user,
                quiz=quiz,
                quiz_data = str(request.data)
            )
            score = 0
            total_questions = 0
            attempted_correct = 0
            attempted_wrong = 0

            for response in quiz_responses:
                question_id = response['questionId']
                selected_option_ids = response.get('optionIds', [])

                try:
                    question = Question.objects.get(id=question_id)
                except Question.DoesNotExist:
                    return Response({'message': 'Invalid question ID'}, status=status.HTTP_400_BAD_REQUEST)

                correct_option_ids = Option.objects.filter(question_id = question_id,is_correct_option=True)
                if set(selected_option_ids) == set(correct_option_ids):
                    score += 1
                    attempted_correct += 1
                else:
                    attempted_wrong += 1

                total_questions += 1

            result.score = score
            result.save()

            response_data = {
                'message': 'Quiz response saved successfully!',
                'score': score,
                'totalQuestions': total_questions,
                'attemptedCorrect': attempted_correct,
                'attemptedWrong': attempted_wrong,
            }

            return Response(response_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Results(views.APIView):
    def get(self, request):
        try:
            queryset = Result.objects.filter(user=request.user)
            items = [{"resultId": item.id, "quizId": item.quiz_id, "category": item.quiz.category.category_name, "quizTitle": item.quiz.quiz_title} for item in queryset]
            response_data = {
                'results': items
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResultDetails(views.APIView):
    def get(self, request, result_id):
        try:
            result = Result.objects.get(id=result_id)
            data = {
                'result_id': result_id,
                'user': result.user.first_name,
                'Category': result.quiz.category.category_name,
                'quizTitle':result.quiz.quiz_title,
                'quiz_data':ast.literal_eval(result.quiz_data),
                'score': result.score,
                'dateCompleted': result.date_completed,
                'createdAt': result.created_at,
                'updatedAt': result.updated_at,
            }
            return Response(data, status=status.HTTP_200_OK)
        except Result.DoesNotExist:
            return Response({'message': 'Result not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    