from django import forms

class UploadForm(forms.Form):
    file = forms.FileField(label='Select a CSV/Excel file')