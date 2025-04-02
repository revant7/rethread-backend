# myapp/management/commands/populate_fts.py
from django.core.management.base import BaseCommand
from django.db import connection
from home.models import Product


class Command(BaseCommand):
    help = "Populate the home_product_fts table"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM home_product_fts")  # clear the fts table first.
            for product in Product.objects.all():
                cursor.execute(
                    """
                    INSERT INTO home_product_fts (unique_id, name, description)
                    VALUES (?, ?, ?)
                    """,
                    (product.unique_id, product.name, product.description),
                )

        self.stdout.write(self.style.SUCCESS("Successfully populated home_product_fts"))
