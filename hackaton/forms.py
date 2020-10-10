from django import forms
from .models import Pyme

class PymeDocumentForm(forms.ModelForm):

    pyme_document = forms.FileField()
    pyme_name =  forms.CharField(max_length=200)

    class Meta:
        model = Pyme
        fields = ('pyme_name', 'pyme_document',)
