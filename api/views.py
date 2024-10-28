from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Favorite, Book, Author, UserHistory
from django.shortcuts import get_object_or_404
from .serializers import BookSerializer, AuthorSerializer, FavoriteSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from rest_framework import viewsets, permissions
from .utils import *
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework import status



# Authentication Endpoints
@api_view(['POST'])
def register(request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    if username is None or username == '':
        return Response({'error': 'Username must not be null.'}, status=400)
    if password is None or password == '':
        return Response({'error': 'Password must not be null.'}, status=400)
    user = User.objects.create_user(username=username, password=password)
    return Response({'message': 'User registered successfully.'})

@api_view(['POST'])
def login(request):
    username = request.data['username']
    password = request.data['password']
    user = User.objects.filter(username=username).first()
    if user and user.check_password(password):
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid credentials'}, status=400)

# Book Views
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Protected for create/update/delete


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Protected for create/update/delete

    def create(self, request, *args, **kwargs):
        author_data = request.data.get('author')
        if author_data:
            author, created = Author.objects.get_or_create(name=author_data)
            request.data['author'] = author.id
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        author_data = request.data.get('author')
        if author_data:
            author, created = Author.objects.get_or_create(name=author_data)
            request.data['author'] = author.id
        return super().update(request, *args, **kwargs)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favorite(request, book_id):
    user = request.user
    book = get_object_or_404(Book, id=book_id)

    if Favorite.objects.filter(user=user).count() >= 20:
        return Response({'error': 'Maximum of 20 favorite books allowed.'}, status=400)

    favorite, created = Favorite.objects.get_or_create(user=user, book=book)
    if not created:
        return Response({'error': 'Book is already in favorites.'}, status=400)

    return Response({'message': f'{book.title} added to favorites.'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_favorite(request, book_id):
    user = request.user
    book = get_object_or_404(Book, id=book_id)

    favorite = Favorite.objects.filter(user=user, book=book).first()
    if favorite:
        favorite.delete()
        return Response({'message': f'{book.title} removed from favorites.'})
    return Response({'error': 'Book not found in favorites.'}, status=404)





class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        book_id = request.data.get('book_id')

        # Check if book_id is provided
        if not book_id:
            return Response({'error': 'book_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the book exists
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Book does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # Create or get favorite
        favorite, created = Favorite.objects.get_or_create(user=request.user, book=book)

        if created:
            recommendations = get_recommendations(request.user)
            recommended_books = BookSerializer(recommendations, many=True).data
            return Response({
                'message': 'Book added to favorites!',
                'recommendations': recommended_books
            })
        return Response({'message': 'Book is already in favorites.'})

    def destroy(self, request, *args, **kwargs):
        favorite = self.get_object()
        favorite.delete()
        return Response({'message': 'Book removed from favorites.'})

    def list(self, request, *args, **kwargs):
        favorites = Favorite.objects.filter(user=request.user).select_related('book')
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        recommendations = get_recommendations(request.user)
        print('Found recommendations', recommendations)
        recommended_books = BookSerializer(recommendations, many=True).data
        return Response(recommended_books)