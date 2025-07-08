from django.urls import path
from .views import (
    QuizListCreateAPIView,
    QuizDetailAPIView,
    AddQuestionAPIView,
    SubmitAnswerAPIView
)

urlpatterns = [
    path('quizzes/', QuizListCreateAPIView.as_view(), name='quiz-list-create'),
    path('quizzes/<int:pk>/', QuizDetailAPIView.as_view(), name='quiz-detail'),
    path('quizzes/<int:pk>/add_question/', AddQuestionAPIView.as_view(), name='add-question'),
    path('quizzes/<int:pk>/submit_answer/', SubmitAnswerAPIView.as_view(), name='submit-answer'),
]
