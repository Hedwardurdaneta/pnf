import flet as ft
import gspread
import openpyxl
import os
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONO_PATH = "icono.ico" 
FONDO_PATH = "fondo.png"
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json") # Nombre corregido según su GitHub

# --- FUNCIÓN DE GUARDADO ---
def guardar_en_nube(nombre_alumno, unidad, puntos):
    alcance = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, alcance)
        cliente = gspread.authorize(creds)
        # Nombre exacto de su archivo y hoja
        hoja = cliente.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
        
        lista_nombres = hoja.col_values(3) # Columna C: Nombre y Apellido
        fila = lista_nombres.index(nombre_alumno) + 1
        
        # NOTA1=D(4), NOTA2=E(5), NOTA3=F(6)
        col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
        
        if col:
            hoja.update_cell(fila, col, puntos)
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# --- INTERFAZ ---
def main(page: ft.Page):
    page.title = "Portal UNERMB"
    page.vertical_alignment = "center" # Corregido para evitar error de su captura
    page.horizontal_alignment = "center"

    state = {"alumno": None, "unidad": None, "idx": 0, "puntos": 0}

    def vista_base(cont):
        return ft.Container(
            content=ft.Column(cont, horizontal_alignment="center", alignment="center", spacing=20),
            expand=True,
            image_src=FONDO_PATH,
            image_fit="cover" # Evita el error 'ImageFit' de su captura
        )

    def login():
        page.clean()
        user_drop = ft.Dropdown(label="Seleccione Usuario", width=300)
        if os.path.exists(EXCEL_PATH):
            wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
            sh = wb.active
            user_drop.options = [ft.dropdown.Option(str(sh.cell(r, 3).value)) for r in range(2, 50) if sh.cell(r, 3).value]

        def entrar(e):
            if user_drop.value:
                state["alumno"] = user_drop.value
                menu()
        
        page.add(vista_base([
            ft.Image(src=ICONO_PATH, width=100),
            ft.Text("ACCESO", size=30, color="white", weight="bold"),
            user_drop,
            ft.FilledButton("INGRESAR", on_click=entrar)
        ]))

    def menu():
        page.clean()
        page.add(vista_base([
            ft.Text(f"Estudiante: {state['alumno']}", color="white"),
            ft.FilledButton("UNIDAD I", on_click=lambda _: examen("UNIDAD I"), width=250),
            ft.FilledButton("UNIDAD II", on_click=lambda _: examen("UNIDAD II"), width=250),
            ft.FilledButton("UNIDAD III", on_click=lambda _: examen("UNIDAD III"), width=250)
        ]))

    def examen(u):
        state.update({"unidad": u, "idx": 0, "puntos": 0})
        preguntas = {"UNIDAD I": [("¿Pregunta 1?", ["A", "B"], "A")], "UNIDAD II": [], "UNIDAD III": []}
        
        def proxima():
            page.clean()
            if state["idx"] < len(preguntas[u]):
                p, ops, corr = preguntas[u][state["idx"]]
                def check(res):
                    if res == corr: state["puntos"] += 1
                    state["idx"] += 1
                    proxima()
                page.add(vista_base([ft.Text(p, color="white"), *[ft.FilledButton(o, on_click=lambda e, o=o: check(o)) for o in ops]]))
            else:
                guardar_en_nube(state["alumno"], state["unidad"], state["puntos"])
                page.add(vista_base([ft.Text(f"Nota: {state['puntos']}", size=40, color="white"), ft.FilledButton("INICIO", on_click=lambda _: menu())]))
        proxima()

    login()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", port=8080)
