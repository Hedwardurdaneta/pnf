import flet as ft
import gspread
import openpyxl
import os
import random
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURACIÓN DE RUTAS Y API ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
# El archivo credentials.json debe estar en la raíz del proyecto
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)
except Exception as e:
    print(f"Error inicializando Google Sheets: {e}")

# --- 2. ESTADO GLOBAL ---
state = {"alumno": None, "cedula": None, "unidad": None, "idx": 0, "puntos": 0}

# --- 3. BANCO DE DATOS ---
contenido = {
    "UNIDAD I": {
        "Algoritmo": "Secuencia de pasos lógicos para resolver un problema.",
        "IDE": "Entorno de Desarrollo Integrado para escribir código.",
        "Depuración": "Proceso de identificar y corregir errores en el código."
    },
    "UNIDAD II": {
        "int": "Tipo de dato para números enteros.",
        "float": "Tipo de dato para números decimales.",
        "str": "Cadenas de texto o caracteres."
    },
    "UNIDAD III": {
        "Flet": "Framework para crear interfaces con Python.",
        "Widget": "Componente visual básico (botón, imagen, etc.).",
        "Container": "Agrupador de elementos con estilo."
    }
}

preguntas = {
    "UNIDAD I": [
        ("¿Qué es un algoritmo?", ["Pasos lógicos", "Un virus", "Hardware"], "Pasos lógicos"),
        ("¿Qué significa IDE?", ["Entorno de Desarrollo", "Internet", "Disco"], "Entorno de Desarrollo")
    ],
    "UNIDAD II": [
        ("¿Qué guarda un 'int'?", ["Enteros", "Letras", "Imágenes"], "Enteros"),
        ("¿Qué guarda un 'float'?", ["Decimales", "Cadenas", "Enteros"], "Decimales")
    ],
    "UNIDAD III": [
        ("¿Para qué sirve Flet?", ["Interfaces", "Hacer café", "Base de datos"], "Interfaces"),
        ("¿Qué es un Widget?", ["Componente visual", "Cable", "Virus"], "Componente visual")
    ]
}

# --- 4. FUNCIONES DE PERSISTENCIA ---
def registrar_nota_google(cedula, unidad, nota):
    try:
        hoja_maestra = client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
        celda = hoja_maestra.find(str(cedula))
        fila = celda.row
        columna = 4 if unidad == "UNIDAD I" else 5 if unidad == "UNIDAD II" else 6
        hoja_maestra.update_cell(fila, columna, nota)
        print(f"✅ Nota {nota} sincronizada en la nube.")
    except Exception as e:
        print(f"❌ Error Google Sheets: {e}")

def guardar_datos_local(nombre_alumno, unidad, puntos):
    if os.path.exists(EXCEL_PATH):
        try:
            wb = openpyxl.load_workbook(EXCEL_PATH)
            sheet = wb.active
            col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
            for i in range(2, 51):
                if str(sheet.cell(row=i, column=3).value) == nombre_alumno:
                    sheet.cell(row=i, column=col).value = puntos
                    break
            wb.save(EXCEL_PATH)
        except: pass

# --- 5. INTERFAZ ---
def main(page: ft.Page):
    page.title = "Portal Educativo UNERMB"
    
    def layout_con_fondo(contenido_vista):
        return ft.Container(
            content=ft.Column(contenido_vista, horizontal_alignment="center", alignment="center", spacing=20),
            expand=True, bgcolor="#F0F2F5", padding=40
        )

    def menu_principal():
        page.clean()
        page.add(layout_con_fondo([
            ft.Text(f"Bienvenido: {state['alumno']}", size=28, weight="bold"),
            *[ft.FilledButton(u, on_click=lambda e, u=u: mostrar_unidad(u), width=320) for u in ["UNIDAD I", "UNIDAD II", "UNIDAD III"]],
            ft.TextButton("Cerrar Sesión", on_click=lambda _: login_view())
        ]))

    def lanzar_pregunta():
        page.clean()
        u = state["unidad"]
        if state["idx"] < len(preguntas[u]):
            p, opciones_orig, correcta = preguntas[u][state["idx"]]
            opciones = list(opciones_orig)
            random.shuffle(opciones)

            def validar(res):
                if res == correcta: state["puntos"] += 1
                state["idx"] += 1
                lanzar_pregunta()

            page.add(layout_con_fondo([
                ft.Text(f"Pregunta {state['idx']+1}", size=18),
                ft.Text(p, size=26, text_align="center"),
                *[ft.FilledButton(o, on_click=lambda e, o=o: validar(o), width=350) for o in opciones]
            ]))
        else:
            # GUARDADO AUTOMÁTICO EN AMBOS SITIOS
            guardar_datos_local(state["alumno"], state["unidad"], state["puntos"])
            registrar_nota_google(state["cedula"], state["unidad"], state["puntos"])
            
            page.add(layout_con_fondo([
                ft.Text("Evaluación Finalizada", size=24),
                ft.Text(f"Nota Final: {state['puntos']}/10", size=80, weight="bold"),
                ft.FilledButton("VOLVER AL MENÚ", on_click=lambda _: menu_principal())
            ]))
        page.update()

    def mostrar_unidad(u):
        state["unidad"], state["idx"], state["puntos"] = u, 0, 0
        page.clean()
        temas = [ft.ListTile(title=ft.Text(t), on_click=lambda e, t=t: mostrar_def(t)) for t in contenido[u].keys()]
        page.add(layout_con_fondo([
            ft.Text(u, size=30, weight="bold"),
            ft.Container(content=ft.Column(temas, scroll="auto"), height=300, width=420, bgcolor="#DEE2E6", border_radius=15),
            ft.FilledButton("📝 INICIAR EVALUACIÓN", on_click=lambda _: lanzar_pregunta(), width=280),
            ft.TextButton("Volver", on_click=lambda _: menu_principal())
        ]))

    def mostrar_def(t):
        page.clean()
        def_texto = contenido[state["unidad"]].get(t, "Sin definición")
        page.add(layout_con_fondo([
            ft.Text(t, size=35, weight="bold"),
            ft.Text(def_texto, size=22, text_align="center"),
            ft.FilledButton("VOLVER", on_click=lambda _: mostrar_unidad(state["unidad"]))
        ]))

    def login_view():
        page.clean()
        datos = {"Admin": "1234"}
        if os.path.exists(EXCEL_PATH):
            try:
                wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
                sh = wb.active
                datos = {str(sh.cell(r, 3).value): str(sh.cell(r, 2).value) for r in range(2, 51) if sh.cell(r, 3).value}
            except: pass

        user_drop = ft.Dropdown(label="Estudiante", width=320, options=[ft.dropdown.Option(n) for n in datos.keys()])
        pass_field = ft.TextField(label="Cédula", password=True, width=320, can_reveal_password=True)

        def ingresar(e):
            if user_drop.value in datos and datos[user_drop.value] == pass_field.value:
                state["alumno"] = user_drop.value
                state["cedula"] = pass_field.value
                menu_principal()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Datos incorrectos"))
                page.snack_bar.open = True
                page.update()

        page.add(layout_con_fondo([
            ft.Text("PORTAL UNERMB", size=36, weight="bold"),
            user_drop, pass_field, 
            ft.FilledButton("INGRESAR", on_click=ingresar, width=220, height=50)
        ]))
        page.update()

    login_view()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=int(os.getenv("PORT", 8080)))
