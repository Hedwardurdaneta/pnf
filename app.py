import flet as ft
import gspread
import openpyxl
import os
import random
from oauth2client.service_account import ServiceAccountCredentials

# ===================== CONFIGURACIÓN =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONO_PATH = os.path.join(BASE_DIR, "assets", "icono.ico")
FONDO_PATH = os.path.join(BASE_DIR, "assets", "fondo.png")
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json")

# ===================== GOOGLE SHEETS =====================
def guardar_en_nube(nombre_alumno, unidad, puntos):
    alcance = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
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
        print(f"Error Google Sheets: {e}")
        return False


# ===================== ESTADO =====================
state = {"alumno": None, "unidad": None, "idx": 0, "puntos": 0}

# (Tus preguntas se mantienen igual)
preguntas = { ... }   # ← pega aquí tus preguntas de las 3 unidades

# ===================== MAIN =====================
def main(page: ft.Page):
    page.title = "Portal PNF - UNERMB"
    page.padding = 0
    page.bgcolor = "#0f0f23"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def layout_contenedor(elementos):
        return ft.Container(
            content=ft.Column(elementos, 
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=25),
            expand=True,
            image_src=FONDO_PATH,
            image_fit="cover",
            alignment=ft.Alignment(0, 0),
        )

    # ... (todas tus funciones: login_view, menu_principal, ir_a_unidad, ejecutar_examen) ...
    # Usa el código que te di anteriormente para estas funciones

    login_view()

# ===================== EJECUCIÓN RAILWAY =====================
if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8080))
    
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets",
        port=port,
        host="0.0.0.0",
        route_url_strategy="path"
    )
