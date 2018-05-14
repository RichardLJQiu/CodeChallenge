from django import forms

class PostForm(forms.Form):
    route = forms.CharField(label='Enter Post Route', help_text='Custom CMS',
                            widget=forms.TextInput(attrs={'cols': "50", 'rows': "10", 'class': 'form-control'}))

class GetForm(forms.Form):
    route = forms.CharField(label='Enter Query Route', help_text='Custom CMS',
                            widget=forms.TextInput(attrs={'cols': "50", 'rows': "10", 'class': 'form-control'}))
