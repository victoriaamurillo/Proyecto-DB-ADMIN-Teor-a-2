
from tkinter import ttk
from src.db.manager import conn_manager


class TreeViewManager:
    def __init__(self, tree_widget, on_select_callback, on_data_request_callback):
        self.tree = tree_widget
        self.on_select = on_select_callback
        self.on_data_request = on_data_request_callback
        self.node_map = {}  
        
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
    
    def refresh_tree(self):
        self.clear()
        for conn_name, db in conn_manager.connections.items():
            self.add_connection(conn_name, db)

    def add_connection(self, conn_name, db):
        try:
            conn_id = self.tree.insert(
                "",
                "end",
                text=f"📦 {conn_name}",
                open=True
            )
            self.node_map[conn_id] = {"type": "connection", "name": conn_name}
        
            schemas = self._get_schemas(db)
            
            if not schemas:
                self.tree.insert(conn_id, "end", text="❌ Sin esquemas")
                return
            for schema in schemas:
                self._add_schema(conn_id, schema, db)
        
        except Exception as e:
            print(f"Error al agregar conexión: {e}")
            self.tree.insert(conn_id, "end", text=f"❌ Error: {str(e)}")
    
    def _add_schema(self, parent_id, schema_name, db):
        schema_id = self.tree.insert(
            parent_id,
            "end",
            text=f"📁 {schema_name}",
            open=True
        )
        self.node_map[schema_id] = {"type": "schema", "name": schema_name}
        tables = self._get_tables(db, schema_name)
        tables_id = self.tree.insert(
            schema_id,
            "end",
            text=f"📋 Tables ({len(tables)})",
            open=True
        )
        self.node_map[tables_id] = {"type": "tables_folder"}
        
        for table_name in tables:
            self._add_table(tables_id, table_name, db)

        views = self._get_views(db, schema_name)
        views_id = self.tree.insert(
            schema_id,
            "end",
            text=f"👁️ Views ({len(views)})",
            open=True
        )
        self.node_map[views_id] = {"type": "views_folder"}

        for view_name in views:
            view_id = self.tree.insert(
                views_id,
                "end",
                text=f"👁️ {view_name}",
                open=False
            )
            self.node_map[view_id] = {
                "type": "view",
                "name": view_name,
                "db": db
            }
        indexes_id = self.tree.insert(schema_id, "end", text="🔍 Indexes", open=False)
        self.node_map[indexes_id] = {"type": "indexes_folder"}

        success, indexes = db.get_indexes(schema_name)
        if success:
            for idx in indexes:
                iid = self.tree.insert(indexes_id, "end", text=f"🔍 {idx[0]}")
                self.node_map[iid] = {"type": "index", "name": idx[0], "db": db}

        functions_id = self.tree.insert(schema_id, "end", text="⚙️ Functions", open=False)
        self.node_map[functions_id] = {"type": "functions_folder"}

        success, funcs = db.get_functions(schema_name)
        if success:
            for fn in funcs:
                fid = self.tree.insert(functions_id, "end", text=f"⚙️ {fn[0]}")
                self.node_map[fid] = {"type": "function", "name": fn[0], "db": db}

    
    def _add_table(self, parent_id, table_name, db):
        count = self._get_table_count(db, table_name)
        
        table_id = self.tree.insert(
            parent_id,
            "end",
            text=f"📄 {table_name} ({count} rows)",
            open=False
        )
        self.node_map[table_id] = {"type": "table", "name": table_name, "db": db}
        columns = self._get_columns(db, table_name)
        for col in columns:
            col_type = col['data_type']
            nullable = "⭕" if col['is_nullable'] == 'YES' else "⚫"
            col_id = self.tree.insert(
                table_id,
                "end",
                text=f"{nullable} {col['column_name']}: {col_type}"
            )
            self.node_map[col_id] = {"type": "column", "name": col['column_name']}
    
    def _on_tree_select(self, event):
        item_id = self.tree.focus()
        node_info = self.node_map.get(item_id, {})
        node_type = node_info.get("type")
        
        if node_type == "table":
            table_name = node_info.get("name")
            db = node_info.get("db")
            if self.on_select:
                self.on_select(node_type, table_name, db)
            if self.on_data_request:
                self.on_data_request(db, table_name)
        elif node_type == "view":
            view_name = node_info.get("name")
            db = node_info.get("db")
            if self.on_select:
                self.on_select("view", view_name, db)
            if self.on_data_request:
                self.on_data_request(db, view_name)
        elif node_type in ["connection", "schema", "tables_folder"]:
            if self.on_select:
                self.on_select(node_type, node_info.get("name"), None)
        elif node_type in ["function","index"]:
            info_name = node_info.get("name")
            db = node_info.get("db")
            if self.on_select:
                self.on_select(node_type, info_name, db)
        else:
            if self.on_select:
                text = self.tree.item(item_id, "text")
                self.on_select("generic", text, None)
    
    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.node_map.clear()

    @staticmethod
    def _get_schemas(db):
        try:
            success, result = db.get_schemas()
            if success and result:
                schemas = result
                return schemas if schemas else ["public"]
            query = """
                SELECT n.nspname AS schema_name
                FROM pg_catalog.pg_namespace n
                WHERE n.nspname NOT LIKE 'pg_%'
                  AND n.nspname <> 'information_schema'
                  AND n.nspname <> 'crdb_internal'
                ORDER BY n.nspname;
            """
            success, result = db.execute_query(query)
            
            if success and result:
                schemas = [row[0] for row in result]
                return schemas if schemas else ["public"]
            
            return ["public"]
            
        except Exception as e:
            print(f"Error obteniendo esquemas: {e}")
            return ["public"]
    
    @staticmethod
    def _get_tables(db, schema="public"):
        try:
            query = f"""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = '{schema}'
                ORDER BY tablename
            """
            success, result = db.execute_query(query)
            if success:
                return [row[0] for row in result] if result else []
        except:
            pass
        return []
    
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
    
    @staticmethod
    def _get_views(db, schema="public"):
        try:
            success, result = db.get_views(schema)
            if success:
                return [row[0] for row in result] if result else []
        except:
            pass
        return []
    
    @staticmethod
    def _get_indexes(db, schema="public"):
        try:
            success, result = db.get_indexes(schema)
            if success:
                return [row[0] for row in result] if result else []
        except:
            pass
        return []
    
    @staticmethod
    def _get_triggers(db, schema="public"):
        try:
            success, result = db.get_triggers(schema)
            if success:
                return [row[0] for row in result] if result else []
        except:
            pass
        return []
    
    @staticmethod
    def _get_functions(db, schema="public"):
        try:
            success, result = db.get_functions(schema)
            if success:
                return [row[0] for row in result] if result else []
        except:
            pass
        return []
    
