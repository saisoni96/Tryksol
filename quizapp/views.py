from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .utils import generate_otp, send_otp_via_sms
from .models import User, Category, Quiz, Question, Option, Result
from django.contrib.auth import authenticate, logout
from quizapp.serializers import UserRegisterSerializer
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

class SendOTPView(views.APIView):
    def post(self, request):
        try:
            mobile_number = request.data.get('mobile_number')
            
            if not mobile_number:
                return Response({'message': 'Mobile number is required.', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})
            try:
                user = User.objects.get(username=str(mobile_number))
            except:
                user = User.objects.create(username=str(mobile_number), mobile_number=mobile_number)
            otp = generate_otp()
            user.otp = otp
            user.save()
            result= send_otp_via_sms(mobile_number,otp)
            return Response({'message': 'OTP sent successfully.', 'otp': otp, 'status': 'Success', 'statusCode': status.HTTP_200_OK})
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.", 
                            'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})

class VerifyOTPView(views.APIView):
    def post(self, request):
        try:
            mobile_number = request.data.get('mobile_number')
            otp = request.data.get('otp')
            print("otppppp")
            user = User.objects.get(mobile_number=mobile_number)
            print(user)
            if not (mobile_number and otp):
                return Response({'message': 'Mobile number is required.', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})

            if user.otp == otp:
                user.otp_verified = True
                return Response({'message': 'OTP verification successful.', 'status': 'Success', 'statusCode': status.HTTP_200_OK})
            return Response({'message': 'Invalid OTP.', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})
        except ObjectDoesNotExist:
            return Response({'message': 'User not found.', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.", 
                            'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})

class UserRegisterView(views.APIView):
    def post(self, request):
        try:
            serializer = UserRegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Registration successful.', 'status': 'Success', 'statusCode': status.HTTP_200_OK})
        except serializers.ValidationError as e:
            # If a ValidationError occurs, extract the error messages from the serializer
            error_messages = serializer.errors
            return Response({'message': error_messages, 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.", 
                            'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})

class UserProfileView(views.APIView):
    def get(self, request):
        try:
            user=request.user
            return Response( {"first_name": user.first_name, "last_name": user.last_name, "email": user.email, "mobile_number":user.mobile_number,"dob":user.dob,"status":status.HTTP_200_OK})
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.", 
                            'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})


class UserProfileUpdateView(views.APIView):
    def patch(self, request):
        try:
            user = request.user
            if 'dob' in request.data:
                user.dob = request.data['dob']
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            if 'email' in request.data:
                user.email = request.data['email']
            user.save()
            return Response({
                'message': 'Profile updated successfully.',
                'status': 'Success',
                'statusCode': status.HTTP_200_OK
            })
        except Exception as e:
            return Response({
                'message': "An unexpected server error occurred. Please try again later.",
                'status': 'Failed',
                'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR
            })

class CheckUserView(views.APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'message': 'User is authenticated',
                'status': 'Success',
                'statusCode': status.HTTP_200_OK,
                "user_code":1
            })
        else:
            return Response({
                'message': 'User is not authenticated',
                'status': 'Success',
                'statusCode': status.HTTP_200_OK,
                "user_code":0
            })

class UserLoginView(views.APIView):
    def post(self, request):
        try:
            mobile_number = request.data.get('mobile_number')
            email = request.data.get('email')
            password = request.data.get('password')

            if not (mobile_number or email):
                return Response({'message': 'You must provide either a mobile number or an email.','status': 'Failed', 'statusCode':status.HTTP_400_BAD_REQUEST})

            if not password:
                return Response({'message': 'Password is required.', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})

            user = None
            if mobile_number:
                user = User.objects.filter(mobile_number=mobile_number).first()
            elif email:
                user = User.objects.filter(email=email).first()

            if not user:
                return Response({'message': 'Invalid credentials.', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})
            authenticated_user = authenticate(request=request, username=user.username, password=password)

            if authenticated_user is None:
                return Response({'message': 'Invalid credentials.', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})

            token, created = Token.objects.get_or_create(user=authenticated_user)

            return Response({'access_token': token.key, 'message': 'Login successful.', 'status': 'Success', 'statusCode': status.HTTP_200_OK})
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.", 
                            'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})

class ResetPasswdView(views.APIView):
    def post(self, request):
        try:
            mobile_number = request.data.get('mobile_number')
            new_password = request.data.get('new_password')

            if not (mobile_number and new_password):
                return Response({'message': 'Mobile number and new password are required.', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})

            user = User.objects.filter(mobile_number=mobile_number).first()
            if not user:
                return Response({'message': 'User not found with the provided mobile number.', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})

            user.set_password(new_password)
            user.save()

            return Response({'message': 'Password reset successful.', 'status': 'Success', 'statusCode': status.HTTP_200_OK})
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.", 
                            'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})

class LogoutView(views.APIView):
    def post(self, request):
        try:
            if request.user.is_authenticated:
                try:
                    token = Token.objects.get(user=request.user)
                    token.delete()
                except Token.DoesNotExist:
                    pass  # Token not found, user already logged out

            return Response({'message': 'Logout successful.', 'status': 'Success', 'statusCode': status.HTTP_200_OK})
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.", 
                            'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})

class CategoryListView(views.APIView):
    def get(self, request):
        try:
            name= request.GET.get('search', None)
            if name :
                categories = Category.objects.filter(category_name__icontains=name)
            else:
                categories = Category.objects.all()
            items = [{"categoryId": category.id, "categoryName": category.category_name, "categoryDescription": category.description} for category in categories]
            return Response(items, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.", 
                            'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})

class quizListView(views.APIView):
    def get(self, request, category_id):
        try:
            name= request.GET.get('search', None)
            if name :
                quiz = Quiz.objects.filter(category_id=category_id,quiz_title__icontains=name) 
            else:
                quiz = Quiz.objects.filter(category_id=category_id)     
            items = [{"quizId": item.id, "quizName": item.quiz_title, "quizDescription": item.quiz_description, "quizNumOfQuestions": item.num_questions, "quizTimer": item.timer} for item in quiz]
            return Response({'items':items,'status': 'Success', 'statusCode':status.HTTP_200_OK})
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.", 
                            'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})

class FetchNewQuiz(views.APIView):
    def get(self, request, quiz_id):
        try:
            user = request.user
            quiz=Quiz.objects.get(id=quiz_id)
            all_questions = Question.objects.filter(quiz=quiz)
            selected_questions = all_questions.order_by('?')[:quiz.num_questions]

            serialized_questions = []
            for question in selected_questions:
                options = Option.objects.filter(question=question)
                serialized_options = [{"optionId": option.id, "isCorrectOption": option.is_correct_option, "optionText": option.option_text} for option in options]

                serialized_question = {
                    'questionId': question.id,
                    'questionText': question.question_text,
                    'options': serialized_options,
                }
                serialized_questions.append(serialized_question)

            response_data = {
                'quizId': quiz.id,
                'questions': serialized_questions,
                'noOfQuestions':quiz.num_questions,
                'timer':quiz.timer,
                'status': 'Success',
                'statusCode': status.HTTP_200_OK
            }
            return Response(response_data)
        except Category.DoesNotExist:
            return Response({'message': 'Invalid categoryId', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.", 
                            'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})

class SaveQuizResponse(views.APIView):
    def post(self, request):
        try:
            user = request.user
            response_data = []

            quiz_id = request.data.get("quizId")
            if quiz_id is None:
                return Response({'message': 'No quizId provided', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})

            try:
                quiz = Quiz.objects.get(id=quiz_id)
            except Quiz.DoesNotExist:
                return Response({'message': 'Invalid quizId', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})

            total_score = 0
            total_questions = 0

            total_attempted_correct = 0
            total_attempted_wrong = 0

            responses = request.data.get("responses", [])

            for response_item in responses:
                selected_options = response_item.get("selectedOptions", [])
                quiz_responses_data = response_item.get("quizResponses", [])
                score = 0
                attempted_correct = 0
                attempted_wrong = 0

                for response in quiz_responses_data:
                    question_id = response['questionId']
                    selected_option_ids = {option['optionId'] for option in selected_options}  # Use set for faster membership testing
                    correct_option_ids = set(Option.objects.filter(question_id=question_id, is_correct_option=True).values_list('id', flat=True))
                    if selected_option_ids == correct_option_ids:
                        score += 1
                        attempted_correct += 1
                    else:
                        attempted_wrong += 1    

                total_score += score
                total_questions += len(quiz_responses_data)  
                total_attempted_correct += attempted_correct
                total_attempted_wrong += attempted_wrong
            modified_result = modify_json(request.data)
            result = Result.objects.create(
                user=user,
                quiz=quiz,
                quiz_data=modified_result,
                score=total_score
            )

            response_data = {
                "message": "Quiz response saved successfully!",
                "score": round(total_score / total_questions * 100,2),
                "totalQuestions": quiz.num_questions,
                "totalAttempted": total_attempted_correct + total_attempted_wrong,
                "attemptedCorrect": total_attempted_correct,
                "attemptedWrong": total_attempted_wrong,
                "status": "Success",
                "statusCode": 200
            }
                
            return Response(response_data)
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.",
                             'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})

def modify_json(input_json):
    modified_list = []

    for response in input_json["responses"]:
        for quiz_response in response["quizResponses"]:
            modified_entry = {
                "question": quiz_response["questionText"],
                "options": []
            }
            for option in quiz_response["options"]:
                is_selected = option in response["selectedOptions"]
                modified_entry["options"].append({**option, "selected": is_selected})

            modified_list.append(modified_entry)
    return modified_list

class Results(views.APIView):
    def get(self, request):
        try:
            queryset = Result.objects.filter(user=request.user)
            items = [{"resultId": item.id, 
                      "quizId": item.quiz_id, 
                    "user": item.user.first_name,
                    "Category": item.quiz.category.category_name,
                    "quizTitle": item.quiz.quiz_title,
                    "score": item.score,
                    "dateCompleted": item.date_completed,
                    "category": item.quiz.category.category_name, 
                    "quizTitle": item.quiz.quiz_title
                    } 
                    for item in queryset]
            response_data = {
                'results': items,
                'status': 'Success',
                'statusCode': status.HTTP_200_OK

            }
            return Response(response_data)
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.", 
                            'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})

class ResultDetails(views.APIView):
    def get(self, request, result_id):
        try:
            result = Result.objects.get(id=result_id)
            data = {
                'result_id': result_id,
                'user': result.user.first_name,
                'quiz_data': result.quiz_data,
                'status': 'Success',
                'statusCode': status.HTTP_200_OK
            }
            return Response(data)
        except Result.DoesNotExist:
            return Response({'message': 'Result not found.', 'status': 'Failed', 'statusCode': status.HTTP_400_BAD_REQUEST})
        except Exception as e:
            return Response({'message': "An unexpected server error occurred. Please try again later.", 
                            'status': 'Failed', 'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR})
