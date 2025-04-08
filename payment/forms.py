# forms.py

from django import forms

class PaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Amount $$$")
    currency = forms.ChoiceField(
        choices=[('btc', 'Bitcoin'), ('eth', 'Ethereum'), ('usdt', 'Usdt')],
        label="Payment Currency"
    )
