import flet as ft
import gspread
import openpyxl
import os
import random
import time
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURACIÓN DE RUTAS Y CONSTANTES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONDO_PATH = "assets/fondo_unermb.png"
EXCEL_LOCAL = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")

# --- 2. CONEXIÓN SEGURA A GOOGLE SHEETS ---
# Se utiliza el archivo credentials.json presente en la raíz de su repositorio
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    if os.path.exists(CREDS_JSON):
        creds = Credentials.from_service_account_file(CREDS_JSON, scopes=scope)
        client = gspread.authorize(creds)
        # Se vincula con su hoja de cálculo específica de la UNERMB
        sheet_google = client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
    else:
        sheet_google = None
        print("Aviso: credentials.json no encontrado.")
except Exception as e:
    sheet_google = None
    print(f"Error de conexión con Google API: {e}")

# --- 3. BANCO DE DATOS ACADÉMICO (10 TEMAS Y 10 PREGUNTAS POR UNIDAD) ---
contenido_unermb = {
    "UNIDAD I": {
        "Algoritmo": "Secuencia finita de instrucciones precisas para resolver un problema.",
        "IDE": "Entorno de Desarrollo Integrado que combina editor, compilador y depurador.",
        "Depuración": "Proceso de identificar, analizar y eliminar errores de software.",
        "Compilación": "Traducción del código fuente (alto nivel) a código máquina (binario).",
        "Sintaxis": "Conjunto de reglas gramaticales que rigen la escritura del código.",
        "Variable": "Espacio reservado en la memoria RAM con un nombre simbólico.",
        "Código Fuente": "Conjunto de líneas de texto escritas en un lenguaje de programación.",
        "Comentario": "Anotaciones para humanos que el compilador o intérprete ignora.",
        "Hardware": "Componentes físicos y electrónicos que conforman el computador.",
        "Software": "Parte lógica, programas y datos que permiten el funcionamiento del hardware."
    },
    "UNIDAD II": {
        "int": "Tipo de dato que representa números enteros positivos o negativos.",
        "float": "Tipo de dato para números reales con representación decimal.",
        "str": "Tipo de dato para cadenas de caracteres o texto.",
        "bool": "Tipo lógico que representa valores de verdad: True o False.",
        "Lista": "Colección ordenada y mutable de elementos en Python.",
        "Operador": "Símbolo que realiza cálculos (+, -) o comparaciones (==, !=).",
        "Asignación": "Operación de almacenar un valor en una variable usando '='.",
        "if": "Estructura de control condicional que bifurca el flujo del programa.",
        "while": "Estructura de repetición basada en el cumplimiento de una condición.",
        "for": "Estructura de repetición que itera sobre una secuencia o rango."
    },
    "UNIDAD III": {
        "Flet": "Framework basado en Flutter para crear interfaces de usuario con Python.",
        "Widget": "Componente básico de la interfaz (botones, textos, imágenes).",
        "Label": "Control especializado en mostrar texto estático en la pantalla.",
        "Entry": "Campo de entrada de datos (TextField) para la interacción del usuario.",
        "Button": "Componente interactivo que dispara eventos al ser presionado.",
        "Container": "Elemento de diseño que permite agrupar, dar color y margen a otros widgets.",
        "Evento": "Señal que indica que algo ha sucedido (clic, cambio de texto).",
        "Layout": "Forma en la que se organizan visualmente los componentes en la app.",
        "Mainloop": "Ciclo de vida principal que mantiene la aplicación respondiendo.",
        "Color": "Propiedad estética fundamental para la experiencia de usuario (UX)."
    }
}

