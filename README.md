# Bike Repair Management

Prototipo local para gestionar las reparaciones de un taller de bicicletas.

La aplicación permite:

- registrar una nueva orden de reparación;
- consultar las órdenes existentes;
- cambiar su estado entre `Pendiente`, `En reparación` y `Terminada`.

El objetivo ha sido resolver el flujo solicitado de forma sencilla, verificable
y con especial atención a la privacidad, la seguridad y el tratamiento de los
datos.

## Tecnologías utilizadas

### Backend

- Python
- FastAPI
- Pydantic
- SQLite
- pytest

### Frontend

- React
- TypeScript
- Vite

### Entorno

- Docker
- Docker Compose

Docker es opcional. La aplicación también puede ejecutarse directamente con
Python y Node.js.

## Ejecución rápida con Docker

Con Docker y Docker Compose instalados, desde la raíz del repositorio:

```sh
docker compose up --build
```

En instalaciones antiguas de Docker Compose puede utilizarse:

```sh
docker-compose up --build
```

Una vez iniciados los servicios:

- Frontend: http://localhost:5173
- API: http://localhost:8000/repair-orders
- Documentación interactiva: http://localhost:8000/docs

Para detener la aplicación:

```sh
docker compose down
```

o, con Docker Compose v1:

```sh
docker-compose down
```

La base de datos SQLite se almacena en un volumen persistente de Docker, por lo
que las órdenes se conservan aunque se recree el contenedor del backend.

Los puertos se publican únicamente en la interfaz local `127.0.0.1`.

## Ejecución sin Docker

### Requisitos

- Python 3.10 o superior
- Node.js 22.12 o superior

### Backend

Desde la raíz del repositorio:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Después:

```sh
python -m uvicorn backend.main:create_app --factory --host 127.0.0.1 --port 8000
```

La documentación interactiva estará disponible en:

```text
http://127.0.0.1:8000/docs
```

En ejecución local, el backend crea `repair_orders.sqlite3` en la raíz del
repositorio.

Este archivo se encuentra excluido de Git.

### Frontend

En una segunda terminal:

```sh
cd frontend
npm ci
npm run dev
```

Abrir:

```text
http://localhost:5173
```

Vite utiliza el puerto `5173` y está configurado para no cambiar
automáticamente a otro puerto si este se encuentra ocupado.

## Funcionamiento

Cada orden de reparación contiene:

- `id`: identificador generado por el servidor;
- `customer_code`: código ficticio de cliente;
- `bicycle_description`: descripción de la bicicleta;
- `reported_issue`: problema comunicado;
- `status`: estado actual de la reparación.

Los estados internos permitidos son:

- `pending`;
- `in_progress`;
- `completed`.

La interfaz los presenta respectivamente como:

- Pendiente;
- En reparación;
- Terminada.

Las nuevas órdenes comienzan siempre en estado `pending`.

## API

| Método | Ruta | Función |
| --- | --- | --- |
| `POST` | `/repair-orders` | Crear una orden de reparación |
| `GET` | `/repair-orders` | Consultar las órdenes existentes |
| `PATCH` | `/repair-orders/{id}/status` | Modificar el estado de una orden |

La creación de una reparación acepta únicamente:

- `customer_code`: entre 1 y 40 caracteres;
- `bicycle_description`: entre 1 y 200 caracteres;
- `reported_issue`: entre 1 y 500 caracteres.

El backend elimina los espacios en blanco sobrantes antes de validar las
longitudes.

Los campos no esperados se rechazan en lugar de ignorarse silenciosamente.

También se rechazan:

- campos obligatorios ausentes;
- valores vacíos;
- valores formados únicamente por espacios;
- tipos de datos incorrectos;
- estados distintos de los permitidos.

FastAPI y Pydantic devuelven `422` cuando los datos enviados no son válidos.

## Decisiones principales

### Mantener el alcance pequeño

El ejercicio tiene un límite máximo de tres horas, por lo que he priorizado una
solución pequeña y fácil de comprender frente a introducir infraestructura o
abstracciones que no aportasen valor al problema.

No se han añadido funcionalidades como autenticación, notificaciones,
inventario, facturación o despliegue en la nube porque no forman parte del
alcance solicitado.

### FastAPI y Pydantic

FastAPI permite definir una API pequeña y explícita, mientras que Pydantic se
utiliza para validar los datos recibidos.

La validación principal se realiza siempre en el backend.

El servidor controla, entre otras cosas:

- los campos admitidos;
- las longitudes;
- los estados permitidos;
- la generación del identificador;
- el estado inicial de una reparación.

El frontend no se considera una fuente de confianza.

### SQLite sin ORM

Se utiliza directamente el módulo `sqlite3` de Python.

El dominio actual requiere únicamente un modelo principal y tres operaciones,
por lo que introducir un ORM habría aumentado la complejidad sin aportar una
ventaja clara para este prototipo.

Todas las consultas que utilizan datos variables están parametrizadas.

Por ejemplo, los datos enviados por el usuario nunca se concatenan directamente
dentro de una sentencia SQL.

La base de datos también incluye una restricción sobre los valores permitidos
para el estado.

### Persistencia

SQLite es la única fuente de persistencia.

El frontend conserva únicamente el estado necesario para representar la
interfaz y no utiliza `localStorage` ni otra persistencia paralela.

En ejecución local se utiliza un archivo SQLite.

En Docker, la ruta de la base de datos se configura mediante:

```text
BIKE_REPAIR_DATABASE_PATH
```

y los datos se almacenan en un volumen persistente.

### Escrituras confirmadas por el backend

El frontend no considera una modificación guardada hasta haber recibido una
respuesta correcta del servidor.

Por ejemplo, al cambiar el estado de una reparación, la interfaz conserva el
último estado confirmado si la petición falla.

