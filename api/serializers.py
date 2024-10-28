from rest_framework import serializers
from .models import Author, Book, Favorite

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Book
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = Favorite
        fields = ['book']