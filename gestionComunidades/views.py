from django.http import HttpResponse
from django.template import Template, Context
import datetime
from django.template.loader import get_template
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from gestionComunidades.models import RelacionComunidadUsuario, Comunidad
from gestionUsuarios.models import Preferencias, Preferencias_valor
from gestionActividades.models import Actividad
from django.db.models import Q, Count, Max, Aggregate
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.contrib import auth


# Create your views here.
def listar_comunidad(request):
    if request.user.is_authenticated:
        current_user = request.user
        comunidad = RelacionComunidadUsuario.objects.filter(id_integrante_id=current_user.id)
        excluir = []
        for ex in comunidad:
            com = ex.id_comunidad_id
            excluir.append(com)
        nueva_comunidad = Comunidad.objects.filter(~Q(id__in=excluir))
        contexto = {'comunidad':comunidad,'nueva_comunidad':nueva_comunidad}
        return render(request, "comunidad/listar.html",contexto)
    else:
        invitado_comunidad = Comunidad.objects.all().order_by('-id')
        contexto = {'invitado_comunidad':invitado_comunidad}
        return render(request, "comunidad/listar.html",contexto)




def crear_comunidad(request):
    if request.method == 'POST':
        current_user = request.user
        comunidad_titulo = request.POST['titulo']
        comunidad_descripcion = request.POST['descripcion']
        comunidad_imagen = request.FILES['imagenes']
        comunidad_foto_descripcion = request.POST['foto_descripcion']
        fs = FileSystemStorage()
        nombre_imagen = get_random_string(length=32,allowed_chars=datetime.datetime.now().strftime("%d%b%Y%H%M%S%f"))+comunidad_imagen.name
        guardar_imagen = fs.save(nombre_imagen, comunidad_imagen)

        comunidad_integrantes = request.POST['integrantes']
        comunidad_integrantes_split = comunidad_integrantes.split(',')

        comunidad_info = Comunidad(
                titulo=comunidad_titulo, 
                descripcion=comunidad_descripcion,
                imagen_principal=fs.url(guardar_imagen),
                imagen_descripcion=comunidad_foto_descripcion,
                fundador_id=current_user.id)
        comunidad_info.save()

        for x in comunidad_integrantes_split:
            integrante = User.objects.get(username=x)
            relacioncomunidadintegrante_info = RelacionComunidadUsuario(
                id_comunidad_id = comunidad_info.id,
                id_integrante_id = integrante.id
            )
            relacioncomunidadintegrante_info.save()
        relacioncomunidadintegrante_info = RelacionComunidadUsuario(
            id_comunidad_id = comunidad_info.id,
            id_integrante_id = current_user.id
        )
        relacioncomunidadintegrante_info.save()            
        return redirect('/comunidad/crear/?e=1')


    return render(request, "comunidad/crear.html",)


def ver_comunidad(request):
    id_com=request.GET['id']
    comunidad = Comunidad.objects.filter(id=id_com)
    integrantes = RelacionComunidadUsuario.objects.filter(id_comunidad_id=id_com)
    if request.user.is_authenticated:
        current_user = request.user
        miembro = RelacionComunidadUsuario.objects.filter(Q(id_comunidad_id=id_com) & Q(id_integrante_id=current_user.id))
    else:
        miembro = None
    contexto = {'comunidad':comunidad,'integrantes':integrantes, 'miembro':miembro}
    return render(request, "comunidad/ver.html",contexto)




def actividad_comunidad(request):
    if request.user.is_authenticated:
        current_user = request.user

        #Sacamos los ID de las actividades en donde el usuario individualmente está participando
        actividades_agregadas_usuario = Actividad.objects.exclude(id_usuario_id=current_user.id)
        
        #Calculamos donde el usuario está dentro de un colectivo que está haciendo una actividad
        #-----obtengo los id de los colectivos a los que pertenece
        usuario_en_comunidad = RelacionComunidadUsuario.objects.filter(id_integrante_id=current_user.id) 
        #-----obtengo los id de las actividades que está ayudando los id de colectivo que pertenece el usuario 
        actividades_agregadas_comunidad = Actividad.objects.filter(id_comunidad_id__in=usuario_en_comunidad.values_list('id_comunidad_id',flat=True))

        contexto = {'actividades':actividades_agregadas_comunidad}
        return render(request, "comunidad/actividad.html",contexto)
    else:
        return render(request, "comunidad/actividad.html",)