### CORS

El backend permite peticiones únicamente desde los dos orígenes utilizados por
el frontend local:

```text
http://localhost:5173
http://127.0.0.1:5173
```

Los métodos permitidos son únicamente:

```text
GET
POST
PATCH
```

No se utilizan orígenes comodín ni credenciales CORS.

### Docker

Docker se incluye como forma opcional de reproducir el entorno completo.

La configuración intenta mantener la misma sencillez que el resto del proyecto.

Los contenedores:

- utilizan imágenes oficiales de Python y Node;
- ejecutan los procesos con usuarios no root;
- publican los servicios únicamente sobre `127.0.0.1`;
- utilizan contextos de build restringidos mediante `.dockerignore`;
- no incluyen la base de datos local;
- no incluyen archivos `.env`;
- no incluyen el repositorio Git;
- no contienen credenciales ni secretos.

El contenedor del backend almacena SQLite en:

```text
/data/repair_orders.sqlite3
```

mediante un volumen persistente.

## Privacidad y tratamiento de datos

El prototipo utiliza exclusivamente datos ficticios.

No existe ningún campo específico para almacenar:

- nombres;
- teléfonos;
- correos electrónicos;
- direcciones;
- información de pago;
- credenciales;
- otros datos personales de contacto.

Las órdenes se relacionan únicamente con un `customer_code` ficticio.

Además, los modelos de entrada están configurados para rechazar campos
inesperados.

Por ejemplo, una petición que intentase introducir:

```json
{
  "customer_code": "CLI-001",
  "bicycle_description": "Bicicleta urbana",
  "reported_issue": "La cadena salta",
  "phone": "000000000"
}
```

sería rechazada en lugar de almacenar silenciosamente el campo `phone`.

Los campos de texto libre podrían contener técnicamente información personal si
un usuario decidiese introducirla. Por este motivo la interfaz y la
documentación indican que deben utilizarse únicamente datos ficticios.

No se ha añadido detección automática de información personal porque no forma
parte del alcance solicitado.

### Relación con clientes en un producto con datos reales

Si fuese necesario almacenar datos de contacto reales, no los incorporaría
directamente dentro de cada reparación.

Separaría los datos identificativos del cliente de los datos operativos de la
reparación.

Conceptualmente:

```text
Customer
    id
    name
    phone
    email

RepairOrder
    id
    customer_id
    bicycle_description
    reported_issue
    status
```

La reparación almacenaría únicamente una referencia interna al cliente.

El acceso a sus datos personales seguiría el principio de mínimo privilegio.

Por ejemplo, una persona que únicamente necesite consultar qué bicicleta debe
reparar y qué problema presenta no tendría por qué disponer automáticamente
del teléfono o correo electrónico del cliente.

Antes de trabajar con datos personales reales sería necesario incorporar
controles adicionales como autenticación, autorización, gestión de accesos,
protección de secretos, políticas de conservación y trazabilidad apropiada.

## Comprobaciones realizadas

La implementación se ha comprobado mediante:

- revisión manual de los cambios generados;
- comparación con `SPEC.md` y `AGENTS.md`;
- revisión de los modelos de entrada;
- revisión de la validación del backend;
- revisión de las consultas SQLite;
- comprobación del uso de consultas parametrizadas;
- comprobación del rechazo de campos inesperados;
- comprobación de estados inválidos;
- pruebas de persistencia;
- prueba con texto similar a una inyección SQL;
- revisión de la configuración CORS;
- pruebas manuales mediante Swagger;
- pruebas manuales del flujo completo en navegador;
- pruebas de comportamiento cuando el backend no está disponible;
- comprobación de TypeScript;
- build del frontend;
- pruebas de configuración de la base de datos;
- ejecución mediante Docker Compose;
- recreación de contenedores comprobando la persistencia;
- comprobación de que los procesos de los contenedores no se ejecutan como
  root;
- revisión final mediante una sesión de IA separada de la utilizada para
  implementar.

Actualmente la suite contiene **87 pruebas automatizadas** relacionadas con el
backend, validación, persistencia, CORS y configuración de la base de datos.

Para ejecutarlas:

```sh
pytest -v
```

Los tests utilizan bases de datos SQLite temporales y no modifican la base de
datos local del desarrollador.

Para verificar el frontend:

```sh
cd frontend
npm run typecheck
npm run build
```

Los directorios `frontend/node_modules/` y `frontend/dist/` se encuentran
excluidos de Git.

## Uso de inteligencia artificial

Se ha utilizado OpenAI Codex como herramienta de apoyo durante el desarrollo.

La IA se ha empleado para ayudar en la implementación, generación de pruebas y
revisión del código, pero las decisiones de producto, alcance, privacidad y
aceptación final de los cambios se han mantenido bajo revisión humana.

Los cambios generados no se han considerado correctos por defecto y se han
revisado y ejecutado independientemente antes de aceptarlos.

El proceso completo y las precauciones adoptadas se describen en:

[`AI_USAGE.md`](AI_USAGE.md)

La posible evolución del prototipo hacia un producto real se describe
separadamente en:

[`EVOLUTION.md`](EVOLUTION.md)

## Tiempo empleado

Tiempo aproximado empleado: **2 horas 30 minutos**.

El desarrollo se ha mantenido dentro del límite máximo de tres horas indicado
para el ejercicio.

Dentro de ese tiempo he priorizado:

1. completar correctamente el flujo solicitado;
2. mantener una arquitectura sencilla;
3. validar los datos en el backend;
4. cuidar privacidad y seguridad;
5. disponer de pruebas automatizadas;
6. comprobar manualmente la aplicación;
7. facilitar una ejecución reproducible;
8. documentar las decisiones tomadas.