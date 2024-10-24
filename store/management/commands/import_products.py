# Import necessary modules
import pandas as pd
from django.core.management.base import BaseCommand
from store.models import Product, Category

class Command(BaseCommand):
    help = 'Import products from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str)

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        try:
            # Read the Excel file
            df = pd.read_excel(excel_file)

            # Print the columns to check names
            print("Columns in the Excel file:", df.columns.tolist())

            # Iterate through the DataFrame and create products
            for index, row in df.iterrows():
                name = row['Name']  # Adjusted to match Excel column name
                price = row['Price ($)']  # Adjusted to match Excel column name
                category_name = row['Category']  # Adjusted to match Excel column name
                description = row.get('Description', '')  # Adjusted to match Excel column name                image = models.ImageField(upload_to='uploads/products/', blank=True, null=True)
                # Get or create category
                category, created = Category.objects.get_or_create(name=category_name)

                # Create product
                Product.objects.create(name=name, price=price, category=category, description=description)

            self.stdout.write(self.style.SUCCESS('Products imported successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing products: {e}'))
