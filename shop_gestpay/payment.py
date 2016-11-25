# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from decimal import Decimal

import gestpypay

from django.conf import settings
from django.conf.urls import url
from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django_fsm import transition
from shop.models.cart import CartModel
from shop.models.order import OrderModel, OrderPayment
from shop.payment.base import PaymentProvider
from shop_gestpay import settings as sgs
from shop_gestpay.forms import GestPayForm

LANGUAGE_CODES = {
    'it': '1',
    'en': '2',
    'es': '3',
    'fr': '4',
    'de': '5',
}

CURRENCY_CODES = {
    'AUD': '109',
    'BRL': '234',
    'CAD': '12',
    'CHF': '3',
    'CYN': '144',
    'CZK': '223',
    'DKK': '7',
    'EUR': '242',
    'GBP': '2',
    'HKD': '103',
    'HUF': '153',
    'ITL': '18',
    'JPY': '71',
    'NOK': '8',
    'PLN': '237',
    'RUB': '244',
    'SEK': '9',
    'SGD': '124',
    'USD': '1',
}

logger = logging.getLogger(__name__)


class GestPayPayment(PaymentProvider):
    namespace = 'gestpay'

    def get_urls(self):
        return [
            url(r'^$', self.payment_view, name='payment'),
            url(r'^return/$', self.return_view, name='return'),
            url(r'^error/$', self.error_view, name='error'),
            url(r'^success/$', self.success_view, name='success'),
        ]

    def get_payment_request(self, cart, request):
        """
        Redirect to `payment_view` or directly post to GestPay.
        """
        if sgs.PAYMENT_VIEW:
            return 'window.location.href="%s";' % reverse('shop:%s:payment' % self.namespace)

        try:
            cart.update(request)
            assert cart.extra.get('payment_modifier') == self.namespace
            assert cart.total > 0
        except AssertionError:
            return redirect(sgs.CART_URL)

        form = GestPayPayment.process_payment(cart, request)
        return form.get_js_expression()

    @classmethod
    def get_handler(cls):
        """
        Returns a GestPay handler.
        """
        handler = gestpypay.GestPayCrypt()
        handler.debug = settings.DEBUG
        handler.ProtocolAuthServer = 'https'
        handler.DomainName = sgs.SERVER
        handler.FullUrl = '%s://%s/pagam/pagam.aspx' % (handler.ProtocolAuthServer, handler.DomainName)
        return handler

    @classmethod
    def process_payment(cls, cart, request):
        """
        Returns a form for the current cart do submited or presented to the
        customer in a payment view.
        """
        handler = cls.get_handler()
        handler.SetShopLogin(sgs.SHOP_LOGIN)
        handler.SetCurrency(CURRENCY_CODES.get(cart.total.currency))
        handler.SetAmount('{:.2f}'.format(cart.total.as_decimal()))
        handler.SetShopTransactionID(str(cart.id))

        # Send optional root parameters as defined in settings. When enabled
        # GestPay will require you to configure the additional parameters in
        # their 'BackOffice' admin.
        if sgs.SEND_BUYER_NAME:
            name = '{} {}'.format(cart.customer.first_name, cart.customer.last_name).strip()
            name = name or (cart.billing_address.name if cart.billing_address else cart.shipping_address.name)
            handler.SetBuyerName(name)
        if sgs.SEND_BUYER_EMAIL:
            handler.SetBuyerEmail(cart.customer.email)
        if sgs.SEND_LANGUAGE and request.LANGUAGE_CODE in LANGUAGE_CODES:
            handler.SetLanguage(LANGUAGE_CODES[request.LANGUAGE_CODE])

        if not handler.Encrypt():
            msg = 'GestPay encrypting error: [%s] %s' % (handler.GetErrorCode(), handler.GetErrorDescription())
            logger.error(msg)
            raise SuspiciousOperation(msg)

        return GestPayForm(action=handler.FullUrl, a=handler.GetShopLogin(), b=handler.GetEncryptedString())

    @classmethod
    def decrypt(cls, request):
        """
        Returns a handler with string decrypted.
        """
        shop_login = request.GET['a']
        encrypted_string = request.GET['b']

        handler = cls.get_handler()
        handler.SetShopLogin(shop_login)
        handler.SetEncryptedString(encrypted_string)

        if not handler.Decrypt():
            msg = 'GestPay decrypting error: [%s] %s' % (handler.GetErrorCode(), handler.GetErrorDescription())
            logger.error('{0}; ShopLogin: {1}; EncryptedString: {2}'.format(msg, shop_login, encrypted_string))
            raise SuspiciousOperation(msg)
        return handler

    @classmethod
    @method_decorator(never_cache)
    def payment_view(cls, request):
        """
        View that handles payment if PAYMENT_VIEW setting is True.
        Here is where the customer get's to take a final look at the cart
        before completing the purchase.
        """
        try:
            assert sgs.PAYMENT_VIEW is True
            cart = CartModel.objects.get_from_request(request)
            cart.update(request)
            assert cart.extra.get('payment_modifier') == cls.namespace
            assert cart.total > 0
        except (CartModel.DoesNotExist, AssertionError):
            return redirect(sgs.CART_URL)

        form = cls.process_payment(cart, request)
        return render(request, 'shop_gestpay/payment.html', {'form': form, 'cart': cart})

    @classmethod
    @method_decorator(never_cache)
    def return_view(cls, request):
        """
        View that is accessed by the GestPay when the transaction is complete.
        Here the data returned is validated and cart is either converted
        to an order or gets deleted. Response with result is sent back to
        GestPay where the customer is redirected to error or success url.
        """
        try:
            handler = cls.decrypt(request)
        except KeyError:
            return redirect(sgs.CART_URL)

        try:
            cart = CartModel.objects.get(id=handler.GetShopTransactionID())
        except CartModel.DoesNotExist:
            msg = "Cart with id %s doesn't exist" % handler.GetShopTransactionID()
            logger.error(msg)
            raise SuspiciousOperation(msg)

        result = handler.GetTransactionResult()
        logger.info('GestPay response: {0}; ShopLogin: {1}; EncryptedString: {2}'.format(
            result, handler.GetShopLogin(), handler.GetEncryptedString()))

        # Result can be OK, KO or XX. Which stands for positive, negative or
        # suspended transaction. Here an order gets a created.
        if result == 'OK':
            order = OrderModel.objects.create_from_cart(cart, request)
            order.add_gestpay_payment(handler)
            order.extra['transaction_id'] = handler.GetShopTransactionID()
            order.save()
            cart.delete()
        if result == 'KO':
            cart.empty()
        if result == 'XX':
            pass
        return HttpResponse('Received transaction result: %s' % result)

    @classmethod
    @method_decorator(never_cache)
    def error_view(cls, request):
        """
        There has been an error in transaction. Render the error template.
        """
        try:
            handler = cls.decrypt(request)
        except KeyError:
            return redirect(sgs.CART_URL)

        if sgs.ERROR_MESSAGE:
            messages.error(request, sgs.ERROR_MESSAGE)
        return render(request, 'shop_gestpay/error.html', {
            'error_code': handler.GetErrorCode(),
            'error_description': handler.GetErrorDescription(),
        })

    @classmethod
    @method_decorator(never_cache)
    def success_view(cls, request):
        """
        Payment is completed successfully. Redirect to the latest order.
        """
        if sgs.SUCCESS_MESSAGE:
            messages.success(request, sgs.SUCCESS_MESSAGE)
        if sgs.THANK_YOU_URL:
            return redirect(sgs.THANK_YOU_URL)
        return HttpResponseRedirect(OrderModel.objects.get_latest_url())


