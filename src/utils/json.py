import json
import os

def export_connection_to_json(connection):
    try:
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        FILE_PATH = os.path.join(PROJECT_ROOT, "connections.json")

        connection_data = {
            "dbname": connection.dbname,
            "user": connection.user,
            "password": connection.password,
            "host": connection.host,
            "port": connection.port,
            "sslmode": connection.sslmode,
            "name": getattr(connection, 'name', f"{connection.user}@{connection.host}")
        }
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                try:
                    connections = json.load(f)
                    if not isinstance(connections, list):
                        connections = []
                except json.JSONDecodeError:
                    connections = []
        else:
            connections = []
        conn_exists = False
        for idx, conn in enumerate(connections):
            if conn.get("name") == connection_data["name"]:
                connections[idx] = connection_data
                conn_exists = True
                break
        
        if not conn_exists:
            connections.append(connection_data)

        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(connections, f, indent=4, ensure_ascii=False)

        action = "actualizada" if conn_exists else "guardada"
        return True, f"Conexión {action} en {FILE_PATH}"

    except Exception as e:
        return False, f"Error al guardar: {str(e)}"


def load_connections_from_json():
    try:
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        FILE_PATH = os.path.join(PROJECT_ROOT, "connections.json")
        
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                connections = json.load(f)
                if isinstance(connections, list):
                    return connections
        return []
    except Exception as e:
        print(f"Error al cargar conexiones: {e}")
        return []

