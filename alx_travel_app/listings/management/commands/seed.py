from django.core.management.base import BaseCommand
from django_seed import Seed
from listings.models import Listing
import random

class Command(BaseCommand):
    help = "Seed the database with sample listings"

    def handle(self, *args, **kwargs):
        seeder = Seed.seeder()

        # Seed 10 sample listings
        seeder.add_entity(Listing, 10, {
            'price_per_night': lambda x: random.randint(50, 500),
        })

        inserted_pks = seeder.execute()
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(inserted_pks[Listing])} listings successfully!"))
