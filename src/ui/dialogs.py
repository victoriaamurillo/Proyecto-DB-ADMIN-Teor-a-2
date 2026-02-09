"""
Diálogos y ventanas modales de la aplicación.
"""
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from src.db.manager import conn_manager


DATA_TYPES = [
    "integer",
    "bigint",
    "smallint",
    "real",
    "double precision",
    "numeric",
    "decimal",
    "character varying",
    "text",
    "boolean",
    "date",
    "time",
    "timestamp",
    "json",
    "jsonb",
    "uuid",
    "bytea"
]


class ConnectionDialog:
    
    def __init__(self, parent, on_success_callback):
        self.parent = parent
        self.on_success = on_success_callback
        self.window = None
        self.fields = {}
        
        self._create_dialog()
    
    def _create_dialog(self):
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Nueva conexión")
        self.window.geometry("380x420")
        self.window.grab_set()
        
        scroll = ctk.CTkScrollableFrame(self.window)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        defaults = {
            "dbname": "defaultdb",
            "user": "root",
            "password": "",
            "host": "localhost",
            "port": "26257",
            "sslmode": "disable"
        }
        
        for label in ["dbname", "user", "password", "host", "port", "sslmode"]:
            ctk.CTkLabel(scroll, text=label, font=("Arial", 10)).pack(anchor="w", padx=10)
            entry = ctk.CTkEntry(scroll)
            entry.pack(fill="x", padx=10, pady=5)
            entry.insert(0, defaults[label])
            self.fields[label] = entry
        
        ctk.CTkLabel(scroll, text="Nombre conexión", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(15, 0))
        self.conn_name = ctk.CTkEntry(scroll)
        self.conn_name.pack(fill="x", padx=10, pady=5)
        self.conn_name.insert(0, f"{defaults['user']}@{defaults['host']}")
        
        button_frame = ctk.CTkFrame(scroll)
        button_frame.pack(fill="x", padx=10, pady=15)
        
        ctk.CTkButton(
            button_frame,
            text="✅ Conectar",
            command=self._connect,
            font=("Arial", 11)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Cancelar",
            command=self.window.destroy,
            font=("Arial", 11)
        ).pack(side="left", padx=5)
    
    def _connect(self):
        try:
            db_params = {
                "dbname": self.fields["dbname"].get(),
                "user": self.fields["user"].get(),
                "password": self.fields["password"].get(),
                "host": self.fields["host"].get(),
                "port": int(self.fields["port"].get()),
                "sslmode": self.fields["sslmode"].get()
            }
            
            conn_name = self.conn_name.get() or f"{db_params['user']}@{db_params['host']}"

            success, msg = conn_manager.add_connection(conn_name, db_params)
            
            if success:
                messagebox.showinfo("Éxito", msg)
                self.window.destroy()
                if self.on_success:
                    self.on_success(conn_name)
            else:
                messagebox.showerror("Error", msg)
        
        except Exception as e:
            messagebox.showerror("Error", str(e))


