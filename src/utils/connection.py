import psycopg2
from psycopg2.extras import RealDictCursor


class DatabaseConnection:
    
    def __init__(self, dbname, user, password, host, port, sslmode="require"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.sslmode = sslmode
        self.conn = None
        self.is_connected = False
        
        self._connect()
    
    def _connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                sslmode=self.sslmode
            )
            self.is_connected = True
        except Exception as e:
            self.is_connected = False
            raise Exception(f"Error al conectar: {str(e)}")
    
    def execute_query(self, query, fetch=True):
        if not self.is_connected:
            return False, "No hay conexión activa"
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            
            if cursor.description: 
                result = cursor.fetchall()
            else:
                self.conn.commit()
                result = f"Filas afectadas: {cursor.rowcount}"
            
            cursor.close()
            return True, result
        
        except Exception as e:
            try:
                self.conn.rollback()
            except:
                pass
            return False, f"Error ejecutando query: {str(e)}"
    
    def execute_query_dict(self, query):
        if not self.is_connected:
            return False, "No hay conexión activa"
        
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return True, result
        
        except Exception as e:
            try:
                self.conn.rollback()
            except:
                pass
            return False, f"Error: {str(e)}"
    
    def get_tables(self):
        query = """
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """
        return self.execute_query(query)
    
    def get_views(self, schema_name="public"):
        query = f"""
            SELECT c.relname AS viewname
            FROM pg_catalog.pg_class c
            JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind = 'v'
              AND n.nspname = '{schema_name}'
            ORDER BY c.relname
        """
        return self.execute_query(query)
    
    def get_functions(self, schema="public"):
        try:
            query = f"""
                SELECT routine_name
                FROM information_schema.routines
                WHERE routine_schema = '{schema}'
                ORDER BY routine_name
            """
            return self.execute_query(query)
        except Exception as e:
            print(f"Error obteniendo funciones: {e}")
            return False, []

    def get_indexes(self, schema="public"):
        try:

            query = f"""
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = '{schema}'
                ORDER BY indexname
            """
            return self.execute_query(query)
        except Exception as e:
            print(f"Error obteniendo índices: {e}")
            return False, []

    def get_triggers(self, schema="public"):
        try:
            query = f"""
                SELECT trigger_name
                FROM information_schema.triggers
                WHERE trigger_schema = '{schema}'
                ORDER BY trigger_name
            """
            return self.execute_query(query)
        except Exception as e:
            print(f"Error obteniendo triggers: {e}")
            return False, []

    def get_materialized_views(self, schema="public"):
        try:
    
            query = f"""
                SELECT matviewname
                FROM pg_matviews
                WHERE schemaname = '{schema}'
                ORDER BY matviewname
            """
            return self.execute_query(query)
        except Exception as e:
            print(f"Error obteniendo mat views: {e}")
            return False, []

    def get_schemas(self):
        """
        Obtiene todos los esquemas de la base de datos.
        
        Returns:
            tuple: (éxito: bool, esquemas: list de strings)
        """
        query = """
            SELECT n.nspname AS schema_name
            FROM pg_catalog.pg_namespace n
            WHERE n.nspname NOT LIKE 'pg_%'
              AND n.nspname <> 'information_schema'
              AND n.nspname <> 'crdb_internal'
            ORDER BY n.nspname
        """
        success, result = self.execute_query_dict(query)
        if success:
            return success, [row['schema_name'] for row in result]
        return success, result
    
    def get_schema_info(self, schema_name="public"):
        query = f"""
            SELECT 
                t.tablename,
                a.attname as column_name,
                pg_catalog.format_type(a.atttypid, a.atttypmod) as data_type,
                a.attnotnull as not_null,
                a.attnum as column_position
            FROM pg_tables t
            JOIN pg_class c ON c.relname = t.tablename
            JOIN pg_attribute a ON a.attrelid = c.oid
            WHERE t.schemaname = '{schema_name}'
            AND a.attnum > 0
            ORDER BY t.tablename, a.attnum
        """
        return self.execute_query_dict(query)
    
    def get_table_columns(self, table_name):
        query = f"""
            SELECT
            a.attname AS column_name,
            pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
            NOT a.attnotnull AS is_nullable
            FROM pg_catalog.pg_attribute a
            JOIN pg_catalog.pg_class c ON c.oid = a.attrelid
            JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = '{table_name}'
              AND a.attnum > 0
              AND NOT a.attisdropped
            ORDER BY a.attnum
        """
        return self.execute_query_dict(query)
    
    def get_table_count(self, table_name):
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        success, result = self.execute_query_dict(query)
        if success:
            return success, result[0]['count']
        return success, result
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.is_connected = False
    
    def __del__(self):
        self.close()
    
    def __enter__(self):
        return self
    
    def get_function_ddl(self, function_name, schema="public"):
        query = f"""
            SELECT pg_get_functiondef(p.oid) as ddl
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            WHERE p.proname = '{function_name}'
              AND n.nspname = '{schema}'
        """
        success, result = self.execute_query_dict(query)
        if success and result:
            ddl = result[0]['ddl'].replace(';', ';\n')
            return True, ddl
        return False, f"No se encontró la función {function_name}"
    
    
    def get_view_ddl(self, view_name, schema="public"):
        query = f"""
            SELECT 'CREATE OR REPLACE VIEW ' || table_schema || '.' || table_name || ' AS ' || view_definition as ddl
            FROM information_schema.views
            WHERE table_schema = '{schema}'
              AND table_name = '{view_name}'
        """
        success, result = self.execute_query_dict(query)
        if success and result:
            ddl = result[0]['ddl'].replace(';', ';\n')
            return True, ddl
        return False, f"No se encontró la vista {view_name}"
    
    
    def get_index_ddl(self, index_name, schema="public"):
        query = f"""
            SELECT pg_get_indexdef(indexrelid) as ddl
            FROM pg_index i
            JOIN pg_class c ON c.oid = i.indexrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = '{index_name}'
              AND n.nspname = '{schema}'
        """
        success, result = self.execute_query_dict(query)
        if success and result:
            ddl = result[0]['ddl'].replace(';', ';\n')
            return True, ddl
        return False, f"No se encontró el índice {index_name}"
    
    
    def get_trigger_ddl(self, trigger_name, schema="public"):
        query = f"""
            SELECT 'CREATE TRIGGER ' || trigger_name || ' ' || action_timing || ' ' || event_manipulation ||
                   ' ON ' || event_object_table || ' FOR EACH ROW EXECUTE FUNCTION ' || action_statement as ddl
            FROM information_schema.triggers
            WHERE trigger_schema = '{schema}'
              AND trigger_name = '{trigger_name}'
        """
        success, result = self.execute_query_dict(query)
        if success and result:
            ddl = result[0]['ddl'].replace(';', ';\n')
            return True, ddl
        return False, f"No se encontró el trigger {trigger_name}"
    