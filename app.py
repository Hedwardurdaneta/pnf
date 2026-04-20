import flet as ft
import gspread
import openpyxl
import os
from google.oauth2.service_account import Credentials

# --- [ CONFIGURACIÓN DE RUTAS Y ESTILO ] ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")
EXCEL_LOCAL = os.path.join(BASE_DIR, "Programacion.xlsx")
COLOR_FONDO = "#8babf1"
COLOR_BOTON = "#f0f4fa"
COLOR_TEXTO_BOTON = "#1976d2"

# --- [ CONTENIDO ACADÉMICO COMPLETO ] ---
CONTENIDO = {
    "UNIDAD I": {
        "Algoritmo": "Secuencia de pasos lógicos para resolver un problema.",
        "IDE": "Entorno de Desarrollo Integrado para escribir código.",
        "Depuración": "Proceso de identificar y corregir errores en el código.",
        "Compilación": "Traducción de código de alto nivel a lenguaje máquina.",
        "Sintaxis": "Reglas que definen cómo escribir instrucciones.",
        "Variable": "Espacio en memoria para almacenar un dato.",
        "Código Fuente": "Instrucciones escritas por el programador.",
        "Comentario": "Líneas ignoradas por el compilador para documentar.",
        "Hardware": "Componentes físicos del sistema informático.",
        "Software": "Programas y reglas lógicas del sistema."
    },
    "UNIDAD II": {
        "int": "Tipo de dato para números enteros.",
        "float": "Tipo de dato para números decimales.",
        "str": "Cadenas de texto o caracteres.",
        "bool": "Tipo lógico: True (Verdadero) o False (Falso).",
        "Lista": "Colección organizada de múltiples valores.",
        "Operador": "Símbolos para realizar operaciones (+, -, *, /).",
        "Asignación": "Guardar un valor en una variable usando '='.",
        "if": "Condicional que ejecuta código si se cumple algo.",
        "while": "Bucle que repite código mientras se cumpla una condición.",
        "for": "Bucle para repetir código un número fijo de veces."
    },
    "UNIDAD III": {
        "Flet": "Framework para crear interfaces con Python.",
        "Widget": "Componente visual básico (botón, imagen, etc.).",
        "Label": "Control para mostrar texto estático.",
        "Entry": "Campo de texto para entrada del usuario.",
        "Button": "Componente interactivo para ejecutar acciones.",
        "Container": "Agrupador de elementos con estilo.",
        "Evento": "Acción detectada como un clic o tecla pulsada.",
        "Layout": "Organización visual de los elementos.",
        "Mainloop": "Bucle que mantiene la app abierta e interactiva.",
        "Color": "Atributo para personalizar fondos y textos."
    }
}

PREGUNTAS = {
    "UNIDAD I": [
        ("¿Qué es un algoritmo?", ["Pasos lógicos", "Un virus", "Hardware"], "Pasos lógicos"),
        ("¿Qué significa IDE?", ["Entorno de Desarrollo", "Internet", "Disco"], "Entorno de Desarrollo"),
        ("¿Qué es la depuración?", ["Corregir errores", "Borrar archivos", "Instalar"], "Corregir errores"),
        ("¿Qué hace la compilación?", ["Traducir código", "Apagar PC", "Imprimir"], "Traducir código"),
        ("¿Qué es la sintaxis?", ["Reglas de escritura", "Un tipo de monitor", "Teclado"], "Reglas de escritura"),
        ("¿Dónde se guarda una variable?", ["Memoria", "Caja", "Papel"], "Memoria"),
        ("¿Qué es el código fuente?", ["Instrucciones", "Electricidad", "Agua"], "Instrucciones"),
        ("¿El compilador lee comentarios?", ["No", "Sí", "A veces"], "No"),
        ("¿Qué es el hardware?", ["Parte física", "Programas", "Internet"], "Parte física"),
        ("¿Qué es el software?", ["Parte lógica", "Cables", "Monitor"], "Parte lógica")
    ],
    "UNIDAD II": [
        ("¿Qué guarda un 'int'?", ["Enteros", "Letras", "Imágenes"], "Enteros"),
        ("¿Qué guarda un 'float'?", ["Decimales", "Cadenas", "Enteros"], "Decimales"),
        ("¿Qué es un 'str'?", ["Texto", "Números", "Bucle"], "Texto"),
        ("¿Valores del 'bool'?", ["True/False", "1/100", "A/B"], "True/False"),
        ("¿Qué es una lista?", ["Colección", "Una sola variable", "Un error"], "Colección"),
        ("¿Qué es '+'?", ["Operador", "Variable", "Widget"], "Operador"),
        ("¿Símbolo de asignación?", ["=", "==", "+"], "="),
        ("¿Qué es 'if'?", ["Condicional", "Bucle", "Variable"], "Condicional"),
        ("¿Qué es 'while'?", ["Bucle", "Condición única", "Salida"], "Bucle"),
        ("¿Qué es 'for'?", ["Bucle repetitivo", "Suma", "Texto"], "Bucle repetitivo")
    ],
    "UNIDAD III": [
        ("¿Para qué sirve Flet?", ["Interfaces", "Hacer café", "Base de datos"], "Interfaces"),
        ("¿Qué es un Widget?", ["Componente visual", "Cable", "Virus"], "Componente visual"),
        ("¿Qué muestra un Label?", ["Texto", "Video", "Música"], "Texto"),
        ("¿Qué es un Entry?", ["Entrada de texto", "Salida", "Imagen"], "Entrada de texto"),
        ("¿Qué hace un Button?", ["Ejecuta acción", "Nada", "Cierra todo"], "Ejecuta acción"),
        ("¿Qué es un Container?", ["Agrupador", "Variable", "Lista"], "Agrupador"),
        ("¿Qué es un clic?", ["Evento", "Error", "Hardware"], "Evento"),
        ("¿Qué es el Layout?", ["Organización", "Color", "Nombre"], "Organización"),
        ("¿Qué es el Mainloop?", ["Bucle de la app", "Un cable", "Un botón"], "Bucle de la app"),
        ("¿El color es un atributo?", ["Sí", "No", "Solo en web"], "Sí")
    ]
}

