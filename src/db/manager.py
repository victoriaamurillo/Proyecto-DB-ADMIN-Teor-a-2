from src.utils.connection import DatabaseConnection
from src.utils.json import export_connection_to_json, load_connections_from_json
import json
import os


class ConnectionManager:
    def __init__(self):
        self.connections = {}
        self.active_connection = None
        self._load_saved_connections()
    
    def _load_saved_connections(self):
        try:
            saved_connections = load_connections_from_json()
            
            for conn_data in saved_connections:
                try:
                    conn_name = conn_data.get("name", f"{conn_data['user']}@{conn_data['host']}")
                    
                    db_params = {
                        "dbname": conn_data.get("dbname"),
                        "user": conn_data.get("user"),
                        "password": conn_data.get("password"),
                        "host": conn_data.get("host"),
                        "port": conn_data.get("port", 5432),
                        "sslmode": conn_data.get("sslmode", "require")
                    }
                    db = DatabaseConnection(**db_params)
                    db.name = conn_name
                    self.connections[conn_name] = db
                    if self.active_connection is None:
                        self.active_connection = conn_name
                    
                except Exception as e:
                    print(f"⚠️ No se pudo conectar a {conn_name}: {str(e)}")
                    continue
        
        except Exception as e:
            print(f"Error al cargar conexiones guardadas: {e}")
    
    def add_connection(self, name, db_params):
        try:
            db = DatabaseConnection(**db_params)
            self.connections[name] = db
            self.active_connection = name
            
            db.name = name
            success, msg = export_connection_to_json(db)
            
            return True, f"Conectado a {name}"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
    
    def get_active_connection(self):
        if not self.active_connection:
            return None
        return self.connections.get(self.active_connection)
    
    def set_active_connection(self, name):
        if name in self.connections:
            self.active_connection = name
            return True
        return False
    
    def list_connections(self):
        return list(self.connections.keys())
    
    def remove_connection(self, name):
        if name in self.connections:
            self.connections[name].close()
            del self.connections[name]
            if self.active_connection == name:
                self.active_connection = None
            return True
        return False
    
    def close_all(self):
        for db in self.connections.values():
            db.close()
        self.connections.clear()
        self.active_connection = None

conn_manager = ConnectionManager()
