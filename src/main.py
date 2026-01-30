import customtkinter as ctk
from tkinter import ttk
from connection import createConnection, executeQuery


# =========================
# CONFIG UI
# =========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("DBAdmin CRDB")
app.geometry("900x500")


# =========================
# DB FUNCTIONS
# =========================
def get_tables(config):
    try:
        conn, status = createConnection(**config)
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        conn.close()
        return [t[0] for t in tables]
    except:
        return []


# =========================
# TOP BAR
# =========================
top_bar = ctk.CTkFrame(app, height=50)
top_bar.pack(fill="x", padx=10, pady=(10, 0))

connections = []  # guardamos configs

def open_connection_window():
    win = ctk.CTkToplevel(app)
    win.title("Nueva conexión")
    win.geometry("350x320")
    win.grab_set()

    # FRAME SCROLLEABLE
    scroll = ctk.CTkScrollableFrame(win)
    scroll.pack(fill="both", expand=True, padx=10, pady=10)

    fields = {}
    for label in ["dbname", "user", "password", "host", "port", "sslmode"]:
        ctk.CTkLabel(scroll, text=label).pack(anchor="w", padx=10)
        entry = ctk.CTkEntry(scroll)
        entry.pack(fill="x", padx=10, pady=5)
        fields[label] = entry

    # valores por defecto
    fields["dbname"].insert(0, "defaultdb")
    fields["user"].insert(0, "root")
    fields["host"].insert(0, "localhost")
    fields["port"].insert(0, "26257")
    fields["sslmode"].insert(0, "disable")

    def connect():
        config = {
            "dbname": fields["dbname"].get(),
            "user": fields["user"].get(),
            "password": fields["password"].get(),
            "host": fields["host"].get(),
            "port": int(fields["port"].get()),
            "sslmode": fields["sslmode"].get()
        }

        connections.append(config)
        add_connection_to_tree(config)
        win.destroy()

    ctk.CTkButton(
        scroll,
        text="Conectar",
        command=connect
    ).pack(pady=15)

ctk.CTkButton(
    top_bar,
    text="➕ Nueva conexión",
    command=open_connection_window
).pack(side="left", padx=10)


# =========================
# SQL EDITOR
# =========================
def open_sql_editor():
    if not connections:
        info_label.configure(text="❌ No hay conexión activa")
        return

    config = connections[-1]  # usa la última conexión

    win = ctk.CTkToplevel(app)
    win.title("SQL Editor")
    win.geometry("700x500")
    win.grab_set()

    editor = ctk.CTkTextbox(win)
    editor.pack(fill="both", expand=True, padx=10, pady=10)

    result_box = ctk.CTkTextbox(win, height=150)
    result_box.pack(fill="x", padx=10, pady=(0, 10))

    def run_query():
        query = editor.get("1.0", "end").strip()
        if not query:
            return

        conn, status = createConnection(**config)
        ok, result = executeQuery(conn, query)
        conn.close()

        result_box.delete("1.0", "end")
        result_box.insert("end", str(result))

    ctk.CTkButton(win, text="▶ Ejecutar", command=run_query).pack(pady=5)


ctk.CTkButton(
    top_bar,
    text="🧠 SQL Editor",
    command=open_sql_editor
).pack(side="left", padx=10)


# =========================
# MAIN AREA
# =========================
main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# TREE
tree = ttk.Treeview(main_frame)
tree.pack(side="left", fill="y", padx=(0, 10))

# RIGHT PANEL
right_panel = ctk.CTkFrame(main_frame)
right_panel.pack(side="right", fill="both", expand=True)

info_label = ctk.CTkLabel(
    right_panel,
    text="Selecciona un nodo",
    font=("Arial", 16)
)
info_label.pack(pady=50)


# =========================
# TREE LOGIC
# =========================
def add_connection_to_tree(config):
    name = f"{config['user']}@{config['host']}:{config['port']}"
    root = tree.insert("", "end", text=f"📦 {name}", open=True)

    tables_node = tree.insert(root, "end", text="📁 Tables")
    tree.insert(root, "end", text="📁 Views")
    tree.insert(root, "end", text="📁 Indexes")
    tree.insert(root, "end", text="📁 Functions")

    for t in get_tables(config):
        tree.insert(tables_node, "end", text=t)


def on_select(event):
    item = tree.focus()
    text = tree.item(item, "text")
    info_label.configure(text=f"Seleccionado: {text}")

tree.bind("<<TreeviewSelect>>", on_select)


app.mainloop()
