from django.core.management.base import BaseCommand, CommandError
from myapps.partner.importer import CSVImporter

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+')

	def handle(self, *args, **options):
		for file_path in options['file']:
			importer = CSVImporter(file_path)
			importer.main()
