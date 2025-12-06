import tkinter as tk
import tkinter.ttk as ttk
import os
from tkinter import messagebox

from funtions import (
    check_sql_server_connection,
    sync_catalogs_from_sqlserver_to_sqlite,
    initialize_database,
    sqlite3,
    get_connection,
    BASE_DIR,
    SQLITE_DB
)

# -------------------------------
#   Funciones de sincronización
# -------------------------------



def sync_catalogs():
    try:
        sync_catalogs_from_sqlserver_to_sqlite()
        messagebox.showinfo("Sincronización", "Catálogos sincronizados correctamente.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def sync_temporal_data():
    messagebox.showinfo("Info", "Función de subir SQLite → SQL Server pendiente de implementar.")

# -------------------------------
#   Crear formularios dinámicos
# -------------------------------

def show_home(frame_right):
    clear_frame(frame_right)
    tk.Label(frame_right, text="Bienvenido", font=("Arial", 16)).pack(pady=20)

def show_form_registro(frame_right):
    clear_frame(frame_right)

    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------
    # Cargar libros desde SQLite
    # -------------------------
    cursor.execute("SELECT id, NOMBRE FROM CAT_LIBROS_BIBLIA ORDER BY id")
    libros = cursor.fetchall()

    # Diccionario: Nombre → ID
    libros_dict = { nombre: id_ for (id_, nombre) in libros }

    # Lista solo de nombres para el combo
    libros_nombres = list(libros_dict.keys())

    conn.close()

    # -------------------------
    # UI
    # -------------------------

    tk.Label(frame_right, text="Registrar Versículo", font=("Arial", 16)).pack(pady=10)

    # ===== LIBRO =====
    tk.Label(frame_right, text="Libro").pack()
    combo_libro = ttk.Combobox(frame_right, values=libros_nombres, state="readonly")
    combo_libro.pack(pady=5)

    # ===== CAPÍTULO =====
    tk.Label(frame_right, text="Capítulo").pack()
    combo_capitulo = ttk.Combobox(frame_right, values=[], state="readonly")
    combo_capitulo.pack(pady=5)

    # ===== VERSÍCULO INICIO =====
    tk.Label(frame_right, text="Versículo inicio").pack()
    combo_v_ini = ttk.Combobox(frame_right, values=[], state="readonly")
    combo_v_ini.pack(pady=5)

    # ===== VERSÍCULO FIN =====
    tk.Label(frame_right, text="Versículo fin").pack()
    combo_v_fin = ttk.Combobox(frame_right, values=[], state="readonly")
    combo_v_fin.pack(pady=5)

    # ===== TEXTO =====
    tk.Label(frame_right, text="Texto del versículo").pack(pady=10)
    txt_contenido = tk.Text(frame_right, width=80, height=10)
    txt_contenido.pack(pady=10)

    # -------------------------
    # EVENTOS DINÁMICOS
    # -------------------------

    def on_select_libro(event):
        nombre_libro = combo_libro.get()
        libro_id = libros_dict[nombre_libro]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT CAPITULOS FROM CAT_LIBROS_BIBLIA WHERE id = ?", (libro_id,))
        cap_max = cursor.fetchone()[0]
        conn.close()

        # Llenar capítulos 1..CAPITULOS
        combo_capitulo["values"] = list(range(1, cap_max + 1))
        combo_capitulo.set("")

    combo_libro.bind("<<ComboboxSelected>>", on_select_libro)

    def on_select_capitulo(event):
        nombre_libro = combo_libro.get()
        libro_id = libros_dict[nombre_libro]
        cap = combo_capitulo.get()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) 
            FROM BIBLIA 
            WHERE LIBRONUM=? AND CAPITULO=?
        """, (libro_id, cap))

        vers_max = cursor.fetchone()[0]
        conn.close()

        combo_v_ini["values"] = list(range(1, vers_max + 1))
        combo_v_fin["values"] = list(range(1, vers_max + 1))

        combo_v_ini.set("")
        combo_v_fin.set("")

    combo_capitulo.bind("<<ComboboxSelected>>", on_select_capitulo)

    # -------------------------
    # GUARDAR
    # -------------------------

    def guardar():
        libro_nombre = combo_libro.get()
        libro_id = libros_dict.get(libro_nombre)
        cap = combo_capitulo.get()
        v_ini = combo_v_ini.get()
        v_fin = combo_v_fin.get()
        texto = txt_contenido.get("1.0", tk.END).strip()

        if not libro_id or not cap or not v_ini or not v_fin or not texto:
            messagebox.showerror("Error", "Completa todos los campos.")
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO TEMPORAL_DAT_BIBLIA
            (TIPO_ID, LIBRO_ID, CAPITULO, VERSICULO_INICIO, VERSICULO_FIN, MODULO, TEXTO)
            VALUES (1, ?, ?, ?, ?, 1, ?)
        """, (libro_id, cap, v_ini, v_fin, texto))

        conn.commit()
        conn.close()

        messagebox.showinfo("OK", "Versículo guardado correctamente.")
        txt_contenido.delete("1.0", tk.END)

    tk.Button(frame_right, text="Guardar", bg="green", fg="white", command=guardar).pack(pady=20)


