import flet as ft
import gspread
import openpyxl
import os
import random
import asyncio
import json
from google.oauth2.service_account import Credentials

# --- [ CONFIGURACIÓN ] ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")
EXCEL_LOCAL = os.path.join(BASE_DIR, "Programacion.xlsx")
COLOR_FONDO = "#0c6980"
COLOR_BOTON = "#f0f4fa"
COLOR_TEXTO_BOTON = "#1976d2"

# ... [CONTENIDO y PREGUNTAS se mantienen igual] ...

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
        ("¿Qué es la sintaxis?", ["Reglas de escritura", "Teclado", "Monitor"], "Reglas de escritura"),
        ("¿Dónde se guarda una variable?", ["Memoria", "Caja", "Papel"], "Memoria"),
        ("¿Qué es el código fuente?", ["Instrucciones", "Electricidad", "Agua"], "Instrucciones"),
        ("¿El compilador lee comentarios?", ["No", "Sí", "A veces"], "No"),
        ("¿Qué es el hardware?", ["Parte física", "Programas", "Internet"], "Parte física"),
        ("¿Qué es el software?", ["Parte lógica", "Monitor", "Cables"], "Parte lógica")
    ],
    "UNIDAD II": [
        ("¿Qué guarda un 'int'?", ["Enteros", "Letras", "Imágenes"], "Enteros"),
        ("¿Qué guarda un 'float'?", ["Decimales", "Cadenas", "Enteros"], "Decimales"),
        ("¿Qué es un 'str'?", ["Texto", "Números", "Bucle"], "Texto"),
        ("¿Valores del 'bool'?", ["True/False", "A/B", "1/100"], "True/False"),
        ("¿Qué es una lista?", ["Colección", "Variable única", "Error"], "Colección"),
        ("¿Qué es '+'?", ["Operador", "Variable", "Widget"], "Operador"),
        ("¿Símbolo de asignación?", ["=", "==", "+"], "="),
        ("¿Qué es 'if'?", ["Condicional", "Bucle", "Variable"], "Condicional"),
        ("¿Qué es 'while'?", ["Bucle", "Salida", "Suma"], "Bucle"),
        ("¿Qué es 'for'?", ["Bucle repetitivo", "Suma", "Texto"], "Bucle repetitivo")
    ],
    "UNIDAD III": [
        ("¿Para qué sirve Flet?", ["Interfaces", "Hardware", "Café"], "Interfaces"),
        ("¿Qué es un Widget?", ["Componente visual", "Cable", "Virus"], "Componente visual"),
        ("¿Qué muestra un Label?", ["Texto", "Video", "Música"], "Texto"),
        ("¿Qué es un Entry?", ["Entrada de texto", "Salida", "Imagen"], "Entrada de texto"),
        ("¿Qué hace un Button?", ["Ejecuta acción", "Nada", "Cierra"], "Ejecuta acción"),
        ("¿Qué es un Container?", ["Agrupador", "Variable", "Lista"], "Agrupador"),
        ("¿Qué es un clic?", ["Evento", "Error", "Hardware"], "Evento"),
        ("¿Qué es el Layout?", ["Organización", "Color", "Nombre"], "Organización"),
        ("¿Qué es el Mainloop?", ["Bucle de la app", "Cable", "Botón"], "Bucle de la app"),
        ("¿El color es un atributo?", ["Sí", "No", "Solo web"], "Sí")
    ]
}

# --- [ MOTOR DE NUBE CON DIAGNÓSTICO ] ---
class CloudService:
    def __init__(self):
        self.sheet = None
        self.last_error = ""
        self.creds_source = "Ninguna"
        self._connect()

    def _connect(self):
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            creds = None
            
            # Opción 1: Variable de entorno (Render)
            google_creds_env = os.getenv("GOOGLE_CREDENTIALS")
            if google_creds_env:
                try:
                    creds_info = json.loads(google_creds_env)
                    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
                    self.creds_source = "Variable de entorno"
                except json.JSONDecodeError as e:
                    self.last_error = f"JSON inválido en variable de entorno: {e}"
                    return
                except Exception as e:
                    self.last_error = f"Error con variable de entorno: {e}"
                    return
            
            # Opción 2: Archivo local
            elif os.path.exists(CREDS_JSON):
                try:
                    creds = Credentials.from_service_account_file(CREDS_JSON, scopes=scopes)
                    self.creds_source = "Archivo local"
                except Exception as e:
                    self.last_error = f"Error leyendo archivo: {e}"
                    return
            
            else:
                self.last_error = "No se encontraron credenciales (ni archivo ni variable de entorno)"
                return
            
            if not creds:
                self.last_error = "No se pudieron cargar las credenciales"
                return
            
            # Conectar con Google Sheets
            try:
                client = gspread.authorize(creds)
            except Exception as e:
                self.last_error = f"Error al autorizar con Google: {e}"
                return
            
            try:
                workbook = client.open("Ingenieria de software II")
            except gspread.SpreadsheetNotFound:
                self.last_error = "No se encontró el libro 'Ingenieria de software II'"
                return
            except Exception as e:
                self.last_error = f"Error abriendo libro: {e}"
                return
            
            try:
                self.sheet = workbook.worksheet("Notas_PNF_UNERMB")
            except gspread.WorksheetNotFound:
                self.last_error = "No se encontró la hoja 'Notas_PNF_UNERMB'"
                return
            except Exception as e:
                self.last_error = f"Error accediendo a hoja: {e}"
                return
                
        except Exception as e:
            self.last_error = f"Error general: {e}"

    def update_nota(self, cedula, unidad, nota):
        if not self.sheet:
            return False
        
        try:
            ceds = self.sheet.col_values(2)
            cedula_str = str(cedula).strip()
            
            if cedula_str not in ceds:
                self.last_error = f"Cédula '{cedula_str}' no encontrada en la hoja"
                return False
            
            row = ceds.index(cedula_str) + 1
            col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad, 4)
            
            self.sheet.update_cell(row, col, nota)
            self.last_error = ""
            return True
            
        except Exception as e:
            self.last_error = f"Error al actualizar celda: {e}"
            return False

