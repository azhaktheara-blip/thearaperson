from django import forms
from .models import ContactMessage
class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    class Meta:
        model=ContactMessage
        fields=['name','email','subject','budget','message']
    def clean_message(self):
        value=self.cleaned_data['message'].strip()
        if len(value)<20: raise forms.ValidationError('Please share at least 20 characters about your project.')
        return value
    def clean_name(self):
        value=self.cleaned_data['name'].strip()
        if len(value)<2: raise forms.ValidationError('Please enter your name (at least 2 characters).')
        return value
