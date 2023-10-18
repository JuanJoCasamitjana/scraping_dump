import requests
import urllib.request
from bs4 import BeautifulSoup
import sqlite3
import tkinter as tk
from tkinter import Button, Entry, Label, Listbox, Scrollbar, Spinbox, StringVar, messagebox, simpledialog

URL = "https://resultados.as.com/resultados/futbol/primera/2021_2022/calendario/"
DB = "furbo.db"


def crear_tabla(cursor: sqlite3.Cursor):
    cursor.execute('DROP TABLE jornadas')
    cursor.execute(
                   '''CREATE TABLE IF NOT EXISTS jornadas (
                   id INTEGER PRIMARY KEY,
                   jornada INTEGER,
                   equipo_local TEXT,
                   equipo_visitante,
                   gol_local INTEGER,
                   gol_visitante INTEGER,
                   link TEXT,
                   scorer_local TEXT,
                   scorer_visitante TEXT
                   )''')

def insertar_jornada(cursor: sqlite3.Cursor, conn: sqlite3.Connection, jornada: dict) :
    cursor.execute('''INSERT INTO jornadas (jornada, equipo_local, equipo_visitante, gol_local, gol_visitante, link)
                   values(?,?,?,?,?,?)''', (jornada['jornada'], jornada['equipo_local'], jornada['equipo_visitante'], jornada['gol_local'], jornada['gol_visitante'], jornada['link']))
    conn.commit()

def scrape_jornadas(url: str) -> list:
    jornadas = list()
    response = urllib.request.urlopen(URL)
    soup = BeautifulSoup(response, 'html.parser')
    lista_jornadas_raw = soup.find_all('div', class_='cont-modulo resultados')

    for jornada_raw in lista_jornadas_raw :
        num_jornada = int(jornada_raw.h2.a.string.split(" ")[1].strip())
        partidos = jornada_raw.find_all('tr', id=True)
        for partido in partidos:
            jornada = {}
            jornada['jornada'] = num_jornada
            jornada['equipo_local'] = partido.find('td', class_='col-equipo-local').a.find('span', class_='nombre-equipo').text
            jornada['equipo_visitante'] = partido.find('td', class_='col-equipo-visitante').a.find('span', class_='nombre-equipo').text
            resultado_partido = partido.find('td', class_='col-resultado').a.text.split("-")
            jornada['gol_local'] = int(resultado_partido[0].strip())
            jornada['gol_visitante'] = int(resultado_partido[1].strip())
            jornada['link'] = partido.find('td', class_='col-resultado').a.get('href')
            jornadas.append(jornada)
    return jornadas





def cargar_datos() : 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    crear_tabla(cursor)
    jornadas = scrape_jornadas(URL)
    for jornada in jornadas:
        insertar_jornada(cursor, conn, jornada)

    cursor.execute('SELECT count(*) FROM jornadas')
    num_jornadas = cursor.fetchone()[0]
    messagebox.showinfo("Información", f"Se han almacenado {num_jornadas} jornadas en la base de datos.")
    conn.close()

def listar_jornadas():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM jornadas')
    jornadas = cursor.fetchall()

    if not jornadas:
        messagebox.showinfo("Información", "No se encontraron jornadas en la base de datos.")
    else:
        ventana_listado = tk.Toplevel()
        ventana_listado.title("Listado de Jornadas")
        listbox = Listbox(ventana_listado)
        scrollbar = Scrollbar(ventana_listado)
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)

        for jornada in jornadas:
            listbox.insert(tk.END, f"Jornada {jornada[1]} - {jornada[2]} {jornada[4]} - {jornada[3]} {jornada[5]}")

        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ventana_listado.mainloop()

    conn.close()