class GestPayWorkflowMixin(object):
    """
    A workflow mixin to add transitons for GestPay payment.
    """
    TRANSITION_TARGETS = {
        'paid_with_gestpay': _('Paid using GestPay'),
    }

    @transition(field='status', source=['created'], target='paid_with_gestpay', custom=dict(admin=False))
    def add_gestpay_payment(self, handler):
        """
        Adds a payment object to the order for the given GestPay handler.
        """
        transaction_id = handler.GetBankTransactionID()
        payment = OrderPayment(order=self, transaction_id=transaction_id, payment_method=GestPayPayment.namespace)
        currency = list(CURRENCY_CODES.keys())[list(CURRENCY_CODES.values()).index(handler.GetCurrency())]
        assert payment.amount.currency == currency, 'Currency mismatch'
        payment.amount = payment.amount.__class__(Decimal(handler.GetAmount()))
        payment.save()

    def is_fully_paid(self):
        return super(GestPayWorkflowMixin, self).is_fully_paid()

    @transition(field='status', source='paid_with_gestpay', conditions=[is_fully_paid], custom=dict(
                admin=True, button_name=_('Acknowledge Payment')))
    def acknowledge_gestpay_payment(self):
        """
        Acknowledge payment when the order has been paid with GestPay.
        """
        self.acknowledge_payment()
