import os
import tkinter as tk
from tkinter import messagebox
from whoosh.index import create_in
from whoosh.fields import TEXT, ID, Schema, DATETIME, KEYWORD
from whoosh.qparser import QueryParser
from whoosh.query import Term
from whoosh import qparser
from whoosh.index import open_dir

index_doc = "./whoosh1/Docs/"
agenda = "Agenda/agenda.txt"
correos = "Correos/"

# Crear un esquema para indexar correos electrónicos
schema = Schema(sender=ID(stored=True),
                recipients=KEYWORD(stored=True),
                date=DATETIME(stored=True),
                subject=TEXT(stored=True),
                body=TEXT(stored=True))
agenda = {}


# Crear o abrir el índice
email_index="email_index"
if not os.path.exists(email_index):
    os.mkdir(email_index)
    index = create_in(email_index, schema)
else:
     index = open_dir(email_index,schema=schema)


# Función para cargar correos electrónicos en el índice
def cargar_correos():
    # Bucle para cargar correos del rango 1 a 6
    index = create_in(email_index, schema)
    num_correos = 0
    for i in range(1, 7):
        archivo_correo = f"{index_doc}{correos}{i}.txt"
        if os.path.exists(archivo_correo):
            with open(archivo_correo, "r", encoding="utf-8") as archivo:
                lineas = archivo.readlines()
                if len(lineas) >= 5:
                    sender = lineas[0].strip()
                    recipients = lineas[1].strip()
                    date = lineas[2].strip()
                    subject = lineas[3].strip()
                    body = " ".join(lineas[4:]).strip()

                    writer = index.writer()
                    writer.add_document(sender=sender, recipients=recipients, date=date, subject=subject, body=body)
                    writer.commit()

    # Cargar datos de la agenda
    agenda_file = f"{index_doc}{agenda}"
    if os.path.exists(agenda_file):
        with open(agenda_file, "r", encoding="utf-8") as agenda_reader:
            lineas = agenda_reader.readlines()
            for i in range(0, len(lineas), 2):
                email = lineas[i].strip()
                nombre_apellidos = lineas[i + 1].strip()
                agenda[nombre_apellidos] = email
                agenda[email] = nombre_apellidos
    with index.searcher() as searcher:
        query = qparser.QueryParser("sender", schema).parse('*')
        results = list(searcher.search(query))
        num_correos = len(results)

    messagebox.showinfo("Información", f"{num_correos} correos y agenda cargados en el índice.")


# Función para listar correos electrónicos
# Función para listar correos electrónicos
def listar_correos():
    root_listar = tk.Toplevel(root)
    root_listar.title("Listar Correos")

    listbox = tk.Listbox(root_listar, width=100)
    listbox.pack(fill=tk.BOTH, expand=True)

    # Realizar una consulta para obtener todos los correos en el índice
    with index.searcher() as searcher:
        query = qparser.QueryParser("sender", schema).parse('*')
        results = searcher.search(query)
        for result in results:
            listbox.insert(tk.END, "_____________________________________")
            listbox.insert(tk.END, f"Remitente: {result['sender']}")
            listbox.insert(tk.END, f"Destinatarios: {result['recipients']}")
            listbox.insert(tk.END, f"Fecha: {result['date']}")
            listbox.insert(tk.END, f"Asunto: {result['subject']}")
            listbox.insert(tk.END, "Cuerpo:")
            listbox.insert(tk.END, result['body'])
            listbox.insert(tk.END, "_____________________________________")

    scrollbar = tk.Scrollbar(root_listar)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    root_listar.mainloop()

# Función para buscar correos por cuerpo
def buscar_por_cuerpo():
    root_buscar_cuerpo = tk.Toplevel(root)
    root_buscar_cuerpo.title("Buscar por Cuerpo")

    label = tk.Label(root_buscar_cuerpo, text="Ingresa el término de búsqueda en el cuerpo:")
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
            query_parser = qparser.QueryParser("body", schema)
            query = query_parser.parse(query)
            results = searcher.search(query)
            for result in results:
                listbox.insert(tk.END, "_____________________________________")
                listbox.insert(tk.END, f"Remitente: {result['sender']}")
                listbox.insert(tk.END, f"Destinatarios: {result['recipients']}")
                listbox.insert(tk.END, f"Fecha: {result['date']}")
                listbox.insert(tk.END, f"Asunto: {result['subject']}")
                listbox.insert(tk.END, "Cuerpo:")
                listbox.insert(tk.END, result['body'])
                listbox.insert(tk.END, "_____________________________________")

    boton_buscar = tk.Button(root_buscar_cuerpo, text="Buscar", command=realizar_busqueda)
    boton_buscar.pack()

    scrollbar = tk.Scrollbar(root_buscar_cuerpo)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    root_buscar_cuerpo.mainloop()

