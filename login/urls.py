from django.urls import path
from .views import CustomLogin, update_activity
from login import views


app_name = 'login'
urlpatterns = [
    path('', views.CustomLogin, name='login'),
    path('register', RegisterForm, name="register"),

]

#urlpatterns = [
#    path('', login, name='login'),
#    #path('register', RegisterForm, name="register"),
#]