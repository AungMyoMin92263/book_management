from django.urls import path, include
from .views import register, login
from rest_framework.routers import DefaultRouter
from .views import FavoriteViewSet, AuthorViewSet, BookViewSet

router = DefaultRouter()
router.register(r'favorites', FavoriteViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'books', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register, name='register'),
    path('login/', login, name='login'),

]