# Función para buscar correos por fecha
def buscar_por_fecha():
    root_buscar_fecha = tk.Toplevel(root)
    root_buscar_fecha.title("Buscar por Fecha")

    label = tk.Label(root_buscar_fecha, text="Ingresa la fecha (YYYYMMDD):")
    label.pack()

    entrada_fecha = tk.Entry(root_buscar_fecha)
    entrada_fecha.pack()

    listbox = tk.Listbox(root_buscar_fecha, width=100)
    listbox.pack(fill=tk.BOTH, expand=True)

    def realizar_busqueda():
        fecha = entrada_fecha.get()

        if not fecha:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una fecha.")
            return

        with index.searcher() as searcher:
            query_parser = qparser.QueryParser("date", schema)
            query = query_parser.parse(fecha)
            results = searcher.search(query)
            for result in results:
                listbox.insert(tk.END, "_____________________________________")
                listbox.insert(tk.END, f"Remitente: {result['sender']}")
                listbox.insert(tk.END, f"Destinatarios: {result['recipients']}")
                listbox.insert(tk.END, f"Fecha: {result['date']}")
                listbox.insert(tk.END, f"Asunto: {result['subject']}")
                listbox.insert(tk.END, "Cuerpo:")
                listbox.insert(tk.END, result['body'])
                listbox.insert(tk.END, "_____________________________________")

    boton_buscar = tk.Button(root_buscar_fecha, text="Buscar", command=realizar_busqueda)
    boton_buscar.pack()

    scrollbar = tk.Scrollbar(root_buscar_fecha)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    root_buscar_fecha.mainloop()

# Función para buscar correos spam
def buscar_spam():
    root_buscar_spam = tk.Toplevel(root)
    root_buscar_spam.title("Buscar Spam")

    label = tk.Label(root_buscar_spam, text="Ingresa la palabra para buscar correos spam:")
    label.pack()

    entrada_spam = tk.Entry(root_buscar_spam)
    entrada_spam.pack()

    listbox = tk.Listbox(root_buscar_spam, width=100)
    listbox.pack(fill=tk.BOTH, expand=True)

    def realizar_busqueda():
        palabra_spam = entrada_spam.get()

        if not palabra_spam:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una palabra para buscar correos spam.")
            return

        with index.searcher() as searcher:
            query_parser = qparser.QueryParser("subject", schema)
            query = query_parser.parse(palabra_spam)
            results = searcher.search(query)
            for result in results:
                listbox.insert(tk.END, "_____________________________________")
                listbox.insert(tk.END, f"Remitente: {result['sender']}")
                listbox.insert(tk.END, f"Destinatarios: {result['recipients']}")
                listbox.insert(tk.END, f"Fecha: {result['date']}")
                listbox.insert(tk.END, f"Asunto: {result['subject']}")
                listbox.insert(tk.END, "Cuerpo:")
                listbox.insert(tk.END, result['body'])
                listbox.insert(tk.END, "_____________________________________")

    boton_buscar = tk.Button(root_buscar_spam, text="Buscar", command=realizar_busqueda)
    boton_buscar.pack()

    scrollbar = tk.Scrollbar(root_buscar_spam)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    root_buscar_spam.mainloop()


# Crear la ventana principal
root = tk.Tk()
root.title("Correo Electrónico")

# Crear un menú
menu = tk.Menu(root)
root.config(menu=menu)

# Menú "Datos"
menu_datos = tk.Menu(menu)
menu.add_cascade(label="Datos", menu=menu_datos)
menu_datos.add_command(label="Cargar", command=cargar_correos)
menu_datos.add_command(label="Listar", command=listar_correos)
menu_datos.add_command(label="Salir", command=root.quit)

# Menú "Buscar"
menu_buscar = tk.Menu(menu)
menu.add_cascade(label="Buscar", menu=menu_buscar)
menu_buscar.add_command(label="Cuerpo", command=buscar_por_cuerpo)
menu_buscar.add_command(label="Fecha", command=buscar_por_fecha)
menu_buscar.add_command(label="Spam", command=buscar_spam)

# Inicializar variables para entradas de búsqueda
entrada_busqueda = tk.StringVar()
entrada_fecha = tk.StringVar()
entrada_spam = tk.StringVar()

root.mainloop()

