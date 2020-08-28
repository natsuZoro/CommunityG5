from django.http import HttpResponse
from django.template import Template, Context
import datetime
from django.template.loader import get_template
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from gestionUsuarios.models import Preferencias, Preferencias_valor
from gestionComunidades.models import RelacionComunidadUsuario, Comunidad
from gestionActividades.models import Valor, Departamento, Provincia, Distrito, Categoria, Actividad, RelacionActividadUsuario, RelacionActividadValor
from gestionColectivos.models import RelacionColectivoActividad, RelacionColectivoUsuario
from django.db.models import Q, Count, Max, Aggregate
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.contrib import auth
from datetime import datetime
from django.views.generic import View

# Create your views here.
def actividad_certificado(request):
    if request.user.is_authenticated:
        id_act = request.GET['c']
        id_use = request.user.id
        valores = RelacionActividadValor.objects.filter(id_actividad_id=int(id_act))
        actividad = Actividad.objects.filter(id=int(id_act))
        usuario = User.objects.filter(id=int(id_use))
        colectivo_pertenece = RelacionColectivoUsuario.objects.filter(id_integrante_id=int(id_use))
        colectivo = RelacionColectivoActividad.objects.filter(Q(id_actividad_id=int(id_act)) & Q(id_colectivo_id__in=colectivo_pertenece.values_list('id_colectivo_id',flat=True))).distinct('id_colectivo_id')
        fecha = RelacionActividadUsuario.objects.filter(Q(id_actividad_id=int(id_act)) & Q(id_usuario_id=int(id_use)))

        contexto = {'colectivo':colectivo,'usuario':usuario,'valores':valores,'actividad':actividad,'fecha':fecha}
        return render(request, "actividad/certificado.html",contexto)
    else:
        return redirect('/')
    



def actividades_realizadas(request):
    current_user = request.user
    usuario = current_user.id
    actividades = RelacionActividadUsuario.objects.filter(Q(id_usuario_id=usuario) & Q(realizado=True))
    contexto = {'actividades':actividades}
    return render(request, "colectivo/realizadas.html",contexto)





def unirse_actividad(request):
    if request.method == 'POST':
        #tomamos los dos valores del formulario
        actividad = int(request.POST['actividad'])
        colectivo = int(request.POST['colectivo'])

        #en caso quiera apoyar solo le asignamos el id usuario a la tabla
        if colectivo == 0:
            current_user = request.user
            usuario = current_user.id
            colectivo = None
        else:
            usuario = None

        #guardamos los datos
        relacionColectivoActividad_info = RelacionColectivoActividad(
                id_actividad_id=actividad,
                id_colectivo_id=colectivo, 
                id_usuario_id=usuario)
        relacionColectivoActividad_info.save()

        #cargamos a todos los integrantes en la nueva tabla
        if colectivo:
            integrantes = RelacionColectivoUsuario.objects.filter(id_colectivo_id=colectivo)
            usuario = User.objects.filter(id__in=integrantes.values_list("id_integrante_id",flat=True))
            for x in usuario:
                relacionactividadusuario_info = RelacionActividadUsuario(
                    id_actividad_id = actividad,
                    id_usuario_id = x.id
                )
                relacionactividadusuario_info.save()

        #redireccionamos
        return redirect('/actividad/listar/?e=1')

    return redirect('/')




def culminar_actividad(request):
    if request.method == 'POST':
        #tomamos los dos valores del formulario
        actividad = int(request.POST['actividad'])

        #guardamos los datos
        Actividad.objects.filter(id=actividad).update(culminada=True)

        #redireccionamos
        return redirect('/comunidad/actividad/?e=1')

    return redirect('/')




