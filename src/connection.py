import psycopg2


def createConnection(dbname, user, password, host, port, sslmode):
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            sslmode=sslmode
        )

        return conn, "Conexion Exitosa"
    except Exception as e:
        return None, f"Error: {str(e)}"
    
def executeQuery(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)

        if cursor.description:  # SELECT
            result = cursor.fetchall()
        else:  # INSERT / UPDATE / DELETE
            conn.commit()
            result = f"Filas afectadas: {cursor.rowcount}"

        cursor.close()
        return True, result

    except Exception as e:
        return False, str(e)




    



