import flet as ft
import gspread
import openpyxl
import os
import random
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
FONDO_URL = "https://raw.githubusercontent.com/Hedwardurdaneta/pnf-PNF/main/assets/fondo_unermb.png"

# --- CONEXIÓN GOOGLE SHEETS ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)
except Exception as e:
    print(f"Error de conexión: {e}")

# --- BANCO DE PREGUNTAS (RELLENE AQUÍ SUS 10 PREGUNTAS) ---
preguntas_reales = {
    "UNIDAD I": [
        ("¿Qué es un algoritmo?", ["Pasos lógicos", "Hardware", "Un virus"], "Pasos lógicos"),
        ("¿Qué significa IDE?", ["Entorno de Desarrollo", "Internet", "Disco"], "Entorno de Desarrollo"),
        # Agregue aquí las 8 restantes...
    ],
    "UNIDAD II": [
        ("¿Qué guarda un 'int'?", ["Enteros", "Letras", "Decimales"], "Enteros"),
        # Agregue aquí las 9 restantes...
    ],
    "UNIDAD III": [
        ("¿Para qué sirve Flet?", ["Interfaces", "Base de datos", "Redes"], "Interfaces"),
        # Agregue aquí las 9 restantes...
    ]
}

state = {"alumno": None, "cedula": None, "unidad": None, "idx": 0, "puntos": 0}

def main(page: ft.Page):
    page.title = "Portal Educativo UNERMB"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    def contenedor_principal(contenido):
        return ft.Container(
            content=ft.Column(contenido, horizontal_alignment="center", alignment="center", spacing=25),
            expand=True,
            image_src=FONDO_URL,
            image_fit=ft.ImageFit.COVER,
            alignment=ft.alignment.center
        )

    def menu_principal():
        page.clean()
        page.add(contenedor_principal([
            ft.Text(f"Bienvenido: {state['alumno']}", size=32, weight="bold", color="white", shadow=ft.BoxShadow(blur_radius=10, color="black")),
            ft.ElevatedButton("UNIDAD I", on_click=lambda _: ir_a_unidad("UNIDAD I"), width=350, height=60, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
            ft.ElevatedButton("UNIDAD II", on_click=lambda _: ir_a_unidad("UNIDAD II"), width=350, height=60),
            ft.ElevatedButton("UNIDAD III", on_click=lambda _: ir_a_unidad("UNIDAD III"), width=350, height=60),
            ft.TextButton("Cerrar Sesión", on_click=lambda _: login_view(), ft.TextStyle(color="white"))
        ]))

    def ir_a_unidad(u):
        state["unidad"] = u
        state["idx"] = 0
        state["puntos"] = 0
        lanzar_evaluacion()

    def lanzar_evaluacion():
        page.clean()
        lista = preguntas_reales[state["unidad"]]
        
        if state["idx"] < len(lista):
            pregunta, opciones, correcta = lista[state["idx"]]
            ops_random = list(opciones)
            random.shuffle(ops_random)

            def verificar(resp):
                if resp == correcta: state["puntos"] += 1
                state["idx"] += 1
                lanzar_evaluacion()

            page.add(contenedor_principal([
                ft.Text(f"{state['unidad']} - Pregunta {state['idx']+1}/{len(lista)}", color="white", size=20),
                ft.Container(
                    content=ft.Text(pregunta, size=28, weight="bold", text_align="center"),
                    padding=20, bgcolor="white", border_radius=15, width=600
                ),
                *[ft.ElevatedButton(opt, on_click=lambda e, opt=opt: verificar(opt), width=400, height=50) for opt in ops_random]
            ]))
        else:
            finalizar_examen()

    def finalizar_examen():
        # Lógica de guardado en Sheets
        try:
            sh = client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
            celda = sh.find(state["cedula"])
            col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}[state["unidad"]]
            sh.update_cell(celda.row, col, state["puntos"])
        except: pass

        page.clean()
        page.add(contenedor_principal([
            ft.Text("Evaluación Finalizada", size=30, color="white"),
            ft.Text(f"Nota: {state['puntos']}/10", size=80, weight="bold", color="white"),
            ft.ElevatedButton("VOLVER AL MENÚ", on_click=lambda _: menu_principal(), width=250)
        ]))

    def login_view():
        page.clean()
        # Carga de alumnos desde Excel
        alumnos = {}
        try:
            wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
            ws = wb.active
            for r in range(2, 50):
                ced = str(ws.cell(r, 2).value)
                nom = str(ws.cell(r, 3).value)
                if ced and nom: alumnos[nom] = ced
        except: alumnos = {"Admin": "1234"}

        user_drop = ft.Dropdown(label="Usuario", options=[ft.dropdown.Option(n) for n in alumnos.keys()], width=350, bgcolor="white")
        pass_txt = ft.TextField(label="Cédula", password=True, can_reveal_password=True, width=350, bgcolor="white")

        def acceder(e):
            if user_drop.value and pass_txt.value == alumnos.get(user_drop.value):
                state["alumno"] = user_drop.value
                state["cedula"] = pass_txt.value
                menu_principal()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Credenciales Incorrectas"))
                page.snack_bar.open = True
                page.update()

        page.add(contenedor_principal([
            ft.Text("PORTAL DE ACCESO", size=45, weight="bold", color="white"),
            user_drop, pass_txt,
            ft.ElevatedButton("INGRESAR", on_click=acceder, width=200, height=50, bgcolor="#2c5a8d", color="white")
        ]))

    login_view()

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)
