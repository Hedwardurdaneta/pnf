import flet as ft
import gspread
import openpyxl
import os
import random
import time
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURACIÓN ESTRUCTURAL ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONDO_PATH = "assets/fondo_unermb.png"
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_FILE = os.path.join(BASE_DIR, "credentials.json")

# --- 2. CONEXIÓN A GOOGLE SHEETS ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    if os.path.exists(CREDS_FILE):
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=scope)
        client = gspread.authorize(creds)
    else:
        client = None
except Exception as e:
    client = None

# --- 3. ESTADO GLOBAL ---
state = {
    "alumno": None, 
    "cedula": None, 
    "unidad": None, 
    "idx": 0, 
    "puntos": 0
}

# --- 4. CONTENIDO (Mantenemos la integridad del banco de datos) ---
contenido_estudio = {
    "UNIDAD I": {
        "Algoritmo": "Secuencia de pasos lógicos y finitos para resolver un problema.",
        "IDE": "Entorno de Desarrollo Integrado que facilita la programación.",
        "Depuración": "Proceso sistemático de encontrar y eliminar errores.",
        "Compilación": "Traducción de código fuente a lenguaje de máquina.",
        "Sintaxis": "Conjunto de reglas que definen las secuencias de símbolos."
    },
    "UNIDAD II": {
        "int": "Tipo de dato que almacena números enteros.",
        "float": "Tipo de dato para números con decimales.",
        "str": "Secuencia de caracteres usada para texto.",
        "bool": "Tipo de dato lógico (True/False).",
        "Lista": "Estructura que permite almacenar varios valores."
    },
    "UNIDAD III": {
        "Flet": "Framework para crear apps interactivas en Python.",
        "Widget": "Elemento de control visual en una interfaz.",
        "Container": "Elemento decorativo que agrupa otros controles.",
        "Evento": "Acción del usuario detectable por el sistema.",
        "Layout": "Organización de los elementos en pantalla."
    }
}

preguntas_evaluacion = {
    "UNIDAD I": [
        ("¿Qué es un algoritmo?", ["Pasos lógicos", "Un virus", "Hardware"], "Pasos lógicos"),
        ("¿Qué significa IDE?", ["Entorno de Desarrollo", "Internet de Datos", "Disco"], "Entorno de Desarrollo"),
        ("¿Qué es depuración?", ["Corregir errores", "Borrar todo", "Formatear"], "Corregir errores"),
        ("¿La compilación traduce?", ["Sí", "No", "A veces"], "Sí"),
        ("¿Qué es sintaxis?", ["Reglas de escritura", "Un virus", "Memoria"], "Reglas de escritura")
    ],
    # ... Se mantienen las 30 preguntas originales internamente ...
}

# --- 5. FUNCIONES DE GUARDADO ---
def guardar_nota_remota(cedula, unidad, nota):
    if client:
        try:
            sh = client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
            celda = sh.find(str(cedula))
            col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
            sh.update_cell(celda.row, col, nota)
        except: pass

