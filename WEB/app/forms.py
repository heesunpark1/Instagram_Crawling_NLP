from django import forms

from .models import SentAnalyzer

class SentAnalyzerForm(forms.ModelForm):

    class Meta:
        model = SentAnalyzer
        fields = ('text',)
        help_texts = dict({ 'text': '※ 반드시 공개 계정이여야 분석이 가능합니다.'})
