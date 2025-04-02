# your_app/management/commands/import_products_csv.py

import csv
from django.core.management.base import BaseCommand
from home.models import Product  # Replace your_app with your actual app name


class Command(BaseCommand):
    help = "Imports product data from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **options):
        csv_file_path = options["csv_file"]

        try:
            with open(csv_file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Map CSV columns to model fields
                    try:
                        image_links = (
                            [link.strip() for link in row.get("image", "").split(",")]
                            if row.get("image")
                            else []
                        )
                        product_categories = (
                            [
                                category.strip()
                                for category in row.get("product_category", "").split(
                                    ","
                                )
                            ]
                            if row.get("product_category")
                            else []
                        )
                        Product.objects.create(
                            unique_id=row.get(
                                "unique_id"
                            ),  # replace with your column name
                            name=row.get("name"),  # replace with your column name
                            brand=row.get("brand"),  # replace with your column name
                            price=row.get("price"),  # replace with your column name
                            mrp=row.get("mrp"),  # replace with your column name
                            product_category=product_categories,  # replace with your column name. eval is used to convert stringified list to list.
                            description=row.get(
                                "description"
                            ),  # replace with your column name
                            image=image_links,  # replace with your column name
                            quantity=row.get(
                                "quantity"
                            ),  # replace with your column name
                            product_rating=row.get(
                                "product_rating"
                            ),  # replace with your column name
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error importing row: {row}. Error: {e}")
                        )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully imported products from {csv_file_path}"
                )
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found: {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occured: {e}"))
