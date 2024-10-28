import json
from django.core.management.base import BaseCommand
from api.models import Author, Series, Book

class Command(BaseCommand):
    help = 'Import books from a JSON file along with their authors and series'

    def handle(self, *args, **kwargs):
        with open('./books.json', 'r') as f:
            # Clear existing data (optional)
            Book.objects.all().delete()  # Uncomment if you want to clear old data
            Author.objects.all().delete()  # Uncomment if you want to clear old data
            
            # Create a dictionary to hold author and series instances
            author_cache = {}
            series_cache = {}
            
            batch_size = 1000
            books_to_create = []  # Temporary list to hold books
            count = 0  # Counter for processed entries
            
            for line in f:

                entry = json.loads(line)  # Load each line as a JSON object

                # Get or create the author
                author_name = entry['author_name']
                if author_name not in author_cache:
                    author, created = Author.objects.get_or_create(name=author_name)
                    author_cache[author_name] = author
                else:
                    author = author_cache[author_name]

                # Get or create the series
                series_title = entry.get('series')  # Using 'series' field for title
                if series_title:
                    if series_title not in series_cache:
                        series, created = Series.objects.get_or_create(name=series_title)
                        series_cache[series_title] = series
                    else:
                        series = series_cache[series_title]
                else:
                    series = None  # No series information

                # Prepare the book entry
                books_to_create.append(
                    Book(
                        title=entry['title'],
                        author=author,
                        average_rating=entry.get('average_rating', None),
                        series=series
                    )
                )

                # If we've reached the batch size, bulk create the books
                if len(books_to_create) >= batch_size:
                    Book.objects.bulk_create(books_to_create)
                    books_to_create.clear()  # Clear the list for the next batch
                
                count += 1  # Increment the counter

            # Create any remaining books if under the limit
            if books_to_create:
                Book.objects.bulk_create(books_to_create)

        self.stdout.write(self.style.SUCCESS('Books imported successfully with authors and series'))
