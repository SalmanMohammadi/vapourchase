from django.core.management.base import BaseCommand, CommandError
from myapps.partner.importer import CSVImporter

from oscar.apps.catalogue.models import Product, Category, ProductAttribute,\
                                        ProductClass, ProductCategory,\
                                        ProductAttributeValue, AttributeOptionGroup, AttributeOption

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+')
		parser.add_argument(
            '--update',
            action='store_true',
            dest='update',
            default=False,
            help='Update product',
        )

	def handle(self, *args, **options):
		for file_path in options['file']:
			importer = CSVImporter(file_path, options['update'])
			importer.main()