banco_evaluacion = {
    "UNIDAD I": [
        ("¿Qué es un algoritmo?", ["Pasos lógicos", "Un virus", "Un cable"], "Pasos lógicos"),
        ("¿Qué significa IDE?", ["Entorno de Desarrollo", "Internet de Datos", "Disco"], "Entorno de Desarrollo"),
        ("¿Qué es depuración?", ["Corregir errores", "Borrar archivos", "Instalar"], "Corregir errores"),
        ("¿La compilación traduce?", ["Código fuente a máquina", "Binario a texto", "Word a PDF"], "Código fuente a máquina"),
        ("¿Qué es sintaxis?", ["Reglas de escritura", "Un procesador", "Una tecla"], "Reglas de escritura"),
        ("¿Dónde reside una variable?", ["Memoria RAM", "Monitor", "Impresora"], "Memoria RAM"),
        ("¿Qué es código fuente?", ["Texto programado", "Electricidad", "Señal WIFI"], "Texto programado"),
        ("¿El compilador lee comentarios?", ["No", "Sí", "A veces"], "No"),
        ("¿Qué es el hardware?", ["Parte física", "Software", "Internet"], "Parte física"),
        ("¿Qué es el software?", ["Parte lógica", "El teclado", "El mouse"], "Parte lógica")
    ],
    "UNIDAD II": [
        ("¿Qué guarda un 'int'?", ["Números enteros", "Letras", "Imágenes"], "Números enteros"),
        ("¿Qué guarda un 'float'?", ["Decimales", "Cadenas", "Enteros"], "Decimales"),
        ("¿Qué es un 'str'?", ["Texto", "Números", "Bucle"], "Texto"),
        ("¿Valores del 'bool'?", ["True/False", "1 al 10", "A, B, C"], "True/False"),
        ("¿Qué es una lista?", ["Colección de datos", "Variable única", "Un error"], "Colección de datos"),
        ("¿Qué es '+'?", ["Operador", "Variable", "Widget"], "Operador"),
        ("¿Símbolo de asignación?", ["=", "==", "+"], "="),
        ("¿Qué es 'if'?", ["Condicional", "Bucle", "Variable"], "Condicional"),
        ("¿Qué es 'while'?", ["Bucle condicional", "Salida", "Función"], "Bucle condicional"),
        ("¿Qué es 'for'?", ["Bucle iterativo", "Suma", "Texto"], "Bucle iterativo")
    ],
    "UNIDAD III": [
        ("¿Qué es Flet?", ["Framework UI", "Base de datos", "Antivirus"], "Framework UI"),
        ("¿Qué es un Widget?", ["Control visual", "Hardware", "Un virus"], "Control visual"),
        ("¿Qué muestra un Label?", ["Texto", "Video", "Música"], "Texto"),
        ("¿Qué es un Entry?", ["Entrada de texto", "Salida", "Imagen"], "Entrada de texto"),
        ("¿Qué hace un Button?", ["Ejecuta acciones", "Nada", "Cierra todo"], "Ejecuta acciones"),
        ("¿Qué es un Container?", ["Agrupador con estilo", "Variable", "Lista"], "Agrupador con estilo"),
        ("¿Qué es un clic?", ["Un evento", "Un error", "Hardware"], "Un evento"),
        ("¿Qué es el Layout?", ["Organización visual", "Color", "Nombre"], "Organización visual"),
        ("¿Qué es el Mainloop?", ["Ciclo de la app", "Un cable", "Un icono"], "Ciclo de la app"),
        ("¿El color es un atributo?", ["Sí", "No", "Solo en web"], "Sí")
    ]
}

# --- 4. LÓGICA DE PERSISTENCIA ---
def registrar_nota_dual(cedula, nombre, unidad, nota):
    # Registro en Google Sheets
    if sheet_google:
        try:
            cell = sheet_google.find(str(cedula))
            # Columna 4=Nota1, 5=Nota2, 6=Nota3
            col_map = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}
            sheet_google.update_cell(cell.row, col_map[unidad], nota)
        except Exception as e:
            print(f"No se pudo actualizar Google Sheets: {e}")
    
    # Registro en Excel Local (Opcional si el archivo existe)
    if os.path.exists(EXCEL_LOCAL):
        try:
            wb = openpyxl.load_workbook(EXCEL_LOCAL)
            ws = wb.active
            col_ex = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
            for r in range(2, 60):
                if str(ws.cell(r, 3).value) == nombre:
                    ws.cell(r, col_ex).value = nota
                    break
            wb.save(EXCEL_LOCAL)
        except: pass

