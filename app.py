import flet as ft
import gspread
import openpyxl
import os
import random
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# En la web, Flet busca automáticamente en la carpeta 'assets'
ICONO_PATH = "icono.ico" 
FONDO_PATH = "fondo.png"
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json")

# --- 2. PERSISTENCIA EN LA NUBE (Google Sheets) ---
def guardar_en_nube(nombre_alumno, unidad, puntos):
    alcance = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if not os.path.exists(CREDS_PATH):
            print("Error: No se encuentra credentials.json")
            return False

        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, alcance)
        cliente = gspread.authorize(creds)
        
        # Apertura del archivo según imagen 0d011c.png
        hoja_principal = cliente.open("Ingenieria de software II")
        hoja = hoja_principal.worksheet("Notas_PNF_UNERMB")
        
        # Obtenemos la columna C (Nombre y Apellido) para buscar al alumno
        lista_nombres = hoja.col_values(3) 
        
        try:
            fila = lista_nombres.index(nombre_alumno) + 1
            # Mapeo de columnas: NOTA1=D(4), NOTA2=E(5), NOTA3=F(6)
            columna = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
            
            if columna:
                hoja.update_cell(fila, columna, puntos)
                return True
        except ValueError:
            print(f"Alumno {nombre_alumno} no encontrado en la hoja.")
            return False
            
    except Exception as e:
        print(f"Error crítico de conexión: {e}")
        return False

# --- 3. BANCO DE DATOS ---
state = {"alumno": None, "unidad": None, "idx": 0, "puntos": 0}

preguntas = {
    "UNIDAD I": [("¿Qué es un algoritmo?", ["Pasos lógicos", "Hardware"], "Pasos lógicos"), ("¿Qué es Hardware?", ["Físico", "Virtual"], "Físico")],
    "UNIDAD II": [("¿Qué guarda 'int'?", ["Enteros", "Texto"], "Enteros"), ("¿Qué es 'str'?", ["Texto", "Booleano"], "Texto")],
    "UNIDAD III": [("¿Qué es Flet?", ["Framework UI", "Antivirus"], "Framework UI"), ("¿Qué es un Widget?", ["Componente", "Cable"], "Componente")]
}

# --- 4. INTERFAZ GRÁFICA ---
def main(page: ft.Page):
    page.title = "Portal Educativo UNERMB"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Centrado total de la página
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def layout_con_fondo(contenido_vista):
        return ft.Container(
            content=ft.Column(
                contenido_vista, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                alignment=ft.MainAxisAlignment.CENTER, 
                spacing=20
            ),
            expand=True,
            # Se usa 'cover' como string para máxima compatibilidad
            image_src=FONDO_PATH,
            image_fit="cover",
            alignment=ft.alignment.center,
        )

    def menu_principal():
        page.clean()
        page.add(layout_con_fondo([
            ft.Text(f"Estudiante: {state['alumno']}", size=28, color="white", weight="bold"),
            ft.FilledButton("UNIDAD I", on_click=lambda _: mostrar_unidad("UNIDAD I"), width=320),
            ft.FilledButton("UNIDAD II", on_click=lambda _: mostrar_unidad("UNIDAD II"), width=320),
            ft.FilledButton("UNIDAD III", on_click=lambda _: mostrar_unidad("UNIDAD III"), width=320),
            ft.TextButton("Cerrar Sesión", on_click=lambda _: login_view(), style=ft.ButtonStyle(color="white"))
        ]))

    def lanzar_pregunta():
        page.clean()
        u = state["unidad"]
        if state["idx"] < len(preguntas[u]):
            p, opciones, correcta = preguntas[u][state["idx"]]
            def validar(res):
                if res == correcta: state["puntos"] += 1
                state["idx"] += 1
                lanzar_pregunta()
            page.add(layout_con_fondo([
                ft.Text(p, size=26, color="white", text_align="center"),
                *[ft.FilledButton(o, on_click=lambda e, o=o: validar(o), width=350) for o in opciones]
            ]))
        else:
            guardar_en_nube(state["alumno"], state["unidad"], state["puntos"])
            page.add(layout_con_fondo([
                ft.Text("Evaluación Finalizada", size=24, color="white"),
                ft.Text(f"Nota: {state['puntos']}/{len(preguntas[u])}", size=60, color="white", weight="bold"),
                ft.FilledButton("VOLVER AL MENÚ", on_click=lambda _: menu_principal())
            ]))

    def mostrar_unidad(u):
        state["unidad"], state["idx"], state["puntos"] = u, 0, 0
        page.clean()
        page.add(layout_con_fondo([
            ft.Text(u, size=30, weight="bold", color="white"),
            ft.FilledButton("INICIAR EXAMEN", on_click=lambda _: lanzar_pregunta(), width=280),
            ft.TextButton("Cancelar", on_click=lambda _: menu_principal(), style=ft.ButtonStyle(color="white"))
        ]))

    def login_view():
        page.clean()
        datos = {"Admin": "1234"}
        if os.path.exists(EXCEL_PATH):
            try:
                wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
                sh = wb.active
                # Se cargan los usuarios del archivo Programacion.xlsx
                datos = {str(sh.cell(r, 3).value): str(sh.cell(r, 2).value) for r in range(2, 51) if sh.cell(r, 3).value}
            except: pass

        user_drop = ft.Dropdown(label="Usuario", width=320, options=[ft.dropdown.Option(n) for n in datos.keys()])
        pass_field = ft.TextField(label="Cédula", password=True, width=320, can_reveal_password=True)

        def ingresar(e):
            if user_drop.value in datos and datos[user_drop.value] == pass_field.value:
                state["alumno"] = user_drop.value
                menu_principal()
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Credenciales Incorrectas"))
                page.snack_bar.open = True
                page.update()

        page.add(layout_con_fondo([
            ft.Image(src=ICONO_PATH, width=120),
            ft.Text("PORTAL DE ACCESO", size=32, weight="bold", color="white"),
            user_drop, pass_field, 
            ft.FilledButton("INGRESAR", on_click=ingresar, width=220)
        ]))

    login_view()

if __name__ == "__main__":
    # Importante para Railway: assets_dir y puerto
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", port=8080)
