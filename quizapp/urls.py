from django.urls import path
from .views import SendOTPView,VerifyOTPView, UserProfileView, CheckUserView, LogoutView,UserRegisterView,UserLoginView,ResetPasswdView, CategoryListView, quizListView, Results,FetchNewQuiz,SaveQuizResponse,ResultDetails

urlpatterns = [
    path('registration/', UserRegisterView.as_view(), name='registeration'),
    path('sendOTP/', SendOTPView.as_view(), name='send-otp'),
    path('verifyOTP/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', UserLoginView.as_view(), name='registeration'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('check-user/', CheckUserView.as_view(), name='check-user'),
    path('reset/password/', ResetPasswdView.as_view(), name='reset-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('categories/list/', CategoryListView.as_view(), name='categories-list'),
    path('list/<int:category_id>', quizListView.as_view(), name='quiz-list'),
    path('fetchNewQuiz/<int:quiz_id>/', FetchNewQuiz.as_view(), name='get-new-quiz'),
    path('saveQuizResponse/', SaveQuizResponse.as_view(), name='save-quiz-response'),
    path('results/', Results.as_view(), name='results-list'),
    path('result/details/<int:result_id>/', ResultDetails.as_view(), name='result-details'),
]
