from django import template

register = template.Library()

@register.simple_tag
def get_product_cat(product):
	return product.get_categories().all()[0].name