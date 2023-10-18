import requests
from bs4 import BeautifulSoup
import sqlite3
import tkinter as tk
from tkinter import Button, Entry, Label, Listbox, Scrollbar, Spinbox, StringVar, messagebox, simpledialog
import datetime
import sqlite3
import locale
import re

URL = "https://www.recetasgratis.net/Recetas-de-Aperitivos-tapas-listado_receta-1_1.html"
DB = "recetas.db"
locale.setlocale(locale.LC_TIME, 'es_ES')

def create_table(cursor: sqlite3.Cursor) :
    cursor.execute('DROP TABLE recetas')
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS recetas (
            id INTEGER PRIMARY KEY,
            title TEXT,
            difficulty TEXT,
            diners INTEGER,
            cooking_time TEXT,
            author TEXT,
            date_update DATE
        )'''
    )

def insert_recipe(cursor: sqlite3.Cursor, conn: sqlite3.Connection, recipe: dict) :
    cursor.execute('''INSERT INTO recetas (title, difficulty, diners, cooking_time, author, date_update)
                      VALUES (?, ?, ?, ?, ?, ?)''', (recipe['title'], recipe['difficulty'], recipe['diners'], recipe['cooking_time'], recipe['author'],recipe['date_update']))
    conn.commit()

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

def coger_autor_y_fecha(receta: dict, url: str) -> dict:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    autor_y_fecha_raw = soup.find('div', class_='nombre_autor')
    autor = autor_y_fecha_raw.a.text
    fecha = autor_y_fecha_raw.span.text
    fecha = fecha.replace('Actualizado:','').strip()
    fecha = datetime.datetime.strptime(fecha, "%d %B %Y")
    receta['author'] = autor
    receta['date_update'] = fecha
    return receta

def cargar_datos() :
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    create_table(cursor)
    recipes = scrape_recipes(URL)
    for recipe in recipes:
        insert_recipe(cursor, conn, recipe)
    cursor.execute("SELECT count(*) FROM recetas")
    num_recetas = cursor.fetchone()[0]
    messagebox.showinfo("Información", f"Se han almacenado {num_recetas} recetas en la base de datos.")
    conn.close()

def listar_recetas():
    conn = sqlite3.connect("recetas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recetas")
    recipes = cursor.fetchall()
    conn.close()

    list_window = tk.Toplevel(root)
    list_window.title("Listado de Recetas")

    listbox = Listbox(list_window, width=50, height=20)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = Scrollbar(list_window, command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox.config(yscrollcommand=scrollbar.set)

    for recipe in recipes:
        listbox.insert(tk.END, f"{recipe[1]}|  {recipe[2]}|  {recipe[3]}| {recipe[4]}|  {recipe[5]}|  {recipe[6]}") 


def buscar_autor():
    conn = sqlite3.connect("recetas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT author FROM recetas")
    authors = cursor.fetchall()
    conn.close()

    author_window = tk.Toplevel(root)
    author_window.title("Buscar Recetas por Autor")

    label = Label(author_window, text="Selecciona un autor:")
    label.pack()

    author_var = StringVar()
    spinbox = Spinbox(author_window, values=authors, textvariable=author_var)
    spinbox.pack()

    def show_recipes_by_author():
        selected_author = author_var.get()
        conn = sqlite3.connect("recetas.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title, difficulty, diners, cooking_time, author FROM recetas WHERE author=?", (selected_author,))
        author_recipes = cursor.fetchall()
        conn.close()

        recipes_window = tk.Toplevel(root)
        recipes_window.title(f"Recetas de {selected_author}")

        listbox = Listbox(recipes_window, width=50, height=20)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = Scrollbar(recipes_window, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox.config(yscrollcommand=scrollbar.set)

        for recipe in author_recipes:
            listbox.insert(tk.END, f"{recipe[0]}, Dificultad: {recipe[1]}, Comensales: {recipe[2]}, Tiempo: {recipe[3]}, Autor: {recipe[4]}")

    show_button = Button(author_window, text="Mostrar Recetas", command=show_recipes_by_author)
    show_button.pack()


def buscar_fecha():
    def show_recipes_by_date():
        entered_date = date_entry.get()
        fec = re.match(r"\d\d/\d\d/\d{4}",entered_date.strip())
        if fec:
            fecha = datetime.datetime.strptime(entered_date.strip(),"%d/%m/%Y")
            conn = sqlite3.connect("recetas.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recetas WHERE date_update < ?", (fecha,))
            date_recipes = cursor.fetchall()
            conn.close()
        else:
            messagebox.showerror("Error", "Formato de fecha incorrecto")
        try:
            

            date_window = tk.Toplevel(root)
            date_window.title(f"Recetas publicadas antes de {entered_date}")

            listbox = Listbox(date_window, width=50, height=20)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = Scrollbar(date_window, command=listbox.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            listbox.config(yscrollcommand=scrollbar.set)

            for recipe in date_recipes:
                listbox.insert(tk.END, f"{recipe[1]}, Dificultad: {recipe[2]}, Comensales: {recipe[3]}, Tiempo: {recipe[4]}, Autor: {recipe[5]}, Fecha de Publicación: {recipe[6]}")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al buscar recetas por fecha: {str(e)}")

    date_window = tk.Toplevel(root)
    date_window.title("Buscar Recetas por Fecha")

    label = Label(date_window, text="Introduce la fecha (dd/mm/yyyy):")
    label.pack()

    date_entry = Entry(date_window)
    date_entry.pack()

    show_button = Button(date_window, text="Mostrar Recetas", command=show_recipes_by_date)
    show_button.pack()



root = tk.Tk()
root.title("Web Scraping de Recetas")

menu = tk.Menu(root)
root.config(menu=menu)

datos_menu = tk.Menu(menu)
menu.add_cascade(label="Datos", menu=datos_menu)
datos_menu.add_command(label="Cargar", command=cargar_datos)
datos_menu.add_command(label="Listar", command=listar_recetas)
datos_menu.add_separator()
datos_menu.add_command(label="Salir", command=root.quit)

buscar_menu = tk.Menu(menu)
menu.add_cascade(label="Buscar", menu=buscar_menu)
buscar_menu.add_command(label="Autor", command=buscar_autor)
buscar_menu.add_command(label="Fecha", command=buscar_fecha)

root.mainloop()
