import os
import tkinter as tk
from tkinter import messagebox
from whoosh.index import create_in
from whoosh.fields import TEXT, ID, Schema, DATETIME, KEYWORD, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.qparser.dateparse import DateParserPlugin
from whoosh.query import Term
from whoosh import qparser
from whoosh.index import open_dir
import requests
from bs4 import BeautifulSoup
import datetime
import tkinter as tk
from tkinter import Button, Entry, Label, Listbox, Scrollbar, Spinbox, StringVar, messagebox, simpledialog
import locale
import re

locale.setlocale(locale.LC_TIME, 'es_ES')

schema = Schema(title=TEXT(stored=True),
        servings=NUMERIC(stored=True,numtype=int),
        author=TEXT(stored=True),
        updated=DATETIME(stored=True),
        features=KEYWORD(stored=True, commas=True),
        introduction=TEXT)

URL = "https://www.recetasgratis.net/Recetas-de-Aperitivos-tapas-listado_receta-1_1.html"

directory_index = "./whoosh4/index"
if not os.path.exists(directory_index):
    os.mkdir(directory_index)
    index = create_in(directory_index, schema)
if os.path.exists(directory_index):
     index = open_dir(directory_index,schema=schema)


def coger_autor_y_fecha(receta: dict, url: str) -> dict:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    autor_y_fecha_raw = soup.find('div', class_='nombre_autor')
    autor = autor_y_fecha_raw.a.text
    fecha = autor_y_fecha_raw.span.text
    fecha = fecha.replace('Actualizado:','').strip()
    fecha = datetime.datetime.strptime(fecha, "%d %B %Y")
    features_raw = soup.find('div', class_='properties inline')
    features = ""
    if features_raw:
        features = features_raw.text.replace("Características adicionales:\n","")
        features = features.replace("\n","")
        features = features.split(",")
        features = [f.strip() for f in features]
        features = ",".join(features)
    introduction_raw = soup.find('div', class_='intro')
    introduction = ""
    if introduction_raw:
        introduction = introduction_raw.text
    receta['author'] = autor
    receta['date_update'] = fecha
    receta['features'] = features
    receta['introduction'] = introduction
    return receta


def scrape_recipes(url: str) -> list:
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    lista_recetas_raw = soup.find_all('div', class_="resultado link")
    lista_recetas = []
    i=0
    for receta_raw in lista_recetas_raw:
        print('Recetas procesadas: ', i)
        i = 1 +i
        receta = {}
        link_raw = receta_raw.find('a',class_='titulo titulo--resultado')
        link = link_raw.get('href')
        title = link_raw.text
        difficulty =  receta_raw.find('div', class_='info_snippet').span
        if difficulty:
            difficulty = difficulty.text
        else: 
            difficulty = 'unknown'
        properties_raw = receta_raw.find('div', class_='properties')
        if properties_raw :
            diners = int(properties_raw.find('span', class_='property comensales').text)
            time = properties_raw.find('span', class_='property duracion').text
        else:
            diners = -1
            time = 'unknown'
        receta['title'] = title
        receta['difficulty'] = difficulty
        receta['diners'] = diners
        receta['cooking_time'] = time
        receta = coger_autor_y_fecha(receta,link)
        lista_recetas.append(receta)
    return lista_recetas


def cargar_recetas():
    index = create_in(directory_index, schema)
    lista_recetas = scrape_recipes(URL)
    for receta in lista_recetas:
        writer = index.writer()
        writer.add_document(title=receta['title'], 
        servings=receta['diners'], author= receta['author'],
        updated=receta['date_update'], features=receta['features'],
        introduction=receta['introduction'])
        writer.commit()
    with index.searcher() as searcher:
        query = qparser.QueryParser("title", schema).parse('*')
        results = list(searcher.search(query, limit=None))
        num_recetas = len(results)
    messagebox.showinfo("Información", f"{num_recetas} recetas cargadas en el índice.")



