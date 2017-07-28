from django import forms
from oscar.forms import widgets
from django import forms
from django.conf import settings
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_model
from oscar.forms import widgets

Line = get_model('basket', 'line')
Basket = get_model('basket', 'basket')
Product = get_model('catalogue', 'product')

class AddToBasketForm(forms.Form):
    quantity = forms.IntegerField(initial=1, min_value=1, label=_('Quantity'))

    def __init__(self, basket, product, *args, **kwargs):
        # Note, the product passed in here isn't necessarily the product being
        # added to the basket. For child products, it is the *parent* product
        # that gets passed to the form. An optional product_id param is passed
        # to indicate the ID of the child product being added to the basket.
        self.basket = basket
        self.parent_product = product

        super(AddToBasketForm, self).__init__(*args, **kwargs)

        # Dynamically build fields
        if product.is_parent:
            self._create_parent_product_fields(product)

    # Dynamic form building methods

    def _create_parent_product_fields(self, product):
        """
        Adds the fields for a "group"-type product (eg, a parent product with a
        list of children.
        Currently requires that a stock record exists for the children
        """
        self.choices = {}
        for attr in product.attribute_values.all():
            if attr.attribute.type == 'option':
                self.choices[attr.attribute.__str__()] =  []

        for child in product.children.all():
            for attr_value in child.attribute_values.all():
                if attr_value.attribute.__str__() in self.choices:
                    if (attr_value.value_option.__str__(), attr_value.value_option.__str__()) not in self.choices[attr_value.attribute.__str__()]:
                        self.choices[attr_value.attribute.__str__()].append((attr_value.value_option.__str__(), attr_value.value_option.__str__()))

        for key in self.choices:
            self.choices[key].sort(key=lambda tup: tup[1]) 
            self.fields[key] = forms.ChoiceField(
                choices=tuple(self.choices[key]), label= _(key),
                widget=forms.RadioSelect(), required = True)

    def get_product(self, parent, options):

        for child in parent.children.all():
            product = child
            for attr_value in child.attribute_values.all():
                if attr_value.value_option.__str__() not in options and attr_value.attribute.type == 'option':
                    product = None
            if product is not None:
                break
        return product
            
    def clean_quantity(self):
        # Check that the proposed new line quantity is sensible
        qty = self.cleaned_data['quantity']
        basket_threshold = settings.OSCAR_MAX_BASKET_QUANTITY_THRESHOLD
        if basket_threshold:
            total_basket_quantity = self.basket.num_items
            max_allowed = basket_threshold - total_basket_quantity
            if qty > max_allowed:
                raise forms.ValidationError(
                    _("Due to technical limitations we are not able to ship"
                      " more than %(threshold)d items in one order. Your"
                      " basket currently has %(basket)d items.")
                    % {'threshold': basket_threshold,
                       'basket': total_basket_quantity})
        return qty

    @property
    def product(self):
        """
        The actual product being added to the basket
        """
        # Note, the child product attribute is saved in the clean_child_id
        # method
        return getattr(self, 'child_product', self.parent_product)

    def clean(self):
        options = []
        for key in self.choices:
            options.append(self.cleaned_data[key])
        self.child_product = self.get_product(self.parent_product, options)
        info = self.basket.strategy.fetch_for_product(self.product)

        # Check currencies are sensible
        if (self.basket.currency and
                info.price.currency != self.basket.currency):
            raise forms.ValidationError(
                _("This product cannot be added to the basket as its currency "
                  "isn't the same as other products in your basket"))

        # Check user has permission to add the desired quantity to their
        # basket.
        current_qty = self.basket.product_quantity(self.product)
        desired_qty = current_qty + self.cleaned_data.get('quantity', 1)
        is_permitted, reason = info.availability.is_purchase_permitted(
            desired_qty)
        if not is_permitted:
            raise forms.ValidationError(reason)

        return self.cleaned_data


class SimpleAddToBasketForm(AddToBasketForm):
    """
    Simplified version of the add to basket form where the quantity is
    defaulted to 1 and rendered in a hidden widget
    Most of the time, you won't need to override this class. Just change
    AddToBasketForm to change behaviour in both forms at once.
    """

    def __init__(self, *args, **kwargs):
        super(SimpleAddToBasketForm, self).__init__(*args, **kwargs)
        if 'quantity' in self.fields:
            self.fields['quantity'].initial = 1


