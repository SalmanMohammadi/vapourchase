from oscar.apps.catalogue.models import Product, Category, ProductAttribute,\
                                        ProductClass, ProductCategory,\
                                        ProductAttributeValue
from oscar.apps.partner.models import Partner, StockRecord
from oscar.apps.catalogue.categories import create_from_breadcrumbs

import csv

class CSVImporter(object):

	def __init__(self, file_path):
		self.file_path = file_path
		self.partner = Partner.objects.filter(name='self_fulfilled')[0]

	def main(self):
		self.parse_csv()

	def parse_csv(self):
		print "Opening %s..." % self.file_path
		with open(self.file_path, 'r') as file:
			reader = csv.reader(file)
			for row in reader:
				if row[0] == 'E-Liquid':
					self.setup_eliquid()
					continue
				# 0Name || 1Category || 2Price || 3Strength || 4Size || 5Description
				cat = create_from_breadcrumbs(row[1])
				UPC = self.create_upc(row[0], cat, row[3], row[4])
				print UPC


	def create_upc(self, name, category, strength, size):
		return name.upper().replace(' ','') + 
				category.name.upper().replace(' ', '') 


	def setup_eliquid(self):
		self.product_class = ProductClass.objects.filter(name='E-Liquids')
		self.pa = {"Strength": ProductAttribute.objects.filter(name = 'Strength')[0],
					"Size": ProductAttribute.objects.filter(name = "Size")[0]}

