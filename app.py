import flet as ft
import gspread
import openpyxl
import os
import random
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONO_PATH = os.path.join(BASE_DIR, "assets", "icono.ico")
FONDO_PATH = os.path.join(BASE_DIR, "assets", "fondo.png")
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json")

# --- PERSISTENCIA EN GOOGLE SHEETS ---
def guardar_en_nube(nombre_alumno, unidad, puntos):
    alcance = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if not os.path.exists(CREDS_PATH):
            print("Archivo credentials.json no encontrado")
            return False
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, alcance)
        cliente = gspread.authorize(creds)
        hoja_principal = cliente.open("Ingenieria de software II")
        hoja = hoja_principal.worksheet("Notas_PNF_UNERMB")
        
        lista_nombres = hoja.col_values(3)  # Columna C (nombres)
        if nombre_alumno in lista_nombres:
            fila = lista_nombres.index(nombre_alumno) + 1
            columna = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
            if columna:
                hoja.update_cell(fila, columna, puntos)
                return True
        return False
    except Exception as e:
        print(f"Error en sincronización: {e}")
        return False


# --- ESTADO Y BANCO DE PREGUNTAS ---
state = {"alumno": None, "unidad": None, "idx": 0, "puntos": 0}

preguntas = {
    "UNIDAD I": [
        ("¿Qué es un algoritmo?", ["Pasos lógicos", "Hardware", "Un error", "Virus"], "Pasos lógicos"),
        ("¿Qué es Hardware?", ["Componentes físicos", "Virtual", "Software", "Nube"], "Componentes físicos"),
        ("¿Qué es Software?", ["Sistemas lógicos", "Cables", "Monitor", "Teclado"], "Sistemas lógicos"),
        ("¿Qué es el IDE?", ["Entorno de desarrollo", "Internet", "Disco", "Puerto"], "Entorno de desarrollo"),
        ("¿Qué es la sintaxis?", ["Reglas de escritura", "Un cable", "Monitor", "Energía"], "Reglas de escritura"),
        ("¿Qué es un compilador?", ["Traductor de código", "Virus", "Hardware", "Navegador"], "Traductor de código")
    ],
    "UNIDAD II": [
        ("¿Qué guarda 'int'?", ["Números enteros", "Texto", "Decimales", "Listas"], "Números enteros"),
        ("¿Qué guarda 'str'?", ["Cadenas de texto", "Números", "Bucle", "Tuplas"], "Cadenas de texto"),
        ("¿Qué guarda 'float'?", ["Números decimales", "Cadenas", "Enteros", "Nulo"], "Números decimales"),
        ("¿Qué es 'if'?", ["Estructura condicional", "Bucle", "Variable", "Clase"], "Estructura condicional"),
        ("¿Qué es 'for'?", ["Bucle definido", "Suma", "Texto", "Lista"], "Bucle definido"),
        ("¿Qué es una función?", ["Bloque reutilizable", "Error", "Variable", "Dato"], "Bloque reutilizable")
    ],
    "UNIDAD III": [
        ("¿Qué es Flet?", ["Framework de UI", "Antivirus", "Hardware", "OS"], "Framework de UI"),
        ("¿Qué es un Widget?", ["Componente de interfaz", "Cable", "Virus", "Disco"], "Componente de interfaz"),
        ("¿Qué es el Layout?", ["Organización visual", "Color", "Nombre", "Icono"], "Organización visual"),
        ("¿Qué es un evento?", ["Acción del sistema", "Error", "Hardware", "Red"], "Acción del sistema"),
        ("¿Qué es un Label?", ["Elemento de texto", "Botón", "Imagen", "Menú"], "Elemento de texto"),
        ("¿Qué es un Container?", ["Caja de diseño", "Bucle", "Variable", "Clase"], "Caja de diseño")
    ]
}


