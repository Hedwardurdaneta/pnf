import flet as ft
import gspread
import openpyxl
import os
import random
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURACIÓN E INFRAESTRUCTURA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONDO_PATH = "assets/fondo_unermb.png"
EXCEL_LOCAL = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")

# --- 2. GESTIÓN DE GOOGLE SHEETS (PERSISTENCIA) ---
class SpreadsheetManager:
    def __init__(self):
        self.sheet = self._conectar()

    def _conectar(self):
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        try:
            if os.path.exists(CREDS_JSON):
                creds = Credentials.from_service_account_file(CREDS_JSON, scopes=scope)
                client = gspread.authorize(creds)
                return client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
        except Exception as e:
            print(f"Error conexión: {e}")
        return None

    def registrar(self, cedula, unidad, nota):
        if not self.sheet: return False
        try:
            col_cedulas = self.sheet.col_values(2) # Columna B
            ced_limpia = str(cedula).strip()
            if ced_limpia in col_cedulas:
                fila = col_cedulas.index(ced_limpia) + 1
                col_map = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}
                self.sheet.update_cell(fila, col_map.get(unidad), nota)
                return True
        except: return False

db_cloud = SpreadsheetManager()

# --- 3. CONTENIDO ACADÉMICO Y BANCO DE PREGUNTAS ---
CONTENIDO = {
    "UNIDAD I": {
        "material": {
            "Algoritmo": "Secuencia finita de instrucciones precisas para resolver un problema.",
            "IDE": "Entorno de Desarrollo Integrado que combina editor, compilador y depurador.",
            "Depuración": "Proceso de identificar, analizar y eliminar errores de software.",
            "Compilación": "Traducción del código fuente a código máquina.",
            "Software": "Parte lógica, programas y datos del sistema."
        },
        "preguntas": [
            ("¿Qué es un algoritmo?", ["Pasos lógicos", "Un virus", "Hardware"], "Pasos lógicos"),
            ("¿Qué significa IDE?", ["Entorno de Desarrollo", "Internet", "Disco"], "Entorno de Desarrollo"),
            ("¿La compilación traduce a?", ["Código máquina", "Texto", "Imagen"], "Código máquina"),
            ("¿Qué es depuración?", ["Corregir errores", "Borrar", "Instalar"], "Corregir errores"),
            ("¿Software es?", ["Parte lógica", "Teclado", "Cables"], "Parte lógica"),
            ("¿Qué es sintaxis?", ["Reglas de escritura", "Procesador", "Tecla"], "Reglas de escritura"),
            ("¿El hardware es?", ["Parte física", "Programa", "Dato"], "Parte física"),
            ("¿Un comentario lo lee el PC?", ["No", "Sí", "A veces"], "No"),
            ("¿Dónde reside la variable?", ["Memoria RAM", "Monitor", "Mouse"], "Memoria RAM"),
            ("¿Qué es código fuente?", ["Texto programado", "Electricidad", "Señal"], "Texto programado")
        ]
    },
    "UNIDAD II": {
        "material": {
            "int": "Tipo de dato para números enteros.",
            "float": "Tipo de dato para números reales con decimales.",
            "str": "Tipo de dato para cadenas de texto.",
            "bool": "Tipo lógico (True o False).",
            "Listas": "Colecciones ordenadas y mutables de elementos."
        },
        "preguntas": [
            ("¿Qué guarda 'int'?", ["Enteros", "Letras", "Fotos"], "Enteros"),
            ("¿Qué guarda 'float'?", ["Decimales", "Cadenas", "Listas"], "Decimales"),
            ("¿Qué es 'str'?", ["Texto", "Números", "Bucle"], "Texto"),
            ("¿Valores del 'bool'?", ["True/False", "1 al 10", "A y B"], "True/False"),
            ("¿Qué es una lista?", ["Colección de datos", "Variable simple", "Error"], "Colección de datos"),
            ("¿Símbolo de asignación?", ["=", "==", "+"], "="),
            ("¿Qué es 'if'?", ["Condicional", "Bucle", "Suma"], "Condicional"),
            ("¿Qué es 'while'?", ["Bucle condicional", "Salida", "Imagen"], "Bucle condicional"),
            ("¿Qué es 'for'?", ["Bucle iterativo", "Suma", "Texto"], "Bucle iterativo"),
            ("¿El símbolo '+' es?", ["Operador", "Variable", "Widget"], "Operador")
        ]
    },
    "UNIDAD III": {
        "material": {
            "Flet": "Framework para interfaces de usuario con Python.",
            "Widget": "Componente visual de la interfaz.",
            "Container": "Agrupador con propiedades de estilo.",
            "Evento": "Acción detectada por el sistema (ej. clic).",
            "UX": "Experiencia del usuario al usar la app."
        },
        "preguntas": [
            ("¿Qué es Flet?", ["Framework UI", "Base datos", "Virus"], "Framework UI"),
            ("¿Qué es un Widget?", ["Control visual", "Hardware", "Cable"], "Control visual"),
            ("¿Qué hace un Button?", ["Ejecuta acciones", "Nada", "Cierra"], "Ejecuta acciones"),
            ("¿Qué es un Container?", ["Agrupador con estilo", "Variable", "Lista"], "Agrupador con estilo"),
            ("¿Qué es un Label?", ["Texto estático", "Video", "Música"], "Texto estático"),
            ("¿Qué es un clic?", ["Un evento", "Un error", "Hardware"], "Un evento"),
            ("¿Qué es el Layout?", ["Organización visual", "Color", "Nombre"], "Organización visual"),
            ("¿Qué es un Entry?", ["Campo de entrada", "Salida", "Imagen"], "Campo de entrada"),
            ("¿Mainloop sirve para?", ["Mantener app viva", "Apagar", "Sumar"], "Mantener app viva"),
            ("¿UX significa?", ["Experiencia Usuario", "Unidad X", "Uso Extra"], "Experiencia Usuario")
        ]
    }
}

