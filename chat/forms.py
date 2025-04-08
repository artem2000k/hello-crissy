from django import forms
from .models import Interest, UserInterest


class UserInterestForm(forms.ModelForm):
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = UserInterest
        fields = ['interests']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Получаем пользователя
        super().__init__(*args, **kwargs)
        
        # Артем: Закомментил из-за не надобности, думаю можно это вообще стереть
        # if self.user:
        #     # Исключаем интересы, которые у пользователя уже есть
        #     self.fields['interests'].queryset = Interest.objects.exclude(
        #         id__in=self.user.user_interests.values_list('interest__id', flat=True)
        #     )

    def clean_interests(self):
        selected_interests = self.cleaned_data['interests']
        current_interest_count = self.user.user_interests.count()  # Считаем текущее количество интересов у пользователя

        if len(selected_interests) > 10:
            raise forms.ValidationError("Вы не можете выбрать более 10 интересов.")

        return selected_interests
