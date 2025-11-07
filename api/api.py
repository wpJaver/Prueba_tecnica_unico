import os
import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime

load_dotenv()

app = FastAPI()


db = mysql.connector.connect(
    host="localhost",
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASS"),
    database=os.getenv("MYSQL_DB")
)

cursor = db.cursor(dictionary=True)


class Pedido(BaseModel):
    id_cliente: int
    id_producto: int
    id_ciudad: int
    id_mes: int
    id_anio: int
    cantidad: int
    monto: float
    audit_date: Optional[datetime] = None


# GET: ver pedidos
@app.get("/pedidos/")
def ver_pedidos():
    cursor.execute("SELECT * FROM pedidos")
    pedidos = cursor.fetchall()
    return {"pedidos": pedidos}

# POST: crear pedido
@app.post("/pedidos/")
def crear_pedido(pedido: Pedido):
    try:
        query = """
        INSERT INTO pedidos 
        (id_cliente, id_producto, id_ciudad, id_mes, id_anio, cantidad, monto, audit_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            pedido.id_cliente,
            pedido.id_producto,
            pedido.id_ciudad,
            pedido.id_mes,
            pedido.id_anio,
            pedido.cantidad,
            pedido.monto,
            pedido.audit_date if pedido.audit_date else datetime.now()
        )
        cursor.execute(query, values)
        db.commit()
        return {"mensaje": "Pedido creado", "pedido": pedido.dict()}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
