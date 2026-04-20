import flet as ft
import gspread
import openpyxl
import os
import time
from google.oauth2.service_account import Credentials

# --- [ CONFIGURACIÓN Y RUTAS ] ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")
EXCEL_LOCAL = os.path.join(BASE_DIR, "Programacion.xlsx")

# --- [ BANCO DE DATOS SUMINISTRADO ] ---
CONTENIDO_PEDAGOGICO = {
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

PREGUNTAS_BANCO = {
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
class GoogleService:
    def __init__(self):
        self.sheet = self._auth()

    def _auth(self):
        try:
            if os.path.exists(CREDS_JSON):
                scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                creds = Credentials.from_service_account_file(CREDS_JSON, scopes=scope)
                client = gspread.authorize(creds)
                return client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
        except: return None

    def upload_grade(self, cedula, unidad, nota):
        if not self.sheet: return False
        try:
            ceds = self.sheet.col_values(2)
            if str(cedula) in ceds:
                row = ceds.index(str(cedula)) + 1
                col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad, 4)
                self.sheet.update_cell(row, col, nota)
                return True
        except: return False

# --- [ INTERFAZ FLET ] ---
def main(page: ft.Page):
    page.title = "PORTAL UNERMB - INGENIERÍA DE SOFTWARE"
    page.bgcolor = "#8babf1"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    
    cloud = GoogleService()
    state = {"user": "", "id": "", "unit": "", "pts": 0, "idx": 0}

    def go_login(e=None):
        page.clean()
        alumnos = {}
        if os.path.exists(EXCEL_LOCAL):
            try:
                wb = openpyxl.load_workbook(EXCEL_LOCAL, data_only=True)
                ws = wb.active
                for r in range(2, 80):
                    c, n = ws.cell(r, 2).value, ws.cell(r, 3).value
                    if n: alumnos[str(n)] = str(c)
            except: pass

        dd = ft.Dropdown(label="Seleccione su Nombre", width=450, bgcolor="white",
                         options=[ft.dropdown.Option(a) for a in alumnos.keys()])
        tf = ft.TextField(label="Cédula", password=True, width=450, bgcolor="white")

        def login_verify(e):
            if dd.value and alumnos.get(dd.value) == tf.value:
                state["user"], state["id"] = dd.value, tf.value
                go_menu()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Datos Incorrectos"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        page.add(
            ft.Container(height=40),
            ft.Text("INGENIERÍA DE SOFTWARE II", size=32, weight="bold", color="#1a237e"),
            ft.Container(
                content=ft.Column([dd, tf, ft.ElevatedButton("ACCEDER", on_click=login_verify, width=250, height=50)],
                                  horizontal_alignment="center"),
                padding=40, bgcolor="#33ffffff", border_radius=20
            )
        )

    def go_menu():
        page.clean()
        btns = [ft.ElevatedButton(k, on_click=lambda e, k=k: go_study(k), width=380, height=60) 
                for k in CONTENIDO_PEDAGOGICO.keys()]
        page.add(
            ft.Text(f"Bienvenido: {state['user']}", size=22, weight="bold"),
            ft.Divider(color="#1a237e"),
            *btns,
            ft.TextButton("Cerrar Sesión", on_click=go_login)
        )

    def go_study(unit):
        state["unit"] = unit
        page.clean()
        info = CONTENIDO_PEDAGOGICO[unit]
        items = [ft.ListTile(title=ft.Text(k, weight="bold"), subtitle=ft.Text(v)) for k, v in info.items()]
        
        page.add(
            ft.Text(f"MATERIAL: {unit}", size=26, weight="bold"),
            ft.Container(content=ft.Column(items, scroll=ft.ScrollMode.ALWAYS), height=400, bgcolor="white", border_radius=10, padding=10),
            ft.Row([
                ft.ElevatedButton("INICIAR EXAMEN", on_click=lambda _: start_exam(), bgcolor="green", color="white", width=200),
                ft.ElevatedButton("VOLVER", on_click=lambda _: go_menu(), width=200)
            ], alignment="center")
        )

    def start_exam():
        state["pts"] = 0
        state["idx"] = 0
        render_exam()

    def render_exam():
        page.clean()
        bank = PREGUNTAS_BANCO[state["unit"]]
        if state["idx"] < 10:
            q, opts, ans = bank[state["idx"]]
            
            def check(pick):
                if pick == ans: state["pts"] += 1
                state["idx"] += 1
                render_exam()

            page.add(
                ft.Text(f"Pregunta {state['idx']+1} de 10", size=18),
                ft.Container(
                    content=ft.Text(q, size=24, weight="bold", text_align="center"),
                    padding=30, bgcolor="white", border_radius=15, width=600
                ),
                *[ft.ElevatedButton(o, on_click=lambda e, o=o: check(o), width=450, height=50) for o in opts]
            )
        else:
            show_result()

    def show_result():
        page.clean()
        loading = ft.ProgressRing(color="#1a237e")
        status_txt = ft.Text("Guardando nota en la nube...", size=16)
        page.add(ft.Container(height=100), loading, status_txt)
        page.update()
        
        # Subida a Google Sheets
        success = cloud.upload_grade(state["id"], state["unit"], state["pts"])
        
        page.clean()
        # Interfaz de resultado según capturas (image_ce9446.png)
        page.add(
            ft.Text("RESULTADO FINAL", size=35, weight="bold", color="white"),
            ft.Text(f"{state['pts']}/10", size=110, weight="bold", color="yellow"),
            ft.Row([
                ft.Icon(ft.icons.CLOUD_DONE if success else ft.icons.CLOUD_OFF, color="green" if success else "red"),
                ft.Text("Nota sincronizada" if success else "Error de conexión con la nube", 
                        color="green" if success else "red", size=18)
            ], alignment="center"),
            ft.Container(height=20),
            ft.ElevatedButton("REGRESAR AL MENÚ", on_click=lambda _: go_menu(), width=300, height=50)
        )

    go_login()

if __name__ == "__main__":
    # Configuración para Render (Uso de puerto dinámico)
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port, host="0.0.0.0")
