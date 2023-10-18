import logging
import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import requests
from bs4 import BeautifulSoup

# Función para extraer y almacenar datos en la base de datos SQLite
def cargar_estrenos():
    url = 'https://www.elseptimoarte.net/estrenos/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Inicializar la base de datos SQLite
    conn = sqlite3.connect('estrenos.db')
    cursor = conn.cursor()

    # Crear tabla para almacenar los estrenos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estrenos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            titulo_original TEXT,
            paises TEXT,
            fecha_estreno TEXT,
            director TEXT,
            generos TEXT
        )
    ''')

    # Extraer datos de la página y almacenarlos en la base de datos
    estrenos = soup.find('ul',class_='elements')
    lista_estrenos = estrenos.find_all('li')
    num_estrenos = 0
    for estreno in lista_estrenos:
        titulo = estreno.find('h3').find('a').text.strip()
        generos = estreno.find('p', class_='generos').text.strip()
        fecha_estreno = estreno.find_all('p')[1].text.strip()

        cursor.execute('INSERT INTO estrenos (titulo, generos, fecha_estreno) VALUES (?, ?, ?)',
                       (titulo, generos, fecha_estreno))
        num_estrenos += 1

    conn.commit()
    conn.close()
    messagebox.showinfo('Carga Completa', f'Se han cargado {num_estrenos} estrenos en la base de datos.')

# Función para listar los estrenos en una ventana
def listar_estrenos():
    conn = sqlite3.connect('estrenos.db')
    cursor = conn.cursor()

    cursor.execute('SELECT titulo, paises, director FROM estrenos')
    estrenos = cursor.fetchall()
    conn.close()

    # Crear ventana para mostrar los estrenos
    listar_window = tk.Toplevel(main_window)
    listar_window.title('Listado de Estrenos')

    # Crear una listbox con scrollbar
    scrollbar = tk.Scrollbar(listar_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(listar_window, yscrollcommand=scrollbar.set)
    listbox.pack(fill=tk.BOTH, expand=True)

    scrollbar.config(command=listbox.yview)

    for estreno in estrenos:
        listbox.insert(tk.END, f'Título: {estreno[0]}, País: {estreno[1]}, Director: {estreno[2]}')

# Función para buscar por título
def buscar_por_titulo():
    palabra = simpledialog.askstring('Buscar por Título', 'Introduce una palabra en el título:')
    if palabra:
        conn = sqlite3.connect('estrenos.db')
        cursor = conn.cursor()

        cursor.execute('SELECT titulo, paises, director FROM estrenos WHERE titulo LIKE ?', (f'%{palabra}%',))
        resultados = cursor.fetchall()
        conn.close()

        if resultados:
            # Crear ventana para mostrar los resultados
            resultado_window = tk.Toplevel(main_window)
            resultado_window.title('Resultados de Búsqueda por Título')

            # Crear una listbox con scrollbar
            scrollbar = tk.Scrollbar(resultado_window)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            listbox = tk.Listbox(resultado_window, yscrollcommand=scrollbar.set)
            listbox.pack(fill=tk.BOTH, expand=True)

            scrollbar.config(command=listbox.yview)

            for resultado in resultados:
                listbox.insert(tk.END, f'Título: {resultado[0]}, País: {resultado[1]}, Director: {resultado[2]}')
        else:
            messagebox.showinfo('Sin Resultados', 'No se encontraron resultados para la palabra clave.')

# Función para buscar por fecha
def buscar_por_fecha():
    fecha = simpledialog.askstring('Buscar por Fecha', 'Introduce una fecha (dd-mm-aaaa):')
    if fecha:
        conn = sqlite3.connect('estrenos.db')
        cursor = conn.cursor()

        cursor.execute('SELECT titulo, fecha_estreno FROM estrenos WHERE fecha_estreno >= ?', (fecha,))
        resultados = cursor.fetchall()
        conn.close()

        if resultados:
            # Crear ventana para mostrar los resultados
            resultado_window = tk.Toplevel(main_window)
            resultado_window.title('Resultados de Búsqueda por Fecha')

            # Crear una listbox con scrollbar
            scrollbar = tk.Scrollbar(resultado_window)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            listbox = tk.Listbox(resultado_window, yscrollcommand=scrollbar.set)
            listbox.pack(fill=tk.BOTH, expand=True)

            scrollbar.config(command=listbox.yview)

            for resultado in resultados:
                listbox.insert(tk.END, f'Título: {resultado[0]}, Fecha de Estreno: {resultado[1]}')
        else:
            messagebox.showinfo('Sin Resultados', 'No se encontraron resultados para la fecha especificada.')

# Función para buscar por género
def buscar_por_genero():
    generos = ['Drama', 'Comedia', 'Acción', 'Ciencia Ficción', 'Aventura']  # Modificar con los géneros reales
    genero_seleccionado = simpledialog.askinteger('Buscar por Género', 'Selecciona un género:', minvalue=0, maxvalue=len(generos) - 1)
    if genero_seleccionado is not None:
        genero = generos[genero_seleccionado]

        conn = sqlite3.connect('estrenos.db')
        cursor = conn.cursor()

        cursor.execute('SELECT titulo, fecha_estreno FROM estrenos WHERE generos LIKE ?', (f'%{genero}%',))
        resultados = cursor.fetchall()
        conn.close()

        if resultados:
            # Crear ventana para mostrar los resultados
            resultado_window = tk.Toplevel(main_window)
            resultado_window.title(f'Resultados de Búsqueda por Género ({genero})')

            # Crear una listbox con scrollbar
            scrollbar = tk.Scrollbar(resultado_window)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            listbox = tk.Listbox(resultado_window, yscrollcommand=scrollbar.set)
            listbox.pack(fill=tk.BOTH, expand=True)

            scrollbar.config(command=listbox.yview)

            for resultado in resultados:
                listbox.insert(tk.END, f'Título: {resultado[0]}, Fecha de Estreno: {resultado[1]}')
        else:
            messagebox.showinfo('Sin Resultados', f'No se encontraron resultados para el género "{genero}".')

# Función para salir de la aplicación
def salir():
    main_window.destroy()

# Crear ventana principal
main_window = tk.Tk()
main_window.title('Buscador de Estrenos de Cine en España')

# Crear menú
menu = tk.Menu(main_window)
main_window.config(menu=menu)

# Menú "Datos"
menu_datos = tk.Menu(menu)
menu.add_cascade(label='Datos', menu=menu_datos)
menu_datos.add_command(label='Cargar', command=cargar_estrenos)
menu_datos.add_command(label='Listar', command=listar_estrenos)
menu_datos.add_separator()
menu_datos.add_command(label='Salir', command=salir)

# Menú "Buscar"
menu_buscar = tk.Menu(menu)
menu.add_cascade(label='Buscar', menu=menu_buscar)
menu_buscar.add_command(label='Título', command=buscar_por_titulo)
menu_buscar.add_command(label='Fecha', command=buscar_por_fecha)
menu_buscar.add_command(label='Géneros', command=buscar_por_genero)

main_window.mainloop()
