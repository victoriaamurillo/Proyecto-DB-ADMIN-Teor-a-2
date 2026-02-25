# Proyecto DB-ADMIN (Teoría 2) — Manual de instalación y uso

Aplicación tipo “DB Manager” desarrollada en **Python + CustomTkinter**, con soporte de conexión a **CockroachDB** (levantado con Docker) usando el driver **psycopg2**.

---

## Requisitos

### Software
- **Python 3.10+** (recomendado 3.11)
- **Docker Desktop** (para levantar CockroachDB con docker-compose)
- (Opcional) **Git**

### Archivos del proyecto
En la raíz deben existir:
- `main.py`
- `requirements.txt`
- `docker-compose.yml`
- `connections.json` (se genera/actualiza al guardar conexiones)

---

## 1) Levantar la base de datos CockroachDB con Docker

### 1.1 Abrir Docker Desktop
Asegúrate de que Docker Desktop esté ejecutándose (estado: **Running**).

### 1.2 Entrar a la carpeta del proyecto
En PowerShell o CMD:

```bash
cd "RUTA\Proyecto-DB-ADMIN-Teor-a-2"
```

### 1.3 Levantar CockroachDB
Ejecuta:

```bash
docker compose up -d
```

### 1.4 Verificar que está corriendo
```bash
docker ps
```

Debes ver el contenedor en estado **Up**.

### 1.5 (Opcional) Abrir el panel web de CockroachDB
Normalmente está disponible en:

- `http://localhost:8080`

> Nota: el puerto puede variar si se cambió en `docker-compose.yml`.

---

## 2) Instalación del proyecto (Python)

### 2.1 Crear un entorno virtual (recomendado)
En Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 2.2 Instalar dependencias
Con el entorno activado:

```bash
pip install -r requirements.txt
```

---

## 3) Ejecutar la aplicación

En la raíz del proyecto:

```bash
python main.py
```

Esto abrirá la ventana principal de la aplicación.

---

## 4) Crear una conexión a CockroachDB desde la aplicación

1. En la app, presiona **“Nueva conexión”**
2. Completa los campos con valores típicos para CockroachDB local (Docker):

- **Connection name:** `CRDB Local` (o cualquier nombre)
- **Host:** `localhost`
- **Port:** `26257`
- **Database:** `defaultdb`
- **User:** `root`
- **Password:** *(vacío si el contenedor está en modo insecure)*
- **sslmode:** `disable`

3. Presiona **Conectar / Guardar**

Si la conexión es exitosa:
- Se guarda en `connections.json`
- Se carga el árbol de objetos (schemas, tablas, vistas, etc.)

---

## 5) Uso básico (pruebas rápidas)

### 5.1 Ejecutar un SELECT
1. Abre el **SQL Editor**
2. Ejecuta:

```sql
SELECT now();
```

### 5.2 Crear una tabla
Puedes crearla desde **Crear tabla** o usando el SQL Editor:

```sql
CREATE TABLE public.prueba (
  id INT PRIMARY KEY,
  nombre STRING
);
```

Luego presiona **Refrescar** y verifica en el árbol.

### 5.3 Crear una vista
Desde **Crear vista** o SQL Editor:

```sql
CREATE VIEW public.v_prueba AS
SELECT id, nombre FROM public.prueba;
```

---

## 6) Apagar la base de datos (cuando termines)

```bash
docker compose down
```

---

## 7) Problemas comunes

### “Connection refused” / No conecta
- Verifica que Docker Desktop esté corriendo.
- Confirma que el contenedor está activo:

```bash
docker ps
```

Si no está activo:

```bash
docker compose up -d
```

### “Port already in use”
- Hay otro proceso usando ese puerto.
- Detén contenedores anteriores o ajusta puertos en `docker-compose.yml`.

### Error con dependencias (psycopg2 / módulos faltantes)
- Asegúrate de tener el entorno virtual activado y reinstala:

```bash
pip install -r requirements.txt
```

---

## Nota técnica
- La app maneja conexiones guardándolas en `connections.json`.
- El SQL Editor permite **importar/exportar scripts** en archivos `.sql`.
- La metadata y navegación de objetos se consulta mediante tablas del sistema (según disponibilidad en el motor).