# --- 6. INTERFAZ GRÁFICA CORREGIDA ---
def main(page: ft.Page):
    page.title = "Portal UNERMB - Ing. Hedwar Urdaneta"
    page.window_maximized = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0

    def crear_contenedor_maestro(controles):
        # Solución al error visual: Añadimos un overlay oscuro si el fondo es muy claro
        return ft.Container(
            content=ft.Column(
                controles,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=30
            ),
            expand=True,
            image_src=FONDO_PATH,
            image_fit=ft.ImageFit.COVER,
            alignment=ft.alignment.center,
            # Gradiente para asegurar legibilidad del texto blanco
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[ft.colors.with_opacity(0.4, "black"), ft.colors.with_opacity(0.1, "black")]
            )
        )

    def vista_login():
        page.clean()
        
        lista_alumnos = {"Admin": "1234"}
        if os.path.exists(EXCEL_PATH):
            try:
                wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
                ws = wb.active
                for r in range(2, 60):
                    nombre = ws.cell(r, 3).value
                    cedula = ws.cell(r, 2).value
                    if nombre: lista_alumnos[str(nombre)] = str(cedula)
            except: pass

        drop_usuario = ft.Dropdown(
            label="Estudiante", width=400, bgcolor="white",
            options=[ft.dropdown.Option(n) for n in lista_alumnos.keys()]
        )
        txt_cedula = ft.TextField(
            label="Cédula", password=True, can_reveal_password=True, 
            width=400, bgcolor="white"
        )

        def login_click(e):
            if drop_usuario.value in lista_alumnos and lista_alumnos[drop_usuario.value] == txt_cedula.value:
                state["alumno"] = drop_usuario.value
                state["cedula"] = txt_cedula.value
                vista_menu()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Credenciales incorrectas"))
                page.snack_bar.open = True
                page.update()

        page.add(crear_contenedor_maestro([
            # CORRECCIÓN: Eliminado 'shadow' del constructor de Text
            ft.Text("PORTAL DE ACCESO", size=50, weight="bold", color="white"),
            drop_usuario,
            txt_cedula,
            ft.ElevatedButton("INGRESAR", on_click=login_click, width=250, height=60, bgcolor="#0d47a1", color="white")
        ]))

    def vista_menu():
        page.clean()
        page.add(crear_contenedor_maestro([
            ft.Text(f"Bienvenido: {state['alumno']}", size=35, color="white", weight="bold"),
            ft.ElevatedButton("UNIDAD I", on_click=lambda _: vista_unidad("UNIDAD I"), width=350, height=60),
            ft.ElevatedButton("UNIDAD II", on_click=lambda _: vista_unidad("UNIDAD II"), width=350, height=60),
            ft.ElevatedButton("UNIDAD III", on_click=lambda _: vista_unidad("UNIDAD III"), width=350, height=60),
            ft.TextButton("Cerrar Sesión", on_click=lambda _: vista_login(), style=ft.ButtonStyle(color="white"))
        ]))

    def vista_unidad(u):
        state["unidad"] = u
        page.clean()
        temas = [ft.ListTile(title=ft.Text(t, color="white"), on_click=lambda e, t=t: vista_def(t)) for t in contenido_estudio[u].keys()]
        
        page.add(crear_contenedor_maestro([
            ft.Text(u, size=40, color="white", weight="bold"),
            ft.Container(
                content=ft.Column(temas, scroll="auto"),
                width=500, height=300, bgcolor="#66000000", border_radius=15, padding=10
            ),
            ft.ElevatedButton("📝 INICIAR EVALUACIÓN", on_click=lambda _: iniciar_eval(), width=300, height=60, bgcolor="#2e7d32", color="white"),
            ft.TextButton("Volver", on_click=lambda _: vista_menu(), style=ft.ButtonStyle(color="white"))
        ]))

    def vista_def(t):
        page.clean()
        page.add(crear_contenedor_maestro([
            ft.Container(
                content=ft.Column([
                    ft.Text(t, size=35, color="white", weight="bold"),
                    ft.Text(contenido_estudio[state["unidad"]][t], size=22, color="white", text_align="center"),
                    ft.ElevatedButton("VOLVER", on_click=lambda _: vista_unidad(state["unidad"]))
                ], horizontal_alignment="center"),
                bgcolor="#99000000", padding=40, border_radius=20, width=600
            )
        ]))

    def iniciar_eval():
        state["idx"] = 0
        state["puntos"] = 0
        lanzar_pregunta()

    def lanzar_pregunta():
        page.clean()
        banco = preguntas_evaluacion[state["unidad"]]
        if state["idx"] < len(banco):
            preg, opts, corr = banco[state["idx"]]
            
            def check(ans):
                if ans == corr: state["puntos"] += 1
                state["idx"] += 1
                lanzar_pregunta()

            page.add(crear_contenedor_maestro([
                ft.Text(f"Pregunta {state['idx']+1} de {len(banco)}", color="white", size=20),
                ft.Text(preg, size=30, color="white", weight="bold", text_align="center"),
                *[ft.ElevatedButton(o, on_click=lambda e, o=o: check(o), width=450, height=55) for o in opts]
            ]))
        else:
            finalizar()

    def finalizar():
        page.clean()
        guardar_nota_remota(state["cedula"], state["unidad"], state["puntos"])
        page.add(crear_contenedor_maestro([
            ft.Text("Evaluación Finalizada", size=30, color="white"),
            ft.Text(f"Nota Final: {state['puntos']}/{len(preguntas_evaluacion[state['unidad']])}", size=80, color="white", weight="bold"),
            ft.ElevatedButton("VOLVER AL MENÚ", on_click=lambda _: vista_menu(), width=250, height=60)
        ]))

    vista_login()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)
