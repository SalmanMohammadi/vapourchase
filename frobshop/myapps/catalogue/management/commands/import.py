from django.core.management.base import BaseCommand, CommandError
import csv
from oscar.apps.catalogue.models import Product, Category, ProductAttribute,\
                                        ProductClass, ProductCategory,\
                                        ProductAttributeValue
from oscar.apps.partner.models import Partner, StockRecord


class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+')

	def handle(self, *args, **options):
		for file_path in options['file']:
			print "Opening %s..." % file_path
