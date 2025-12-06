import sqlite3
import os
import pyodbc

# ------------------------------------------------------------
# CONFIGURACIÓN SQL SERVER
# ------------------------------------------------------------
server = r"Server404\SERVERHOME"
database = "404webpagedb"
UID = "sa"
PWD = "Luis1996@@"

# ------------------------------------------------------------
# RUTA ABSOLUTA SQLITE
# IMPORTANTE: funciona correcto en PyInstaller (exe)
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB = os.path.join(BASE_DIR, "db.db")


def get_connection():
    return sqlite3.connect(SQLITE_DB)


# ------------------------------------------------------------
# CONEXIÓN A SQL SERVER
# ------------------------------------------------------------
def conectar_sql_server(server, database, username, password):

    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )

    return pyodbc.connect(conn_str)


# ------------------------------------------------------------
# VERIFICAR BD LOCAL
# ------------------------------------------------------------
def ensure_local_db():
    if not os.path.exists(SQLITE_DB):
        initialize_database()


# ------------------------------------------------------------
# CREAR TABLAS EN SQLITE
# ------------------------------------------------------------
def initialize_database():
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TEMPORAL_DAT_BIBLIA (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            TIPO_ID INT NOT NULL,
            LIBRO_ID INT NOT NULL,
            CAPITULO INT NOT NULL,
            VERSICULO_INICIO INT NOT NULL,
            VERSICULO_FIN INT NOT NULL,
            MODULO INT NOT NULL,
            TEXTO TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CAT_LIBROS_BIBLIA (
            id INTEGER PRIMARY KEY,
            LIBRO INT NOT NULL,
            NOMBRE TEXT NOT NULL,
            ABREVIATURA TEXT NOT NULL,
            CAPITULOS INT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BIBLIA (
            id INTEGER PRIMARY KEY,
            LIBRONUM INT NOT NULL,
            CAPITULO INT NOT NULL,
            VERSICULO INT NOT NULL,
            TEXTO TEXT NOT NULL
        );
    """)

    conn.commit()
    conn.close()


# ------------------------------------------------------------
# VERIFICAR SQL SERVER
# ------------------------------------------------------------
def check_sql_server_connection():
    try:
        conn = conectar_sql_server(server, database, UID, PWD)
        conn.close()
        return True
    except Exception as e:
        print("SQL Server no disponible:", e)
        return False


# ------------------------------------------------------------
# SINCRONIZAR CATÁLOGOS SQL → SQLITE
# ------------------------------------------------------------
def sync_catalogs_from_sqlserver_to_sqlite():
    try:
        ensure_local_db()

        sql = conectar_sql_server(server, database, UID, PWD)
        sqlite_db = get_connection()

        sql_cur = sql.cursor()
        sq_cur = sqlite_db.cursor()

        # ---------------------------
        # CAT_LIBROS_BIBLIA
        # ---------------------------
        sql_cur.execute("SELECT id, LIBRO, NOMBRE, ABREVIATURA, CAPITULOS FROM CAT_LIBROS_BIBLIA")
        rows = sql_cur.fetchall()

        data_libros = [(r.id, r.LIBRO, r.NOMBRE, r.ABREVIATURA, r.CAPITULOS if r.CAPITULOS is not None else 0) for r in rows ]

        sq_cur.executemany("""
            INSERT OR IGNORE INTO CAT_LIBROS_BIBLIA (id, LIBRO, NOMBRE, ABREVIATURA, CAPITULOS)
            VALUES (?, ?, ?, ?, ?)
        """, data_libros)

        # ---------------------------
        # BIBLIA
        # ---------------------------
        sql_cur.execute("SELECT id, LIBRONUM, CAPITULO, VERSICULO, TEXTO FROM BIBLIA")
        rows = sql_cur.fetchall()

        data_biblia = [(r.id, r.LIBRONUM, r.CAPITULO, r.VERSICULO, r.TEXTO) for r in rows]

        sq_cur.executemany("""
            INSERT OR IGNORE INTO BIBLIA (id, LIBRONUM, CAPITULO, VERSICULO, TEXTO)
            VALUES (?, ?, ?, ?, ?)
        """, data_biblia)

        sqlite_db.commit()

        return "Catálogos sincronizados correctamente."

    except Exception as e:
        return f"Error al sincronizar catálogos: {e}"

    finally:
        try:
            sqlite_db.close()
            sql.close()
        except:
            pass


# ------------------------------------------------------------
# SUBIR DATOS LOCALES SQLite → SQL Server
# ------------------------------------------------------------
def sync_local_data_to_sqlserver():
    try:
        ensure_local_db()

        sqlite_db = get_connection()
        sql = conectar_sql_server(server, database, UID, PWD)

        sq_cur = sqlite_db.cursor()
        sql_cur = sql.cursor()

        sq_cur.execute("""
            SELECT TIPO_ID, LIBRO_ID, CAPITULO, VERSICULO_INICIO, VERSICULO_FIN, MODULO, TEXTO
            FROM TEMPORAL_DAT_BIBLIA
        """)

        rows = sq_cur.fetchall()

        if len(rows) == 0:
            return "No hay datos locales para enviar."

        sql_cur.executemany("""
            INSERT INTO TEMPORAL_DAT_BIBLIA 
            (TIPO_ID, LIBRO_ID, CAPITULO, VERSICULO_INICIO, VERSICULO_FIN, MODULO, TEXTO)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, rows)

        sql.commit()

        sq_cur.execute("DELETE FROM TEMPORAL_DAT_BIBLIA")
        sqlite_db.commit()

        return "Datos locales enviados correctamente."

    except Exception as e:
        return f"Error al enviar datos locales: {e}"

    finally:
        try:
            sqlite_db.close()
            sql.close()
        except:
            pass


# ------------------------------------------------------------
# SINCRONIZACIÓN COMPLETA
# ------------------------------------------------------------
def sync_all():
    if not check_sql_server_connection():
        return "No hay conexión con SQL Server."

    msg1 = sync_catalogs_from_sqlserver_to_sqlite()
    msg2 = sync_local_data_to_sqlserver()

    return f"{msg1}\n{msg2}"
