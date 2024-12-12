import os
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Avg
from .models import Libro, PuntuacionLibro, Prestamo, Almacen
from .forms import LibroForm, PuntuacionForm
from django.http import FileResponse, Http404
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import TemplateView
from django.contrib.auth import login
from ebooklib import epub, ITEM_DOCUMENT
from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404
from ebooklib import epub
from fpdf import FPDF 
from django.http import HttpResponse
from django.views import View
from ebooklib import epub
from weasyprint import HTML  # Asegúrate de tener weasyprint instalado

# Vista para mostrar la biblioteca del usuario
class BibliotecaView(LoginRequiredMixin, ListView):
    model = Libro
    template_name = 'biblioteca.html'
    context_object_name = 'libros'

    def get_queryset(self):
        return Libro.objects.filter(propietario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puntuaciones'] = PuntuacionLibro.objects.filter(usuario=self.request.user)
        return context

# Vista para mostrar libros disponibles para préstamo
class PrestamosView(ListView):
    model = Libro
    template_name = 'prestamos.html'
    context_object_name = 'libros'

    def get_queryset(self):
        return Libro.objects.filter(en_prestamo=False)

# Vista para prestar un libro
from django.http import Http404

class PrestarLibroView(LoginRequiredMixin, RedirectView):
    pattern_name = 'prestamos'

    def post(self, request, *args, **kwargs):
        libro = get_object_or_404(Libro, id=self.kwargs['libro_id'], en_prestamo=False)

        if not libro.isbn:
            return render(request, 'error.html', {'error': 'El libro debe tener un ISBN registrado antes de ser prestado.'})

        prestamo, created = Prestamo.objects.get_or_create(libro=libro)
        prestamo.usuarios.add(request.user)
        libro.en_prestamo = True
        libro.save()

        return redirect(self.get_redirect_url())


# Vista para devolver un libro
class DevolverLibroView(LoginRequiredMixin, RedirectView):
    pattern_name = 'biblioteca'

    def post(self, request, *args, **kwargs):
        libro = get_object_or_404(Libro, id=self.kwargs['libro_id'])
        prestamo = get_object_or_404(Prestamo, libro=libro)

        # Si el usuario está en la lista de usuarios del préstamo, finalizar el préstamo
        if request.user in prestamo.usuarios.all():
            prestamo.finalizar_prestamo(request.user)

        return redirect(self.get_redirect_url())

# Vista para mostrar detalles del libro
from ebooklib import epub, ITEM_DOCUMENT  # Asegúrate de importar ITEM_DOCUMENT

class DetalleLibroView(LoginRequiredMixin, DetailView):
    model = Libro
    template_name = 'detalle_libro.html'
    context_object_name = 'libro'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        libro = self.get_object()

        # Obtener la ruta del archivo EPUB
        ruta_epub = libro.archivo.path  # Asume que el modelo `Libro` tiene un campo `archivo` para subir el .epub

        # Leer el contenido del EPUB
        contenido = []
        try:
            libro_epub = epub.read_epub(ruta_epub)
            
            # Agregar el print para inspeccionar el contenido del archivo EPUB
            print([item for item in libro_epub.get_items()])  # Depuración

            # Extraer el contenido de los documentos
            for item in libro_epub.get_items_of_type(ITEM_DOCUMENT):
                contenido.append(item.get_content().decode('utf-8'))
        except Exception as e:
            contenido.append(f"Error al leer el archivo EPUB: {e}")

        # Agregar el contenido al contexto
        context['contenido'] = contenido

        # Contexto adicional
        context['puntuacion'] = PuntuacionLibro.objects.filter(libro=libro, usuario=self.request.user).first()
        context['puntuacion_form'] = PuntuacionForm()

        return context

    
# Vista para puntuar un libro
class PuntuarLibroView(LoginRequiredMixin, RedirectView):
    pattern_name = 'detalle_libro'

    def post(self, request, *args, **kwargs):
        libro = get_object_or_404(Libro, id=self.kwargs['libro_id'])
        puntuacion_value = request.POST.get('puntuacion')

        # Validar que la puntuación sea un número entre 1 y 10
        try:
            puntuacion_value = int(puntuacion_value)
            if not (1 <= puntuacion_value <= 10):
                raise ValueError
        except ValueError:
            return render(request, 'error.html', {
                'error': 'La puntuación debe ser un número entero entre 1 y 10.'
            })

        # Crear o actualizar la puntuación del usuario para este libro
        puntuacion, created = PuntuacionLibro.objects.update_or_create(
            usuario=request.user,
            libro=libro,
            defaults={'puntuacion': puntuacion_value}
        )

        return redirect(self.get_redirect_url(libro_id=libro.id))

    def get_redirect_url(self, **kwargs):
        return reverse_lazy(self.pattern_name, kwargs={'pk': kwargs['libro_id']})


class RankingView(LoginRequiredMixin, ListView):
    template_name = 'ranking.html'
    context_object_name = 'ranking'

    def get_queryset(self):
        # Agrupar libros, calcular el promedio y ordenar de mayor a menor
        return (
            PuntuacionLibro.objects.values('libro__titulo', 'libro__autor')
            .annotate(promedio=Avg('puntuacion'))
            .order_by('-promedio')[:10]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_10'] = self.get_queryset()  # Incluir el ranking en el contexto
        return context


class AgregarLibroView(LoginRequiredMixin, CreateView):
    model = Libro
    template_name = 'agregar_libro.html'
    form_class = LibroForm
    success_url = reverse_lazy('biblioteca')

    def get_form_kwargs(self):
        # Asegurarnos de que el usuario actual esté disponible en el formulario
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.propietario = self.request.user  # Asignar el propietario del libro
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('biblioteca')

# Vista para servir archivos EPUB
class ServeEpubView(View):
    def get(self, request, libro_id):
        try:
            libro = get_object_or_404(Libro, id=libro_id)
            # Asegúrate de que el archivo existe
            if libro.archivo:  # Suponiendo que 'archivo' es el campo que almacena el EPUB
                return FileResponse(libro.archivo.open(), content_type='application/epub+zip')
            else:
                raise Http404("El archivo EPUB no se encuentra.")
        except Libro.DoesNotExist:
            raise Http404("Libro no encontrado.")


class RegistroView(CreateView):
    template_name = 'registration/register.html'  # Asegúrate de que esta plantilla exista
    form_class = UserCreationForm  # O tu propio formulario de registro
    success_url = reverse_lazy('login')  # Redirige a la página de inicio de sesión o a donde desees

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Guardar el usuario
            
            # Crear un Almacen para el usuario recién registrado
            almacen = Almacen.objects.create(usuario=user)  # Usamos 'usuario' en lugar de 'propietario'
            
            login(request, user)  # Iniciar sesión con el usuario recién creado
            return redirect('prestamos')  # Redirigir a la vista de préstamos

        return render(request, 'registration/register.html', {'form': form})


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'  # Asegúrate de crear este archivo de plantilla


from ebooklib import epub
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404, render
from django.views import View
from .models import Libro

class LeerLibroView(View):
    def get(self, request, libro_id):
        libro = get_object_or_404(Libro, pk=libro_id)
        try:
            # Leer el archivo EPUB
            archivo_epub = epub.read_epub(libro.archivo.path)

            # Filtrar los capítulos (elementos XHTML)
            capitulos = [item for item in archivo_epub.get_items() if item.media_type == 'application/xhtml+xml']

            if not capitulos:
                return render(request, 'error.html', {
                    "mensaje_error": "No se encontró contenido válido en el archivo EPUB."
                })

            # Construir el contenido completo del libro
            contenido_completo = ""
            for capitulo in capitulos:
                contenido = capitulo.get_content()
                # Procesar el contenido con BeautifulSoup
                soup = BeautifulSoup(contenido, 'html.parser')
                contenido_completo += soup.prettify() + "<hr>"  # Agregar un separador entre capítulos

            return render(request, 'leer_libro.html', {
                "titulo": libro.titulo,
                "contenido": contenido_completo
            })

        except Exception as e:
            return render(request, 'error.html', {"mensaje_error": str(e)})

