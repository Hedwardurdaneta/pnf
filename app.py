import flet as ft
import gspread
import openpyxl
import os
import random
import time
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONO_PATH = "icono.ico" 
FONDO_PATH = "fondo.png"
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json")

# --- 2. PERSISTENCIA EN LA NUBE (Google Sheets) ---
def guardar_en_nube(nombre_alumno, unidad, puntos):
    alcance = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if not os.path.exists(CREDS_PATH):
            return False
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, alcance)
        cliente = gspread.authorize(creds)
        hoja_principal = cliente.open("Ingenieria de software II")
        hoja = hoja_principal.worksheet("Notas_PNF_UNERMB")
        lista_nombres = hoja.col_values(3) 
        if nombre_alumno in lista_nombres:
            fila = lista_nombres.index(nombre_alumno) + 1
            columna = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
            if columna:
                hoja.update_cell(fila, columna, puntos)
                return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# --- 3. BANCO DE DATOS ---
state = {"alumno": None, "unidad": None, "idx": 0, "puntos": 0}

preguntas = {
    "UNIDAD I": [
        ("¿Qué es un algoritmo?", ["Pasos lógicos", "Hardware", "Un error", "Virus"], "Pasos lógicos"),
        ("¿Qué es Hardware?", ["Físico", "Virtual", "Software", "Nube"], "Físico"),
        ("¿Qué es Software?", ["Lógico", "Cables", "Monitor", "Teclado"], "Lógico"),
        ("¿Qué es el IDE?", ["Entorno de desarrollo", "Internet", "Disco", "Puerto"], "Entorno de desarrollo"),
        ("¿Qué es la sintaxis?", ["Reglas de escritura", "Un cable", "Monitor", "Energía"], "Reglas de escritura"),
        ("¿Qué es un compilador?", ["Traductor de código", "Virus", "Hardware", "Navegador"], "Traductor de código")
    ],
    "UNIDAD II": [
        ("¿Qué guarda 'int'?", ["Enteros", "Texto", "Decimales", "Listas"], "Enteros"),
        ("¿Qué guarda 'str'?", ["Texto", "Números", "Bucle", "Tuplas"], "Texto"),
        ("¿Qué guarda 'float'?", ["Decimales", "Cadenas", "Enteros", "Nulo"], "Decimales"),
        ("¿Qué es 'if'?", ["Condicional", "Bucle", "Variable", "Clase"], "Condicional"),
        ("¿Qué es 'for'?", ["Bucle repetitivo", "Suma", "Texto", "Lista"], "Bucle repetitivo"),
        ("¿Qué es una función?", ["Bloque reutilizable", "Error", "Variable", "Dato"], "Bloque reutilizable")
    ],
    "UNIDAD III": [
        ("¿Qué es Flet?", ["Framework UI", "Antivirus", "Hardware", "OS"], "Framework UI"),
        ("¿Qué es un Widget?", ["Componente visual", "Cable", "Virus", "Disco"], "Componente visual"),
        ("¿Qué es el Layout?", ["Organización", "Color", "Nombre", "Icono"], "Organización"),
        ("¿Qué es un evento?", ["Acción detectada", "Error", "Hardware", "Red"], "Acción detectada"),
        ("¿Qué es un Label?", ["Texto estático", "Botón", "Imagen", "Menú"], "Texto estático"),
        ("¿Qué es un Container?", ["Caja de diseño", "Bucle", "Variable", "Clase"], "Caja de diseño")
    ]
}

# --- 4. INTERFAZ GRÁFICA ---
def main(page: ft.Page):
    page.title = "Portal PNF - UNERMB"
    page.padding = 0
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def layout_contenedor(elementos):
        return ft.Container(
            content=ft.Column(
                elementos, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                alignment=ft.MainAxisAlignment.CENTER, 
                spacing=20
            ),
            expand=True,
            image_src=FONDO_PATH,
            image_fit="cover", 
            alignment=ft.alignment.center,
        )

    # Definimos las funciones internas ANTES de llamarlas
    def login_view():
        page.clean()
        usuarios_db = {"Admin": "1234"}
        if os.path.exists(EXCEL_PATH):
            try:
                wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
                sh = wb.active
                usuarios_db = {str(sh.cell(r, 3).value): str(sh.cell(r, 2).value) for r in range(2, 60) if sh.cell(r, 3).value}
            except: pass

        drop_user = ft.Dropdown(label="Seleccione Alumno", width=350, options=[ft.dropdown.Option(n) for n in usuarios_db.keys()])
        txt_pass = ft.TextField(label="Cédula", password=True, can_reveal_password=True, width=350)

        def intentar_login(e):
            if drop_user.value in usuarios_db and usuarios_db[drop_user.value] == txt_pass.value:
                state["alumno"] = drop_user.value
                menu_principal()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Datos incorrectos"))
                page.snack_bar.open = True
                page.update()

        page.add(layout_contenedor([
            ft.Image(src=ICONO_PATH, width=120),
            ft.Text("INGENIERÍA DE SOFTWARE II", size=28, weight="bold", color="white"),
            drop_user, txt_pass, 
            ft.FilledButton("INGRESAR", on_click=intentar_login, width=220, height=50)
        ]))

    def menu_principal():
        page.clean()
        page.add(layout_contenedor([
            ft.Text(f"Estudiante: {state['alumno']}", size=24, color="white", weight="bold"),
            ft.FilledButton("UNIDAD I", on_click=lambda _: ir_a_unidad("UNIDAD I"), width=320, height=50),
            ft.FilledButton("UNIDAD II", on_click=lambda _: ir_a_unidad("UNIDAD II"), width=320, height=50),
            ft.FilledButton("UNIDAD III", on_click=lambda _: ir_a_unidad("UNIDAD III"), width=320, height=50),
            ft.TextButton("CERRAR SESIÓN", on_click=lambda _: login_view(), style=ft.ButtonStyle(color="white"))
        ]))

    def ejecutar_examen():
        page.clean()
        u = state["unidad"]
        if state["idx"] < len(preguntas[u]):
            p, opciones, correcta = preguntas[u][state["idx"]]
            random.shuffle(opciones)
            def validar(res):
                if res == correcta: state["puntos"] += 1
                state["idx"] += 1
                ejecutar_examen()
            page.add(layout_contenedor([
                ft.Text(f"Pregunta {state['idx']+1}", color="#aed6f1", size=18),
                ft.Text(p, size=24, color="white", text_align="center"),
                *[ft.FilledButton(o, on_click=lambda e, o=o: validar(o), width=380, height=45) for o in opciones]
            ]))
        else:
            exito = guardar_en_nube(state["alumno"], state["unidad"], state["puntos"])
            page.add(layout_contenedor([
                ft.Text("Evaluación Finalizada", size=24, color="white"),
                ft.Text(f"Nota: {state['puntos']}/6", size=60, color="white", weight="bold"),
                ft.FilledButton("VOLVER AL MENÚ", on_click=lambda _: menu_principal())
            ]))

    def ir_a_unidad(u):
        state.update({"unidad": u, "idx": 0, "puntos": 0})
        page.clean()
        page.add(layout_contenedor([
            ft.Text(u, size=32, weight="bold", color="white"),
            ft.FilledButton("INICIAR", on_click=lambda _: ejecutar_examen(), width=280, height=50)
        ]))

    # Iniciamos la aplicación llamando a la primera vista
    login_view()

# --- 5. EJECUCIÓN ---
if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", port=8080)
