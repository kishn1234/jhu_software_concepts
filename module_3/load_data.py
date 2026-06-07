import psycopg

conn = psycopg.connect(
    dbname="gradcafe",
    user="kishore.narayanan"
)

print("Connected successfully")

conn.close()