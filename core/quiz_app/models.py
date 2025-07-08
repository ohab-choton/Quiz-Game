from django.db import models


class Quiz(models.Model):
    title=models.CharField(max_length=200)

    def __str__(self):
        return self.title
    
class Question(models.Model):
    quiz=models.ForeignKey(Quiz, related_name='questions' ,on_delete=models.CASCADE)
    text=models.CharField(max_length=100)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question=models.ForeignKey(Question,related_name='answers',on_delete=models.CASCADE)
    text=models.CharField(max_length=150)
    is_correct=models.BooleanField(default=False)

    def __str__(self):
        return self.text
    
