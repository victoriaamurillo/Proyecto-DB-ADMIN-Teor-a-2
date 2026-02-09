import customtkinter as ctk
from tkinter import ttk, messagebox
from src.db.manager import conn_manager
from src.ui.dialogs import ConnectionDialog, SQLEditorDialog, CreateTableDialog, CreateViewDialog
from src.ui.tree_view import TreeViewManager


class MainWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("DBAdmin - DBeaver Style")
        self.root.geometry("1080x600")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.selected_table = None
        self.tree_manager = None
        
        self._create_ui()
    
    def _create_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._create_top_bar()

        self._create_main_content()

        self._load_saved_connections_to_tree()
    
    def _create_top_bar(self):
        top_bar = ctk.CTkFrame(self.root, height=50)
        top_bar.pack(fill="x", padx=10, pady=(10, 0))
        ctk.CTkButton(
            top_bar,
            text="➕ Nueva conexión",
            command=self._open_connection_dialog,
            font=("Arial", 12)
        ).pack(side="left", padx=5)
        self.conn_dropdown = ctk.CTkComboBox(
            top_bar,
            values=["Sin conexiones"],
            state="readonly",
            width=250,
            font=("Arial", 11),
            command=self._on_connection_selected
        )
        self.conn_dropdown.pack(side="left", padx=5)
        self.conn_dropdown.set("Sin conexiones")
        
        ctk.CTkButton(
            top_bar,
            text="🧠 SQL Editor",
            command=self._open_sql_editor,
            font=("Arial", 12)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            top_bar,
            text="🔄 Refrescar",
            command=self._refresh_tree,
            font=("Arial", 12)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            top_bar,
            text="📋 Crear tabla",
            command=self._open_create_table_dialog,
            font=("Arial", 12)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            top_bar,
            text="📋 Crear Vista",
            command=self._open_create_view_dialog,
            font=("Arial", 12)
        ).pack(side="left", padx=5)
    
    def _create_main_content(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
        left_panel = ctk.CTkFrame(main_frame, width=350)
        left_panel.pack(side="left", fill="both", padx=(0, 10))
        
        ctk.CTkLabel(
            left_panel,
            text="🗂️ Navegador",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=5, pady=(0, 5))
        
        tree_frame = ctk.CTkFrame(left_panel)
        tree_frame.pack(fill="both", expand=True)
        
        self.tree = ttk.Treeview(tree_frame, height=30)
        self.tree.pack(fill="both", expand=True)

        self.tree_manager = TreeViewManager(
            self.tree,
            self._on_tree_select,
            self._on_table_selected
        )
        
        right_panel = ctk.CTkFrame(main_frame)
        right_panel.pack(side="right", fill="both", expand=True)
        
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill="both", expand=True)
        
        self._create_info_tab()
       
        self._create_data_tab()
    
    def _create_info_tab(self):
        info_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(info_frame, text="📋 Información")
        
        self.info_label = ctk.CTkLabel(
            info_frame,
            text="Selecciona una tabla para ver detalles",
            font=("Arial", 13),
            justify="left"
        )
        self.info_label.pack(pady=20, padx=20, anchor="nw", fill="both", expand=True)
    
    def _create_data_tab(self):
        data_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(data_frame, text="📊 Datos")
        
        self.data_tree = ttk.Treeview(data_frame)
        self.data_tree.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _open_connection_dialog(self):
        ConnectionDialog(self.root, self._on_connection_added)
    
    def _load_saved_connections_to_tree(self):
        connections = conn_manager.list_connections()
        
        if connections:
            self._update_connection_dropdown()
            for conn_name in connections:
                db = conn_manager.connections[conn_name]
                self.tree_manager.add_connection(conn_name, db)
        else:
            self._update_connection_dropdown()
    
    def _open_sql_editor(self):
        if not conn_manager.get_active_connection():
            messagebox.showwarning(
                "Advertencia",
                "No hay conexión activa"
            )
            return
        
        SQLEditorDialog(self.root)
    
    def _open_create_table_dialog(self):
        if not conn_manager.get_active_connection():
            messagebox.showwarning(
                "Advertencia",
                "No hay conexión activa"
            )
            return
        
        CreateTableDialog(self.root, self._refresh_tree)

    def _open_create_view_dialog(self):
       if not conn_manager.get_active_connection():
           messagebox.showwarning(
               "Advertencia",
               "No hay conexión activa"
            )
           return
       
       CreateViewDialog(self.root, self._refresh_tree)
    
    def _on_connection_added(self, conn_name):
        self._update_connection_dropdown()

        db = conn_manager.connections[conn_name]
        self.tree_manager.add_connection(conn_name, db)
    
    def _update_connection_dropdown(self):
        connections = conn_manager.list_connections()
        if connections:
            self.conn_dropdown.configure(values=connections)
            self.conn_dropdown.set(conn_manager.active_connection or connections[0])
        else:
            self.conn_dropdown.configure(values=["Sin conexiones"])
            self.conn_dropdown.set("Sin conexiones")
    
    def _on_connection_selected(self, choice):
        if choice != "Sin conexiones":
            conn_manager.set_active_connection(choice)
    
    def _refresh_tree(self):
        self.tree_manager.refresh_tree()
    
    def _on_tree_select(self, node_type, name, db):
        if node_type == "table":
            self._show_table_info(name, db)
        elif node_type == "view":
            success,ddl = db.get_view_ddl(name)
            self._show_ddl(name, ddl)
        elif node_type == "function":
            success,ddl = db.get_function_ddl(name)
            self._show_ddl(name, ddl)
            self._clear_data_tab()
        elif node_type == "index":
            success,ddl = db.get_index_ddl(name)
            self._show_ddl(name, ddl)
            self._clear_data_tab()
        else:
            self.info_label.configure(text=f"ℹ️ {name}")
            self._clear_data_tab()

    
    def _on_table_selected(self, db, table_name):
        self._show_table_data(db, table_name)
    
    def _show_ddl(self,name,ddl):
        info_text= f"ℹ️ {name}"
        info_text += "DDL (Data Definition Language):\n"
        info_text += "-" * 60 + "\n"
        info_text += ddl
        self.info_label.configure(text=info_text)
        
    def _show_table_info(self, table_name, db):
        if not db:
            return
        
        self.selected_table = table_name

        columns = self._get_columns(db, table_name)
        count = self._get_table_count(db, table_name)
     
        ddl = f"CREATE TABLE {table_name} (\n"
        
        for idx, col in enumerate(columns):
            col_name = col['column_name']
            col_type = col['data_type']
            is_nullable = col['is_nullable']
            
            ddl += f"    {col_name} {col_type}"
            
            if is_nullable == 'NO':
                ddl += " NOT NULL"
            
            if idx < len(columns) - 1:
                ddl += ",\n"
            else:
                ddl += "\n"
        
        ddl += ");"
        
        info_text = f"📄 Tabla: {table_name}\n"
        info_text += f"📊 Registros: {count}\n"
        info_text += f"📋 Columnas: {len(columns)}\n"
        info_text += "=" * 60 + "\n\n"
        info_text += "DDL (Data Definition Language):\n"
        info_text += "-" * 60 + "\n"
        info_text += ddl
        
        self.info_label.configure(text=info_text)
    
    def _show_table_data(self, db, table_name, limit=100):

        self._clear_data_tab()
        
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            success, data = db.execute_query_dict(query)
            
            if not success or not data:
                self.data_tree.insert("", "end", text="Sin datos")
                return
            
            columns = list(data[0].keys())
            self.data_tree['columns'] = columns
            self.data_tree.column("#0", width=0, stretch=False)
            
            for col in columns:
                self.data_tree.column(col, anchor="w", width=120)
                self.data_tree.heading(col, text=col)
            
            for idx, row in enumerate(data):
                values = [str(row.get(col, "")) for col in columns]
                self.data_tree.insert("", "end", text=str(idx + 1), values=values)
        
        except Exception as e:
            self.data_tree.insert("", "end", text=f"Error: {str(e)}")
    
    def _clear_data_tab(self):
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        self.data_tree['columns'] = ()

        for col in list(self.data_tree['columns']):
            self.data_tree.heading(col, text="")
    
    @staticmethod
    def _get_columns(db, table_name):
        success, result = db.get_table_columns(table_name)
        if success:
            return result
        return []
    
    @staticmethod
    def _get_table_count(db, table_name):
        success, count = db.get_table_count(table_name)
        if success:
            return count
        return 0
    
    def _on_close(self):
        conn_manager.close_all()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()