def listar_actividad(request):
    if request.user.is_authenticated:
        current_user = request.user
        existe_preferencias = Preferencias.objects.filter(id_usuario=current_user.id)
        existe_preferencias_valor = Preferencias_valor.objects.filter(id_usuario=current_user.id)

        #Sacamos los ID de las actividades en donde el usuario individualmente está participando
        actividades_agregadas_usuario = RelacionColectivoActividad.objects.exclude(id_usuario_id=current_user.id)
        
        #Calculamos donde el usuario está dentro de un colectivo que está haciendo una actividad
        #-----obtengo los id de los colectivos a los que pertenece
        usuario_en_colectivo = RelacionColectivoUsuario.objects.filter(id_integrante_id=current_user.id) 
        #-----obtengo los id de las actividades que está ayudando los id de colectivo que pertenece el usuario 
        actividades_agregadas_colectivo = RelacionColectivoActividad.objects.filter(id_colectivo_id__in=usuario_en_colectivo.values_list('id_colectivo_id',flat=True))

        #-----filtro todas las actividades que no tengan el id de las mismaas que está el colectivo del usuario ayudando
        actividades = Actividad.objects.filter(Q(id__in=actividades_agregadas_usuario.values_list('id_actividad_id',flat=True)) | Q(id__in=actividades_agregadas_colectivo.values_list('id_actividad_id',flat=True)))

        #Lo contrario (actividades a las que pertenece como usuario o colectivo)
        #actividades = Actividad.objects.exclude(Q(id__in=RelacionColectivoActividad.objects.filter(id_usuario_id=current_user.id).values_list('id_actividad_id',flat=True)) | Q(id__in=colectivo_en_actividad.values_list('id_actividad_id',flat=True)))


        #acumulamos las actividades en donde el usuario es voluntario
        filtro1 = RelacionActividadUsuario.objects.filter(id_usuario_id=current_user.id)

        #acumulamos las actividades en donde el usuario es creador de la comunidad o integrante del colectivo
        tempo1 = RelacionComunidadUsuario.objects.filter(id_integrante_id=current_user.id)
        filtro2 = Actividad.objects.filter(id_comunidad_id__in=tempo1.values_list('id_comunidad_id',flat=True))
        filtro3 = Actividad.objects.filter(id_usuario_id=current_user.id)

        #if existe_preferencias and existe_preferencias_valor:
        #    print ('Usuario con preferencia')
            #Agrupamos por lo más visitados, ordenamos de mayor a menor el conteo y solo tomamos el primer lugar
        #    preferencia_distrito = Preferencias.objects.filter(id_usuario=current_user.id).values('id_distrito_id').annotate(dcount=Count('id_distrito_id')).order_by('-dcount')
        #    preferencia_valor = Preferencias_valor.objects.filter(id_usuario=current_user.id).values('id_valor_id').annotate(dcount=Count('id_valor_id')).order_by('dcount')
        #    preferencia_categoria = Preferencias.objects.filter(id_usuario=current_user.id).values('id_categoria_id').annotate(dcount=Count('id_categoria_id')).order_by('-dcount')
        
            #obtenemos el mas votado del resultado json y hacemos combinaciones
        #    actividad = RelacionActividadValor.objects.distinct('id_actividad_id').filter(Q(id_actividad_id__fecha_fin__gte=datetime.now()) & (Q(id_actividad_id__id_distrito_id=preferencia_distrito[0].get('id_distrito_id')) | Q(id_actividad_id__id_categoria_id=preferencia_categoria[0].get('id_categoria_id')) | Q(id_valor_id=preferencia_valor[0].get('id_valor_id')) )).exclude(id_actividad_id__in=actividades.values_list('id',flat=True)).exclude(Q(id__in=filtro1.values_list('id_actividad_id',flat=True)) | Q(id__in=filtro2.values_list('id',flat=True)) | Q(id__in=filtro3.values_list('id',flat=True)))
        #else:
        #    print ('Usuario sin preferencia')
        actividad = RelacionActividadValor.objects.filter(id_actividad_id__fecha_fin__gte=datetime.now()).distinct('id_actividad_id').order_by('-id_actividad_id').exclude(id_actividad_id__in=actividades.values_list('id',flat=True)).exclude(Q(id__in=filtro1.values_list('id_actividad_id',flat=True)) | Q(id__in=filtro2.values_list('id',flat=True)) | Q(id__in=filtro3.values_list('id',flat=True)))

        #temporal
        actividad = RelacionActividadValor.objects.filter(id_actividad_id__fecha_fin__gte=datetime.now()).distinct('id_actividad_id').order_by('-id_actividad_id')

        #buscamos los colectivos en el que se encuentra el usuario
        colectivos = RelacionColectivoUsuario.objects.filter(id_integrante_id=current_user.id)
    else:
        print ('Usuario de visita')
        #obtenemos solo filtramos actuales y en orden mas reciente
        actividad = RelacionActividadValor.objects.filter(id_actividad_id__fecha_fin__gte=datetime.now()).distinct('id_actividad_id').order_by('-id_actividad_id')
        colectivos = None
    #Condicion: la fecha no sea pasada && (valor = valorMODA || categoria = categoriaMODA || distrito = distritoMODA)
    contexto = {'actividades':actividad,'colectivos':colectivos}
    
    return render(request, "actividad/listar.html",contexto)




