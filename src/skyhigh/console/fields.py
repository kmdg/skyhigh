__author__ = 'michael'

from django import forms

class ImageModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.image_name or obj.image.name.split('/')[-1]