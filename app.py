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
EXCEL_LOCAL = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")

# --- 2. CONEXIÓN A GOOGLE SHEETS ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    if os.path.exists(CREDS_JSON):
        creds = Credentials.from_service_account_file(CREDS_JSON, scopes=scope)
        client = gspread.authorize(creds)
        sheet_google = client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
    else:
        sheet_google = None
except Exception as e:
    sheet_google = None
    print(f"Error de conexión: {e}")

# --- 3. CONTENIDO ACADÉMICO COMPLETO ---
contenido_unermb = {
    "UNIDAD I": {
        "Algoritmo": "Secuencia finita de instrucciones precisas para resolver un problema.",
        "IDE": "Entorno de Desarrollo Integrado que combina editor, compilador y depurador.",
        "Depuración": "Proceso de identificar, analizar y eliminar errores de software.",
        "Compilación": "Traducción del código fuente a código máquina (binario).",
        "Sintaxis": "Reglas gramaticales que rigen la escritura del código.",
        "Variable": "Espacio reservado en la memoria RAM con un nombre simbólico.",
        "Código Fuente": "Líneas de texto escritas en un lenguaje de programación.",
        "Comentario": "Anotaciones para humanos que el compilador ignora.",
        "Hardware": "Componentes físicos y electrónicos del computador.",
        "Software": "Programas y datos que permiten el funcionamiento del sistema."
    },
    "UNIDAD II": {
        "int": "Tipo de dato para números enteros positivos o negativos.",
        "float": "Tipo de dato para números reales con decimales.",
        "str": "Tipo de dato para cadenas de caracteres o texto.",
        "bool": "Tipo lógico que representa valores True o False.",
        "Lista": "Colección ordenada y mutable de elementos en Python.",
        "Operador": "Símbolo que realiza cálculos o comparaciones.",
        "Asignación": "Operación de guardar un valor en una variable usando '='.",
        "if": "Estructura condicional que bifurca el flujo del programa.",
        "while": "Estructura de repetición basada en una condición.",
        "for": "Estructura que itera sobre una secuencia o rango."
    },
    "UNIDAD III": {
        "Flet": "Framework basado en Flutter para crear interfaces con Python.",
        "Widget": "Componente básico de la interfaz (botones, textos).",
        "Label": "Control especializado en mostrar texto estático.",
        "Entry": "Campo de entrada de datos (TextField) para el usuario.",
        "Button": "Componente que dispara eventos al ser presionado.",
        "Container": "Elemento de diseño para agrupar y dar estilo a otros widgets.",
        "Evento": "Señal que indica una acción (clic, cambio de texto).",
        "Layout": "Organización visual de los componentes en la app.",
        "Mainloop": "Ciclo de vida que mantiene la app respondiendo.",
        "UX": "Experiencia de usuario: cómo interactúa el alumno con el sistema."
    }
}

