# DBAdmin - DBeaver Style

Herramienta gráfica para gestionar bases de datos PostgreSQL/CRDB.

## Estructura del Proyecto

```
src/
├── utils/
│   └── connection.py          # Clase DatabaseConnection (conexión a BD)
├── db/
│   └── manager.py             # ConnectionManager (gestor de conexiones)
└── ui/
    ├── main_window.py         # Ventana principal de la app
    ├── dialogs.py             # Diálogos (conexión, SQL editor)
    └── tree_view.py           # Gestor del árbol de navegación

main.py                          # Punto de entrada (muy simple)
requirements.txt                 # Dependencias
```

## Descripción de Archivos

### `main.py`
**Punto de entrada simple de la aplicación**
- Solo importa `MainWindow` y la ejecuta
- Limpio y fácil de entender

### `src/utils/connection.py`
**Clase `DatabaseConnection`** - Maneja conexiones individuales a la BD
- `__init__`: Conecta a la BD
- `execute_query()`: Ejecuta consultas SQL
- `execute_query_dict()`: Retorna resultados como diccionarios
- `get_tables()`: Lista tablas
- `get_schemas()`: Lista esquemas
- `get_schema_info()`: Información detallada del esquema
- `get_table_columns()`: Columnas de una tabla
- `get_table_count()`: Cantidad de registros
- `close()`: Cierra la conexión

### `src/db/manager.py`
**Clase `ConnectionManager`** - Gestor centralizado de múltiples conexiones
- `add_connection()`: Añade una nueva conexión
- `get_active_connection()`: Obtiene conexión activa
- `set_active_connection()`: Cambia conexión activa
- `list_connections()`: Lista todas las conexiones
- `remove_connection()`: Elimina una conexión
- `close_all()`: Cierra todas las conexiones

### `src/ui/dialogs.py`
**Ventanas modales**

#### Clase `ConnectionDialog`
- Diálogo para crear nuevas conexiones
- Campos: dbname, user, password, host, port, sslmode
- Validación de conexión

#### Clase `SQLEditorDialog`
- Editor SQL con 2 áreas: consultas y resultados
- Soporte para Ctrl+Enter para ejecutar
- Muestra resultados formateados

#### Clase `CreateTableDialog`
- Creación de Tablas 
- Lista de datos a seleccionar
- Selección de llaves primarias y demás

### `src/ui/tree_view.py`
**Clase `TreeViewManager`** - Gestor del árbol tipo DBeaver
- `add_connection()`: Añade conexión al árbol
- `_add_schema()`: Añade esquema con tablas, vistas, índices
- `_add_table()`: Añade tabla con sus columnas
- Maneja eventos de selección en el árbol
- Mapeo de nodos a información

### `src/ui/main_window.py`
**Clase `MainWindow`** - Ventana principal que une todo
- Crea la interfaz gráfica completa
- Gestiona las pestañas: Información y Datos
- Muestra información de tablas seleccionadas
- Muestra datos de tablas en tablas interactivas
- Integra todos los componentes

## Cómo Usar

### Instalación
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Ejecución
```bash
python main.py
```

## Flujo de la Aplicación

1. **Iniciar** → `main.py` → `MainWindow`
2. **Nueva conexión** → `ConnectionDialog` → `ConnectionManager.add_connection()`
3. **Mostrar en árbol** → `TreeViewManager.add_connection()`
4. **Seleccionar tabla** → Datos en pestaña "📊 Datos"
5. **Editor SQL** → `SQLEditorDialog` → Ejecutar consultas

## Modificaciones Futuras

Para añadir nuevas funcionalidades:

- **Nueva funcionalidad DB** → Editar `src/utils/connection.py`
- **Nueva funcionalidad UI** → Editar `src/ui/main_window.py`
- **Nuevo diálogo** → Añadir clase en `src/ui/dialogs.py`
- **Nueva sección en árbol** → Editar `src/ui/tree_view.py`

## Dependencias

- `customtkinter` - UI moderna
- `psycopg2` - Driver PostgreSQL
- `tkinter` - UI (incluida en Python)

