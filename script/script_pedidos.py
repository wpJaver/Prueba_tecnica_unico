import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os
import unicodedata


RUTA_EXCEL = r"C:/Users/USER/Documents/Data/pedidos.xlsx"

# Correos
CORREOS = [
    {"Ciudad": "Cali", "email": "wp.javer@gmail.com"},
    {"Ciudad": "Medellin", "email": "wapluc2@gmail.com"},
    {"Ciudad": "Ibague", "email": "sanchez.javier@correounivalle.edu.co"}
]


load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

MYSQL_CONFIG = {
    "host": "localhost",
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASS"),
    "database": os.getenv("MYSQL_DB")
}


def normalizar_texto(texto):
    if not isinstance(texto, str):
        return texto
    texto = texto.strip().lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = ''.join(c for c in texto if c.isalnum() or c.isspace())
    return texto

def formato_monto(monto):
    try:
        return "{:,.0f}".format(float(monto))
    except Exception:
        return str(monto)

def leer_pedidos(ruta_excel):
    """Lee el Excel con pedidos."""
    df = pd.read_excel(ruta_excel)
    print(f"Pedidos cargados: {len(df)} registros")
    return df

def normalizar_pedidos(df):

    df_normalizado = df.copy()

    for col in df_normalizado.columns:
        if df_normalizado[col].dtype == object:
            df_normalizado[col] = df_normalizado[col].apply(normalizar_texto)

    # Agregar fecha de auditoría
    df_normalizado["Audit_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return df_normalizado

def generar_tabla_html(df):
    filas = []
    for i, row in df.iterrows():
        color = "#ffffff" if i % 2 == 0 else "#f9f9f9"
        filas.append(f"""
            <tr style="background-color:{color};">
                <td style="padding:8px;border:1px solid #ddd;">{row['Cliente']}</td>
                <td style="padding:8px;border:1px solid #ddd;">{formato_monto(row['Monto'])}</td>
            </tr>
        """)
    tabla = f"""
    <table style="border-collapse:collapse;width:100%;font-family:Arial,sans-serif;">
        <thead>
            <tr style="background-color:#4CAF50;color:white;text-align:left;">
                <th style="padding:8px;border:1px solid #ddd;">Cliente</th>
                <th style="padding:8px;border:1px solid #ddd;">Monto</th>
            </tr>
        </thead>
        <tbody>
            {''.join(filas)}
        </tbody>
    </table>
    """
    return tabla

def enviar_email(destinatario, asunto, cuerpo_html):
    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_USER
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo_html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"Correo enviado a {destinatario}")
    except Exception as e:
        print(f"Error enviando correo a {destinatario}: {e}")

def insertar_pedidos(df):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        # Cliente
        cursor.execute("""
            INSERT INTO clientes (nombre_cliente)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE id_cliente=LAST_INSERT_ID(id_cliente)
        """, (row["Cliente"],))
        cursor.execute("SELECT LAST_INSERT_ID()")
        id_cliente = cursor.fetchone()[0]

        # Producto
        cursor.execute("""
            INSERT INTO productos (nombre_producto)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE id_producto=LAST_INSERT_ID(id_producto)
        """, (row["Producto"],))
        cursor.execute("SELECT LAST_INSERT_ID()")
        id_producto = cursor.fetchone()[0]

        # Ciudad
        cursor.execute("""
            INSERT INTO ciudades (nombre_ciudad)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE id_ciudad=LAST_INSERT_ID(id_ciudad)
        """, (row["Ciudad"],))
        cursor.execute("SELECT LAST_INSERT_ID()")
        id_ciudad = cursor.fetchone()[0]

        # audit
        audit_date = row["Audit_date"]
        mes = pd.to_datetime(audit_date).strftime("%B")  
        anio = pd.to_datetime(audit_date).year

        # Mes
        cursor.execute("""
            INSERT INTO meses (nombre_mes)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE id_mes=LAST_INSERT_ID(id_mes)
        """, (mes,))
        cursor.execute("SELECT LAST_INSERT_ID()")
        id_mes = cursor.fetchone()[0]

        # Año
        cursor.execute("""
            INSERT INTO anios (anio)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE id_anio=LAST_INSERT_ID(id_anio)
        """, (anio,))
        cursor.execute("SELECT LAST_INSERT_ID()")
        id_anio = cursor.fetchone()[0]

        # Pedidos
        cantidad = row.get("Cantidad") or 0
        monto = row.get("Monto") or 0

        cursor.execute("""
            INSERT INTO pedidos (
                id_cliente, id_producto, id_ciudad, id_mes, id_anio, cantidad, monto, audit_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (id_cliente, id_producto, id_ciudad, id_mes, id_anio, cantidad, monto, audit_date))

    conn.commit()
    cursor.close()
    conn.close()
    print("Pedidos insertados correctamente en pedidos_db.")

# === FLUJO PRINCIPAL ===
def main():
    print(f"Iniciando - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Leer Excel
    pedidos = leer_pedidos(RUTA_EXCEL)

    # Normalizar datos
    pedidos_normalizados = normalizar_pedidos(pedidos)

    # Insertar en base relacional normalizada
    insertar_pedidos(pedidos_normalizados)

    # Enviar correos por ciudad
    for registro in CORREOS:
        ciudad = registro["Ciudad"]
        email = registro["email"]

        pedidos_ciudad = pedidos_normalizados[pedidos_normalizados["Ciudad"].str.lower() == ciudad.lower()]
        if not pedidos_ciudad.empty:
            tabla_html = generar_tabla_html(pedidos_ciudad)
            cuerpo_html = f"""
            <p>Los clientes de la ciudad de <b>{ciudad}</b> son:</p>
            {tabla_html}
            """
            enviar_email(email, f"Pedidos de {ciudad}", cuerpo_html)
        else:
            print(f"ℹNo hay pedidos para {ciudad}")

if __name__ == "__main__":
    main()
