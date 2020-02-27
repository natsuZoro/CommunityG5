from django.shortcuts import render
from django.http import HttpResponse
from django.template import Template, Context
import datetime
from gestionActividades.models import RelacionActividadValor, RelacionActividadUsuario, Actividad
from gestionColectivos.models import RelacionColectivoActividad, RelacionColectivoUsuario, Colectivo
from django.template.loader import get_template
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from gestionUsuarios.models import Preferencias, Preferencias_valor
from django.db.models import Q, Count, Max, Aggregate
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.contrib import auth

# Create your views here.

def calificar_participantes(request):
    if request.method == 'POST':
        actividad = request.POST['actividad']
        calificados = request.POST['calificados']
        calificados_split = calificados.split(',')
        for y in calificados_split:
            RelacionActividadUsuario.objects.filter(Q(id_actividad_id=int(actividad)) & Q(id_usuario_id=int(y))).update(realizado=True)

        colectivo = RelacionColectivoUsuario.objects.filter(id_integrante_id=int(y))
        RelacionColectivoActividad.objects.filter(Q(id_actividad_id=int(actividad)) & Q(id_colectivo_id__in=colectivo.values_list('id_colectivo_id',flat=True))).update(calificado=True)
        return redirect('/actividad/listar/')

    else:
        id_act = request.GET['a']
        actividad = Actividad.objects.filter(id=int(id_act))
        colectivo = RelacionColectivoActividad.objects.filter(id_actividad_id=int(id_act))
        integrantes = RelacionActividadUsuario.objects.filter(id_actividad_id=int(id_act))
        valor = RelacionActividadValor.objects.filter(id_actividad_id=int(id_act))
        contexto = {'actividad':actividad,'colectivo':colectivo,'integrantes':integrantes,'valor':valor}
        return render(request, "colectivo/calificar.html",contexto)



def actividad_colectivo(request):
    if request.user.is_authenticated:
        current_user = request.user

        #Sacamos los ID de las actividades en donde el usuario individualmente está participando
        actividades_agregadas_usuario = RelacionColectivoActividad.objects.filter(id_usuario_id=current_user.id)

        #Calculamos donde el usuario está dentro de un colectivo que está haciendo una actividad
        #-----obtengo los id de los colectivos a los que pertenece
        usuario_en_colectivo = RelacionColectivoUsuario.objects.filter(id_integrante_id=current_user.id) 
        #-----obtengo los id de las actividades que está ayudando los id de colectivo que pertenece el usuario 
        actividades_agregadas_colectivo = RelacionColectivoActividad.objects.filter(id_colectivo_id__in=usuario_en_colectivo.values_list('id_colectivo_id',flat=True))

        #-----filtro todas las actividades que no tengan el id de las mismaas que está el colectivo del usuario ayudando
        actividades = Actividad.objects.filter(Q(id__in=actividades_agregadas_usuario.values_list('id_actividad_id',flat=True)) | Q(id__in=actividades_agregadas_colectivo.values_list('id_actividad_id',flat=True)))
        
        tempo1 = RelacionColectivoUsuario.objects.filter(id_integrante_id=current_user.id)
        tempo2 = RelacionColectivoActividad.objects.filter(Q(id_colectivo_id__in=tempo1.values_list('id_colectivo_id',flat=True)) & Q(calificado=True))

        tempo = RelacionColectivoActividad.objects.filter(id_actividad_id__in=actividades.values_list('id',flat=True)).distinct('id_actividad_id').exclude(id_actividad_id__in=tempo2.values_list('id_actividad_id',flat=True))

        contexto = {'actividades':tempo}

        return render(request, "colectivo/actividad.html",contexto)
    else:
        return render(request, "colectivo/actividad.html",)




