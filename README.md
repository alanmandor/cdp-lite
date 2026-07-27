# CDP Lite

Una API mínima de *Customer Data Platform* (CDP) construida con Python. Su objetivo es centralizar perfiles de clientes, registrar los eventos que generan y crear segmentos sencillos para consultar audiencias.

El proyecto está pensado como un MVP educativo y ejecutable localmente: no requiere servicios externos y usa SQLite como almacenamiento inicial.

## Alcance del MVP

La primera versión incluirá:

- Perfiles de clientes con datos básicos e identificadores únicos.
- Eventos asociados a cada perfil, como `page_view`, `signup` o `purchase`.
- Segmentos simples basados en atributos del perfil.
- Una API HTTP documentada automáticamente.
- Pruebas automatizadas de los flujos principales.

No forma parte del MVP la autenticación, el procesamiento en tiempo real, la deduplicación avanzada ni la integración con herramientas de marketing. Esas capacidades se pueden añadir cuando la base sea estable.

## Arquitectura propuesta

```text
Cliente HTTP
    |
    v
FastAPI (rutas y validación)
    |
    v
SQLAlchemy (modelos y consultas)
    |
    v
SQLite (cdp_lite.db)
```

La aplicación se organizará así:

```text
app/
  main.py          # punto de entrada de FastAPI
  database.py      # configuración de SQLite y sesiones
  models.py        # tablas de persistencia
  schemas.py       # contratos de entrada y salida de la API
  routers/         # endpoints agrupados por dominio
tests/             # pruebas automatizadas
requirements.txt   # dependencias bloqueadas
```

## Requisitos previos

- Python 3.11 o superior.
- Git (opcional, para control de versiones).

Comprueba Python con:

```powershell
py --version
```

Si el comando no existe, instala Python desde [python.org](https://www.python.org/downloads/) y activa la opción para añadir Python al `PATH` durante la instalación.

## Instalación

Desde la raíz del repositorio, crea un entorno virtual e instala las dependencias:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> Si PowerShell bloquea la activación de scripts, ejecuta `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` únicamente para la sesión actual y vuelve a activar el entorno.

## Ejecución

Cuando exista el punto de entrada de la aplicación, se iniciará en modo desarrollo con:

```powershell
uvicorn app.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000` y su documentación interactiva en `http://127.0.0.1:8000/docs`.

## Pruebas y calidad

```powershell
pytest
ruff check .
```

Las pruebas validarán los casos de uso del MVP. Ruff mantiene un estilo consistente y detecta errores comunes antes de subir cambios al repositorio.

## Dependencias

Las versiones están bloqueadas en `requirements.txt` para que todas las personas que colaboren instalen el mismo conjunto de librerías:

- **FastAPI**: framework para la API.
- **Uvicorn**: servidor ASGI para ejecutar FastAPI.
- **SQLAlchemy**: capa de acceso a datos.
- **Pydantic**: validación y serialización de datos.
- **Pytest + HTTPX**: pruebas de endpoints.
- **Ruff**: análisis estático y estilo.

## Próximos pasos

1. Crear el esqueleto de FastAPI y el endpoint `GET /health`.
2. Añadir la conexión SQLite y el modelo de perfil.
3. Implementar perfiles, eventos y segmentos junto con sus pruebas.
