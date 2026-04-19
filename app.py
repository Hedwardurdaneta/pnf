import flet as ft
import gspread
import openpyxl
import os
import random
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONO_PATH = "icono.ico" 
FONDO_PATH = "fondo.png"
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
# El archivo de credenciales debe llamarse exactamente así en su repositorio
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json")

# --- 2. PERSISTENCIA EN LA NUBE (Google Sheets) ---
def guardar_en_nube(nombre_alumno, unidad, puntos):
    alcance = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if not os.path.exists(CREDS_PATH):
            return False

        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, alcance)
        cliente = gspread.authorize(creds)
        
        # Apertura de la hoja validada
        hoja_principal = cliente.open("Ingenieria de software II")
        hoja = hoja_principal.worksheet("Notas_PNF_UNERMB")
        
        # Columna C: Nombre y Apellido del Estudiante
        lista_nombres = hoja.col_values(3) 
        
        try:
            fila = lista_nombres.index(nombre_alumno) + 1
            # NOTA1=Col D(4), NOTA2=Col E(5), NOTA3=Col F(6)
            columna = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
            
            if columna:
                hoja.update_cell(fila, columna, puntos)
                return True
        except ValueError:
            return False
            
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False

# --- 3. BANCO DE DATOS Y ESTADO (MANTENIENDO SU ESTRUCTURA ORIGINAL) ---
state = {"alumno": None, "unidad": None, "idx": 0, "puntos": 0}

preguntas = {
    "UNIDAD I": [
        ("¿Qué es un algoritmo?", ["Pasos lógicos", "Hardware", "Un error"], "Pasos lógicos"),
        ("¿Qué es Hardware?", ["Físico", "Virtual", "Software"], "Físico"),
        ("¿Qué es Software?", ["Lógico", "Cables", "Monitor"], "Lógico"),
        ("¿Qué es el IDE?", ["Entorno de desarrollo", "Internet", "Disco"], "Entorno de desarrollo"),
        ("¿Qué es la sintaxis?", ["Reglas de escritura", "Un cable", "Monitor"], "Reglas de escritura")
    ],
    "UNIDAD II": [
        ("¿Qué guarda 'int'?", ["Enteros", "Texto", "Decimales"], "Enteros"),
        ("¿Qué guarda 'str'?", ["Texto", "Números", "Bucle"], "Texto"),
        ("¿Qué guarda 'float'?", ["Decimales", "Cadenas", "Enteros"], "Decimales"),
        ("¿Qué es 'if'?", ["Condicional", "Bucle", "Variable"], "Condicional"),
        ("¿Qué es 'for'?", ["Bucle repetitivo", "Suma", "Texto"], "Bucle repetitivo")
    ],
    "UNIDAD III": [
        ("¿Qué es Flet?", ["Framework UI", "Antivirus", "Hardware"], "Framework UI"),
        ("¿Qué es un Widget?", ["Componente visual", "Cable", "Virus"], "Componente visual"),
        ("¿Qué es el Layout?", ["Organización", "Color", "Nombre"], "Organización"),
        ("¿Qué es un evento?", ["Acción detectada", "Error", "Hardware"], "Acción detectada"),
        ("¿Qué es un Label?", ["Texto estático", "Botón", "Imagen"], "Texto estático")
    ]
}

