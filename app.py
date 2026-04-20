import flet as ft
import gspread
import openpyxl
import os
from google.oauth2.service_account import Credentials

# --- [ CONSTANTES DE IDENTIDAD VISUAL ] ---
COLOR_UNERMB_BLUE = "#8babf1"
COLOR_UNERMB_DARK = "#1a237e"
COLOR_SUCCESS = "#2e7d32"
COLOR_ERROR = "#c62828"

# --- [ INFRAESTRUCTURA DE DATOS ] ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")
EXCEL_LOCAL = os.path.join(BASE_DIR, "Programacion.xlsx")

# --- [ CONTENIDO TÉCNICO DE CÁTEDRA ] ---
# Contenido basado en el Programa Nacional de Formación (PNF) en Informática
CONTENIDO_CATEDRA = {
    "UNIDAD I: Ingeniería de Requisitos y Calidad": {
        "material": [
            "Estándar IEEE 830: Especificación de Requisitos de Software (SRS).",
            "Clasificación de Requisitos: Funcionales (acciones) y No Funcionales (atributos).",
            "Métricas de Software: Complejidad Ciclomática de McCabe y Puntos de Función.",
            "Metodologías Ágiles: El Manifiesto Ágil y el marco de trabajo Scrum.",
            "Garantía de Calidad (SQA): Normas ISO/IEC 25000 (SQuaRE)."
        ],
        "evaluacion": [
            ("¿Qué define el estándar IEEE 830?", ["Estructura del SRS", "Diagramas de flujo", "Código fuente"], "Estructura del SRS"),
            ("¿Cuál es un Requisito No Funcional?", ["Disponibilidad del 99%", "Registrar usuario", "Generar factura"], "Disponibilidad del 99%"),
            ("¿Qué mide la Complejidad Ciclomática?", ["Caminos independientes", "Líneas de código", "Número de clases"], "Caminos independientes"),
            ("¿En Scrum, qué es el Sprint Backlog?", ["Tareas del ciclo actual", "Lista de deseos", "Manual técnico"], "Tareas del ciclo actual"),
            ("¿La mantenibilidad en ISO 25000 es?", ["Atributo de calidad", "Un error de lógica", "Una herramienta CASE"], "Atributo de calidad"),
            ("¿Qué es la elicitación?", ["Descubrimiento de requisitos", "Escritura de código", "Pruebas de estrés"], "Descubrimiento de requisitos"),
            ("¿Técnica para validar requisitos?", ["Prototipado", "Compilación", "Formateo"], "Prototipado"),
            ("¿Quién es el Product Owner?", ["Voz del cliente", "Líder técnico", "Administrador de BD"], "Voz del cliente"),
            ("¿Qué es una Historia de Usuario?", ["Descripción de funcionalidad", "Un bug reportado", "Un diagrama UML"], "Descripción de funcionalidad"),
            ("¿Métrica para esfuerzo humano?", ["Meses-Persona", "Líneas por hora", "Puntos por clic"], "Meses-Persona")
        ]
    },
    "UNIDAD II: Arquitectura y Diseño de Objetos": {
        "material": [
            "Patrones de Diseño: Singleton, Factory y MVC (Modelo-Vista-Controlador).",
            "Principios SOLID: Responsabilidad única, Abierto/Cerrado, Liskov, etc.",
            "UML 2.0: Diagramas de Comportamiento (Casos de Uso) y Estructurales (Clases).",
            "POO Avanzada: Acoplamiento, Cohesión y delegación de responsabilidades.",
            "Manejo de Persistencia: Mapeo Objeto-Relacional (ORM) y lógica de negocio."
        ],
        "evaluacion": [
            ("¿Qué busca el principio de Cohesión?", ["Unidad de propósito", "Dependencia externa", "Código extenso"], "Unidad de propósito"),
            ("¿Patrón para una única instancia?", ["Singleton", "Observer", "Strategy"], "Singleton"),
            ("¿En MVC, qué maneja la lógica?", ["Controlador", "Vista", "Modelo"], "Controlador"),
            ("¿Qué representa un Diagrama de Clases?", ["Estructura estática", "Flujo de tiempo", "Hardware"], "Estructura estática"),
            ("¿Qué es el Acoplamiento?", ["Grado de dependencia", "Velocidad de carga", "Color de interfaz"], "Grado de dependencia"),
            ("¿Herencia múltiple en Python?", ["Soportada", "Prohibida", "Solo mediante interfaces"], "Soportada"),
            ("¿Qué es un método abstracto?", ["Sin implementación", "Método privado", "Método estático"], "Sin implementación"),
            ("¿Qué define la 'O' en SOLID?", ["Open/Closed Principle", "Object Oriented", "Only Data"], "Open/Closed Principle"),
            ("¿Relación 'tiene-un' en UML?", ["Agregación", "Herencia", "Generalización"], "Agregación"),
            ("¿Para qué sirve un Decorador?", ["Extender funcionalidad", "Borrar objetos", "Definir tipos"], "Extender funcionalidad")
        ]
    },
    "UNIDAD III: Desarrollo de Ecosistemas con Flet": {
        "material": [
            "Arquitectura de Flet: Motor Flutter con lógica de control en Python.",
            "Ciclo de Vida de la App: Inicialización, actualización de estado y cierre.",
            "Controles Contenedores: Column, Row, Stack y ResponsiveRow.",
            "Integración de APIs: Consumo de servicios REST y WebSockets.",
            "Protocolos de Despliegue: CI/CD, variables de entorno y servidores Render/Heroku."
        ],
        "evaluacion": [
            ("¿Cómo maneja Flet el estado?", ["page.update()", "page.refresh()", "save()"], "page.update()"),
            ("¿Control para superponer elementos?", ["Stack", "Column", "Row"], "Stack"),
            ("¿Qué tecnología renderiza la UI?", ["Flutter", "HTML5", "Swing"], "Flutter"),
            ("¿on_change es un evento de?", ["TextField", "Text", "Image"], "TextField"),
            ("¿Para qué sirven las variables de entorno?", ["Seguridad de llaves", "Aumentar RAM", "Cambiar fuentes"], "Seguridad de llaves"),
            ("¿Qué es el Hot Reload en Flet?", ["Actualización instantánea", "Reinicio de PC", "Carga de BD"], "Actualización instantánea"),
            ("¿Control para diálogos modales?", ["AlertDialog", "SnackBar", "Banner"], "AlertDialog"),
            ("¿Propiedad para el espaciado interno?", ["padding", "margin", "spacing"], "padding"),
            ("¿Cómo se define el puerto en Render?", ["Variable PORT", "Archivo Excel", "Manual"], "Variable PORT"),
            ("¿Framework CSS similar a Flet?", ["Tailwind", "Bootstrap", "No aplica"], "No aplica")
        ]
    }
}

