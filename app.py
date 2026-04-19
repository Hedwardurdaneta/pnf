import flet as ft
import gspread
import openpyxl
import os
import random
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURACIÓN ESTRUCTURAL ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONDO_PATH = "assets/fondo_unermb.png"
EXCEL_LOCAL = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")

# --- 2. CONEXIÓN A GOOGLE SHEETS (HOJA: Notas_PNF_UNERMB) ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    creds = Credentials.from_service_account_file(CREDS_JSON, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
except Exception as e:
    sheet = None
    print(f"Error de conexión: {e}")

# --- 3. BANCO DE DATOS COMPLETO (10 PREGUNTAS POR UNIDAD) ---
banco_preguntas = {
    "UNIDAD I": [
        ("¿Qué es un algoritmo?", ["Pasos lógicos", "Un virus", "Hardware"], "Pasos lógicos"),
        ("¿Qué significa IDE?", ["Entorno de Desarrollo", "Internet", "Disco"], "Entorno de Desarrollo"),
        ("¿Qué es la depuración?", ["Corregir errores", "Borrar archivos", "Instalar"], "Corregir errores"),
        ("¿Función de la compilación?", ["Traducir código", "Apagar PC", "Imprimir"], "Traducir código"),
        ("¿Qué es la sintaxis?", ["Reglas de escritura", "Un procesador", "Teclado"], "Reglas de escritura"),
        ("¿Dónde reside una variable?", ["Memoria RAM", "Monitor", "Impresora"], "Memoria RAM"),
        ("¿Qué es código fuente?", ["Texto programado", "Electricidad", "Internet"], "Texto programado"),
        ("¿El compilador lee comentarios?", ["No", "Sí", "A veces"], "No"),
        ("¿Qué es el hardware?", ["Parte física", "Programas", "Páginas"], "Parte física"),
        ("¿Qué es el software?", ["Parte lógica", "Cables", "Mouse"], "Parte lógica")
    ],
    "UNIDAD II": [
        ("¿Qué guarda un 'int'?", ["Enteros", "Letras", "Imágenes"], "Enteros"),
        ("¿Qué guarda un 'float'?", ["Decimales", "Cadenas", "Enteros"], "Decimales"),
        ("¿Qué es un 'str'?", ["Texto", "Números", "Bucle"], "Texto"),
        ("¿Valores del 'bool'?", ["True/False", "1/100", "A/B"], "True/False"),
        ("¿Qué es una lista?", ["Colección de datos", "Variable única", "Error"], "Colección de datos"),
        ("¿Qué es '+'?", ["Operador", "Variable", "Widget"], "Operador"),
        ("¿Símbolo de asignación?", ["=", "==", "+"], "="),
        ("¿Qué es 'if'?", ["Condicional", "Bucle", "Variable"], "Condicional"),
        ("¿Qué es 'while'?", ["Bucle condicional", "Salida", "Entrada"], "Bucle condicional"),
        ("¿Qué es 'for'?", ["Bucle iterativo", "Suma", "Texto"], "Bucle iterativo")
    ],
    "UNIDAD III": [
        ("¿Qué es Flet?", ["Framework UI", "Base de datos", "Antivirus"], "Framework UI"),
        ("¿Qué es un Widget?", ["Control visual", "Cable", "Virus"], "Control visual"),
        ("¿Qué muestra un Label?", ["Texto", "Video", "Música"], "Texto"),
        ("¿Qué es un Entry?", ["Entrada de texto", "Salida", "Imagen"], "Entrada de texto"),
        ("¿Qué hace un Button?", ["Ejecuta acciones", "Nada", "Cierra todo"], "Ejecuta acciones"),
        ("¿Qué es un Container?", ["Agrupador", "Variable", "Lista"], "Agrupador"),
        ("¿Qué es un clic?", ["Evento", "Error", "Hardware"], "Evento"),
        ("¿Qué es el Layout?", ["Organización", "Color", "Nombre"], "Organización"),
        ("¿Qué es el Mainloop?", ["Ciclo de la app", "Cable", "Botón"], "Ciclo de la app"),
        ("¿El color es un atributo?", ["Sí", "No", "Solo en Linux"], "Sí")
    ]
}