class SQLEditorDialog:
    
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self._create_dialog()
    
    def _create_dialog(self):
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("SQL Editor")
        self.window.geometry("1000x700")
        self.window.grab_set()
        ctk.CTkLabel(
            self.window,
            text="Escribir consulta SQL:",
            font=("Arial", 11, "bold")
        ).pack(padx=10, pady=(10, 0), anchor="w")
        
        self.editor = ctk.CTkTextbox(self.window, height=150)
        self.editor.pack(fill="both", expand=False, padx=10, pady=5)
        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="▶ Ejecutar (Ctrl+Enter)",
            command=self._execute,
            font=("Arial", 11)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="🧹 Limpiar",
            command=lambda: self.editor.delete("1.0", "end"),
            font=("Arial", 11)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="📂 Importar .sql",
            command=self._import_sql_file,
            font=("Arial", 11)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="💾 Guardar .sql",
            command=self._save_sql_file,
            font=("Arial", 11)
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            self.window,
            text="Resultados:",
            font=("Arial", 11, "bold")
        ).pack(padx=10, pady=(10, 0), anchor="w")

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        table_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(table_frame, text="📊 Tabla")
        
        self.result_table = ttk.Treeview(table_frame, height=15)
        self.result_table.pack(fill="both", expand=True, padx=5, pady=5)
       
        msg_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(msg_frame, text="📝 Mensajes")
        
        self.result_box = ctk.CTkTextbox(msg_frame, height=150)
        self.result_box.pack(fill="both", expand=True, padx=5, pady=5)

        self.editor.bind("<Control-Return>", lambda e: self._execute())
    
    def _execute(self):
        query = self.editor.get("1.0", "end").strip()
        if not query:
            messagebox.showwarning("Advertencia", "Escribe una consulta SQL")
            return
        
        db = conn_manager.get_active_connection()
        if not db:
            messagebox.showerror("Error", "No hay conexión activa")
            return
        
        try:
            is_select = query.upper().strip().startswith("SELECT")
            self._clear_result_table()
            if is_select:
                success, result = db.execute_query_dict(query)
                
                if success and result:
                    columns = list(result[0].keys())
                    
                    self.result_table['columns'] = columns
                    self.result_table.column("#0", width=0, stretch=False)
                    
                    for col in columns:
                        self.result_table.column(col, anchor="w", width=100)
                        self.result_table.heading(col, text=col)
                    for idx, row in enumerate(result[:1000]):
                        values = [str(row.get(col, "")) for col in columns]
                        self.result_table.insert("", "end", text=str(idx + 1), values=values)

                    self.result_box.delete("1.0", "end")
                    self.result_box.insert("end", f"✅ Resultados obtenidos: {len(result)} filas")
                    if len(result) > 1000:
                        self.result_box.insert("end", f"\n⚠️ Mostrando 1000 filas de {len(result)}")

                    self.notebook.select(0)
                else:
                    self.result_box.delete("1.0", "end")
                    self.result_box.insert("end", "Sin resultados")
                    self.notebook.select(1)
            else:
                success, result = db.execute_query(query)
                
                self.result_box.delete("1.0", "end")
                
                if success:
                    self.result_box.insert("end", f"✅ {result}")
                else:
                    self.result_box.insert("end", f"❌ Error: {result}")

                self.notebook.select(1)
        
        except Exception as e:
            self.result_box.delete("1.0", "end")
            self.result_box.insert("end", f"❌ Error: {str(e)}")
            self.notebook.select(1)
    
    def _import_sql_file(self):
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo SQL",
                filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")],
                parent=self.window
            )
            
            if not file_path:
                return
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", content)
            
            messagebox.showinfo("Éxito", f"Archivo cargado exitosamente")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")
    
    def _save_sql_file(self):
        try:
            content = self.editor.get("1.0", "end")
            
            if not content.strip():
                messagebox.showwarning("Advertencia", "El editor está vacío")
                return
            file_path = filedialog.asksaveasfilename(
                title="Guardar archivo SQL",
                defaultextension=".sql",
                filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")],
                parent=self.window
            )
            
            if not file_path:
                return
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            messagebox.showinfo("Éxito", f"Archivo guardado en:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")
    
    def _clear_result_table(self):
        for item in self.result_table.get_children():
            self.result_table.delete(item)
        
        self.result_table['columns'] = ()


