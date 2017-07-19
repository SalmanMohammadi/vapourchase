from oscar.apps.catalogue.models import Product, Category, ProductAttribute,\
                                        ProductClass, ProductCategory,\
                                        ProductAttributeValue, AttributeOptionGroup, AttributeOption
from oscar.apps.partner.models import Partner, StockRecord
from oscar.apps.catalogue.categories import create_from_breadcrumbs

import csv
import hashlib
from decimal import Decimal

class CSVImporter(object):

	def __init__(self, file_path):
		self.file_path = file_path
		self.partner = Partner.objects.filter(name='self_fulfilled')[0]
		self.import_liquid = False

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
				if self.import_liquid:
					self.create_liquid(row)
					print "Successfully created %s" %row[0]
				
	def create_liquid(self, row):
		# 0Name || 1Category || 2Price || 3Strength || 4Size || 5Description || 6PGVG ||7Image
		cat = create_from_breadcrumbs(row[1])
		canonincal_product = self.get_or_create_canonincal_product(row[0], cat, row[5])
		for strength in row[3].split('|'):
			for size in row[4].split('|'):
				upc = self.create_liquid_upc(row[0], cat.name, strength, size)
				product_var = Product.objects.filter(upc = upc)

				if not product_var.exists():
					product_var = Product()
					product_var.parent = canonincal_product
					product_var.upc = upc
					product_var.title = row[0]
					product_var.product_class = self.product_class
					product_var.structure = 'child'
					product_var.save()

					cat_prod = ProductCategory.objects.get_or_create(category_id = cat.id,
														 product_id = product_var.id)[0]
					cat_prod.product = product_var
					cat_prod.category = cat
					cat_prod.is_canonical = True
					cat_prod.save()

					strength_attr = ProductAttributeValue.objects.get_or_create(product = product_var, attribute = self.pa['Strength'])[0]
					strength_attr.value_option = AttributeOption.objects.filter(option = strength)[0]
					strength_attr.save()

					pgvg_attr = ProductAttributeValue.objects.get_or_create(product = product_var, attribute = self.pa['PGVG'])[0]
					pgvg_attr.value_text = row[6]
					pgvg_attr.save()

					size_attr = ProductAttributeValue.objects.get_or_create(product = product_var, attribute = self.pa['Size'])[0]
					size_attr.value_option = AttributeOption.objects.filter(option = size)[0]
					size_attr.save()

					rec = StockRecord.objects.get_or_create(partner_sku = upc,
															partner = self.partner,
															product = product_var)[0]
					rec.price_excl_tax = Decimal(row[2])
					rec.save()
				# else:
				# 	product_var = product_var[0]


		return product_var

		

	#Generic canonical product getter/creater for e liquids.
	def get_or_create_canonincal_product(self, name, category, description):
		UPC = self.create_upc(name, category.name)
		product = Product.objects.get_or_create(upc = UPC, 
												product_class = self.product_class)[0]
		product.title = name
		product.description = description
		product.structure = 'parent'
		product.save()

		strength_attr = ProductAttributeValue.objects.get_or_create(product = product, attribute = self.pa['Strength'])[0]
		strength_attr.save()

		pgvg_attr = ProductAttributeValue.objects.get_or_create(product = product, attribute = self.pa['PGVG'])[0]
		pgvg_attr.save()

		size_attr = ProductAttributeValue.objects.get_or_create(product = product, attribute = self.pa['Size'])[0]
		size_attr.save()

		cat_prod = ProductCategory.objects.get_or_create(category_id = category.id,
														 product_id = product.id)[0]
		cat_prod.product = product
		cat_prod.category = category
		cat_prod.is_canonical = True
		cat_prod.save()
		return product

	#Generic product UPC creator.
	def create_upc(self, name, category):
		return hashlib.md5(name.upper().replace(' ','') + category.upper().replace(' ', '')).hexdigest()

	#UPC creator for E-Liquids
	def create_liquid_upc(self, name, category, strength, size):
		return hashlib.md5(name.upper().replace(' ', '') + category.upper().replace(' ', '') + strength + size).hexdigest()

	#Setting up necessary objects for E-liquids.
	def setup_eliquid(self):
		self.import_liquid = True
		self.product_class = ProductClass.objects.filter(name='E-Liquids')[0]
		self.pa = {"Strength": ProductAttribute.objects.filter(name = 'Strength')[0],
					"Size": ProductAttribute.objects.filter(name = "Size")[0],
					"PGVG": ProductAttribute.objects.filter(name = "PG/VG")[0]}


