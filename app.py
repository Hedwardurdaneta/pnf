import flet as ft
import gspread
import openpyxl
import os
import time
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURACIÓN GLOBAL ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")
EXCEL_LOCAL = os.path.join(BASE_DIR, "Programacion.xlsx")
COLOR_PRINCIPAL = "#8babf1"
COLOR_BOTON = "#1a237e"

# --- 2. BANCO DE DATOS ACADÉMICO (30 PREGUNTAS) ---
CONTENIDO_ACADEMICO = {
    "UNIDAD I: Ingeniería de Software y Requisitos": {
        "teoria": [
            "Ciclo de Vida: Planificación, Análisis, Diseño, Codificación, Pruebas y Mantenimiento.",
            "Elicitación: Proceso de recopilar requisitos mediante entrevistas y cuestionarios.",
            "Requisitos Funcionales: Describen comportamientos específicos del sistema.",
            "Requisitos No Funcionales: Atributos de calidad (seguridad, rendimiento, usabilidad).",
            "Modelado UML: Uso de Casos de Uso para representar interacciones de usuarios."
        ],
        "preguntas": [
            ("¿Fase donde se capturan las necesidades?", ["Análisis", "Pruebas", "Diseño"], "Análisis"),
            ("¿La seguridad es un requisito?", ["No Funcional", "Funcional", "De Código"], "No Funcional"),
            ("¿Principal artefacto de Scrum?", ["Product Backlog", "Diagrama Gantt", "C++"], "Product Backlog"),
            ("¿Qué mide la complejidad ciclomática?", ["Caminos lógicos", "Líneas de código", "Peso"], "Caminos lógicos"),
            ("¿Qué es un Stakeholder?", ["Interesado del proyecto", "Un virus", "Un cable"], "Interesado del proyecto"),
            ("¿Métrica para tamaño de software?", ["Puntos de Función", "Kilos", "Voltios"], "Puntos de Función"),
            ("¿Prueba que verifica código interno?", ["Caja Blanca", "Caja Negra", "Caja Gris"], "Caja Blanca"),
            ("¿Rol que prioriza el Backlog?", ["Product Owner", "Scrum Master", "Tester"], "Product Owner"),
            ("¿Qué es refactorización?", ["Mejorar código interno", "Borrar todo", "Formatear"], "Mejorar código interno"),
            ("¿Símbolo de inicio en flujogramas?", ["Óvalo", "Rombo", "Cuadrado"], "Óvalo")
        ]
    },
    "UNIDAD II: Programación Orientada a Objetos": {
        "teoria": [
            "Clase: Plantilla o molde para crear objetos con atributos y métodos.",
            "Encapsulamiento: Ocultar el estado interno y obligar a interactuar mediante métodos.",
            "Herencia: Mecanismo para crear nuevas clases basadas en clases existentes.",
            "Polimorfismo: Capacidad de procesar objetos de forma distinta según su clase.",
            "Abstracción: Enfocarse en las características esenciales eliminando detalles complejos."
        ],
        "preguntas": [
            ("¿Qué es una clase?", ["Molde para objetos", "Una variable", "Un bucle"], "Molde para objetos"),
            ("¿Dato para colecciones Clave-Valor?", ["Diccionario", "Lista", "Tupla"], "Diccionario"),
            ("¿Principio para ocultar datos?", ["Encapsulamiento", "Herencia", "Clase"], "Encapsulamiento"),
            ("¿Cómo se define una función?", ["def", "function", "class"], "def"),
            ("¿Qué es 'self'?", ["Referencia a la instancia", "Un número", "Un error"], "Referencia a la instancia"),
            ("¿Estructura para excepciones?", ["try/except", "if/else", "while"], "try/except"),
            ("¿Qué es el Polimorfismo?", ["Mismas interfaces", "Muchos datos", "Virus"], "Mismas interfaces"),
            ("¿Función para ver longitud?", ["len()", "size()", "count()"], "len()"),
            ("¿Es una lista mutable?", ["Sí", "No", "Solo lectura"], "Sí"),
            ("¿Qué hace __init__?", ["Constructor", "Cierra", "Suma"], "Constructor")
        ]
    },
    "UNIDAD III: Interfaces Gráficas y Flet": {
        "teoria": [
            "Framework Flet: Permite crear interfaces Web/Móvil usando solo Python.",
            "Controles: Elementos visuales como Text, ElevatedButton y TextField.",
            "Eventos: Acciones disparadas por el usuario como on_click o on_change.",
            "Layouts: Organización mediante Column (vertical) y Row (horizontal).",
            "Despliegue: Proceso de publicar la app en servidores como Render."
        ],
        "preguntas": [
            ("¿Flet se basa en?", ["Flutter", "Java", "React"], "Flutter"),
            ("¿Control para entrada de texto?", ["TextField", "Label", "Image"], "TextField"),
            ("¿Comando para refrescar UI?", ["page.update()", "save()", "exit()"], "page.update()"),
            ("¿Qué dispara una acción?", ["Evento", "Variable", "Constante"], "Evento"),
            ("¿Container sirve para?", ["Diseño y agrupación", "Sumar", "Navegar"], "Diseño y agrupación"),
            ("¿Control para mostrar texto?", ["Text", "Button", "Switch"], "Text"),
            ("¿Cómo se añaden controles?", ["page.add()", "page.push()", "page.set()"], "page.add()"),
            ("¿Es componente de navegación?", ["AppBar", "TextField", "Checkbox"], "AppBar"),
            ("¿Qué es un SnackBar?", ["Mensaje emergente", "Un botón", "Un fondo"], "Mensaje emergente"),
            ("¿Atributo para color de fondo?", ["bgcolor", "color", "theme"], "bgcolor")
        ]
    }
}

