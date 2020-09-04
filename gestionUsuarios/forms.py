
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class RegistroForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={
            'class':'form-control',
            'maxlength':'150',
        }
    ),label='Escribe un nombre de usuario')
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={
            'class':'form-control',
            'maxlength':'30',
        }
    ),label='Tu primer nombre')

    last_name = forms.CharField(widget=forms.TextInput(
        attrs={
            'class':'form-control',
            'maxlength':'150',
        }
    ),label='Tus apellidos')
    email = forms.CharField(widget=forms.TextInput(
        attrs={
            'class':'form-control',
            'type':'email',
            'maxlength':'254',
        }
    ),label='Un correo electrónico')
    password1 = forms.CharField(widget=forms.TextInput(
        attrs={
            'class':'form-control',
            'type':'password',
            'maxlength':'32',
            'minlength':'8',
        }
    ),label='Una contraseña',help_text='''
    <ul>
    <li>Su contraseña no puede ser muy similar a su otra información personal.</li>
    <li>Su contraseña debe contener al menos 8 caracteres.</li>
    <li>Su contraseña no puede ser una contraseña de uso común.</li>
    <li>Su contraseña no puede ser completamente numérica.</li>
    </ul>''')
    password2 = forms.CharField(widget=forms.TextInput(
        attrs={
            'class':'form-control',
            'type':'password',
            'maxlength':'32',
            'minlength':'8',
        }
    ),label='Repita la contraseña',help_text='Ingrese la misma contraseña que antes, para la verificación.')
    class Meta:
        model = User
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electronico',
        }
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ] 