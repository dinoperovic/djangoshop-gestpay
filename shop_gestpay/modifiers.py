# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.utils.translation import ugettext_lazy as _
from shop.modifiers.base import PaymentModifier
from shop.rest.serializers import ExtraCartRow
from shop_gestpay.payment import GestPayPayment
from shop_gestpay.settings import COMMISION_PERCENTAGE, MODIFIER_CHOICE_TEXT


class GestPayPaymentModifier(PaymentModifier):
    identifier = GestPayPayment.namespace
    payment_provider = GestPayPayment()
    commision_percentage = COMMISION_PERCENTAGE

    def get_choice(self):
        return (self.identifier, MODIFIER_CHOICE_TEXT)

    def is_disabled(self, cart):
        return cart.total == 0

    def add_extra_cart_row(self, cart, request):
        if not self.is_active(cart) or not self.commision_percentage:
            return
        amount = cart.total * Decimal(self.commision_percentage / 100.0)
        instance = {'label': _("+ %d%% handling fee") % self.commision_percentage, 'amount': amount}
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
        cart.total += amount
