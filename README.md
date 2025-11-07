# Prueba Técnica Unico

Este repositorio contiene los recursos necesarios para probar el flujo de procesamiento de pedidos, incluyendo un archivo de muestra, un script en Python, una API REST y un flujo de n8n.

## Contenido del repositorio

 **`pedidos.xlsx`**  
  Archivo de ejemplo que permite probar el flujo en n8n.

 **`api/`**  Contiene una pequeña API REST que permite gestionar pedidos:  
  - `GET /pedidos` → Retorna una lista de pedidos.  
  - `POST /pedidos` → Permite agregar un nuevo pedido.

 **`flujo_n8n/`**  Contiene el flujo en formato JSON que resuelve la problemática presentada.

 **`script/`**   Contiene un script en Python que realiza el mismo proceso que el flujo de n8n.

## Cómo usar

1. Importa el flujo en la aplicacion n8n desde la carpeta `flujo_n8n/` .  
2. Para probar la API, ejecuta el servidor en la carpeta `api/` utilizando en bash **`uvicorn api:app --reload`**   y realiza llamadas `GET` o `POST` a los endpoints de pedidos.  
