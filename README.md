# GYMBRO-MANAGEMENT-API

## Getting started

Esta es una API creada en Python con FastAPI para manejar la comunicación con la App Web

## Clonación del proyecto

Realizar la clonación estandar

## Levantar el proyecto

# 1.- Creación de un entorno virtual

Crear un entorno virtual ejemplo:  python -m venv entorno


# 2.- Ingresar al entorno creado

Para ingresar al entorno creado se debe correr el comando: .\entorno\Scripts\activate

 
# 3.- Instalar las dependencias del proyecto que estan en la carpeta requirements.txt

Se necesita instalar las dependencias EJemplo: pip install -r requirements.txt

# 4.- Levantar el proyecto usando uvicorn

Para levantar el Proyecto, se debe ingresar los comando: Uvicorn app.main:app --reload 

## Si queremos usarlo en red con nuestra ip, tenemos que agregar: 
--host 0.0.0.0

## Si queremos especificar el puerto, agregamos:
--port 8001

# 5.- Visualizar el Swagger
Ingresar al navegador y colocar: localhost:8000/docs

## No se requiere volver a levantar el proyecto para ver los cambios de lógica

## Si se agrega nuevas dependencias, se necesita volver a crear el archivo requirements
comando para crear: python -m pip freeze > requirements.txt

