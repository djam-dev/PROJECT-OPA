import psycopg2

def get_db_connection():
    return psycopg2.connect(
        dbname="binance_data",
        user="VALDML",
        password="PROJETOPA",
        host="postgres",
        port="5432"
    )