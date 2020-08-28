"""CreciendoEnComunidad URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from CreciendoEnComunidad.views import home, buscar_palabra
from gestionUsuarios.views import logout
from gestionActividades.views import unirse_actividad, listar_actividad, ver_actividad, crear_actividad, categoria, culminar_actividad, actividad_certificado, actividades_realizadas, cambiarDist,cambiarProv
from gestionComunidades.views import listar_comunidad, crear_comunidad, ver_comunidad, actividad_comunidad
from gestionColectivos.views import listar_colectivo, crear_colectivo, ver_colectivo, actividad_colectivo, calificar_participantes, valores

from django.conf import settings
from django.conf.urls.static import static
from gestionUsuarios.views import RegistroUsuario
from django.contrib.auth.views import logout_then_login, login_required, LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home),
    path('actividad/listar/',listar_actividad),
    path('actividad/ver/',ver_actividad),
    path('actividad/crear/',crear_actividad),
    path('actividad/categoria/',categoria),
    path('actividad/culminar/',culminar_actividad), 
    path('actividad/certificado/',actividad_certificado), 

    path('comunidad/listar/',listar_comunidad),
    path('comunidad/crear/',crear_comunidad),
    path('comunidad/ver/',ver_comunidad),
    path('comunidad/actividad/',actividad_comunidad),

    path('colectivo/listar/',listar_colectivo),
    path('colectivo/crear/',crear_colectivo),
    path('colectivo/ver/',ver_colectivo),
    path('colectivo/actividad/',actividad_colectivo),
    path('colectivo/calificar/',calificar_participantes),
    path('colectivo/realizadas/',actividades_realizadas), 
    path('colectivo/valores/',valores),

    path('buscar/palabra/',buscar_palabra),

    path('cuenta/registrar/', RegistroUsuario.as_view()),
    path('cuenta/login/', LoginView.as_view(template_name='cuenta/login.html')),
    path('cuenta/logout/', logout),

    path('actividad/unirse/', unirse_actividad),

    path('cambiarProv/',cambiarProv),
    path('cambiarDist/',cambiarDist)

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)