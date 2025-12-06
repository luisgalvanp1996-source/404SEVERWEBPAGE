import pyodbc

SERVER = r"192.168.1.85\\SERVERHOME,1433"   # O cambia a 192.168.1.85\\SERVERHOME si usas instancia con nombre
DATABASE = "404_server"
USER = "sa"
PASSWORD = "Luis1996@@"

def test_connection():
    try:
        print("Intentando conectar a SQL Server...")

        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"UID={USER};"
            f"PWD={PASSWORD};"
            "TrustServerCertificate=yes;"
        )

        cursor = conn.cursor()
        cursor.execute("SELECT @@SERVERNAME AS Servidor, DB_NAME() AS BaseActual;")
        row = cursor.fetchone()

        print("\n✅ CONEXIÓN EXITOSA")
        print(f"Servidor conectado : {row.Servidor}")
        print(f"Base de datos usada: {row.BaseActual}")

        conn.close()

    except Exception as e:
        print("\n❌ ERROR DE CONEXIÓN")
        print(e)

if __name__ == "__main__":
    test_connection()
