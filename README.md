# djangoshop-gestpay

[![PyPI version](https://img.shields.io/pypi/v/djangoshop-gestpay.svg)](https://pypi.python.org/pypi/djangoshop-gestpay)

**[GestPay](https://www.gestpay.it) Payment Integration for [djangoSHOP](http://www.django-shop.org).**

---

## Requirements

* [django-shop]
* [gestpypay]

## Installation

Install using *pip*:

```bash
pip install djangoshop-gestpay
```

Add the following to your settings:

```python
INSTALLED_APPS += ['shop_gestpay']
SHOP_CART_MODIFIERS += ['shop_gestpay.modifiers.GestPayPaymentModifier']
SHOP_ORDER_WORKFLOWS += ['shop_gestpay.payment.GestPayWorkflowMixin']
SHOP_GESTPAY_SHOP_LOGIN = '<shopLogin>'  # GestPay shop login ID.
```

Additional settings with defaults:

```python
SHOP_GESTPAY_SERVER = 'ecomm.sella.it'  # Set to 'testecomm.sella.it' for testing.
SHOP_GESTPAY_SEND_BUYER_NAME = False  # Send buyer name param to GestPay or not.
SHOP_GESTPAY_SEND_BUYER_EMAIL = False  # Send buyer email param to GestPay or not.
SHOP_GESTPAY_SEND_LANGUAGE = False  # Send language param to GestPay or not.
SHOP_GESTPAY_PAYMENT_VIEW = False  # Set if a separate payment view should be rendered before sending to GestPay.
SHOP_GESTPAY_CART_URL = SHOP_CART_URL = 'shop:cart-list'  # Url of a cart, used to redirect in some cases.
SHOP_GESTPAY_THANK_YOU_URL = SHOP_THANK_YOU_URL = None  # Thank you url, if None latest order is used.
SHOP_GESTPAY_COMMISION_PERCENTAGE = None  # Set to add commision percentage for purchase via GestPay.
SHOP_GESTPAY_MODIFIER_CHOICE_TEXT = 'GestPay'  # Text displayed as a choice for selecting GestPay payment.
SHOP_GESTPAY_ERROR_MESSAGE = None  # Message added to django messages framework there's a transaction error.
SHOP_GESTPAY_SUCCESS_MESSAGE = None  # Message added to django messages framework transaction is successful.
```


[django-shop]: https://github.com/awesto/django-shop
[gestpypay]: https://github.com/giefferre/gestpypay
