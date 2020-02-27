from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from CreciendoEnComunidad.views import home
from gestionUsuarios.forms import RegistroForm
from django.contrib.auth.models import User
from django.contrib import auth

# Create your views here.
class RegistroUsuario(CreateView):
    model = User
    template_name = "cuenta/registrar.html"
    form_class = RegistroForm #UserCreationForm
    success_url = reverse_lazy(home)


def logout(request):
    auth.logout(request)
    return redirect('/')