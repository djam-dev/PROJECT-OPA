import psycopg2

try:
    conn = psycopg2.connect(
        dbname="binance_data",     # nom de la base créée dans pgAdmin ou VS Code
        user="postgres",           # utilisateur PostgreSQL
        password="Masri71854415",  # remplace ici
        host="localhost",
        port="5432"
    )
    print("✅ Connexion réussie à PostgreSQL")
    conn.close()
except Exception as e:
    print("❌ Erreur de connexion :", e)