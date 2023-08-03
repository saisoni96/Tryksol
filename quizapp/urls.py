from django.urls import path
from .views import SendOTPView,VerifyOTPView, LogoutView,UserRegisterView,UserLoginView,ResetPasswordView, CategoryListView,Results,FetchNewQuiz,SaveQuizResponse,ResultDetails

urlpatterns = [
    path('registration/', UserRegisterView.as_view(), name='registeration'),
    path('sendOTP/', SendOTPView.as_view(), name='send-otp'),
    path('verifyOTP/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', UserLoginView.as_view(), name='registeration'),
    path('reset/password/', ResetPasswordView.as_view(), name='reset-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('categories/list/', CategoryListView.as_view(), name='login'),
    path('fetchNewQuiz/<int:category_id>/', FetchNewQuiz.as_view(), name='get-new-quiz'),
    path('saveQuizResponse/', SaveQuizResponse.as_view(), name='save-quiz-response'),
    path('results/', Results.as_view(), name='results-list'),
    path('results/<int:quiz_room_id>/', ResultDetails.as_view(), name='result'),
]