# --- 4. INTERFAZ GRÁFICA (RECUPERANDO TODAS LAS LÍNEAS DE DISEÑO) ---
def main(page: ft.Page):
    page.title = "Portal Educativo UNERMB"
    
    # CORRECCIÓN DE ALINEACIÓN (Soluciona el error de sus capturas 6, 7 y 8)
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0

    def layout_con_fondo(contenido_vista):
        return ft.Container(
            content=ft.Column(
                contenido_vista, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                alignment=ft.MainAxisAlignment.CENTER, 
                spacing=20
            ),
            expand=True,
            image_src=FONDO_PATH,
            # CORRECCIÓN DE IMAGEFIT: Usamos el string "cover" directamente para evitar fallos
            image_fit="cover", 
            alignment=ft.alignment.center,
        )

    def menu_principal():
        page.clean()
        page.add(layout_con_fondo([
            ft.Text(f"Bienvenido: {state['alumno']}", size=24, color="white", weight="bold"),
            ft.FilledButton("UNIDAD I", on_click=lambda _: mostrar_unidad("UNIDAD I"), width=320, height=50),
            ft.FilledButton("UNIDAD II", on_click=lambda _: mostrar_unidad("UNIDAD II"), width=320, height=50),
            ft.FilledButton("UNIDAD III", on_click=lambda _: mostrar_unidad("UNIDAD III"), width=320, height=50),
            ft.TextButton("Cerrar Sesión", on_click=lambda _: login_view(), style=ft.ButtonStyle(color="white"))
        ]))

    def lanzar_pregunta():
        page.clean()
        u = state["unidad"]
        if state["idx"] < len(preguntas[u]):
            p, opciones, correcta = preguntas[u][state["idx"]]
            random.shuffle(opciones)
            
            def validar(res):
                if res == correcta: state["puntos"] += 1
                state["idx"] += 1
                lanzar_pregunta()
                
            page.add(layout_con_fondo([
                ft.Text(f"Pregunta {state['idx']+1}", color="#a3e4d7", size=18),
                ft.Text(p, size=24, color="white", text_align="center", weight="w500"),
                *[ft.FilledButton(o, on_click=lambda e, o=o: validar(o), width=350, height=45) for o in opciones]
            ]))
        else:
            # Registro en la nube
            guardar_en_nube(state["alumno"], state["unidad"], state["puntos"])
            page.add(layout_con_fondo([
                ft.Text("Evaluación Finalizada", size=24, color="white"),
                ft.Text(f"Puntaje: {state['puntos']}/5", size=60, color="white", weight="bold"),
                ft.FilledButton("REGRESAR AL INICIO", on_click=lambda _: menu_principal(), width=250)
            ]))

    def mostrar_unidad(u):
        state.update({"unidad": u, "idx": 0, "puntos": 0})
        page.clean()
        page.add(layout_con_fondo([
            ft.Text(u, size=32, weight="bold", color="white"),
            ft.FilledButton("INICIAR EXAMEN", on_click=lambda _: lanzar_pregunta(), width=280, height=50),
            ft.TextButton("Volver", on_click=lambda _: menu_principal(), style=ft.ButtonStyle(color="white"))
        ]))

    def login_view():
        page.clean()
        datos = {"Admin": "1234"}
        if os.path.exists(EXCEL_PATH):
            try:
                wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
                sh = wb.active
                # Columna C: Nombre, Columna B: Cédula
                datos = {str(sh.cell(r, 3).value): str(sh.cell(r, 2).value) for r in range(2, 51) if sh.cell(r, 3).value}
            except: pass

        user_drop = ft.Dropdown(label="Estudiante", width=320, options=[ft.dropdown.Option(n) for n in datos.keys()])
        pass_field = ft.TextField(label="Cédula", password=True, width=320, can_reveal_password=True)

        def ingresar(e):
            if user_drop.value in datos and datos[user_drop.value] == pass_field.value:
                state["alumno"] = user_drop.value
                menu_principal()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Credenciales Incorrectas"))
                page.snack_bar.open = True
                page.update()

        page.add(layout_con_fondo([
            ft.Image(src=ICONO_PATH, width=120),
            ft.Text("PORTAL DE ACCESO UNERMB", size=28, weight="bold", color="white"),
            user_drop, pass_field, 
            ft.FilledButton("INGRESAR AL SISTEMA", on_click=ingresar, width=220, height=50)
        ]))

    login_view()

if __name__ == "__main__":
    # Configuración de despliegue web
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", port=8080)
