from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz, Question, Answer
from .serializers import QuizSerializer

class QuizListCreateAPIView(APIView):
    def get(self, request):
        quizzes = Quiz.objects.all()
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return None

    def get(self, request, pk):
        quiz = self.get_object(pk)
        if not quiz:
            return Response({'error': 'Quiz not found'}, status=404)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)

    def put(self, request, pk):
        quiz = self.get_object(pk)
        if not quiz:
            return Response({'error': 'Quiz not found'}, status=404)
        serializer = QuizSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        quiz = self.get_object(pk)
        if not quiz:
            return Response({'error': 'Quiz not found'}, status=404)
        quiz.delete()
        return Response(status=204)


class AddQuestionAPIView(APIView):
    def post(self, request, pk):
        try:
            quiz = Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=404)
        #ক্লায়েন্ট থেকে আসা JSON body থেকে ডেটা বের করছি।
        question_text = request.data.get('text')
        answers_data = request.data.get('answers', [])

        if not question_text:
            return Response({'error': 'Question text is required'}, status=400)

        question = Question.objects.create(quiz=quiz, text=question_text)

        for answer_data in answers_data:
            Answer.objects.create(
                question=question,
                text=answer_data['text'],
                is_correct =answer_data['is_correct']
            )

        return Response({'message': 'Question added successfully'}, status=201)


class SubmitAnswerAPIView(APIView):
    def post(self, request, pk):
        question_id = request.data.get('question_id')
        answer_id = request.data.get('answer_id')

        try:
            question = Question.objects.get(id=question_id, quiz_id=pk)
        except Question.DoesNotExist:
            return Response({'error': 'Invalid question id'}, status=400)

        try:
            answer = question.answers.get(id=answer_id)
        except Answer.DoesNotExist:
            return Response({'error': 'Invalid answer id'}, status=400)
        
        # session এ কাউন্ট রাখি
        if 'correct_count' not in request.session:
            request.session['correct_count'] = 0
        if 'wrong_count' not in request.session:
            request.session['wrong_count'] = 0

        if answer.is_correct:
            request.session['correct_count'] += 1
            result = '✅ Correct answer'
        else:
            request.session['wrong_count'] += 1
            result = '❌ Incorrect answer'

        request.session.modified = True
        return Response({
            'message': result,
            'correct_so_far': request.session['correct_count'],
            'wrong_so_far': request.session['wrong_count']
        }, status=200)