def categoria(request):
    id_cat=request.GET['c']
    if request.user.is_authenticated:
        current_user = request.user
        #acumulamos las actividades en donde el usuario es voluntario
        filtro1 = RelacionActividadUsuario.objects.filter(id_usuario_id=current_user.id)

        #acumulamos las actividades en donde el usuario es creador de la comunidad o integrante del colectivo
        tempo1 = RelacionComunidadUsuario.objects.filter(id_integrante_id=current_user.id)
        filtro2 = Actividad.objects.filter(id_comunidad_id__in=tempo1.values_list('id_comunidad_id',flat=True))
        filtro3 = Actividad.objects.filter(id_usuario_id=current_user.id)
        actividad = Actividad.objects.filter(id_categoria_id=id_cat).exclude(Q(id__in=filtro1.values_list('id_actividad_id',flat=True)) | Q(id__in=filtro2.values_list('id',flat=True)) | Q(id__in=filtro3.values_list('id',flat=True)))

        actividad = Actividad.objects.filter(id_categoria_id=id_cat)

    else:
        actividad = Actividad.objects.filter(id_categoria_id=id_cat)

    categoria = Categoria.objects.filter(id=id_cat)
    contexto = {'actividades':actividad, 'categoria':categoria}
    return render(request, "actividad/categoria.html",contexto)





def ver_actividad(request):
    id_act=request.GET['id']
    actividad = Actividad.objects.filter(id=id_act)
    valor = RelacionActividadValor.objects.filter(id_actividad_id=id_act)

    if request.user.is_authenticated:
        current_user = request.user
        for x in actividad: preferencia_categoria = x.id_categoria_id
        for x in actividad: preferencia_distrito = x.id_distrito_id     
        preferencia_info = Preferencias(
                id_usuario=current_user.id, 
                id_categoria_id=preferencia_categoria, 
                id_distrito_id=preferencia_distrito)
        preferencia_info.save()
        for x in valor: 
            preferencia_valor = x.id_valor_id
            preferencia_info_valor = Preferencias_valor(
                    id_usuario=current_user.id, 
                    id_valor_id=preferencia_valor)
            preferencia_info_valor.save()
        
        

        #Sacamos los ID de las actividades en donde el usuario individualmente está participando
        actividades_agregadas_usuario = RelacionColectivoActividad.objects.exclude(id_usuario_id=current_user.id)
        
        #Calculamos donde el usuario está dentro de un colectivo que está haciendo una actividad
        #-----obtengo los id de los colectivos a los que pertenece
        usuario_en_colectivo = RelacionColectivoUsuario.objects.filter(id_integrante_id=current_user.id) 
        #-----obtengo los id de las actividades que está ayudando los id de colectivo que pertenece el usuario 
        actividades_agregadas_colectivo = RelacionColectivoActividad.objects.filter(id_colectivo_id__in=usuario_en_colectivo.values_list('id_colectivo_id',flat=True))

        #-----filtro todas las actividades que no tengan el id de las mismaas que está el colectivo del usuario ayudando
        actividades = Actividad.objects.filter(Q(id__in=actividades_agregadas_usuario.values_list('id_actividad_id',flat=True)) | Q(id__in=actividades_agregadas_colectivo.values_list('id_actividad_id',flat=True)))

        if actividades.filter(id=id_act):
            pertenece = actividades.filter(id=id_act)
        else:
            pertenece = None
    else:
        pertenece = None
        print ('Usuario de visita')

    contexto = {'actividades':actividad,'valores':valor,'pertenece':pertenece}
    return render(request, "actividad/ver.html",contexto)