def show_config(frame_right):
    clear_frame(frame_right)
    tk.Label(frame_right, text="Configuración", font=("Arial", 16)).pack(pady=20)

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def prepare_database():
    if not os.path.exists(BASE_DIR):
        print("Base local no existe. Creando...")
        initialize_database()
    else:
        print("Base local ya existe, no se inicializa.")
# -------------------------------
#   MAIN WINDOW
# -------------------------------

def main():
    # Ventana principal
    window = tk.Tk()
    window.title("Recursos Offline - Escritorio")
    window.state("zoomed")
    
    # ------------------------------------------
    # BARRA DE MENÚ AL ESTILO WINDOWS
    # ------------------------------------------
    menubar = tk.Menu(window)

    # --- Menu Archivo
    menu_archivo = tk.Menu(menubar, tearoff=0)
    menu_archivo.add_command(label="Salir", command=window.quit)
    menubar.add_cascade(label="Archivo", menu=menu_archivo)

    # --- Menu Sincronizar
    menu_sync = tk.Menu(menubar, tearoff=0)
    menu_sync.add_command(label="Actualizar catálogos (SQL → SQLite)", command=sync_catalogs)
    menu_sync.add_command(label="Subir datos (SQLite → SQL Server)", command=sync_temporal_data)
    menubar.add_cascade(label="Sincronizar", menu=menu_sync)

    # --- Menu Herramientas
    menu_tools = tk.Menu(menubar, tearoff=0)
    menu_tools.add_command(label="Configuración", command=lambda: show_config(frame_right))
    menubar.add_cascade(label="Herramientas", menu=menu_tools)

    # --- Menu Ayuda
    menu_help = tk.Menu(menubar, tearoff=0)
    menu_help.add_command(label="Acerca de")
    menubar.add_cascade(label="Ayuda", menu=menu_help)

    window.config(menu=menubar)

    # ------------------------------------------
    # DASHBOARD (Panel izquierdo + contenido)
    # ------------------------------------------

    # Panel izquierdo
    frame_left = tk.Frame(window, width=200, bg="#0c3c12")
    frame_left.pack(side="left", fill="y")

    # Panel derecho (contenido dinámico)
    global frame_right
    frame_right = tk.Frame(window, bg="#ffffff")
    frame_right.pack(side="right", fill="both", expand=True)

    # Botones del panel izquierdo
    btn_home = tk.Button(
        frame_left, text="Inicio", bg="#145c1b", fg="white",
        command=lambda: show_home(frame_right)
    )
    btn_home.pack(fill="x", pady=5)

    btn_registrar = tk.Button(
        frame_left, text="Registrar Versículos", bg="#145c1b", fg="white",
        command=lambda: show_form_registro(frame_right)
    )
    btn_registrar.pack(fill="x", pady=5)

    btn_config = tk.Button(
        frame_left, text="Configuración", bg="#145c1b", fg="white",
        command=lambda: show_config(frame_right)
    )
    btn_config.pack(fill="x", pady=5)

    # Pantalla inicial
    show_home(frame_right)

    window.mainloop()

if __name__ == "__main__":
    prepare_database()
    main()
