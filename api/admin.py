from django.contrib import admin
from .models import Author, Book, Series, UserHistory

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Display the author's ID and name in the admin list view

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'average_rating', 'series_name')

    def series_name(self, obj):
        return obj.series.name if obj.series else 'No Series'  # Display series name or 'No Series' if none
    series_name.short_description = 'Series' 

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(UserHistory)
class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'viewed_at')  # Display fields for the history log
    list_filter = ('user', 'viewed_at') 