# --- 4. APLICACIÓN PRINCIPAL ---
def main(page: ft.Page):
    page.title = "Portal Educativo UNERMB - Ing. Hedwar Urdaneta"
    page.bgcolor = "#8babf1"
    page.padding = 0
    
    state = {"user": None, "cedula": None, "unidad": None, "puntos": 0, "idx": 0}

    def layout_centrado(controles):
        return ft.Stack([
            ft.Image(src=FONDO_PATH, width=page.width, height=page.height, fit=ft.ImageFit.COVER),
            ft.Container(
                content=ft.Column(controles if isinstance(controles, list) else [controles], 
                                horizontal_alignment="center", alignment="center", spacing=20),
                expand=True, alignment=ft.alignment.center,
                bgcolor="#CC000000" # Fondo semi-transparente para lectura
            )
        ], expand=True)

    def login():
        page.clean()
        usuarios = {"Admin": "1234"}
        if os.path.exists(EXCEL_LOCAL):
            try:
                wb = openpyxl.load_workbook(EXCEL_LOCAL, data_only=True)
                ws = wb.active
                for r in range(2, 60):
                    nom = ws.cell(r, 3).value # Columna C
                    ced = ws.cell(r, 2).value # Columna B
                    if nom: usuarios[str(nom)] = str(ced)
            except: pass

        dd = ft.Dropdown(label="Seleccione Estudiante", width=400, bgcolor="white", options=[ft.dropdown.Option(n) for n in usuarios.keys()])
        tf = ft.TextField(label="Cédula", password=True, width=400, bgcolor="white")

        def acceder(e):
            if dd.value in usuarios and usuarios[dd.value] == tf.value:
                state.update({"user": dd.value, "cedula": tf.value}); menu()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Credenciales Incorrectas")); page.snack_bar.open = True; page.update()

        page.add(layout_centrado([ft.Text("SISTEMA UNERMB", size=40, color="white", weight="bold"), dd, tf, 
                                  ft.ElevatedButton("INGRESAR", on_click=acceder, width=200)]))

    def menu():
        page.clean()
        page.add(layout_centrado([
            ft.Text(f"Bienvenido, {state['user']}", color="white", size=25),
            *[ft.ElevatedButton(u, on_click=lambda e, u=u: unidad(u), width=350, height=50) for u in CONTENIDO.keys()],
            ft.TextButton("Salir", on_click=lambda _: login(), style=ft.ButtonStyle(color="white"))
        ]))

    def unidad(u):
        state["unidad"] = u
        page.clean()
        items = [ft.ListTile(title=ft.Text(t, color="white"), on_click=lambda e, t=t: definicion(t)) for t in CONTENIDO[u]["material"].keys()]
        page.add(layout_centrado([
            ft.Text(u, color="white", size=30, weight="bold"),
            ft.Container(content=ft.Column(items, scroll="auto"), height=250, width=500, bgcolor="#55000000", padding=10),
            ft.ElevatedButton("INICIAR EVALUACIÓN", on_click=lambda _: start_ex(), bgcolor="green", color="white", width=300),
            ft.TextButton("Volver", on_click=lambda _: menu(), style=ft.ButtonStyle(color="white"))
        ]))

    def definicion(t):
        page.clean()
        page.add(layout_centrado([
            ft.Text(t, size=35, color="white", weight="bold"),
            ft.Text(CONTENIDO[state["unidad"]]["material"][t], size=22, color="white", text_align="center"),
            ft.ElevatedButton("ENTENDIDO", on_click=lambda _: unidad(state["unidad"]))
        ]))

    def start_ex():
        state.update({"idx": 0, "puntos": 0}); render_p()

    def render_p():
        page.clean()
        preguntas = CONTENIDO[state["unidad"]]["preguntas"]
        if state["idx"] < len(preguntas):
            p, opts, c = preguntas[state["idx"]]
            def validar(ans):
                if ans == c: state["puntos"] += 1
                state["idx"] += 1; render_p()
            page.add(layout_centrado([
                ft.Text(f"Pregunta {state['idx']+1}/10", color="white"),
                ft.Container(content=ft.Text(p, size=24, color="black", weight="bold"), bgcolor="white", padding=20, border_radius=10),
                *[ft.ElevatedButton(o, on_click=lambda e, o=o: validar(o), width=400) for o in opts]
            ]))
        else:
            finalizar()

    def finalizar():
        page.clean()
        pts = state["puntos"]
        page.add(layout_centrado([
            ft.Text("RESULTADO", size=30, color="white"),
            ft.Text(f"{pts}/10", size=100, color="yellow", weight="bold"),
            ft.Text("Sincronizando...", color="white", italic=True)
        ]))
        page.update()
        
        exito = db_cloud.registrar(state["cedula"], state["unidad"], pts)
        page.controls[0].controls[1].content.controls[2].value = "✅ Nota registrada con éxito" if exito else "⚠️ Error al conectar con Google Sheets"
        page.controls[0].controls[1].content.controls[2].color = "green" if exito else "red"
        page.add(ft.ElevatedButton("IR AL MENÚ", on_click=lambda _: menu(), width=250))
        page.update()

    login()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
