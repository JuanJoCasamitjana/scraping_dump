import requests
import urllib.request
from bs4 import BeautifulSoup
import sqlite3
from tkinter import *
from tkinter import messagebox

URL = "https://totalsport.es/Outlet-de-deporte/hombre/"
DB = "zapatos.db"

def create_table(cursor: sqlite3.Cursor) :
    cursor.execute('DROP TABLE IF EXISTS articulos')
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS articulos (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            categoria TEXT,
            referencia TEXT,
            descuento INTEGER,
            es_novedad BOOLEAN,
            precio_original DECIMAL,
            tallas TEXT
        )'''
    )
    cursor.execute("DROP TABLE IF EXISTS CATEGORIAS")
    cursor.execute('''CREATE TABLE CATEGORIAS
            (CATEGORIA TEXT  );''')
    cursor.execute("DROP TABLE IF EXISTS tallas")
    cursor.execute('''CREATE TABLE tallas
            (talla TEXT  );''')

def insert(cursor: sqlite3.Cursor, conn: sqlite3.Connection, articulos: tuple) :
    conn.execute("""INSERT INTO articulos (nombre, categoria, referencia, descuento, es_novedad, precio_original, tallas) VALUES (?,?,?,?,?,?,?)""",
                        articulos)
    conn.commit()

def insert_categoria(cursor: sqlite3.Cursor, conn: sqlite3.Connection, categoria: str):
    conn.execute("""INSERT INTO categorias (categoria) VALUES (?)""",
                        (categoria,))
    conn.commit()
def insert_talla(cursor: sqlite3.Cursor, conn: sqlite3.Connection, talla: str):
    conn.execute("""INSERT INTO tallas (talla) VALUES (?)""",
                        (talla,))
    conn.commit()

def scrape_articulos(url: str) -> (list, set, set):
    NUMERO_DE_PAGINA=4
    lista_articulos = []
    categorias_set = set()
    tallas_set = set()
    for p in range(1,NUMERO_DE_PAGINA+1):
        
        f = urllib.request.urlopen(url+"?page="+str(p))
        # print(n_p)
        s = BeautifulSoup(f, "html.parser")
        lista_linkzapatillas = s.find("div", class_="products row products-grid").find_all("div", class_="js-product-miniature-wrapper")
        for i in lista_linkzapatillas:
            nombre=i.find("div",class_="product-description").h3.a.string.strip()
            categorias= i.find('div', class_='product-category-name').text
            categorias_set.add(categorias)
            novedad = i.find('ul',class_='product-flags').find('li',class_='new')
            es_novedad = novedad != None
            tallas = [talla.text for talla in i.find('div', class_='iqitsizeguide-avaiable-sizes').find_all('span')]
            tallas_set.add(talla for talla in tallas)
            tallas = ",".join(tallas)
            referencia= i.find("div",class_="product-description").find("div",class_="product-reference text-muted").a.string.strip()
            descuento= "".join(i.find("div",class_="thumbnail-container").ul.li.stripped_strings)
            if descuento==None:
                descuento= 0
            if(descuento.__contains__("-")):
                descuento=descuento.replace("-","")
            if(descuento.__contains__("%")):
                descuento=descuento.replace("%","")
            descuento=int(descuento)
            preciooriginal=i.find("div",class_="product-description").find("div",class_="product-price-and-shipping").a.span.string.strip()
            if preciooriginal.__contains__("€"):
                precio_original=preciooriginal.replace("€","").strip()
            precio_original=float(precio_original.replace(",","."))
            articulo = (nombre, categorias, referencia, descuento, es_novedad, precio_original, tallas)
            lista_articulos.append(articulo)
    return (lista_articulos,categorias_set, tallas_set)

                
def cargar():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    create_table(cursor)
    res = scrape_articulos(URL)
    articulos = res[0]
    categorias = res[1]
    tallas = res[2]
    for articulo in articulos:
        insert(cursor, conn, articulo)
    for categoria in categorias:
        insert_categoria(cursor, conn, categoria)
    for talla in tallas:
        insert_talla(cursor, conn, categoria)
    cursor.execute("SELECT count(*) FROM articulos")
    num_recetas = cursor.fetchone()[0]
    messagebox.showinfo("Información", f"Se han almacenado {num_recetas} articulos en la base de datos.")
    conn.close()

#cursor -> NOMBRE, CATEGORIA, REFERENCIA, PRECIO, TALLAS, DESCUENTO
def listar_articulos(cursor):      
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END, "------------------------------------------------------------------------\n\n")
        lb.insert(END, 'attr: ' + str(row[0]) + "\n")
        s = "Nombre: " + str(row[0]) + ' Categoría: ' + str(row[1]) + ' Ref: ' + str(row[2]) + ' Precio: ' + str(row[3]) + ' Tallas: ' + str(row[4]) + "\n"
        lb.insert(END,s)
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

def listar_descuento(cursor):      
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        precio = row[2]
        descuento = row[3]
        precio_descuento = precio * (1 - descuento/100)
        lb.insert(END, "------------------------------------------------------------------------\n\n")
        lb.insert(END, 'attr: ' + str(row[0]) + "\n")
        s = "Nombre: " + str(row[0]) + ' Categoría: ' + str(row[1]) + ' Precio: ' + str(row[2]) + ' Descuento: ' + str(row[3]) + 'Precio con descuento:' + str(precio_descuento) +"\n"
        lb.insert(END,s)
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

def buscar_por_talla():  
    def listar(event):
        conn = sqlite3.connect(DB)
        conn.text_factory = str
        cursor = conn.execute("SELECT nombre, categoria, referencia, precio_original, tallas, descuento FROM articulos WHERE tallas LIKE '%" + str(talla.get()) + "%'")
        conn.close
        listar_articulos(cursor)
    
    conn = sqlite3.connect(DB)
    conn.text_factory = str
    cursor = conn.execute("SELECT talla FROM tallas")
    
    tallas = [c[0] for c in cursor]

    ventana = Toplevel()
    label = Label(ventana, text="Introduzca talla: ")
    label.pack(side=LEFT)
    talla = Spinbox(ventana,width=30, values=tallas)
    talla.bind("<Return>", listar)
    talla.pack(side=LEFT)

    conn.close()

def buscar_por_precio():
    def listar(event):
        conn = sqlite3.connect(DB)
        conn.text_factory = str
        cursor = conn.execute("SELECT nombre, categoria, referencia, precio_original, tallas, descuento FROM articulos WHERE precio_original < ? ORDER BY precio_original", (str(entry.get()),))
        conn.close
        listar_articulos(cursor)

    ventana = Toplevel()
    label = Label(ventana, text="Indique el precio máximo: ")
    label.pack(side=LEFT)
    entry = Entry(ventana)
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)

def ventana_principal():
    def listar_arts():
            conn = sqlite3.connect(DB)
            conn.text_factory = str
            cursor = conn.execute("SELECT nombre, categoria, referencia, precio_original, tallas, descuento FROM articulos")
            conn.close
            listar_articulos(cursor)
    def listar_desc():
            conn = sqlite3.connect(DB)
            conn.text_factory = str
            cursor = conn.execute("SELECT nombre, categoria, precio_original, descuento FROM articulos")
            conn.close
            listar_descuento(cursor)

    raiz = Tk()

    menu = Menu(raiz)

    #DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar todo", command=listar_arts)
    menudatos.add_command(label="Listar descuento", command=listar_desc)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    #BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Precio", command=buscar_por_precio)
    menubuscar.add_command(label="Tallas", command=buscar_por_talla)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()



if __name__ == "__main__":
    ventana_principal()

#scrape_articulos(URL)