class CreateTableDialog:
    
    def __init__(self, parent, on_success_callback=None):
        self.parent = parent
        self.on_success = on_success_callback
        self.window = None
        self.table_name_var = None
        self.columns_list = []  
        self.columns_data = [] 
        
        self._create_dialog()
    
    def _create_dialog(self):
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Crear tabla")
        self.window.geometry("600x700")
        self.window.grab_set()
        
        main_scroll = ctk.CTkScrollableFrame(self.window)
        main_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            main_scroll,
            text="Schema:",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        db = conn_manager.get_active_connection()
        schemas = ["public"] 
        if db:
            success, result = db.get_schemas()
            if success and result:
                schemas = result
        
        self.schema_var = ctk.CTkComboBox(
            main_scroll,
            values=schemas,
            state="readonly",
            font=("Arial", 11)
        )
        self.schema_var.pack(fill="x", pady=(0, 15))
        self.schema_var.set(schemas[0] if schemas else "public")
        
        ctk.CTkLabel(
            main_scroll,
            text="Nombre de la tabla:",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.table_name_var = ctk.CTkEntry(main_scroll)
        self.table_name_var.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            main_scroll,
            text="Columnas:",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 10))

        columns_scroll = ctk.CTkScrollableFrame(main_scroll, height=300)
        columns_scroll.pack(fill="both", expand=True, pady=(0, 10))
        
        self.columns_container = columns_scroll
        
        self._add_column_widget()
        
        add_col_btn = ctk.CTkButton(
            main_scroll,
            text="➕ Añadir columna",
            command=self._add_column_widget,
            font=("Arial", 10),
            height=30
        )
        add_col_btn.pack(fill="x", pady=10)
        
        button_frame = ctk.CTkFrame(main_scroll)
        button_frame.pack(fill="x", pady=(15, 0))
        
        ctk.CTkButton(
            button_frame,
            text="✅ Crear tabla",
            command=self._create_table,
            font=("Arial", 11)
        ).pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Cancelar",
            command=self.window.destroy,
            font=("Arial", 11)
        ).pack(side="left", padx=5, fill="x", expand=True)
    
    def _add_column_widget(self):
        col_index = len(self.columns_list)
        col_frame = ctk.CTkFrame(self.columns_container)
        col_frame.pack(fill="x", pady=8)
        
        row1 = ctk.CTkFrame(col_frame)
        row1.pack(fill="x", padx=5, pady=3)
        
        ctk.CTkLabel(row1, text="Nombre:", width=60).pack(side="left", padx=(0, 5))
        name_entry = ctk.CTkEntry(row1, width=150)
        name_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(row1, text="Tipo:", width=50).pack(side="left", padx=(15, 5))
        type_combo = ttk.Combobox(
            row1,
            values=DATA_TYPES,
            state="readonly",
            width=20
        )
        type_combo.set("integer")
        type_combo.pack(side="left", padx=5)
        
        remove_btn = ctk.CTkButton(
            row1,
            text="🗑",
            width=40,
            command=lambda: self._remove_column_widget(col_index)
        )
        remove_btn.pack(side="left", padx=(10, 0))
        
        row2 = ctk.CTkFrame(col_frame)
        row2.pack(fill="x", padx=5, pady=3)
        
        nullable_var = ctk.BooleanVar()
        pk_var = ctk.BooleanVar()
        
        ctk.CTkCheckBox(
            row2,
            text="Opcional",
            variable=nullable_var
        ).pack(side="left")
        
        ctk.CTkCheckBox(
            row2,
            text="Clave primaria",
            variable=pk_var,
            command=lambda: self._on_pk_toggle(col_index, pk_var)
        ).pack(side="left", padx=(20, 0))

        ctk.CTkLabel(col_frame, text="", height=1).pack(fill="x")

        column_data = {
            "frame": col_frame,
            "remove_btn": remove_btn,
            "name_entry": name_entry,
            "type_combo": type_combo,
            "nullable_var": nullable_var,
            "pk_var": pk_var
        }
        
        self.columns_list.append(column_data)
        self.columns_data.append(column_data)
    
    def _remove_column_widget(self, col_index):
        if len(self.columns_list) <= 1:
            messagebox.showwarning("Advertencia", "Debe haber al menos una columna")
            return
        
        col_data = self.columns_data[col_index]
        col_data["frame"].destroy()
        self.columns_list.pop(col_index)
        self.columns_data.pop(col_index)
    
    def _on_pk_toggle(self, col_index, pk_var):
        if not pk_var.get():
            return
        for i, col_data in enumerate(self.columns_data):
            if i != col_index:
                col_data["pk_var"].set(False)
    
    def _get_column_definitions(self):
        definitions = []
        pk_column = None
        
        for col_data in self.columns_data:
            name = col_data["name_entry"].get().strip()
            col_type = col_data["type_combo"].get()
            nullable = col_data["nullable_var"].get()
            is_pk = col_data["pk_var"].get()
            
            if not name:
                messagebox.showerror("Error", "Todos los nombres de columnas son requeridos")
                return None
            if not name.isidentifier():
                messagebox.showerror("Error", f"'{name}' no es un nombre válido")
                return None
            definition = f"{name} {col_type}"
            
            if is_pk:
                definition += " PRIMARY KEY"
                pk_column = name
            elif not nullable:
                definition += " NOT NULL"
            
            definitions.append(definition)
        
        if not definitions:
            messagebox.showerror("Error", "Debe tener al menos una columna")
            return None

        if not pk_column and all(d for d in definitions):
            definitions[0] = definitions[0].replace(" NOT NULL", "")
            if not definitions[0].endswith(" PRIMARY KEY"):
                if not self.columns_data[0]["nullable_var"].get():
                    definitions[0] += " PRIMARY KEY"
        
        return definitions
    
    def _create_table(self):
        schema_name = self.schema_var.get().strip()
        table_name = self.table_name_var.get().strip()
        
        if not table_name:
            messagebox.showerror("Error", "El nombre de la tabla es requerido")
            return
        
        if not table_name.isidentifier():
            messagebox.showerror("Error", f"'{table_name}' no es un nombre válido")
            return
        columns = self._get_column_definitions()
        if columns is None:
            return
        full_table_name = f"{schema_name}.{table_name}" if schema_name else table_name
        sql = f"CREATE TABLE {full_table_name} (\n"
        sql += ",\n".join(f"  {col}" for col in columns)
        sql += "\n)"

        db = conn_manager.get_active_connection()
        if not db:
            messagebox.showerror("Error", "No hay conexión activa")
            return
        
        try:
            success, result = db.execute_query(sql)
            
            if success:
                messagebox.showinfo("Éxito", f"Tabla '{table_name}' creada en schema '{schema_name}'")
                self.window.destroy()
                if self.on_success:
                    self.on_success()
            else:
                messagebox.showerror("Error", f"No se pudo crear la tabla:\n{result}")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la tabla:\n{str(e)}")