def listar_recetas():
    root_listar = tk.Toplevel(root)
    root_listar.title("Listar Recetas")

    listbox = tk.Listbox(root_listar, width=100)
    listbox.pack(fill=tk.BOTH, expand=True)

    # Realizar una consulta para obtener todos los correos en el índice
    with index.searcher() as searcher:
        query = qparser.QueryParser("title", schema).parse('*')
        results = searcher.search(query, limit=None)
        for result in results:
            listbox.insert(tk.END, "_____________________________________")
            listbox.insert(tk.END, f"Titulo: {result['title']}")
            listbox.insert(tk.END, f"Comensales: {result['servings']}")
            listbox.insert(tk.END, f"Fecha: {result['updated']}")
            listbox.insert(tk.END, f"Autor: {result['author']}")
            listbox.insert(tk.END, f"Caracteristicas: {result['features']}")
            listbox.insert(tk.END, "_____________________________________")

    scrollbar = tk.Scrollbar(root_listar)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    root_listar.mainloop()

def buscar_por_caracteristicas_titulo():
    def realizar_busqueda():
        caracteristica = spinbox.get()
        palabras_clave = entry.get()

        with index.searcher() as searcher:
            
            query1 = '"'+ str(caracteristica) +'"'
            query2 = str(palabras_clave)
            parsed_query = QueryParser("title", schema).parse('features:'+query1+' '+query2)
            results = searcher.search(parsed_query, limit=10)
            print(results)
            # Crear una ventana para mostrar los resultados
            ventana_resultados = tk.Toplevel(root)
            ventana_resultados.title("Resultados de la Búsqueda")

            listbox_resultados = tk.Listbox(ventana_resultados, width=100)
            listbox_resultados.pack(fill=tk.BOTH, expand=True)

            for result in results:
                listbox_resultados.insert(tk.END, "_____________________________________")
                listbox_resultados.insert(tk.END, f"Titulo: {result['title']}")
                listbox_resultados.insert(tk.END, f"Comensales: {result['servings']}")
                listbox_resultados.insert(tk.END, f"Fecha: {result['updated']}")
                listbox_resultados.insert(tk.END, f"Autor: {result['author']}")
                listbox_resultados.insert(tk.END, f"Caracteristicas: {result['features']}")
                listbox_resultados.insert(tk.END, "_____________________________________")

    # Crear la ventana para la búsqueda por características y título
    root_caracteristicas_titulo = tk.Toplevel(root)
    root_caracteristicas_titulo.title("Búsqueda por Características y Título")

    with index.searcher() as searcher:
        docs = searcher.iter_docs()
        fset = set()
        for res in docs:
            fs = res[1]['features'].split(",")
            fset.update(fs)
        features_indexadas = list(fset)

    spinbox = tk.Spinbox(root_caracteristicas_titulo, values=features_indexadas, wrap=True)
    spinbox.pack()

    label_entry = tk.Label(root_caracteristicas_titulo, text="Palabras clave:")
    label_entry.pack()

    entry = tk.Entry(root_caracteristicas_titulo)
    entry.pack()

    boton_buscar = tk.Button(root_caracteristicas_titulo, text="Buscar", command=realizar_busqueda)
    boton_buscar.pack()

