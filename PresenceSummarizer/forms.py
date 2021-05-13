from django import forms
from .models import *

class RequestForm(forms.ModelForm):
    class Meta:
        model = ScanRequest
        fields = ['name', 'img' , 'vid']