def listar_colectivo(request):
    #validmos si está logueado
    if request.user.is_authenticated:
        current_user = request.user

        #capturamos todos los colectivos a los que pertenece el usuario
        colectivo = RelacionColectivoUsuario.objects.filter(id_integrante_id=current_user.id)
        excluir = []

        #excluyemos aquellos colectivos en donde está presente el usuario logueado
        for ex in colectivo:
            com = ex.id_colectivo_id
            excluir.append(com)

        #capturamos todos los colectivos a los que NO pertenece el usuario
        nuevo_colectivo = Colectivo.objects.filter(~Q(id__in=excluir))

        #renderizamos
        contexto = {'colectivo':colectivo,'nuevo_colectivo':nuevo_colectivo}
        return render(request, "colectivo/listar.html",contexto)
    else:
        #en caso no estar logeado se lista todos los colectivos
        invitado_colectivo = Colectivo.objects.all().order_by('-id')
        contexto = {'invitado_colectivo':invitado_colectivo}
        return render(request, "colectivo/listar.html",contexto)






def crear_colectivo(request):
    if request.method == 'POST':
        #tomamos el usuario logueado
        current_user = request.user

        #recogemos el contenido del formulario
        colectivo_titulo = request.POST['titulo']
        colectivo_descripcion = request.POST['descripcion']
        colectivo_imagen = request.FILES['imagenes']
        colectivo_foto_descripcion = request.POST['foto_descripcion']

        #guardamos la imagen en el servidor
        fs = FileSystemStorage()
        nombre_imagen = get_random_string(length=32,allowed_chars=datetime.datetime.now().strftime("%d%b%Y%H%M%S%f"))+colectivo_imagen.name
        guardar_imagen = fs.save(nombre_imagen, colectivo_imagen)

        #separamos los integrantes
        colectivo_integrantes = request.POST['integrantes']
        colectivo_integrantes_split = colectivo_integrantes.split(',')

        #elegimos al lider
        colectivo_lider_fundador = request.POST['lider']
        if colectivo_lider_fundador == "0":
            tempo = colectivo_integrantes_split[0]
            integrante = User.objects.get(username=tempo)
            lider = integrante.id
        elif colectivo_lider_fundador == "1":
            lider = current_user.id

        #guardamos los datos recogidos en el modelo Colectivo
        colectivo_info = Colectivo(
                titulo=colectivo_titulo, 
                descripcion=colectivo_descripcion,
                imagen_principal=fs.url(guardar_imagen),
                imagen_descripcion=colectivo_foto_descripcion,
                fundador_id=current_user.id,
                lider_id=lider)
        colectivo_info.save()

        #tomamos el id_colectivo nuevo generado y guardamos sus integrantes
        for x in colectivo_integrantes_split:
            integrante = User.objects.get(username=x)
            relacioncolectivointegrante_info = RelacionColectivoUsuario(
                id_colectivo_id = colectivo_info.id,
                id_integrante_id = integrante.id
            )
            relacioncolectivointegrante_info.save()

        #añadimos por defecto como integrante al creador del colectivo 
        relacioncolectivointegrante_info = RelacionColectivoUsuario(
            id_colectivo_id = colectivo_info.id,
            id_integrante_id = current_user.id
        )
        relacioncolectivointegrante_info.save()
        
        #redireccionamos a la misma pagina con un mensaje de OK
        return redirect('/colectivo/crear/?e=1')

    return render(request, "colectivo/crear.html",)



def ver_colectivo(request):
    id_com=request.GET['id']
    colectivo = Colectivo.objects.filter(id=id_com)
    integrantes = RelacionColectivoUsuario.objects.filter(id_colectivo_id=id_com)
    if request.user.is_authenticated:
        current_user = request.user
        miembro = RelacionColectivoUsuario.objects.filter(Q(id_colectivo_id=id_com) & Q(id_integrante_id=current_user.id))
    else:
        miembro = None
    contexto = {'colectivo':colectivo,'integrantes':integrantes, 'miembro':miembro}
    return render(request, "colectivo/ver.html",contexto)




def valores(request):
    if request.user.is_authenticated:
        current_user = request.user
        tempo1 = RelacionActividadUsuario.objects.filter(Q(id_usuario_id=current_user.id) & Q(realizado=True))
        tempo2 = RelacionActividadValor.objects.filter(id_actividad_id__in=tempo1.values_list('id_actividad_id',flat=True))
        tempo3 = tempo2.values('id_valor_id__titulo').annotate(dcount=Count('id_valor_id')).order_by('-dcount')
        contexto = {'tempo3':tempo3}
        return render(request, "colectivo/valores.html",contexto)
    else:
        return render(request, "colectivo/valores.html",)