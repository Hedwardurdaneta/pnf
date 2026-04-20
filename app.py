import flet as ft
import gspread
import openpyxl
import os
from google.oauth2.service_account import Credentials

# --- [ CONFIGURACIÓN DE RUTAS Y COLORES ] ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")
EXCEL_LOCAL = os.path.join(BASE_DIR, "Programacion.xlsx")
COLOR_FONDO = "#8babf1"
COLOR_BOTON = "#f0f4fa"
COLOR_TEXTO_BOTON = "#1976d2"

# --- [ BANCO DE DATOS (CONTENIDO Y EVALUACIÓN) ] ---
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

# --- [ SERVICIO DE SINCRONIZACIÓN GOOGLE SHEETS ] ---
class GoogleSheetsSync:
    def __init__(self):
        self.sheet = self._authenticate()

    def _authenticate(self):
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            if os.path.exists(CREDS_JSON):
                creds = Credentials.from_service_account_file(CREDS_JSON, scopes=scopes)
                # Abrir por nombre exacto de la hoja suministrada en la imagen previa
                client = gspread.authorize(creds)
                return client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
        except Exception as e:
            print(f"ERROR_AUTH: {e}")
        return None

    def sync_nota(self, cedula, unidad, nota):
        if not self.sheet: return False
        try:
            # Columna B es donde están las cédulas (columna 2)
            ced_list = self.sheet.col_values(2)
            if str(cedula) in ced_list:
                row_index = ced_list.index(str(cedula)) + 1
                # Columna D=4 (U-I), E=5 (U-II), F=6 (U-III)
                col_index = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad, 4)
                self.sheet.update_cell(row_index, col_index, nota)
                return True
        except: return False

# --- [ INTERFAZ DE USUARIO CON FLET ] ---
def main(page: ft.Page):
    page.title = "Portal Educativo UNERMB"
    page.bgcolor = COLOR_FONDO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    sync_engine = GoogleSheetsSync()
    session = {"user": "", "id": "", "unit": "", "score": 0, "q_idx": 0}

    def navigate(view_func):
        page.clean()
        view_func()
        page.update()

    def login_view():
        users = {}
        if os.path.exists(EXCEL_LOCAL):
            try:
                wb = openpyxl.load_workbook(EXCEL_LOCAL, data_only=True)
                ws = wb.active
                for i in range(2, 100):
                    c, n = ws.cell(i, 2).value, ws.cell(i, 3).value
                    if n: users[str(n)] = str(c)
            except: pass

        dd = ft.Dropdown(label="Seleccione Estudiante", width=400, bgcolor="white",
                         options=[ft.dropdown.Option(u) for u in users.keys()])
        tf = ft.TextField(label="Cédula", password=True, width=400, bgcolor="white")

        def handle_login(e):
            if dd.value and users.get(dd.value) == tf.value:
                session["user"], session["id"] = dd.value, tf.value
                navigate(menu_view)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Datos Incorrectos"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        page.add(
            ft.Text("INGENIERÍA DE SOFTWARE II", size=28, weight="bold", color="white"),
            ft.Container(height=20),
            ft.Container(
                content=ft.Column([dd, tf, ft.ElevatedButton("ACCEDER", on_click=handle_login, width=200, height=50)],
                                  horizontal_alignment="center"),
                padding=30, bgcolor="#33ffffff", border_radius=15
            )
        )

    def menu_view():
        page.add(
            ft.Text(f"Ingeniero(a): {session['user']}", size=20, color="white"),
            ft.Divider(color="white"),
            *[ft.ElevatedButton(u, on_click=lambda e, u=u: study_unit(u), width=350, height=60) for u in CONTENIDO.keys()],
            ft.TextButton("Salir", on_click=lambda _: navigate(login_view), style=ft.ButtonStyle(color="white"))
        )

    def study_unit(u):
        session["unit"] = u
        navigate(study_view)

    def study_view():
        u = session["unit"]
        items = [ft.ListTile(title=ft.Text(k, weight="bold"), subtitle=ft.Text(v)) for k, v in CONTENIDO[u].items()]
        page.add(
            ft.Text(f"CONTENIDO: {u}", size=24, color="white", weight="bold"),
            ft.Container(content=ft.Column(items, scroll=ft.ScrollMode.ALWAYS, height=400),
                         bgcolor="white", border_radius=10, padding=10, width=600),
            ft.Row([
                ft.ElevatedButton("EVALUACIÓN", on_click=lambda _: start_exam(), bgcolor="green", color="white"),
                ft.ElevatedButton("VOLVER", on_click=lambda _: navigate(menu_view))
            ], alignment="center")
        )

    def start_exam():
        session["score"] = 0
        session["q_idx"] = 0
        navigate(exam_view)

    def exam_view():
        bank = PREGUNTAS[session["unit"]]
        if session["q_idx"] < 10:
            q, opts, ans = bank[session["q_idx"]]
            
            def check_ans(pick):
                if pick == ans: session["score"] += 1
                session["q_idx"] += 1
                navigate(exam_view)

            page.add(
                ft.Text(f"Pregunta {session['q_idx'] + 1} de 10", color="white"),
                ft.Container(content=ft.Text(q, size=24, weight="bold", text_align="center"),
                             padding=40, bgcolor="white", border_radius=20, width=700),
                *[ft.ElevatedButton(o, on_click=lambda e, o=o: check_ans(o), width=500, height=55,
                                   style=ft.ButtonStyle(bgcolor=COLOR_BOTON, color=COLOR_TEXTO_BOTON)) for o in opts]
            )
        else:
            navigate(result_view)

    def result_view():
        # Carga mientras sincroniza
        page.add(ft.ProgressRing(color="white"), ft.Text("Sincronizando...", color="white"))
        page.update()
        
        success = sync_engine.sync_nota(session["id"], session["unit"], session["score"])
        
        page.clean()
        page.add(
            ft.Text("RESULTADO FINAL", size=36, weight="bold", color="white"),
            ft.Text(f"{session['score']}/10", size=110, weight="bold", color="yellow"),
            ft.Row([
                ft.Icon(ft.icons.CLOUD_DONE if success else ft.icons.CLOUD_OFF, color="white"),
                ft.Text("Nota sincronizada" if success else "Error de conexión con la nube", color="white")
            ], alignment="center"),
            ft.ElevatedButton("REGRESAR AL MENÚ", on_click=lambda _: navigate(menu_view), width=300, height=55)
        )

    login_view()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port, host="0.0.0.0")
