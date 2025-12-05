import sqlite3

def initialize_database(db):
    """Initializes the SQLite database with users and posts tables."""
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TEMPORAL_DAT_BIBLIA (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            TIPO_ID INT NOT NULL,
            LIBRO_ID INT NOT NULL,
            CAPITULO INT NOT NULL,
            VERSICULO_INICIO INT NOT NULL,
            VERSICULO_FIN INT NOT NULL,
            MODULO INT NOT NULL,
            TEXTO NVARCHAR(MAX) NOT NULL,
        );
    ''')

    # Create posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CAT_LIBROS_BIBLIA (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            LIBRO INT NOT NULL,
            NOMBRE NVARCHAR(100) NOT NULL,
            ABREVIATURA NVARCHAR(20) NOT NULL,
            CAPITULOS INT NOT NULL,
        );
    ''')

    # Create posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BIBLIA (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            LIBRONUM INT NOT NULL,
            CAPITULO INT NOT NULL,
            VERSICULO INT NOT NULL,
            TEXTO NVARCHAR(MAX) NOT NULL,
        );
    ''')

    conn.commit()
    conn.close()

def connect_db(db):
    """Connects to the SQLite database."""
    return sqlite3.connect(db)


server = 'Server404\SERVERHOME'
database = '404webpagedb'
UID = 'sa'
PWD = 'Luis1996@@'


def conectar_sql_server(server, database, username, password):
    """Connects to a SQL Server database."""
    import pyodbc
    conn_str = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password}'
    )
    return pyodbc.connect(conn_str)
