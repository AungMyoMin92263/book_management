import json
from django.core.management.base import BaseCommand
from api.models import Series

class Command(BaseCommand):
    help = 'Import series from a JSON file'

    def handle(self, *args, **kwargs):
        with open('./series.json', 'r') as f:
            # Clear existing series (optional)
            Series.objects.all().delete()
            
            batch_size = 1000
            series_to_create = []  # Temporary list to hold series
            count = 0  # Counter for processed entries

            for line in f:

                entry = json.loads(line)  # Load each line as a JSON object
                
                # Prepare the series entry
                series_to_create.append(
                    Series(
                        name=entry['title'],
                    )
                )

                # If we've reached the batch size, bulk create the series
                if len(series_to_create) >= batch_size:
                    Series.objects.bulk_create(series_to_create)
                    series_to_create.clear()  # Clear the list for the next batch
                
                count += 1  # Increment the counter

            # Create any remaining series if under the limit
            if series_to_create:
                Series.objects.bulk_create(series_to_create)

        self.stdout.write(self.style.SUCCESS('Series imported successfully'))
