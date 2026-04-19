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

# ===================== GUARDAR EN GOOGLE SHEETS =====================
def guardar_en_nube(nombre_alumno, unidad, puntos):
    alcance = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if not os.path.exists(CREDS_PATH):
            print("❌ credentials.json no encontrado")
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
        print(f"Error en Google Sheets: {e}")
        return False


# ===================== ESTADO Y PREGUNTAS =====================
state = {"alumno": None, "unidad": None, "idx": 0, "puntos": 0}

preguntas = {
    "UNIDAD I": [ ... ],   # (mantengo igual que antes)
    "UNIDAD II": [ ... ],
    "UNIDAD III": [ ... ]
}

# ===================== MAIN =====================
def main(page: ft.Page):
    page.title = "Portal PNF - UNERMB"
    page.padding = 0
    page.bgcolor = "#0f0f23"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # ===================== CONTENEDOR PRINCIPAL (CORREGIDO) =====================
    def layout_contenedor(elementos):
        return ft.Container(
            content=ft.Column(
                elementos,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=25,
            ),
            expand=True,
            image_src=FONDO_PATH,
            image_fit="cover",
            alignment=ft.Alignment(0, 0),        # ← Esta es la forma correcta ahora
        )

    # ===================== VISTAS =====================
    def menu_principal():
        page.clean()
        page.add(layout_contenedor([
            ft.Text(f"BIENVENIDO: {state['alumno']}", size=26, color="white", weight="bold"),
            ft.FilledButton("UNIDAD I: FUNDAMENTOS", on_click=lambda _: ir_a_unidad("UNIDAD I"), width=380, height=60),
            ft.FilledButton("UNIDAD II: PROGRAMACIÓN", on_click=lambda _: ir_a_unidad("UNIDAD II"), width=380, height=60),
            ft.FilledButton("UNIDAD III: INTERFACES", on_click=lambda _: ir_a_unidad("UNIDAD III"), width=380, height=60),
            ft.TextButton("Cerrar Sesión", on_click=lambda _: login_view()),
        ]))

    def ejecutar_examen():
        page.clean()
        u = state["unidad"]

        if state["idx"] < len(preguntas[u]):
            p, opciones, correcta = preguntas[u][state["idx"]]
            random.shuffle(opciones)

            def validar(res):
                if res == correcta:
                    state["puntos"] += 1
                state["idx"] += 1
                ejecutar_examen()

            page.add(layout_contenedor([
                ft.Text(f"Evaluación {u} - {state['idx']+1}/6", color="#74c0fc", size=20, weight="bold"),
                ft.Text(p, size=27, color="white", text_align=ft.TextAlign.CENTER, weight="bold"),
                *[ft.FilledButton(o, on_click=lambda e, resp=o: validar(resp), width=420, height=55) for o in opciones]
            ]))
        else:
            exito = guardar_en_nube(state["alumno"], state["unidad"], state["puntos"])
            page.add(layout_contenedor([
                ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400, size=80),
                ft.Text("PRUEBA FINALIZADA", size=30, color="white", weight="bold"),
                ft.Text(f"{state['puntos']} / 6", size=70, color="white", weight="bold"),
                ft.Text("Sincronización exitosa" if exito else "Error al subir nota", color=ft.Colors.GREY_400),
                ft.FilledButton("REGRESAR AL INICIO", on_click=lambda _: menu_principal(), width=320, height=55)
            ]))

    def ir_a_unidad(u):
        state.update({"unidad": u, "idx": 0, "puntos": 0})
        page.clean()
        page.add(layout_contenedor([
            ft.Text(f"Evaluación: {u}", size=34, weight="bold", color="white"),
            ft.Text("¿Está listo para comenzar?", size=18, color="#bbbbbb"),
            ft.FilledButton("EMPEZAR EXAMEN", on_click=lambda _: ejecutar_examen(), width=320, height=60),
            ft.TextButton("Volver", on_click=lambda _: menu_principal()),
        ]))

    def login_view():
        # ... (mantengo igual, solo cambié alignment si había)
        # (copia el login_view del código anterior que te di)

        # Para no alargar, te recomiendo usar el login_view del mensaje anterior.

    login_view()


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", port=8080)
