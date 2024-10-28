from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone

class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Series(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    average_rating = models.FloatField(null=True, blank=True)
    series = models.ForeignKey(Series, null=True, blank=True, on_delete=models.SET_NULL)  # Optional relationship

    def __str__(self):
        return self.title








class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f'{self.user.username} -> {self.book.title}'
    


class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} {self.book.title} on {self.viewed_at}"

    class Meta:
        ordering = ['-viewed_at']