# --- [ MOTOR DE PERSISTENCIA ] ---
class GoogleSheetsEngine:
    def __init__(self):
        self.worksheet = self._connect()

    def _connect(self):
        try:
            if os.path.exists(CREDS_JSON):
                scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                creds = Credentials.from_service_account_file(CREDS_JSON, scopes=scopes)
                client = gspread.authorize(creds)
                # Basado en la imagen de la hoja suministrada
                return client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
        except: return None

    def update_grade(self, cedula, unidad, grade):
        if not self.worksheet: return False
        try:
            # Columna B: Cedula (según image_cd9139.png)
            ced_list = self.worksheet.col_values(2)
            if str(cedula) in ced_list:
                row_idx = ced_list.index(str(cedula)) + 1
                # Mapeo de columnas: NOTA1(D=4), NOTA2(E=5), NOTA3(F=6)
                col_map = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}
                col_idx = col_map.get(unidad[:8], 4)
                self.sheet_update(row_idx, col_idx, grade)
                return True
        except: return False

    def sheet_update(self, r, c, val):
        self.worksheet.update_cell(r, c, val)

# --- [ LÓGICA DE LA APLICACIÓN ] ---
def main(page: ft.Page):
    page.title = "SISTEMA ACADÉMICO UNERMB - INGENIERÍA"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = COLOR_UNERMB_BLUE
    page.window_width = 1200
    page.window_height = 800
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    db = GoogleSheetsEngine()
    session = {"user": None, "id": None, "unit": None, "score": 0, "idx": 0}

    # --- Vistas ---
    def route_login():
        page.clean()
        users_db = {}
        if os.path.exists(EXCEL_LOCAL):
            try:
                wb = openpyxl.load_workbook(EXCEL_LOCAL, data_only=True)
                ws = wb.active
                for row in range(2, 100):
                    ced, nom = ws.cell(row, 2).value, ws.cell(row, 3).value
                    if nom: users_db[str(nom)] = str(ced)
            except: pass

        drop = ft.Dropdown(label="Seleccione su Nombre y Apellido", width=500, bgcolor="white")
        for u in users_db.keys(): drop.options.append(ft.dropdown.Option(u))
        
        pwd = ft.TextField(label="Cédula de Identidad", password=True, width=500, bgcolor="white", can_reveal_password=True)

        def do_login(e):
            if drop.value and users_db.get(drop.value) == pwd.value:
                session["user"], session["id"] = drop.value, pwd.value
                route_menu()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Credenciales Incorrectas"), bgcolor=COLOR_ERROR)
                page.snack_bar.open = True
                page.update()

        page.add(
            ft.Image(src="https://unermb.edu.ve/wp-content/uploads/2021/03/LOGO-UNERMB-1.png", width=150),
            ft.Text("INGENIERÍA DE SOFTWARE II", size=32, weight="bold", color=COLOR_UNERMB_DARK),
            ft.Container(height=20),
            ft.Container(
                content=ft.Column([drop, pwd, ft.ElevatedButton("ENTRAR AL PORTAL", on_click=do_login, width=300, height=50, style=ft.ButtonStyle(bgcolor=COLOR_UNERMB_DARK, color="white"))], horizontal_alignment="center"),
                padding=40, bgcolor="#22ffffff", border_radius=20
            )
        )

    def route_menu():
        page.clean()
        page.add(
            ft.Text(f"Bienvenido, Ing. {session['user']}", size=22, weight="bold"),
            ft.Text("MÓDULOS DE APRENDIZAJE PNF INFORMATICA", size=16),
            ft.Divider(height=40),
            ft.Row([
                ft.Card(content=ft.Container(
                    content=ft.Column([ft.Icon(ft.icons.MENU_BOOK, size=40), ft.Text(k, text_align="center"), ft.ElevatedButton("Estudiar y Evaluar", on_click=lambda e, k=k: route_study(k))], horizontal_alignment="center"),
                    padding=20, width=300
                )) for k in CONTENIDO_CATEDRA.keys()
            ], wrap=True, alignment="center")
        )

    def route_study(unit):
        session["unit"] = unit
        page.clean()
        textos = [ft.Text(f"➤ {t}", size=18) for t in CONTENIDO_CATEDRA[unit]["material"]]
        page.add(
            ft.Text(unit, size=28, weight="bold", color=COLOR_UNERMB_DARK),
            ft.Container(content=ft.Column(textos, spacing=15), padding=30, bgcolor="white", border_radius=15, width=800),
            ft.Row([
                ft.ElevatedButton("IR AL EXAMEN", on_click=lambda _: route_exam(), bgcolor=COLOR_SUCCESS, color="white", height=50),
                ft.TextButton("Volver", on_click=lambda _: route_menu())
            ], alignment="center")
        )

    def route_exam():
        session["score"], session["idx"] = 0, 0
        render_question()

    def render_question():
        page.clean()
        preguntas = CONTENIDO_CATEDRA[session["unit"]]["evaluacion"]
        if session["idx"] < 10:
            q, opts, ans = preguntas[session["idx"]]
            
            def check(choice):
                if choice == ans: session["score"] += 1
                session["idx"] += 1
                render_question()

            page.add(
                ft.Text(f"Unidad: {session['unit']}", size=14),
                ft.ProgressBar(value=(session["idx"]+1)/10, width=600, color=COLOR_UNERMB_DARK),
                ft.Text(f"Pregunta {session['idx']+1} de 10", size=20, weight="bold"),
                ft.Container(content=ft.Text(q, size=24, text_align="center"), padding=40, bgcolor="white", border_radius=20, width=700),
                *[ft.ElevatedButton(o, on_click=lambda e, o=o: check(o), width=500, height=55) for o in opts]
            )
        else:
            route_result()

    def route_result():
        page.clean()
        page.add(ft.Text("PROCESANDO RESULTADOS...", size=20))
        page.update()
        
        success = db.update_grade(session["id"], session["unit"], session["score"])
        
        page.clean()
        page.add(
            ft.Text("EVALUACIÓN FINALIZADA", size=30, weight="bold"),
            ft.Text(f"Puntaje: {session['score']} / 10", size=90, color="orange", weight="bold"),
            ft.Icon(ft.icons.CHECK_CIRCLE if success else ft.icons.CLOUD_OFF, size=50, color=COLOR_SUCCESS if success else COLOR_ERROR),
            ft.Text("Nota sincronizada con Google Sheets" if success else "Error al guardar en la nube", size=18),
            ft.ElevatedButton("REGRESAR AL MENÚ", on_click=lambda _: route_menu(), width=300, height=50)
        )

    route_login()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=int(os.getenv("PORT", 8080)))