def crear_actividad(request):
    if request.method == 'POST':
        current_user = request.user
        actividad_titulo = request.POST['titulo']
        actividad_descripcion = request.POST['descripcion']
        actividad_fecha_inicio = request.POST['fecha_inicio']
        actividad_fecha_fin = request.POST['fecha_fin']
        actividad_distrito = request.POST['distrito']
        actividad_direccion = request.POST['direccion']
        actividad_categoria = request.POST['categoria']
        actividad_referencia = request.POST['referencia']

        actividad_comunidad = request.POST['comunidad']
        actividad_valor = request.POST['valores']
        actividad_valor_split = actividad_valor.split(',')

        valores = 0
        for j in actividad_valor_split:
            valores = valores + 1

        print(valores)
        _tempo = '##'+actividad_valor+'##'
        print(_tempo)

        fecha_1 = datetime.strptime(actividad_fecha_inicio, '%Y-%m-%d')
        fecha_2 = datetime.strptime(actividad_fecha_fin, '%Y-%m-%d')
        
        if fecha_1 > fecha_2: 
            return redirect('/actividad/crear/?e=4')
        elif fecha_1 < datetime.now():
            return redirect('/actividad/crear/?e=4')
        else:
            if valores <= 4 and valores > 0 and str(actividad_valor) != '':
                actividad_imagen = request.FILES['imagenes']
                actividad_foto_descripcion = request.POST['foto_descripcion']

                formato = ''
                for w in actividad_imagen.name.split('.'):
                    formato = str(w)
                    print(w)

                if formato == 'jpg' or formato == 'png':

                    fs = FileSystemStorage()
                    nombre_imagen = get_random_string(length=32,allowed_chars=datetime.now().strftime("%d%b%Y%H%M%S%f"))+actividad_imagen.name
                    guardar_imagen = fs.save(nombre_imagen, actividad_imagen)

                    #validamos si pertenece a comunidad o a un usuario en particular
                    if int(actividad_comunidad) == 0:
                        id_comunidad = None
                        id_usuario = request.user.id
                    else:
                        id_comunidad = int(actividad_comunidad)
                        id_usuario = None

                    actividad_info = Actividad(
                        titulo=actividad_titulo, 
                        descripcion=actividad_descripcion, 
                        fecha_inicio=actividad_fecha_inicio, 
                        fecha_fin=actividad_fecha_fin, 
                        id_distrito_id=actividad_distrito, 
                        id_categoria_id=actividad_categoria, 
                        direccion=actividad_direccion, 
                        referencia=actividad_referencia,
                        imagen_principal=fs.url(guardar_imagen),
                        imagen_descripcion=actividad_foto_descripcion,
                        id_comunidad_id=id_comunidad,
                        id_usuario_id=id_usuario,
                    )
                    actividad_info.save()

                    for x in actividad_valor_split:
                        relacionActividadValor_info = RelacionActividadValor(
                            id_actividad_id = actividad_info.id,
                            id_valor_id = int(x),
                        )
                        relacionActividadValor_info.save()
                    return redirect('/actividad/crear/?e=1')
                else:
                    return redirect('/actividad/crear/?e=3')
            else:
                return redirect('/actividad/crear/?e=2')


    current_user = request.user
    comunidad = RelacionComunidadUsuario.objects.filter(id_integrante_id=current_user.id)
    valor = Valor.objects.all()
    dep = Departamento.objects.all()
    prov = Provincia.objects.all().select_related('id_departamento')
    categoria = Categoria.objects.all()
    dis = Distrito.objects.all().select_related('id_provincia__id_departamento')

#    for h in dis:
                                        #t = str(h.nombre) + ' '+ str(h.id_provincia.nombre) + ' '+ str(h.id_provincia.id_departamento.nombre)
 #       t = h.id_provincia.id

#    players = Distrito.objects.all().select_related('id_provincia__id_departamento')
#    for player in players:
#        t = player.nombre + ' ' + player.id_provincia.nombre + ' ' + player.id_provincia.id_departamento.nombre
#        print (t)

    contexto = {'dep':dep,'prov':prov, 'dis':dis,'categoria':categoria,'comunidad':comunidad,'valor':valor}
    return render(request,"actividad/crear.html",contexto)




def cambiarProv(request):
    cod_dep = int(request.GET.get('codigo_departamento'))
    prov = Provincia.objects.filter(id_departamento_id=cod_dep)
    html = '<option value=""></option>'
    for i in prov:
        html = html + '<option value="' + str(i.id) + '"> '+ str(i.nombre)+ '</option>'

    return HttpResponse(html)

def cambiarDist(request):
    cod_prov = int(request.GET.get('codigo_provincia'))
    dist = Distrito.objects.filter(id_provincia_id=cod_prov)
    html = '<option value=""></option>'
    for i in dist:
        html = html + '<option value="' + str(i.id) + '"> '+ str(i.nombre)+ '</option>'

    return HttpResponse(html)