# --- 3. GESTIÓN DE PERSISTENCIA (GOOGLE SHEETS) ---
class CloudService:
    def __init__(self):
        self.ws = self._connect()

    def _connect(self):
        try:
            if os.path.exists(CREDS_JSON):
                creds = Credentials.from_service_account_file(
                    CREDS_JSON, 
                    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                )
                client = gspread.authorize(creds)
                return client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
        except Exception as e:
            print(f"Error Cloud: {e}")
        return None

    def update_score(self, cedula, unidad, score):
        if not self.ws: return False
        try:
            ceds = self.ws.col_values(2) # Columna B
            if str(cedula) in ceds:
                row = ceds.index(str(cedula)) + 1
                col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad[:8], 4)
                self.ws.update_cell(row, col, score)
                return True
        except: return False

# --- 4. INTERFAZ DE USUARIO ---
def main(page: ft.Page):
    page.title = "PORTAL ACADÉMICO UNERMB"
    page.bgcolor = COLOR_PRINCIPAL
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    
    db = CloudService()
    state = {"name": "", "id": "", "unit": "", "score": 0, "q_idx": 0}

    def show_toast(msg, color=ft.colors.RED):
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def login_view():
        page.clean()
        alumnos = {}
        if os.path.exists(EXCEL_LOCAL):
            try:
                book = openpyxl.load_workbook(EXCEL_LOCAL, data_only=True)
                ws = book.active
                for r in range(2, 100):
                    n, c = ws.cell(r, 3).value, ws.cell(r, 2).value
                    if n: alumnos[str(n)] = str(c)
            except: pass

        dd = ft.Dropdown(label="Seleccione Estudiante", width=450, bgcolor="white",
                         options=[ft.dropdown.Option(n) for n in alumnos.keys()])
        tf = ft.TextField(label="Cédula", password=True, width=450, bgcolor="white", can_reveal_password=True)

        def attempt_login(e):
            if dd.value in alumnos and alumnos[dd.value] == tf.value:
                state["name"], state["id"] = dd.value, tf.value
                menu_view()
            else:
                show_toast("Credenciales inválidas")

        page.add(
            ft.Container(height=50),
            ft.Text("SISTEMA DE EVALUACIÓN PNF", size=35, weight="bold", color="white"),
            ft.Text("Ingeniería de Software II", size=20, color="white"),
            ft.Container(
                content=ft.Column([dd, tf, ft.ElevatedButton("INGRESAR", on_click=attempt_login, width=250, height=50, 
                                  style=ft.ButtonStyle(bgcolor=COLOR_BOTON, color="white"))], 
                                  horizontal_alignment="center"),
                padding=40, bgcolor="#22000000", border_radius=20
            )
        )

    def menu_view():
        page.clean()
        page.add(
            ft.Text(f"Bienvenido, {state['name']}", size=24, color="white", weight="bold"),
            ft.Divider(color="white"),
            *[ft.Container(
                content=ft.ElevatedButton(k, on_click=lambda e, k=k: study_view(k), width=400, height=60),
                margin=5
            ) for k in CONTENIDO_ACADEMICO.keys()],
            ft.TextButton("Cerrar Sesión", on_click=lambda _: login_view(), style=ft.ButtonStyle(color="white"))
        )

    def study_view(unit):
        state["unit"] = unit
        page.clean()
        teoria = CONTENIDO_ACADEMICO[unit]["teoria"]
        page.add(
            ft.Text(unit, size=28, color="white", weight="bold"),
            ft.Container(
                content=ft.Column([ft.Text(f"• {t}", size=18, color="white") for t in teoria], spacing=15),
                padding=20, bgcolor="#44000000", border_radius=15, width=600
            ),
            ft.ElevatedButton("COMENZAR EVALUACIÓN", on_click=lambda _: start_quiz(), 
                              bgcolor="green", color="white", width=300, height=50),
            ft.TextButton("Volver al Menú", on_click=lambda _: menu_view(), style=ft.ButtonStyle(color="white"))
        )

    def start_quiz():
        state["score"] = 0
        state["q_idx"] = 0
        quiz_view()

    def quiz_view():
        page.clean()
        qs = CONTENIDO_ACADEMICO[state["unit"]]["preguntas"]
        if state["q_idx"] < 10:
            pregunta, opciones, correcta = qs[state["q_idx"]]
            
            def check_ans(picked):
                if picked == correcta: state["score"] += 1
                state["q_idx"] += 1
                quiz_view()

            page.add(
                ft.Text(f"Pregunta {state['q_idx'] + 1} de 10", color="white", size=16),
                ft.Container(
                    content=ft.Text(pregunta, size=22, weight="bold", text_align="center"),
                    padding=30, bgcolor="white", border_radius=15, width=600
                ),
                *[ft.ElevatedButton(o, on_click=lambda e, o=o: check_ans(o), width=450, height=50) for o in opciones]
            )
        else:
            finish_view()

    def finish_view():
        page.clean()
        loading = ft.ProgressRing(color="white")
        status = ft.Text("Sincronizando con Google Sheets...", color="white")
        page.add(
            ft.Text("RESULTADO FINAL", size=30, color="white", weight="bold"),
            ft.Text(f"{state['score']}/10", size=100, color="yellow", weight="bold"),
            loading, status
        )
        page.update()
        
        success = db.update_score(state["id"], state["unit"], state["score"])
        loading.visible = False
        status.value = "✅ Nota guardada exitosamente" if success else "⚠️ Error de conexión con la nube"
        status.color = "green" if success else "red"
        
        page.add(ft.ElevatedButton("REGRESAR AL MENÚ", on_click=lambda _: menu_view(), width=300, height=50))
        page.update()

    login_view()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, port=port, view=ft.AppView.WEB_BROWSER, host="0.0.0.0")
