# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms


class GestPayForm(forms.Form):
    """
    A base form with required fields for GestPay integration.

    `a`: Shop login.
    `b`: Encrypted string.
    """
    action = None

    a = forms.CharField(widget=forms.HiddenInput)
    b = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, action, a, b, *args, **kwargs):
        super(GestPayForm, self).__init__(*args, **kwargs)
        self.action = action
        self.fields['a'].initial = a
        self.fields['b'].initial = b

    def get_js_expression(self):
        js_expression = """
            (function () {{
              var form = document.createElement('form');
              form.setAttribute('action', '{action}');
              form.setAttribute('method', 'POST');
              var a = document.createElement('input');
              a.setAttribute('type', 'hidden');
              a.setAttribute('name', 'a');
              a.setAttribute('value', '{a}');
              var b = document.createElement('input');
              b.setAttribute('type', 'hidden');
              b.setAttribute('name', 'b');
              b.setAttribute('value', '{b}');
              form.appendChild(a);
              form.appendChild(b);
              document.body.appendChild(form);
              form.submit();
            }})();""".format(action=self.action, a=self['a'].value(), b=self['b'].value())
        return js_expression.replace('  ', '').replace('\n', '')
