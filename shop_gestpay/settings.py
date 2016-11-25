# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

# GestPay shop login ID.
SHOP_LOGIN = settings.SHOP_GESTPAY_SHOP_LOGIN

# Set to 'testecomm.sella.it' for testing.
SERVER = getattr(settings, 'SHOP_GESTPAY_SERVER', 'ecomm.sella.it')

# Send buyer name param to GestPay or not.
SEND_BUYER_NAME = getattr(settings, 'SHOP_GESTPAY_SEND_BUYER_NAME', False)

# Send buyer email param to GestPay or not.
SEND_BUYER_EMAIL = getattr(settings, 'SHOP_GESTPAY_SEND_BUYER_EMAIL', False)

# Send language param to GestPay or not.
SEND_LANGUAGE = getattr(settings, 'SHOP_GESTPAY_SEND_LANGUAGE', False)

# Set if a separate payment view should be rendered before sending to GestPay.
PAYMENT_VIEW = getattr(settings, 'SHOP_GESTPAY_PAYMENT_VIEW', False)

# Url of a cart, used to redirect in some cases.
CART_URL = getattr(settings, 'SHOP_GESTPAY_CART_URL', getattr(settings, 'SHOP_CART_URL', 'shop:cart-list'))

# Thank you url, if None latest order is used.
THANK_YOU_URL = getattr(settings, 'SHOP_GESTPAY_THANK_YOU_URL', getattr(settings, 'SHOP_THANK_YOU_URL', None))

# Set to add commision percentage for purchase via GestPay.
COMMISION_PERCENTAGE = getattr(settings, 'SHOP_GESTPAY_COMMISION_PERCENTAGE', None)

# Text displayed as a choice for selecting GestPay payment.
MODIFIER_CHOICE_TEXT = getattr(settings, 'SHOP_GESTPAY_MODIFIER_CHOICE_TEXT', 'GestPay')

# Message added to django messages framework there's a transaction error.
ERROR_MESSAGE = getattr(settings, 'SHOP_GESTPAY_ERROR_MESSAGE', None)

# Message added to django messages framework transaction is successful.
SUCCESS_MESSAGE = getattr(settings, 'SHOP_GESTPAY_SUCCESS_MESSAGE', None)
