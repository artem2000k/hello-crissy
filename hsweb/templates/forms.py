from django.contrib.auth.forms import usercreationform

class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Buyer