class CreateViewDialog:

    def __init__(self, parent, on_success_callback=None):
        self.parent = parent
        self.on_success = on_success_callback
        self.window = None
        self.view_name_var = None
        self.sql_text = None

        self._create_dialog()

    def _create_dialog(self):
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Crear vista")
        self.window.geometry("600x500")
        self.window.grab_set()

        main = ctk.CTkFrame(self.window)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(main, text="Schema:", font=("Arial", 11, "bold")).pack(anchor="w")

        db = conn_manager.get_active_connection()
        schemas = ["public"]
        if db:
            success, result = db.get_schemas()
            if success and result:
                schemas = result

        self.schema_var = ctk.CTkComboBox(
            main, values=schemas, state="readonly"
        )
        self.schema_var.pack(fill="x", pady=(0, 15))
        self.schema_var.set(schemas[0])
        ctk.CTkLabel(
            main, text="Nombre de la vista:", font=("Arial", 11, "bold")
        ).pack(anchor="w")

        self.view_name_var = ctk.CTkEntry(main)
        self.view_name_var.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            main, text="Definición SQL (SELECT):", font=("Arial", 11, "bold")
        ).pack(anchor="w")

        self.sql_text = ctk.CTkTextbox(main, height=200)
        self.sql_text.pack(fill="both", expand=True, pady=(0, 15))

        btns = ctk.CTkFrame(main)
        btns.pack(fill="x")

        ctk.CTkButton(
            btns, text="✅ Crear vista", command=self._create_view
        ).pack(side="left", expand=True, padx=5)

        ctk.CTkButton(
            btns, text="❌ Cancelar", command=self.window.destroy
        ).pack(side="left", expand=True, padx=5)

    def _create_view(self):
        schema = self.schema_var.get().strip()
        view_name = self.view_name_var.get().strip()
        sql_body = self.sql_text.get("1.0", "end").strip()

        if not view_name:
            messagebox.showerror("Error", "El nombre de la vista es requerido")
            return

        if not view_name.isidentifier():
            messagebox.showerror("Error", f"'{view_name}' no es un nombre válido")
            return

        if not sql_body.lower().startswith("select"):
            messagebox.showerror(
                "Error", "La definición de la vista debe comenzar con SELECT"
            )
            return

        if ";" in sql_body:
            messagebox.showerror(
                "Error", "No se permiten múltiples sentencias SQL"
            )
            return

        full_name = f"{schema}.{view_name}"
        sql = f"CREATE VIEW {full_name} AS\n{sql_body}"

        db = conn_manager.get_active_connection()
        if not db:
            messagebox.showerror("Error", "No hay conexión activa")
            return

        success, result = db.execute_query(sql)

        if success:
            messagebox.showinfo(
                "Éxito", f"Vista '{view_name}' creada en schema '{schema}'"
            )
            self.window.destroy()
            if self.on_success:
                self.on_success()
        else:
            messagebox.showerror(
                "Error", f"No se pudo crear la vista:\n{result}"
            )