def buscar_por_fecha():
    root_buscar_fecha = tk.Toplevel(root)
    root_buscar_fecha.title("Buscar por Fecha")

    label = tk.Label(root_buscar_fecha, text="Ingresa la fecha (DD/MM/AAAA):")
    label.pack()

    entrada_fecha = tk.Entry(root_buscar_fecha)
    entrada_fecha.pack()

    listbox = tk.Listbox(root_buscar_fecha, width=100)
    listbox.pack(fill=tk.BOTH, expand=True)

    def realizar_busqueda():
        fecha = entrada_fecha.get()
        patron = r"^(0[1-9]|[1-2][0-9]|3[0-1])/(0[1-9]|1[0-2])/\d{4}$"
        correcta = re.match(fecha, patron)
        if not fecha:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una fecha.")
            return
        if correcta:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una fecha en formato DD/MM/YYYY.")
            return

        with index.searcher() as searcher:
            date_parser = DateParserPlugin(schema["updated"])
            query_parser = qparser.QueryParser("updated", schema, plugins=[date_parser])
            fecha = datetime.datetime.strptime(fecha,"%d/%m/%Y").strftime("%Y-%m-%d")
            query = query_parser.parse(fecha)
            results = searcher.search(query)
            for result in results:
                listbox.insert(tk.END, "_____________________________________")
                listbox.insert(tk.END, f"Titulo: {result['title']}")
                listbox.insert(tk.END, f"Comensales: {result['servings']}")
                listbox.insert(tk.END, f"Fecha: {result['updated']}")
                listbox.insert(tk.END, f"Autor: {result['author']}")
                listbox.insert(tk.END, f"Caracteristicas: {result['features']}")
                listbox.insert(tk.END, "_____________________________________")

    boton_buscar = tk.Button(root_buscar_fecha, text="Buscar", command=realizar_busqueda)
    boton_buscar.pack()

    scrollbar = tk.Scrollbar(root_buscar_fecha)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    root_buscar_fecha.mainloop()

def buscar_por_titulo_o_introduccion():
    root_buscar_cuerpo = tk.Toplevel(root)
    root_buscar_cuerpo.title("Buscar por titulo o introducción")

    label = tk.Label(root_buscar_cuerpo, text="Ingresa el término de búsqueda:")
    label.pack()

    entrada_busqueda = tk.Entry(root_buscar_cuerpo)
    entrada_busqueda.pack()

    listbox = tk.Listbox(root_buscar_cuerpo, width=100)
    listbox.pack(fill=tk.BOTH, expand=True)

    def realizar_busqueda():
        query = entrada_busqueda.get()

        if not query:
            messagebox.showwarning("Advertencia", "Por favor, ingresa un término de búsqueda.")
            return

        with index.searcher() as searcher:
            query = MultifieldParser(["title","introduction"], schema).parse('"'+ str(query) + '"')
            results = searcher.search(query, limit=3)
            for result in results:
                listbox.insert(tk.END, "_____________________________________")
                listbox.insert(tk.END, f"Titulo: {result['title']}")
                listbox.insert(tk.END, f"Comensales: {result['servings']}")
                listbox.insert(tk.END, f"Fecha: {result['updated']}")
                listbox.insert(tk.END, f"Autor: {result['author']}")
                listbox.insert(tk.END, f"Caracteristicas: {result['features']}")
                listbox.insert(tk.END, "_____________________________________")

    boton_buscar = tk.Button(root_buscar_cuerpo, text="Buscar", command=realizar_busqueda)
    boton_buscar.pack()

    scrollbar = tk.Scrollbar(root_buscar_cuerpo)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    root_buscar_cuerpo.mainloop()





# Crear la ventana principal
root = tk.Tk()
root.title("Correo Electrónico")

# Crear un menú
menu = tk.Menu(root)
root.config(menu=menu)

# Menú "Datos"
menu_datos = tk.Menu(menu)
menu.add_cascade(label="Datos", menu=menu_datos)
menu_datos.add_command(label="Cargar", command=cargar_recetas)
menu_datos.add_command(label="Listar", command=listar_recetas)
menu_datos.add_command(label="Salir", command=root.quit)

# Menú "Buscar"
menu_buscar = tk.Menu(menu)
menu.add_cascade(label="Buscar", menu=menu_buscar)
menu_buscar.add_command(label="Titulo o introduccion", command=buscar_por_titulo_o_introduccion)
menu_buscar.add_command(label="Fecha", command=buscar_por_fecha)
menu_buscar.add_command(label="Caracteristicas y titulo", command=buscar_por_caracteristicas_titulo)

# Inicializar variables para entradas de búsqueda
entrada_busqueda = tk.StringVar()
entrada_fecha = tk.StringVar()
entrada_spam = tk.StringVar()

root.mainloop()

