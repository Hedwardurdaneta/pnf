import flet as ft
import gspread
import openpyxl
import os
import random
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONO_PATH = "icono.ico" 
FONDO_PATH = "fondo.png"
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json")

# --- 2. PERSISTENCIA ---
def guardar_en_nube(alumno, unidad, puntos):
    alcance = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if not os.path.exists(CREDS_PATH): return False
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, alcance)
        cliente = gspread.authorize(creds)
        hoja = cliente.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
        lista = hoja.col_values(3)
        if alumno in lista:
            fila = lista.index(alumno) + 1
            col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
            if col: 
                hoja.update_cell(fila, col, puntos)
                return True
        return False
    except: return False

# --- 3. BANCO DE PREGUNTAS (Reducido para brevedad) ---
state = {"alumno": None, "unidad": None, "idx": 0, "puntos": 0}
preguntas = {
    "UNIDAD I": [("¿Qué es un algoritmo?", ["Pasos lógicos", "Virus", "Hardware"], "Pasos lógicos")],
    "UNIDAD II": [("¿Qué guarda un 'int'?", ["Enteros", "Letras", "Decimales"], "Enteros")],
    "UNIDAD III": [("¿Para qué sirve Flet?", ["Interfaces", "Café", "Base de datos"], "Interfaces")]
}

# --- 4. INTERFAZ ---
def main(page: ft.Page):
    page.title = "Portal UNERMB"
    page.padding = 0
    # CORRECCIÓN: Uso de constantes directas para evitar error de 'center'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def layout_con_fondo(elementos):
        return ft.Container(
            content=ft.Column(elementos, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            expand=True,
            image_src=FONDO_PATH,
            image_fit="cover",
            alignment=ft.alignment.center # SINTAXIS CORRECTA
        )

    def menu_principal():
        page.clean()
        page.add(layout_con_fondo([
            ft.Text(f"Estudiante: {state['alumno']}", size=24, color="white", weight="bold"),
            ft.FilledButton("UNIDAD I", on_click=lambda _: ir_a_unidad("UNIDAD I"), width=300),
            ft.FilledButton("UNIDAD II", on_click=lambda _: ir_a_unidad("UNIDAD II"), width=300),
            ft.FilledButton("UNIDAD III", on_click=lambda _: ir_a_unidad("UNIDAD III"), width=300),
            ft.TextButton("SALIR", on_click=lambda _: login_view(), style=ft.ButtonStyle(color="white"))
        ]))

    def ir_a_unidad(u):
        state.update({"unidad": u, "idx": 0, "puntos": 0})
        # Lógica de examen similar a su versión original...
        menu_principal() # Temporal para prueba

    def login_view():
        page.clean()
        # Carga de usuarios desde Excel
        usuarios = {"Admin": "1234"}
        if os.path.exists(EXCEL_PATH):
            wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
            sh = wb.active
            usuarios = {str(sh.cell(r, 3).value): str(sh.cell(r, 2).value) for r in range(2, 60) if sh.cell(r, 3).value}

        drop = ft.Dropdown(label="Usuario", width=350, options=[ft.dropdown.Option(n) for n in usuarios.keys()])
        pwd = ft.TextField(label="Cédula", password=True, width=350)

        def acceder(e):
            if drop.value in usuarios and usuarios[drop.value] == pwd.value:
                state["alumno"] = drop.value
                menu_principal()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Credenciales Incorrectas"))
                page.snack_bar.open = True
                page.update()

        page.add(layout_con_fondo([
            ft.Image(src=ICONO_PATH, width=100),
            ft.Text("PORTAL DE ACCESO", size=30, weight="bold", color="white"),
            drop, pwd,
            ft.FilledButton("INGRESAR", on_click=acceder, width=200)
        ]))

    login_view()

if __name__ == "__main__":
    # Uso de ft.app para compatibilidad con Railway
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", port=int(os.getenv("PORT", 8080)))
