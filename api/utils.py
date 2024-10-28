from django.db.models import Q
from .models import Book, Favorite, UserHistory

def get_recommendations(user):
    # Get favorite books for the user
    favorites = Favorite.objects.filter(user=user).select_related('book')

    # Gather favorite books
    favorite_books = [favorite.book for favorite in favorites]
    print('Favorites:', favorite_books)

    # Max of 20 favorites
    if len(favorite_books) > 20:
        favorite_books = favorite_books[:20]

    # Prepare a list of authors and series from favorite books
    authors = set(book.author for book in favorite_books)
    series = set(book.series for book in favorite_books if book.series)
    favorite_book_ids = set(book.id for book in favorite_books)

    # Prepare a list of viewed books
    viewed_books = UserHistory.objects.filter(user=user).values_list('book', flat=True)
    viewed_book_ids = set(viewed_books)

    print('Series:', series, 'Favorite Book IDs:', favorite_book_ids)

    # No. 1: Recommend a book from the same series (if available)
    same_series = Book.objects.filter(series__in=series).exclude(id__in=favorite_book_ids | viewed_book_ids).distinct().first()

    # No. 2: Recommend a book from the same author (if available)
    same_author = Book.objects.filter(author__in=authors).exclude(id__in=favorite_book_ids | viewed_book_ids).distinct().first()

    # No. 3: Recommend based on user preferences (e.g., top-rated books they haven't read yet)
    # Assuming user preferences based on top ratings
    top_rated = Book.objects.exclude(id__in=favorite_book_ids | viewed_book_ids).order_by('-average_rating').first()

    # Step 4: Collaborative filtering (similar users)
    similar_users = Favorite.objects.filter(book__in=favorite_books).exclude(user=user).values_list('user', flat=True)
    recommended_by_similar_users = Book.objects.filter(favorite__user__in=similar_users).exclude(id__in=favorite_book_ids | viewed_book_ids).distinct().first()

    # Step 5: Recommendations based on user history (excluding favorites)
    recommendations_from_history = Book.objects.filter(id__in=viewed_books).exclude(id__in=favorite_book_ids).distinct()[:5]

    # Combine recommendations
    recommendations = [same_series, same_author, top_rated, recommended_by_similar_users]
    recommendations = list(filter(lambda x: x is not None, recommendations))

    needed_recommendations = 5 - len(recommendations)

    # Add additional recommendations from history if needed
    if needed_recommendations > 0:
        recommendations += list(recommendations_from_history[:needed_recommendations])

    # Return the final list of recommendations
    return recommendations







