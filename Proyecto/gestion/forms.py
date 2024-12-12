from django import forms
from .models import Libro, Prestamo, PuntuacionLibro, Almacen
from ebooklib import epub
import requests
import tempfile  # Asegúrate de importar tempfile
import os  

# Formulario para subir un libro
class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['archivo']  # Solo el archivo para extracción automática

    def __init__(self, *args, **kwargs):
        # Asegurarnos de que el usuario sea pasado como argumento al formulario
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')

        # Verificar que el archivo sea .epub
        if archivo:
            if not archivo.name.endswith('.epub'):
                raise forms.ValidationError('El archivo debe estar en formato EPUB.')

            # Crear un archivo temporal
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                # Guardar el archivo subido en el archivo temporal
                for chunk in archivo.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name  # Guardar la ruta del archivo temporal

            # Leer el archivo EPUB desde la ruta temporal
            try:
                libro_epub = epub.read_epub(temp_file_path)
            except Exception as e:
                raise forms.ValidationError(f'Error al leer el archivo EPUB: {str(e)}')

            # Extraer metadatos y asignarlos a la instancia
            self.instance.titulo = self.extraer_metadato(libro_epub, 'title')
            self.instance.autor = self.extraer_metadato(libro_epub, 'creator')
            self.instance.edicion = self.extraer_metadato(libro_epub, 'identifier')
            
            # Intentar obtener el ISBN desde Open Library, no de los metadatos
            isbn = self.obtener_isbn_open_library(libro_epub)
            if isbn:
                self.instance.isbn = isbn

            # Consultar Open Library para obtener la editorial usando ISBN
            if self.instance.isbn:
                self.instance.tematica = self.obtener_tematica_open_library(self.instance.isbn)
                self.instance.edicion = self.obtener_editorial_open_library(self.instance.isbn)

            # Asignar el almacen del usuario actual
            if self.user:
                try:
                    # Usar 'usuario' en lugar de 'propietario' y manejar el caso de no existencia
                    almacen = Almacen.objects.get(usuario=self.user)
                except Almacen.DoesNotExist:
                    # Si no existe, crear un nuevo almacen para el usuario
                    almacen = Almacen.objects.create(usuario=self.user)

                self.instance.almacen = almacen

            # Eliminar el archivo temporal después de usarlo
            os.remove(temp_file_path)

        return archivo

    def extraer_metadato(self, libro_epub, campo):
        """
        Extrae un metadato específico del archivo EPUB.
        """
        metadato = libro_epub.get_metadata('DC', campo)
        return metadato[0][0] if metadato else None

    def obtener_isbn_open_library(self, libro_epub):
        """
        Obtiene el ISBN desde Open Library a partir de los metadatos EPUB, si es que Open Library
        tiene una API que pueda recuperar el ISBN de algún otro dato del libro (como el título o el autor).
        """
        # Extraer el título y el autor del EPUB, si no se obtiene ISBN de los metadatos
        titulo = self.extraer_metadato(libro_epub, 'title')
        autor = self.extraer_metadato(libro_epub, 'creator')
        
        # Usar el título y autor para consultar la API de Open Library
        if titulo and autor:
            try:
                query = f'https://openlibrary.org/search.json?title={titulo}&author={autor}'
                response = requests.get(query)
                if response.status_code == 200:
                    data = response.json()
                    if data['docs']:
                        first_book = data['docs'][0]
                        isbn_list = first_book.get('isbn', [])
                        if isbn_list:
                            return isbn_list[0]  # Retornar el primer ISBN encontrado
            except requests.RequestException:
                # Si hay un error con la API, retornar None
                return None
        return None

    def obtener_tematica_open_library(self, isbn):
        """
        Llama a la API de Open Library para obtener la temática de un libro
        a partir del ISBN, devolviendo el primer tema si existe.
        """
        try:
            response = requests.get(f'https://openlibrary.org/isbn/{isbn}.json')
            if response.status_code == 200:
                data = response.json()
                temas = data.get('subjects', [])
                return temas[0] if temas else None
        except requests.RequestException:
            # Manejo en caso de error de conexión con la API
            return None
        return None

    def obtener_editorial_open_library(self, isbn):
        """
        Llama a la API de Open Library para obtener la editorial de un libro
        a partir del ISBN y la asigna al campo 'edicion'.
        """
        try:
            response = requests.get(f'https://openlibrary.org/isbn/{isbn}.json')
            if response.status_code == 200:
                data = response.json()
                editorial = data.get('publishers', [])
                return editorial[0] if editorial else None  # Retorna la primera editorial disponible
        except requests.RequestException:
            # Manejo en caso de error de conexión con la API
            return None
        return None


# Formulario para gestionar el préstamo de un libro
class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['libro']  # Se asume que el libro se selecciona desde la biblioteca

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo los libros que están disponibles para préstamo
        self.fields['libro'].queryset = Libro.objects.filter(en_prestamo=False)

# Formulario para calificar un libro
class PuntuacionForm(forms.ModelForm):
    class Meta:
        model = PuntuacionLibro
        fields = ['puntuacion']

    def clean_puntuacion(self):
        puntuacion = self.cleaned_data.get('puntuacion')

        # Verificar que la puntuación esté entre 1 y 10
        if puntuacion is None or not (1 <= puntuacion <= 10):
            raise forms.ValidationError('La puntuación debe estar entre 1 y 10.')
        
        return puntuacion

