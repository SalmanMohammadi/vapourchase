import json

from django import shortcuts
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, View
from extra_views import ModelFormSetView

from oscar.apps.basket import signals
from oscar.core import ajax
from oscar.core.compat import user_is_authenticated
from oscar.core.loading import get_class, get_classes, get_model
from oscar.core.utils import redirect_to_referrer, safe_referrer

Applicator = get_class('offer.applicator', 'Applicator')
(BasketLineForm, AddToBasketForm, BasketVoucherForm, SavedLineForm) = get_classes(
    'basket.forms', ('BasketLineForm', 'AddToBasketForm',
                     'BasketVoucherForm', 'SavedLineForm'))
OrderTotalCalculator = get_class(
    'checkout.calculators', 'OrderTotalCalculator')
BasketMessageGenerator = get_class('basket.utils', 'BasketMessageGenerator')

class BasketAddView(FormView):

    form_class = AddToBasketForm
    product_model = get_model('catalogue', 'product')
    add_signal = signals.basket_addition
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        self.product = shortcuts.get_object_or_404(
            self.product_model, pk=kwargs['pk'])
        return super(BasketAddView, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(BasketAddView, self).get_form_kwargs()
        kwargs['basket'] = self.request.basket
        kwargs['product'] = self.product
        return kwargs

    def form_invalid(self, form):
        msgs = []
        for error in form.errors.values():
            msgs.append(error.as_text())
        clean_msgs = [m.replace('* ', '') for m in msgs if m.startswith('* ')]
        messages.error(self.request, ",".join(clean_msgs))

        return redirect_to_referrer(self.request, 'basket:summary')

    def form_valid(self, form):
        offers_before = self.request.basket.applied_offers()

        self.request.basket.add_product(
            form.product, form.cleaned_data['quantity'])

        messages.success(self.request, self.get_success_message(form),
                         extra_tags='safe noicon')

        # Check for additional offer messages
        BasketMessageGenerator().apply_messages(self.request, offers_before)

        # Send signal for basket addition
        self.add_signal.send(
            sender=self, product=form.product, user=self.request.user,
            request=self.request)

        return super(BasketAddView, self).form_valid(form)

    def get_success_message(self, form):
        return render_to_string(
            'basket/messages/addition.html',
            {'product': form.product,
             'quantity': form.cleaned_data['quantity']})

    def get_success_url(self):
        post_url = self.request.POST.get('next')
        if post_url and is_safe_url(post_url, self.request.get_host()):
            return post_url
        return safe_referrer(self.request, 'basket:summary')
        def form_valid(self, form):
                offers_before = self.request.basket.applied_offers()

                self.request.basket.add_product(
                    form.product, form.cleaned_data['quantity'])

                messages.success(self.request, self.get_success_message(form),
                                 extra_tags='safe noicon')

                # Check for additional offer messages
                BasketMessageGenerator().apply_messages(self.request, offers_before)

                # Send signal for basket addition
                self.add_signal.send(
                    sender=self, product=form.product, user=self.request.user,
                    request=self.request)

                return super(BasketAddView, self).form_valid(form)

