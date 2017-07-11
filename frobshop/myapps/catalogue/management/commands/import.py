from django.core.management.base import BaseCommand, CommandError
import csv



class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+')

	def handle(self, *args, **options):
		for file_path in options['file']:
			print "Opening %s..." % file_path