# --- 4. BANCO DE EVALUACIÓN (30 PREGUNTAS) ---
banco_evaluacion = {
    "UNIDAD I": [
        ("¿Qué es un algoritmo?", ["Pasos lógicos", "Un virus", "Hardware"], "Pasos lógicos"),
        ("¿Qué es un IDE?", ["Entorno de Desarrollo", "Internet", "Disco"], "Entorno de Desarrollo"),
        ("¿Qué es depuración?", ["Corregir errores", "Borrar todo", "Instalar"], "Corregir errores"),
        ("¿Qué hace la compilación?", ["Traduce código", "Apaga PC", "Limpia"], "Traduce código"),
        ("¿Qué es sintaxis?", ["Reglas de escritura", "Procesador", "Teclado"], "Reglas de escritura"),
        ("¿Dónde vive la variable?", ["Memoria RAM", "Monitor", "Mouse"], "Memoria RAM"),
        ("¿Qué es código fuente?", ["Texto programado", "Electricidad", "Cable"], "Texto programado"),
        ("¿El compilador lee comentarios?", ["No", "Sí", "A veces"], "No"),
        ("¿Qué es hardware?", ["Parte física", "Programas", "Datos"], "Parte física"),
        ("¿Qué es software?", ["Parte lógica", "Teclado", "Cables"], "Parte lógica")
    ],
    "UNIDAD II": [
        ("¿Qué guarda 'int'?", ["Enteros", "Letras", "Fotos"], "Enteros"),
        ("¿Qué guarda 'float'?", ["Decimales", "Texto", "Listas"], "Decimales"),
        ("¿Qué es 'str'?", ["Texto", "Números", "Bucle"], "Texto"),
        ("¿Valores de 'bool'?", ["True/False", "1 a 10", "A/B"], "True/False"),
        ("¿Qué es una lista?", ["Colección de datos", "Variable simple", "Error"], "Colección de datos"),
        ("¿Símbolo de suma?", ["+", "*", "/"], "+"),
        ("¿Símbolo asignación?", ["=", "==", "!"], "="),
        ("¿Qué es 'if'?", ["Condicional", "Bucle", "Suma"], "Condicional"),
        ("¿Qué es 'while'?", ["Bucle condicional", "Salida", "Imagen"], "Bucle condicional"),
        ("¿Qué es 'for'?", ["Bucle iterativo", "Suma", "Texto"], "Bucle iterativo")
    ],
    "UNIDAD III": [
        ("¿Qué es Flet?", ["Framework UI", "Base datos", "Virus"], "Framework UI"),
        ("¿Qué es un Widget?", ["Control visual", "Hardware", "Cable"], "Control visual"),
        ("¿Qué es un Label?", ["Texto estático", "Video", "Música"], "Texto estático"),
        ("¿Qué es un Entry?", ["Entrada texto", "Salida", "Botón"], "Entrada texto"),
        ("¿Qué hace un Button?", ["Acciones", "Nada", "Cierra"], "Acciones"),
        ("¿Qué es Container?", ["Agrupador", "Variable", "Lista"], "Agrupador"),
        ("¿Qué es un clic?", ["Evento", "Error", "Hardware"], "Evento"),
        ("¿Qué es Layout?", ["Organización", "Color", "Nombre"], "Organización"),
        ("¿Qué es Mainloop?", ["Ciclo de app", "Cable", "Icono"], "Ciclo de app"),
        ("¿UX es experiencia?", ["Sí", "No", "Tal vez"], "Sí")
    ]
}

