import flet as ft
import gspread
import openpyxl
import os
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Flet en la web busca en la carpeta 'assets' automáticamente
ICONO_PATH = "icono.ico" 
FONDO_PATH = "fondo.png"
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json")

# --- GUARDADO EN GOOGLE SHEETS ---
def guardar_en_nube(nombre_alumno, unidad, puntos):
    alcance = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if not os.path.exists(CREDS_PATH): return False
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, alcance)
        cliente = gspread.authorize(creds)
        hoja = cliente.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
        lista_nombres = hoja.col_values(3) # Columna C
        try:
            fila = lista_nombres.index(nombre_alumno) + 1
            col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
            if col:
                hoja.update_cell(fila, col, puntos)
                return True
        except: return False
    except: return False

# --- INTERFAZ ---
def main(page: ft.Page):
    page.title = "Portal Educativo UNERMB"
    # IMPORTANTE: Usamos constantes directas para evitar el error de su captura
    page.vertical_alignment = "center" 
    page.horizontal_alignment = "center"

    state = {"alumno": None, "unidad": None, "idx": 0, "puntos": 0}
    preguntas = {
        "UNIDAD I": [("¿Qué es Hardware?", ["Físico", "Virtual"], "Físico")],
        "UNIDAD II": [("¿Qué es int?", ["Entero", "Texto"], "Entero")],
        "UNIDAD III": [("¿Flet es UI?", ["Sí", "No"], "Sí")]
    }

    def vista_contenedor(elementos):
        return ft.Container(
            content=ft.Column(elementos, horizontal_alignment="center", alignment="center", spacing=20),
            expand=True,
            image_src=FONDO_PATH,
            image_fit="cover" # Corregido: se usa string para evitar error ImageFit
        )

    def login():
        page.clean()
        user_drop = ft.Dropdown(label="Usuario", width=300, options=[ft.dropdown.Option("Admin")])
        # Carga desde Excel si existe
        if os.path.exists(EXCEL_PATH):
            wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
            sh = wb.active
            user_drop.options = [ft.dropdown.Option(str(sh.cell(r, 3).value)) for r in range(2, 50) if sh.cell(r, 3).value]

        def entrar(e):
            if user_drop.value:
                state["alumno"] = user_drop.value
                menu()
        
        page.add(vista_contenedor([
            ft.Image(src=ICONO_PATH, width=100),
            ft.Text("ACCESO ESTUDIANTIL", size=25, color="white", weight="bold"),
            user_drop,
            ft.FilledButton("INGRESAR", on_click=entrar, width=200)
        ]))

    def menu():
        page.clean()
        page.add(vista_contenedor([
            ft.Text(f"Bienvenido: {state['alumno']}", color="white", size=20),
            ft.FilledButton("UNIDAD I", on_click=lambda _: examen("UNIDAD I"), width=300),
            ft.FilledButton("UNIDAD II", on_click=lambda _: examen("UNIDAD II"), width=300),
            ft.FilledButton("UNIDAD III", on_click=lambda _: examen("UNIDAD III"), width=300)
        ]))

    def examen(u):
        state["unidad"], state["idx"], state["puntos"] = u, 0, 0
        def mostrar_p():
            page.clean()
            if state["idx"] < len(preguntas[u]):
                p, opciones, correcta = preguntas[u][state["idx"]]
                def validar(res):
                    if res == correcta: state["puntos"] += 1
                    state["idx"] += 1
                    mostrar_p()
                page.add(vista_contenedor([
                    ft.Text(p, size=22, color="white"),
                    *[ft.FilledButton(o, on_click=lambda e, o=o: validar(o), width=300) for o in opciones]
                ]))
            else:
                guardar_en_nube(state["alumno"], state["unidad"], state["puntos"])
                page.add(vista_contenedor([
                    ft.Text(f"Nota: {state['puntos']}", size=40, color="white"),
                    ft.FilledButton("VOLVER", on_click=lambda _: menu())
                ]))
        mostrar_p()

    login()

if __name__ == "__main__":
    # assets_dir es vital para Railway
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", port=8080)
