from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .utils import generate_otp
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

class ResetPasswordView(views.APIView):
    def post(self, request):
        try:
            access_token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]
            mobile_number = request.POST.get('mobile_number')
            new_password = request.POST.get('new_password')

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
            items = [{"categoryId": category.category_id, "categoryName": category.category_name,"categoryDescription":category.description} for category in categories]
            return Response(items, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FetchNewQuiz(views.APIView):
    def get(self, request, category_id):
        try:
            category = Category.objects.get(category_id=category_id)
            quiz = Quiz.objects.create(category=category)
            quiz_id = quiz.quiz_id

            all_questions = Question.objects.filter(quiz=quiz)
            selected_questions = all_questions.order_by('?')[:60]

            serialized_questions = []
            for question in selected_questions:
                options = Option.objects.filter(question=question)
                serialized_options = [{"optionId": option.option_id, "optionText": option.option_text} for option in options]

                serialized_question = {
                    'questionId': question.question_id,
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
                quiz = Quiz.objects.get(quiz_id=quiz_id)
            except Quiz.DoesNotExist:
                return Response({'message': 'Invalid quizId'}, status=status.HTTP_400_BAD_REQUEST)

            result = Result.objects.create(
                user=request.user,
                quiz=quiz,
            )

            score = 0
            total_questions = 0
            attempted_correct = 0
            attempted_wrong = 0

            for response in quiz_responses:
                question_id = response['questionId']
                selected_option_id = response['selectedOptionId']

                try:
                    question = Question.objects.get(question_id=question_id)
                except Question.DoesNotExist:
                    return Response({'message': 'Invalid question ID'}, status=status.HTTP_400_BAD_REQUEST)

                selected_option = Option.objects.get(option_id=selected_option_id)

                if selected_option.is_correct_option:
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
            quiz_ids = queryset.values_list('quiz_id', flat=True)
            return Response(list(quiz_ids), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResultDetails(views.APIView):
    def get(self, request, quiz_id):
        try:
            result = Result.objects.get(quiz_id=quiz_id)

            data = {
                'quizId': quiz_id,
                'user': result.user.username,
                'quizCategory': result.quiz.category.category_name,
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






# class CategoryListView(views.APIView):
#     def get(self, request):
#         user_id = request.user.id
#         queryset = Category.objects.all()
#         items  = [{"categoryId" : item.id,"categoryName":item.name}for item in queryset]
#         return Response(items,status=status.HTTP_200_OK)
    
# class FetchNewQuiz(views.APIView):
#     def get(self,request,category_id):
#         user_id = request.user.id
#         # Create a new QuizSession object to get a unique quiz_room_id
#         quiz_session = QuizSession.objects.create(user=request.user)

#         # Get the quiz_room_id from the newly created QuizSession object
#         quiz_room_id = quiz_session.pk
        
#         # Assuming you have a queryset to filter questions based on category
#         all_questions = Questions.objects.filter(category_id=category_id)

#         # Randomly select 60 questions from the pool of available questions
#         selected_questions = all_questions.order_by('?')[:60]

#         # Your logic to serialize the selected questions into JSON data
#         serialized_questions = []
#         for question in selected_questions:
#             serialized_question = {
#                 'id': question.id,
#                 'title': question.title,
#                 'option1': question.option1,
#                 'option2': question.option2,
#                 'option3': question.option3,
#                 'option4': question.option4,
#                 'correct_option':question.correct_option,
#             }
#             serialized_questions.append(serialized_question)

#         response_data = {
#             'quiz_room_id': quiz_room_id,
#             'questions': serialized_questions,
#         }
#         return Response(response_data)

# class SaveQuizResponse(views.APIView):
#     def post(self, request):
#         user_id = request.user.id
#         quiz_room_id = request.data.get('quiz_room_id')
#         quiz_responses = request.data.get('quiz_responses')

#         try:
#             # Retrieve the QuizSession based on the quiz_room_id
#             quiz_session = QuizSession.objects.get(quiz_room_id=quiz_room_id)
#         except QuizSession.DoesNotExist:
#             return Response({'message': 'Invalid quiz_room_id'}, status=400)

#         # Create a new Result object for the user's quiz attempt
#         result = Result.objects.create(
#             user=request.user,
#             quiz_room_id=quiz_session,
#             quiz_data=quiz_responses,
#         )

#         # Calculate the score based on the user's responses
#         score = 0
#         total_questions = 0
#         attempted_correct = 0
#         attempted_wrong = 0

#         for response in quiz_responses:
#             question_id = response['question_id']
#             selected_option = response['selected_option']

#             # Retrieve the Quiz object based on the question_id
#             try:
#                 quiz = Questions.objects.get(id=question_id)
#             except Questions.DoesNotExist:
#                 return Response({'message': 'Invalid question ID'}, status=400)

#             # Check if the selected option is correct
#             if selected_option == quiz.correct_option:
#                 score += 1
#                 attempted_correct += 1
#             else:
#                 attempted_wrong += 1

#             total_questions += 1

#         # Update the score in the Result object
#         result.score = score
#         result.number_of_correct_answers = attempted_correct
#         result.number_of_wrong_answers = attempted_wrong
#         result.save()

#         response_data = {
#             'message': 'Quiz response saved successfully!',
#             'score': score,
#             'total_questions': total_questions,
#             'attempted_correct': attempted_correct,
#             'attempted_wrong': attempted_wrong,
#         }

#         return Response(response_data)

# class Results(views.APIView):
#     def get(request):
#         user_id = request.user.id
#         # Get a list of quiz room IDs for the specific user
#         queryset = Result.objects.filter(user_id=user_id)

#         if not queryset.exists():
#             # Return an empty list if no results are found for the user
#             return Response([], status=status.HTTP_200_OK)

#         # Get a list of quiz room IDs from the queryset
#         quiz_room_ids = queryset.values_list('quiz_room_id', flat=True)

#         # Convert the queryset to a list and send the response
#         return Response(list(quiz_room_ids), status=status.HTTP_200_OK)


# class ResultDetails(views.APIView):
#     def get(self, request, quiz_room_id):
#         user_id = request.user.id
#         # Get the quiz session result based on the quiz room ID (quiz_room_id)
#         result = get_object_or_404(Result, quiz_room_id=quiz_room_id)

#         # Get the associated quiz session details
#         quiz_session = get_object_or_404(QuizSession, pk=quiz_room_id)

#         data = {
#             'quiz_room_id': quiz_room_id,
#             'user': result.user.username,
#             'quiz_category': quiz_session.category.name,
#             'score': result.score,
#             'number_of_correct_answers': result.number_of_correct_answers,
#             'number_of_wrong_answers': result.number_of_wrong_answers,
#             'date_completed': result.date_completed,
#             'created_at': result.created_at,
#             'updated_at': result.updated_at,
#         }
#         return Response(data, status=status.HTTP_200_OK)
    
    
