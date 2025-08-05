from django import forms

class Step1Form(forms.Form):
    company_name = forms.CharField(label='Name of your product',max_length=100)
    product_description = forms.CharField(label='Discribe your product') 

class Step2Form(forms.Form):
    competitors = forms.CharField(label=' How does your product differ from competitors? ')
    problem_solve = forms.CharField(label='What problem does your product/service solve?') 
#  max_length=200, widget=forms.Textarea(attrs={'rows': 3}
class Step3Form(forms.Form):
    price_category = forms.CharField(label='Price category: your average price')
    customer = forms.CharField(label='Who are you selling your service/product to?')