def buscar_jornada():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    jornadas = cursor.execute('SELECT DISTINCT jornada FROM jornadas').fetchall()
    jornadas_disponibles = [j[0] for j in jornadas]
    jornada_seleccionada = simpledialog.askinteger("Buscar Jornada", "Ingrese el número de jornada:", minvalue=min(jornadas_disponibles), maxvalue=max(jornadas_disponibles))

    if jornada_seleccionada:
        cursor.execute('SELECT * FROM jornadas WHERE jornada = ?', (jornada_seleccionada,))
        jornadas = cursor.fetchall()

        if not jornadas:
            messagebox.showinfo("Información", f"No se encontraron partidos para la jornada {jornada_seleccionada}.")
        else:
            ventana_listado = tk.Toplevel()
            ventana_listado.title(f"Listado de Jornada {jornada_seleccionada}")
            listbox = Listbox(ventana_listado)
            scrollbar = Scrollbar(ventana_listado)
            listbox.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=listbox.yview)

            for jornada in jornadas:
                listbox.insert(tk.END, f"{jornada[2]} {jornada[4]} - {jornada[3]} {jornada[5]}")

            listbox.pack(fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            ventana_listado.mainloop()

    conn.close()


def estadistica_jornada():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    jornadas = cursor.execute('SELECT DISTINCT jornada FROM jornadas').fetchall()
    jornadas_disponibles = [j[0] for j in jornadas]
    jornada_seleccionada = simpledialog.askinteger("Estadísticas de Jornada", "Ingrese el número de jornada:", minvalue=min(jornadas_disponibles), maxvalue=max(jornadas_disponibles))

    if jornada_seleccionada:
        cursor.execute('SELECT COUNT(*) FROM jornadas WHERE jornada = ?', (jornada_seleccionada,))
        total_partidos = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM jornadas WHERE jornada = ? AND gol_local = gol_visitante', (jornada_seleccionada,))
        empates = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM jornadas WHERE jornada = ? AND gol_local > gol_visitante', (jornada_seleccionada,))
        victorias_local = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM jornadas WHERE jornada = ? AND gol_local < gol_visitante', (jornada_seleccionada,))
        victorias_visitante = cursor.fetchone()[0]

        messagebox.showinfo("Estadísticas de Jornada", f"Jornada {jornada_seleccionada}\nTotal de Partidos: {total_partidos}\nEmpates: {empates}\nVictorias Local: {victorias_local}\nVictorias Visitante: {victorias_visitante}")

    conn.close()


def buscar_goles():
    def actualizar_equipos_locales():
        # Obtiene la jornada seleccionada
        jornada_seleccionada = int(spin_jornada.get())

        # Obtiene la lista de equipos locales para la jornada seleccionada
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        equipos_locales = cursor.execute('SELECT DISTINCT equipo_local FROM jornadas WHERE jornada = ?', (jornada_seleccionada,)).fetchall()
        conn.close()

        # Actualiza el Spinbox de equipo local con los equipos disponibles
        equipos_locales_disponibles = [e[0] for e in equipos_locales]
        spin_equipo_local['values'] = equipos_locales_disponibles

    def mostrar_goleadores():
        jornada_seleccionada = int(spin_jornada.get())
        equipo_local_seleccionado = spin_equipo_local.get()

        link_partido = obtener_link_partido(jornada_seleccionada, equipo_local_seleccionado)
        goleadores = scrape_goles(link_partido)

        ventana_goleadores = tk.Toplevel()
        ventana_goleadores.title("Goleadores del Partido")
        
        lbl_goleadores = Label(ventana_goleadores, text=f"Goleadores del partido ({jornada_seleccionada}):")
        lbl_goleadores.pack()

        lbl_goleadores_local = Label(ventana_goleadores, text=f"Local: {goleadores['local']}")
        lbl_goleadores_local.pack()

        lbl_goleadores_visitante = Label(ventana_goleadores, text=f"Visitante: {goleadores['visitant']}")
        lbl_goleadores_visitante.pack()

    ventana_buscar_goles = tk.Toplevel()
    ventana_buscar_goles.title("Buscar Goles")

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    jornadas = cursor.execute('SELECT DISTINCT jornada FROM jornadas').fetchall()
    conn.close()

    jornadas_disponibles = [j[0] for j in jornadas]

    lbl_jornada = Label(ventana_buscar_goles, text="Jornada:")
    lbl_jornada.pack()
    spin_jornada = Spinbox(ventana_buscar_goles, values=jornadas_disponibles, command=actualizar_equipos_locales)
    spin_jornada.pack()

    lbl_equipo_local = Label(ventana_buscar_goles, text="Equipo Local:")
    lbl_equipo_local.pack()
    spin_equipo_local = Spinbox(ventana_buscar_goles, values=[], state="readonly")
    spin_equipo_local.pack()

    btn_mostrar_goleadores = Button(ventana_buscar_goles, text="Mostrar Goleadores", command=mostrar_goleadores)
    btn_mostrar_goleadores.pack()

    ventana_buscar_goles.mainloop()


def obtener_link_partido(jornada, equipo_local):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Busca el enlace en la base de datos utilizando la jornada y el equipo local
    cursor.execute('SELECT link FROM jornadas WHERE jornada = ? AND equipo_local = ?', (jornada, equipo_local))
    resultado = cursor.fetchone()

    conn.close()

    if resultado:
        # Si se encontró un enlace en la base de datos, lo devuelve
        return resultado[0]
    else:
        # En caso de no encontrar el enlace, puedes manejarlo de acuerdo a tus necesidades.
        # Aquí, simplemente retornamos una cadena vacía.
        return ""


def scrape_goles(url: str) -> dict:
    scorers = dict()
    response = urllib.request.urlopen(url)
    soup = BeautifulSoup(response, 'html.parser')
    team_local = soup.find('div', class_='scr-hdr__team is-local')
    team_visitant = soup.find('div',class_='scr-hdr__team is-visitor')
    local_scorers = " ".join([scr.text for scr in team_local.find('div',class_='scr-hdr__scorers').find_all('span', class_=False)])
    visitant_scorers = " ".join([scr.text for scr in team_visitant.find('div',class_='scr-hdr__scorers').find_all('span', class_=False)])
    scorers['local'] = local_scorers
    scorers['visitant'] = visitant_scorers
    return scorers








root = tk.Tk()
root.title("Web Scraping de Furbo")

menu = tk.Menu(root)
root.config(menu=menu)

datos_menu = tk.Menu(menu)
menu.add_cascade(label="Datos", menu=datos_menu)
datos_menu.add_command(label="Cargar", command=cargar_datos)
datos_menu.add_command(label="Listar", command=listar_jornadas)
datos_menu.add_separator()
datos_menu.add_command(label="Salir", command=root.quit)

buscar_menu = tk.Menu(menu)
menu.add_cascade(label="Buscar", menu=buscar_menu)
buscar_menu.add_command(label="Buscar Jornada", command=buscar_jornada)
buscar_menu.add_command(label="Estadísticas de jornada", command=estadistica_jornada)
buscar_menu.add_command(label="Buscar goles", command=buscar_goles)

root.mainloop()