# --- [ APLICACIÓN FLET ] ---
async def main(page: ft.Page):
    page.title = "SISTEMA ACADÉMICO UNERMB"
    page.bgcolor = COLOR_FONDO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    cloud = CloudService()
    state = {"name": "", "id": "", "unit": "", "pts": 0, "idx": 0, "timer_active": False}

    async def navigate(func):
        page.clean()
        await func()
        page.update()

    async def view_login():
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

        async def do_login(e):
            if dd.value and students.get(dd.value) == tf.value:
                state["name"], state["id"] = dd.value, tf.value
                await navigate(view_menu)
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

    async def view_menu():
        page.add(
            ft.Text(f"Bienvenido: {state['name']}", size=20, color="white"),
            ft.Divider(color="white"),
            *[ft.ElevatedButton(u, on_click=lambda e, x=u: asyncio.run(start_unit(x)), width=350, height=55) for u in CONTENIDO.keys()],
            ft.TextButton("Cerrar Sesión", on_click=lambda _: asyncio.run(navigate(view_login)), style=ft.ButtonStyle(color="white"))
        )

    async def start_unit(u):
        state["unit"] = u
        await navigate(view_study)

    async def view_study():
        items = [ft.ListTile(title=ft.Text(k, weight="bold"), subtitle=ft.Text(v)) for k, v in CONTENIDO[state["unit"]].items()]
        page.add(
            ft.Text(f"MATERIAL: {state['unit']}", size=24, color="white", weight="bold"),
            ft.Container(content=ft.Column(items, scroll=ft.ScrollMode.ALWAYS, height=400), bgcolor="white", padding=15, border_radius=10, width=600),
            ft.Row([
                ft.ElevatedButton("EXAMEN", on_click=lambda _: asyncio.run(start_exam()), bgcolor="#0c6980", color="white"),
                ft.ElevatedButton("VOLVER", on_click=lambda _: asyncio.run(navigate(view_menu)))
            ], alignment="center")
        )

    async def start_exam():
        state["pts"], state["idx"] = 0, 0
        await navigate(view_exam)

    async def view_exam():
        bank = PREGUNTAS[state["unit"]]
        if state["idx"] < 10:
            q, opts, ans = bank[state["idx"]]
            opciones_mezcladas = list(opts)
            random.shuffle(opciones_mezcladas)

            lbl_timer = ft.Text("15", size=35, weight="bold", color="yellow")
            current_instance_idx = state["idx"]
            state["timer_active"] = True

            async def check(pick):
                if state["timer_active"]:
                    state["timer_active"] = False
                    if pick == ans: state["pts"] += 1
                    state["idx"] += 1
                    await navigate(view_exam)

            page.add(
                ft.Row([ft.Icon(ft.icons.TIMER, color="white"), lbl_timer], alignment="center"),
                ft.Text(f"Pregunta {state['idx']+1} de 10", color="white"),
                ft.Container(content=ft.Text(q, size=22, weight="bold", text_align="center"), padding=35, bgcolor="white", border_radius=15, width=650),
                *[ft.ElevatedButton(o, on_click=lambda e, x=o: asyncio.run(check(x)), width=450, height=50, 
                                   style=ft.ButtonStyle(bgcolor=COLOR_BOTON, color=COLOR_TEXTO_BOTON)) for o in opciones_mezcladas]
            )

            for i in range(15, -1, -1):
                if not state["timer_active"] or state["idx"] != current_instance_idx:
                    break
                lbl_timer.value = str(i)
                if i <= 5: lbl_timer.color = "red"
                page.update()
                await asyncio.sleep(1)
                
                if i == 0 and state["timer_active"] and state["idx"] == current_instance_idx:
                    state["timer_active"] = False
                    state["idx"] += 1
                    await navigate(view_exam)
        else:
            await navigate(view_result)

    async def view_result():