# --- 5. LÓGICA DE INTERFAZ ---
def main(page: ft.Page):
    page.title = "Portal UNERMB - Ing. Hedwar Urdaneta"
    page.padding = 0
    state = {"user": None, "cedula": None, "unidad": None, "puntos": 0, "idx": 0}

    def registrar_nota(nota):
        if not sheet_google: return False
        try:
            lista_c = sheet_google.col_values(2) # Columna B
            ced = str(state["cedula"]).strip()
            if ced in lista_c:
                f = lista_c.index(ced) + 1
                col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(state["unidad"])
                sheet_google.update_cell(f, col, nota)
                return True
            return False
        except: return False

    def layout_centrado(controles):
        return ft.Stack([
            ft.Image(src=FONDO_PATH, width=page.width, height=page.height, fit=ft.ImageFit.COVER),
            ft.Container(
                content=ft.Column(controles if isinstance(controles, list) else [controles], 
                                horizontal_alignment="center", alignment="center", spacing=20),
                expand=True, alignment=ft.alignment.center,
                gradient=ft.LinearGradient(colors=[ft.colors.with_opacity(0.7, "black"), ft.colors.with_opacity(0.4, "black")])
            )
        ], expand=True)

    def login():
        page.clean()
        db = {"Admin": "1234"}
        if os.path.exists(EXCEL_LOCAL):
            try:
                wb = openpyxl.load_workbook(EXCEL_LOCAL, data_only=True)
                ws = wb.active
                for r in range(2, 60):
                    if ws.cell(r, 3).value: db[str(ws.cell(r, 3).value)] = str(ws.cell(r, 2).value)
            except: pass
        
        d_u = ft.Dropdown(label="Estudiante", width=400, bgcolor="white", options=[ft.dropdown.Option(n) for n in db.keys()])
        t_c = ft.TextField(label="Cédula", password=True, width=400, bgcolor="white")

        def entrar(e):
            if d_u.value in db and db[d_u.value] == t_c.value:
                state.update({"user": d_u.value, "cedula": t_c.value}); menu()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Datos incorrectos")); page.snack_bar.open = True; page.update()

        page.add(layout_centrado([ft.Text("PORTAL UNERMB", size=40, color="white", weight="bold"), d_u, t_c, 
                                  ft.ElevatedButton("INGRESAR", on_click=entrar, width=200)]))

    def menu():
        page.clean()
        page.add(layout_centrado([
            ft.Text(f"Bienvenido: {state['user']}", color="white", size=25),
            *[ft.ElevatedButton(u, on_click=lambda e, u=u: unidad(u), width=300, height=50) for u in ["UNIDAD I", "UNIDAD II", "UNIDAD III"]],
            ft.TextButton("Cerrar Sesión", on_click=lambda _: login(), style=ft.ButtonStyle(color="white"))
        ]))

    def unidad(u):
        state["unidad"] = u
        page.clean()
        items = [ft.ListTile(title=ft.Text(t, color="white"), on_click=lambda e, t=t: definicion(t)) for t in contenido_unermb[u].keys()]
        page.add(layout_centrado([
            ft.Text(u, color="white", size=30, weight="bold"),
            ft.Container(content=ft.Column(items, scroll="auto"), height=300, width=500, bgcolor="#88000000", border_radius=15, padding=10),
            ft.ElevatedButton("INICIAR EXAMEN", on_click=lambda _: start_ex(), bgcolor="green", color="white", width=250),
            ft.TextButton("Volver", on_click=lambda _: menu(), style=ft.ButtonStyle(color="white"))
        ]))

    def definicion(t):
        page.clean()
        page.add(layout_centrado([
            ft.Container(content=ft.Column([
                ft.Text(t, size=30, color="white", weight="bold"),
                ft.Text(contenido_unermb[state["unidad"]][t], size=20, color="white", text_align="center"),
                ft.ElevatedButton("VOLVER", on_click=lambda _: unidad(state["unidad"]))
            ], horizontal_alignment="center"), bgcolor="#aa000000", padding=30, border_radius=20, width=500)
        ]))

    def start_ex():
        state.update({"idx": 0, "puntos": 0}); render_p()

    def render_p():
        page.clean()
        b = banco_evaluacion[state["unidad"]]
        if state["idx"] < len(b):
            p, opts, c = b[state["idx"]]
            def val(ans):
                if ans == c: state["puntos"] += 1
                state["idx"] += 1; render_p()
            page.add(layout_centrado([
                ft.Text(f"Pregunta {state['idx']+1}/10", color="white"),
                ft.Container(content=ft.Text(p, size=24, color="black", weight="bold", text_align="center"), bgcolor="white", padding=20, border_radius=10, width=600),
                *[ft.ElevatedButton(o, on_click=lambda e, o=o: val(o), width=400) for o in opts]
            ]))
        else:
            finalizar()

    def finalizar():
        page.clean()
        page.update()
        pts = state["puntos"]
        res = ft.Column([ft.Text("RESULTADO", size=30, color="white"),
                         ft.Text(f"{pts}/10", size=90, color="yellow", weight="bold"),
                         ft.Text("Guardando...", color="white", italic=True)], horizontal_alignment="center")
        page.add(layout_centrado(res))
        page.update()
        
        exito = registrar_nota(pts)
        res.controls[2].value = "✅ Nota registrada en Google Sheets" if exito else "⚠️ Error al guardar en la nube"
        res.controls[2].color = "green" if exito else "red"
        page.add(ft.ElevatedButton("MENU PRINCIPAL", on_click=lambda _: menu(), width=250))
        page.update()

    login()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