# --- INTERFAZ GRÁFICA ---
def main(page: ft.Page):
    page.title = "Portal PNF - UNERMB"
    page.padding = 0
    page.spacing = 0
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#1a1a2e"

    def layout_contenedor(elementos):
        return ft.Container(
            content=ft.Column(
                elementos,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=25
            ),
            expand=True,
            image_src=FONDO_PATH,
            image_fit="cover",
            alignment=ft.Alignment.CENTER,          # ← Corrección principal
        )

    def menu_principal():
        page.clean()
        page.add(layout_contenedor([
            ft.Text(f"BIENVENIDO: {state['alumno']}", size=24, color="white", weight="bold"),
            ft.FilledButton("UNIDAD I: FUNDAMENTOS", 
                           on_click=lambda _: ir_a_unidad("UNIDAD I"), 
                           width=360, height=55),
            ft.FilledButton("UNIDAD II: PROGRAMACIÓN", 
                           on_click=lambda _: ir_a_unidad("UNIDAD II"), 
                           width=360, height=55),
            ft.FilledButton("UNIDAD III: INTERFACES", 
                           on_click=lambda _: ir_a_unidad("UNIDAD III"), 
                           width=360, height=55),
            ft.TextButton("Cerrar Sesión", 
                         on_click=lambda _: login_view(), 
                         style=ft.ButtonStyle(color=ft.Colors.WHITE))
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
                ft.Text(f"Evaluación {u} - {state['idx']+1}/6", 
                       color="#aed6f1", size=19, weight="bold"),
                ft.Text(p, size=26, color="white", text_align="center", weight="bold"),
                *[ft.FilledButton(o, on_click=lambda e, o=o: validar(o), 
                                width=400, height=52) for o in opciones]
            ]))
        else:
            # Fin del examen
            exito = guardar_en_nube(state["alumno"], state["unidad"], state["puntos"])
            page.add(layout_contenedor([
                ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400, size=70),
                ft.Text("PRUEBA FINALIZADA", size=28, color="white", weight="bold"),
                ft.Text(f"Calificación: {state['puntos']} / 6", 
                       size=55, color=ft.Colors.WHITE, weight="bold"),
                ft.Text("Sincronización exitosa" if exito else "Error al subir nota", 
                       color=ft.Colors.GREY_400, size=18),
                ft.FilledButton("REGRESAR AL INICIO", 
                               on_click=lambda _: menu_principal(), 
                               width=300, height=50)
            ]))

    def ir_a_unidad(u):
        state.update({"unidad": u, "idx": 0, "puntos": 0})
        page.clean()
        page.add(layout_contenedor([
            ft.Text(f"Evaluación: {u}", size=32, weight="bold", color="white"),
            ft.Text("¿Está listo para comenzar?", color="#d1d1d1", size=18),
            ft.FilledButton("EMPEZAR EXAMEN", 
                           on_click=lambda _: ejecutar_examen(), 
                           width=300, height=55),
            ft.TextButton("Volver", 
                         on_click=lambda _: menu_principal(), 
                         style=ft.ButtonStyle(color=ft.Colors.WHITE))
        ]))

    def login_view():
        page.clean()
        usuarios_db = {"Admin": "1234"}

        if os.path.exists(EXCEL_PATH):
            try:
                wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
                sh = wb.active
                usuarios_db = {
                    str(sh.cell(r, 3).value): str(sh.cell(r, 2).value) 
                    for r in range(2, 60) 
                    if sh.cell(r, 3).value
                }
            except Exception as e:
                print("Error al leer Excel:", e)

        drop_user = ft.Dropdown(
            label="Seleccione su Nombre",
            width=380,
            options=[ft.dropdown.Option(n) for n in usuarios_db.keys()],
            bgcolor=ft.Colors.WHITE10
        )
        txt_pass = ft.TextField(
            label="Cédula", 
            password=True, 
            can_reveal_password=True, 
            width=380
        )

        def intentar_login(e):
            if (drop_user.value in usuarios_db and 
                usuarios_db[drop_user.value] == txt_pass.value):
                state["alumno"] = drop_user.value
                menu_principal()
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Credenciales Incorrectas", color=ft.Colors.RED_300),
                    bgcolor=ft.Colors.RED_900
                )
                page.snack_bar.open = True
                page.update()

        page.add(layout_contenedor([
            ft.Image(src=ICONO_PATH, width=140),
            ft.Text("INGENIERÍA DE SOFTWARE II", 
                   size=32, weight="bold", color="white"),
            ft.Text("Portal de Acceso Académico", 
                   color="#d1d1d1", size=18),
            drop_user,
            txt_pass,
            ft.FilledButton("ACCEDER", 
                           on_click=intentar_login, 
                           width=260, height=55)
        ]))

    login_view()


# --- EJECUCIÓN ---
if __name__ == "__main__":
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER, 
        assets_dir="assets", 
        port=8080
    )