# --- [ MOTOR DE NUBE ] ---
class CloudService:
    def __init__(self):
        self.sheet = self._connect()

    def _connect(self):
        try:
            if os.path.exists(CREDS_JSON):
                scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                creds = Credentials.from_service_account_file(CREDS_JSON, scopes=scopes)
                return gspread.authorize(creds).open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
        except: return None

    def update_nota(self, cedula, unidad, nota):
        if not self.sheet: return False
        try:
            ceds = self.sheet.col_values(2)
            if str(cedula) in ceds:
                row = ceds.index(str(cedula)) + 1
                col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad, 4)
                self.sheet.update_cell(row, col, nota)
                return True
        except: return False

# --- [ APLICACIÓN FLET ] ---
def main(page: ft.Page):
    page.title = "SISTEMA ACADÉMICO UNERMB"
    page.bgcolor = COLOR_FONDO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    
    cloud = CloudService()
    state = {"name": "", "id": "", "unit": "", "pts": 0, "idx": 0}

    def navigate(func):
        page.clean()
        func()
        page.update()

    def view_login():
        students = {}
        if os.path.exists(EXCEL_LOCAL):
            wb = openpyxl.load_workbook(EXCEL_LOCAL, data_only=True)
            ws = wb.active
            for r in range(2, 100):
                c, n = ws.cell(r, 2).value, ws.cell(r, 3).value
                if n: students[str(n)] = str(c)

        dd = ft.Dropdown(label="Seleccione su Nombre", width=400, bgcolor="white",
                         options=[ft.dropdown.Option(s) for s in students.keys()])
        tf = ft.TextField(label="Cédula", password=True, width=400, bgcolor="white")

        def do_login(e):
            if dd.value and students.get(dd.value) == tf.value:
                state["name"], state["id"] = dd.value, tf.value
                navigate(view_menu)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Credenciales Incorrectas"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        page.add(
            ft.Text("INGENIERÍA DE SOFTWARE II", size=30, weight="bold", color="white"),
            ft.Container(height=20),
            ft.Container(content=ft.Column([dd, tf, ft.ElevatedButton("ENTRAR", on_click=do_login, width=200)],
                                          horizontal_alignment="center"), 
                         padding=40, bgcolor="#33ffffff", border_radius=20)
        )

    def view_menu():
        page.add(
            ft.Text(f"Bienvenido: {state['name']}", size=20, color="white"),
            ft.Divider(color="white"),
            *[ft.ElevatedButton(u, on_click=lambda e, x=u: start_unit(x), width=350, height=55) for u in CONTENIDO.keys()],
            ft.TextButton("Cerrar Sesión", on_click=lambda _: navigate(view_login), style=ft.ButtonStyle(color="white"))
        )

    def start_unit(u):
        state["unit"] = u
        navigate(view_study)

    def view_study():
        items = [ft.ListTile(title=ft.Text(k, weight="bold"), subtitle=ft.Text(v)) for k, v in CONTENIDO[state["unit"]].items()]
        page.add(
            ft.Text(f"MATERIAL: {state['unit']}", size=24, color="white", weight="bold"),
            ft.Container(content=ft.Column(items, scroll=ft.ScrollMode.ALWAYS, height=400), bgcolor="white", padding=15, border_radius=10, width=600),
            ft.Row([
                ft.ElevatedButton("EXAMEN", on_click=lambda _: start_exam(), bgcolor="green", color="white"),
                ft.ElevatedButton("VOLVER", on_click=lambda _: navigate(view_menu))
            ], alignment="center")
        )

    def start_exam():
        state["pts"], state["idx"] = 0, 0
        navigate(view_exam)

    def view_exam():
        bank = PREGUNTAS[state["unit"]]
        if state["idx"] < 10:
            q, opts, ans = bank[state["idx"]]
            def check(pick):
                if pick == ans: state["pts"] += 1
                state["idx"] += 1
                navigate(view_exam)
            
            page.add(
                ft.Text(f"Pregunta {state['idx']+1} de 10", color="white"),
                ft.Container(content=ft.Text(q, size=22, weight="bold", text_align="center"), padding=35, bgcolor="white", border_radius=15, width=650),
                *[ft.ElevatedButton(o, on_click=lambda e, x=o: check(x), width=450, height=50, 
                                   style=ft.ButtonStyle(bgcolor=COLOR_BOTON, color=COLOR_TEXTO_BOTON)) for o in opts]
            )
        else:
            navigate(view_result)

    def view_result():
        page.add(ft.ProgressRing(), ft.Text("Guardando nota...", color="white"))
        page.update()
        success = cloud.update_nota(state["id"], state["unit"], state["pts"])
        page.clean()
        page.add(
            ft.Text("EVALUACIÓN FINALIZADA", size=28, color="white", weight="bold"),
            ft.Text(f"{state['pts']}/10", size=110, color="yellow", weight="bold"),
            ft.Row([ft.Icon(ft.icons.CLOUD_DONE if success else ft.icons.CLOUD_OFF, color="white"),
                    ft.Text("Sincronizado" if success else "Error de conexión", color="white")], alignment="center"),
            ft.ElevatedButton("REGRESAR AL MENÚ", on_click=lambda _: navigate(view_menu), width=300)
        )

    view_login()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=int(os.getenv("PORT", 8080)), host="0.0.0.0")