# --- 4. LÓGICA DE INTERFAZ ---
def main(page: ft.Page):
    page.title = "Portal Educativo UNERMB"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    
    state = {"user": None, "cedula": None, "unidad": None, "puntos": 0, "idx": 0}

    def registrar_en_nube(nota):
        if sheet:
            try:
                cell = sheet.find(str(state["cedula"]))
                col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(state["unidad"])
                sheet.update_cell(cell.row, col, nota)
            except: print("Usuario no encontrado en la hoja.")

    def container_ui(content_list):
        return ft.Container(
            content=ft.Column(content_list, horizontal_alignment="center", alignment="center", spacing=20),
            expand=True, image_src=FONDO_PATH, image_fit="cover", alignment=ft.alignment.center,
            gradient=ft.LinearGradient(begin=ft.alignment.top_center, end=ft.alignment.bottom_center, 
                                      colors=[ft.colors.with_opacity(0.5, "black"), ft.colors.with_opacity(0.2, "black")])
        )

    def login():
        page.clean()
        # Carga de alumnos desde Excel local
        alumnos = {"Admin": "1234"}
        if os.path.exists(EXCEL_LOCAL):
            wb = openpyxl.load_workbook(EXCEL_LOCAL, data_only=True)
            ws = wb.active
            for r in range(2, 100):
                if ws.cell(r, 3).value: alumnos[str(ws.cell(r, 3).value)] = str(ws.cell(r, 2).value)

        drop = ft.Dropdown(label="Seleccione Alumno", width=400, bgcolor="white", options=[ft.dropdown.Option(n) for n in alumnos.keys()])
        pass_f = ft.TextField(label="Cédula", password=True, width=400, bgcolor="white")

        def ingresar(e):
            if drop.value in alumnos and alumnos[drop.value] == pass_f.value:
                state.update({"user": drop.value, "cedula": pass_f.value})
                menu()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Datos incorrectos")); page.snack_bar.open = True; page.update()

        page.add(container_ui([ft.Text("ACCESO PNF", size=40, color="white", weight="bold"), drop, pass_f, 
                              ft.ElevatedButton("ENTRAR", on_click=ingresar, width=200, height=50)]))

    def menu():
        page.clean()
        page.add(container_ui([
            ft.Text(f"Bienvenido: {state['user']}", size=25, color="white"),
            ft.ElevatedButton("UNIDAD I", on_click=lambda _: start_test("UNIDAD I"), width=300),
            ft.ElevatedButton("UNIDAD II", on_click=lambda _: start_test("UNIDAD II"), width=300),
            ft.ElevatedButton("UNIDAD III", on_click=lambda _: start_test("UNIDAD III"), width=300)
        ]))

    def start_test(u):
        state.update({"unidad": u, "idx": 0, "puntos": 0})
        show_question()

    def show_question():
        page.clean()
        preguntas = banco_preguntas[state["unidad"]]
        if state["idx"] < len(preguntas):
            p, opts, corr = preguntas[state["idx"]]
            def check(a):
                if a == corr: state["puntos"] += 1
                state["idx"] += 1; show_question()

            page.add(container_ui([
                ft.Text(f"{state['unidad']} - {state['idx']+1}/10", color="white"),
                ft.Container(content=ft.Text(p, size=24, weight="bold", text_align="center"), bgcolor="white", padding=20, border_radius=10, width=600),
                *[ft.ElevatedButton(o, on_click=lambda e, o=o: check(o), width=400) for o in opts]
            ]))
        else:
            registrar_en_nube(state["puntos"])
            page.add(container_ui([ft.Text("RESULTADO", size=30, color="white"), 
                                  ft.Text(f"{state['puntos']}/10", size=80, color="white", weight="bold"),
                                  ft.ElevatedButton("VOLVER", on_click=lambda _: menu())]))
        page.update()

    login()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