# --- 5. INTERFAZ GRÁFICA (CENTRADO TOTAL Y CONTRASTE) ---
def main(page: ft.Page):
    page.title = "Sistema de Evaluación PNF - UNERMB"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_maximized = True
    page.padding = 0
    page.spacing = 0

    state = {"user": None, "cedula": None, "unidad": None, "puntos": 0, "idx": 0}

    def layout_centrado(controles):
        return ft.Stack([
            ft.Image(src=FONDO_PATH, width=page.width, height=page.height, fit=ft.ImageFit.COVER),
            ft.Container(
                content=ft.Column(controles, horizontal_alignment="center", alignment="center", spacing=25),
                expand=True, alignment=ft.alignment.center,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center, end=ft.alignment.bottom_center,
                    colors=[ft.colors.with_opacity(0.6, "black"), ft.colors.with_opacity(0.3, "black")]
                )
            )
        ], expand=True)

    def login_view():
        page.clean()
        # Carga dinámica de usuarios
        usuarios_db = {"Admin": "1234"}
        if os.path.exists(EXCEL_LOCAL):
            try:
                wb = openpyxl.load_workbook(EXCEL_LOCAL, data_only=True)
                ws = wb.active
                for r in range(2, 60):
                    if ws.cell(r, 3).value: usuarios_db[str(ws.cell(r, 3).value)] = str(ws.cell(r, 2).value)
            except: pass

        drop_u = ft.Dropdown(label="Seleccione su nombre", width=400, bgcolor="white", border_radius=12,
                             options=[ft.dropdown.Option(n) for n in usuarios_db.keys()])
        txt_c = ft.TextField(label="Cédula de Identidad", password=True, can_reveal_password=True, width=400, bgcolor="white", border_radius=12)

        def intentar_login(e):
            if drop_u.value in usuarios_db and usuarios_db[drop_u.value] == txt_c.value:
                state.update({"user": drop_u.value, "cedula": txt_c.value})
                menu_view()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Credenciales Incorrectas")); page.snack_bar.open = True; page.update()

        page.add(layout_centrado([
            ft.Text("ACCESO ESTUDIANTIL", size=40, weight="bold", color="white"),
            drop_u, txt_c,
            ft.ElevatedButton("INGRESAR", on_click=intentar_login, width=250, height=60, bgcolor="#1a4d7c", color="white")
        ]))

    def menu_view():
        page.clean()
        page.add(layout_centrado([
            ft.Text(f"Bienvenido, {state['user']}", size=30, color="white", weight="bold"),
            *[ft.ElevatedButton(u, on_click=lambda e, u=u: unidad_view(u), width=350, height=65) for u in ["UNIDAD I", "UNIDAD II", "UNIDAD III"]],
            ft.TextButton("Salir de sesión", on_click=lambda _: login_view(), style=ft.ButtonStyle(color="white"))
        ]))

    def unidad_view(u):
        state["unidad"] = u
        page.clean()
        items = [ft.ListTile(title=ft.Text(t, color="white", weight="bold"), on_click=lambda e, t=t: def_view(t)) for t in contenido_unermb[u].keys()]
        
        page.add(layout_centrado([
            ft.Text(f"Material: {u}", size=35, color="white", weight="bold"),
            ft.Container(content=ft.Column(items, scroll="auto"), width=500, height=300, bgcolor="#77000000", border_radius=20, padding=15),
            ft.ElevatedButton("INICIAR EXAMEN", on_click=lambda _: start_exam(), width=300, height=60, bgcolor="green", color="white"),
            ft.TextButton("Volver", on_click=lambda _: menu_view(), style=ft.ButtonStyle(color="white"))
        ]))

    def def_view(t):
        page.clean()
        page.add(layout_centrado([
            ft.Container(
                content=ft.Column([
                    ft.Text(t, size=35, color="white", weight="bold"),
                    ft.Text(contenido_unermb[state["unidad"]][t], size=22, color="white", text_align="center"),
                    ft.ElevatedButton("ENTENDIDO", on_click=lambda _: unidad_view(state["unidad"]))
                ], horizontal_alignment="center"),
                bgcolor="#99000000", padding=40, border_radius=25, width=600
            )
        ]))

    def start_exam():
        state.update({"idx": 0, "puntos": 0})
        render_pregunta()

    def render_pregunta():
        page.clean()
        u = state["unidad"]
        banco = banco_evaluacion[u]
        if state["idx"] < len(banco):
            preg, opts, corr = banco[state["idx"]]
            random.shuffle(opts)

            def validar(ans):
                if ans == corr: state["puntos"] += 1
                state["idx"] += 1; render_pregunta()

            page.add(layout_centrado([
                ft.Text(f"Pregunta {state['idx']+1} / 10", color="white", size=20),
                ft.Container(content=ft.Text(preg, size=28, weight="bold", text_align="center"), bgcolor="white", padding=25, border_radius=15, width=650),
                *[ft.ElevatedButton(o, on_click=lambda e, o=o: validar(o), width=450, height=55) for o in opts]
            ]))
        else:
            finalizar_test()

    def finalizar_test():
        page.clean()
        registrar_nota_dual(state["cedula"], state["user"], state["unidad"], state["puntos"])
        page.add(layout_centrado([
            ft.Text("RESULTADO DE EVALUACIÓN", size=30, color="white"),
            ft.Text(f"{state['puntos']} / 10", size=110, color="white", weight="bold"),
            ft.ElevatedButton("REGRESAR AL MENÚ", on_click=lambda _: menu_view(), width=300, height=60)
        ]))

    login_view()

if __name__ == "__main__":
    puerto = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=puerto)
