import requests
from bs4 import BeautifulSoup
import sqlite3
import tkinter as tk
from tkinter import Button, Entry, Label, Listbox, Scrollbar, Spinbox, StringVar, messagebox, simpledialog

import sqlite3


# URL de la página de vinos tintos
url = "https://www.vinissimus.com/es/vinos/tinto/?cursor={}"

# Crear una función para extraer datos de una página
def scrape_page(page_number):
    response = requests.get(url.format(page_number * 36))  # Cada página aumenta el cursor en 36
    soup = BeautifulSoup(response.content, 'html.parser')
    lista_vinos_raw = soup.find_all('div', class_='product-list-item')
    # Aquí debes extraer la información de los vinos (nombre, precio, denominación, bodega, tipos de uvas)
    vinos = []
    for vino_raw in lista_vinos_raw:
        vino = {}
        vino['nombre'] = vino_raw.find('h2', class_='title heading').text
        vino['precio'] = float(vino_raw.find('p', class_='price uniq small').text.replace(',', '.').split(' ')[0])
        vino['denominacion'] = vino_raw.find('div', class_='region').text
        vino['bodega'] = vino_raw.find('div', class_='cellar-name').text
        vino['tipos_uvas'] = vino_raw.find('div', class_='tags').text
        vinos.append(vino)
        
    # Luego, devuelve los datos en una lista de diccionarios
    return vinos


# Conectar a la base de datos SQLite
conn = sqlite3.connect("vinos.db")
cursor = conn.cursor()

# Crear una tabla para almacenar los vinos
cursor.execute('''CREATE TABLE IF NOT EXISTS vinos (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT,
                    precio DECIMAL,
                    denominacion TEXT,
                    bodega TEXT,
                    tipos_uvas TEXT
                )''')

# Insertar datos en la tabla
def insertar_vino(vino):
    cursor.execute('''INSERT INTO vinos (nombre, precio, denominacion, bodega, tipos_uvas)
                      VALUES (?, ?, ?, ?, ?)''', (vino['nombre'], vino['precio'], vino['denominacion'], vino['bodega'], vino['tipos_uvas']))
    conn.commit()


# Función para cargar datos desde la base de datos
def cargar_datos():
    conn = sqlite3.connect("vinos.db")
    cursor = conn.cursor()
    datos_pagina_1 = scrape_page(0)
    datos_pagina_2 = scrape_page(1)
    datos_pagina_3 = scrape_page(2)
    
    for vino in datos_pagina_1 + datos_pagina_2 + datos_pagina_3:
        insertar_vino(vino)
    
    cursor.execute("SELECT COUNT(*) FROM vinos")
    num_vinos = cursor.fetchone()[0]
    messagebox.showinfo("Información", f"Se han almacenado {num_vinos} vinos en la base de datos.")
    conn.close()


# Función para listar los vinos
def listar_vinos():
    lista_vinos_window = tk.Toplevel(root)
    lista_vinos_window.title("Listado de Vinos")
    
    scrollbar = Scrollbar(lista_vinos_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox = Listbox(lista_vinos_window, yscrollcommand=scrollbar.set)
    listbox.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)
    
    cursor.execute("SELECT nombre, precio, bodega, denominacion FROM vinos")
    vinos = cursor.fetchall()
    lista_vinos_window.geometry('900x300')
    
    for vino in vinos:
        listbox.insert(tk.END, f"Nombre: {vino[0]}, Precio: {vino[1]}, Bodega: {vino[2]}, Denominación: {vino[3]}")

# Función para buscar por denominación

def mostrar_vinos_por_denominacion(denominacion):
    vinos_denominacion_window = tk.Toplevel(root)
    vinos_denominacion_window.title(f"Vinos de la Denominación: {denominacion}")
    
    scrollbar = Scrollbar(vinos_denominacion_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox = Listbox(vinos_denominacion_window, yscrollcommand=scrollbar.set)
    listbox.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)
    
    cursor.execute("SELECT nombre, precio, bodega, denominacion FROM vinos WHERE denominacion=?", (denominacion,))
    vinos = cursor.fetchall()
    vinos_denominacion_window.geometry('900x300')
    for vino in vinos:
        listbox.insert(tk.END, f"Nombre: {vino[0]}, Precio: {vino[1]}, Bodega: {vino[2]}, Denominación: {vino[3]}")


def buscar_denominacion():
    denominacion_window = tk.Toplevel(root)
    denominacion_window.title("Buscar por Denominación")
    
    denominacion_label = Label(denominacion_window, text="Selecciona una denominación:")
    denominacion_label.pack()
    
    denominaciones = cursor.execute("SELECT DISTINCT denominacion FROM vinos").fetchall()
    denominaciones = [den[0] for den in denominaciones]
    
    denominacion_var = StringVar()
    denominacion_spinbox = Spinbox(denominacion_window, values=denominaciones, textvariable=denominacion_var)
    denominacion_spinbox.pack()

    denominacion_window.geometry('900x300')
    buscar_button = Button(denominacion_window, text="Buscar", command=lambda: mostrar_vinos_por_denominacion(denominacion_var.get()))
    buscar_button.pack()

# Función para buscar por precio

def mostrar_vinos_por_precio(max_precio):
    vinos_precio_window = tk.Toplevel(root)
    vinos_precio_window.title(f"Vinos con Precio Menor a {max_precio}")
    
    scrollbar = Scrollbar(vinos_precio_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox = Listbox(vinos_precio_window, yscrollcommand=scrollbar.set)
    listbox.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)
    
    vinos_precio_window.geometry('900x300')
    cursor.execute("SELECT nombre, precio, bodega, denominacion FROM vinos WHERE precio < ?", (max_precio,))
    vinos = cursor.fetchall()
    
    for vino in vinos:
        listbox.insert(tk.END, f"Nombre: {vino[0]}, Precio: {vino[1]}, Bodega: {vino[2]}, Denominación: {vino[3]}")


def buscar_precio():
    precio_window = tk.Toplevel(root)
    precio_window.title("Buscar por Precio")
    
    precio_label = Label(precio_window, text="Introduce un precio máximo:")
    precio_label.pack()
    
    precio_var = StringVar()
    precio_entry = Entry(precio_window, textvariable=precio_var)
    precio_entry.pack()
    
    precio_window.geometry('900x300')
    buscar_button = Button(precio_window, text="Buscar", command=lambda: mostrar_vinos_por_precio(float(precio_var.get())))
    buscar_button.pack()

def mostrar_vinos_por_uva(tipo_uva):
    vinos_uva_window = tk.Toplevel(root)
    vinos_uva_window.title(f"Vinos con Tipo de Uva: {tipo_uva}")
    
    scrollbar = Scrollbar(vinos_uva_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox = Listbox(vinos_uva_window, yscrollcommand=scrollbar.set)
    listbox.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)
    
    vinos_uva_window.geometry('900x300')
    cursor.execute("SELECT nombre, tipos_uvas FROM vinos WHERE tipos_uvas LIKE ?", (f"%{tipo_uva}%",))
    vinos = cursor.fetchall()
    
    for vino in vinos:
        listbox.insert(tk.END, f"Nombre: {vino[0]}, Tipos de Uvas: {vino[1]}")


# Función para buscar por tipo de uva
def buscar_uvas():
    uvas_window = tk.Toplevel(root)
    uvas_window.title("Buscar por Tipo de Uva")
    
    uva_label = Label(uvas_window, text="Selecciona un tipo de uva:")
    uva_label.pack()
    
    uvas = cursor.execute("SELECT DISTINCT tipos_uvas FROM vinos").fetchall()
    uvas = [uva[0] for uva in uvas]
    
    uva_var = StringVar()
    uva_spinbox = Spinbox(uvas_window, values=uvas, textvariable=uva_var)
    uva_spinbox.pack()
    
    uvas_window.geometry('900x300')
    buscar_button = Button(uvas_window, text="Buscar", command=lambda: mostrar_vinos_por_uva(uva_var.get()))
    buscar_button.pack()

# Crear la ventana principal
root = tk.Tk()
root.title("Web Scraping de Vinos")

# Crear el menú
menu = tk.Menu(root)
root.config(menu=menu)

# Opción "Datos" con submenús
datos_menu = tk.Menu(menu)
menu.add_cascade(label="Datos", menu=datos_menu)
datos_menu.add_command(label="Cargar", command=cargar_datos)
datos_menu.add_command(label="Listar", command=listar_vinos)
datos_menu.add_separator()
datos_menu.add_command(label="Salir", command=root.quit)

# Opción "Buscar" con submenús
buscar_menu = tk.Menu(menu)
menu.add_cascade(label="Buscar", menu=buscar_menu)
buscar_menu.add_command(label="Denominación", command=buscar_denominacion)
buscar_menu.add_command(label="Precio", command=buscar_precio)
buscar_menu.add_command(label="Uvas", command=buscar_uvas)

# Iniciar la interfaz gráfica
root.mainloop()



# Cerrar la conexión a la base de datos

