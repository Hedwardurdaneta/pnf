import flet as ft
import gspread
import openpyxl
import os
import random
import time
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURACIÓN ESTRUCTURAL ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONO_PATH = "icono.ico" 
FONDO_PATH = "assets/fondo_unermb.png"
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_FILE = os.path.join(BASE_DIR, "credentials.json")

# --- 2. CONEXIÓN ROBUSTA A GOOGLE SHEETS ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    if os.path.exists(CREDS_FILE):
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=scope)
        client = gspread.authorize(creds)
    else:
        client = None
        print("Archivo credentials.json no encontrado.")
except Exception as e:
    client = None
    print(f"Error crítico de API: {e}")

# --- 3. ESTADO GLOBAL DE LA SESIÓN ---
state = {
    "alumno": None, 
    "cedula": None, 
    "unidad": None, 
    "idx": 0, 
    "puntos": 0,
    "respuestas_usuario": []
}

# --- 4. BANCO DE DATOS ÍNTEGRO (10 PREGUNTAS POR UNIDAD) ---
contenido_estudio = {
    "UNIDAD I": {
        "Algoritmo": "Secuencia de pasos lógicos y finitos para resolver un problema.",
        "IDE": "Entorno de Desarrollo Integrado que facilita la programación.",
        "Depuración": "Proceso sistemático de encontrar y eliminar errores.",
        "Compilación": "Traducción de código fuente a lenguaje de máquina.",
        "Sintaxis": "Conjunto de reglas que definen las secuencias de símbolos.",
        "Variable": "Nombre que representa un valor almacenado en memoria.",
        "Código Fuente": "Texto escrito en un lenguaje de programación.",
        "Comentario": "Texto no ejecutable usado para documentar el código.",
        "Hardware": "Componentes físicos y tangibles de una computadora.",
        "Software": "Conjunto de programas y rutinas lógicas del sistema."
    },
    "UNIDAD II": {
        "int": "Tipo de dato que almacena números enteros sin decimales.",
        "float": "Tipo de dato para números reales con coma flotante.",
        "str": "Secuencia de caracteres usada para representar texto.",
        "bool": "Tipo de dato lógico que solo puede ser True o False.",
        "Lista": "Estructura de datos que permite almacenar varios valores.",
        "Operador": "Símbolo que indica una operación matemática o lógica.",
        "Asignación": "Acción de dar un valor a una variable usando el signo '='.",
        "if": "Estructura condicional que evalúa una expresión lógica.",
        "while": "Bucle que se repite mientras se cumple una condición.",
        "for": "Bucle diseñado para iterar sobre una secuencia definida."
    },
    "UNIDAD III": {
        "Flet": "Framework que permite crear apps interactivas en Python.",
        "Widget": "Elemento de control visual en una interfaz gráfica.",
        "Label": "Control que muestra texto estático al usuario.",
        "Entry": "Espacio de entrada para que el usuario escriba datos.",
        "Button": "Elemento que dispara una función al ser presionado.",
        "Container": "Elemento decorativo que agrupa otros controles.",
        "Evento": "Acción del usuario que el sistema puede detectar.",
        "Layout": "Esquema de organización de los elementos en pantalla.",
        "Mainloop": "Ciclo infinito que mantiene la aplicación en ejecución.",
        "Color": "Propiedad visual usada para diferenciar elementos de la UI."
    }
}

preguntas_evaluacion = {
    "UNIDAD I": [
        ("¿Qué es un algoritmo?", ["Pasos lógicos", "Un virus", "Un cable"], "Pasos lógicos"),
        ("¿Qué significa IDE?", ["Entorno de Desarrollo", "Internet de Datos", "Disco Externo"], "Entorno de Desarrollo"),
        ("¿Qué es la depuración?", ["Corregir errores", "Borrar archivos", "Instalar Office"], "Corregir errores"),
        ("¿Qué hace la compilación?", ["Traducir código", "Limpiar el PC", "Reiniciar Windows"], "Traducir código"),
        ("¿Qué es la sintaxis?", ["Reglas de escritura", "Un tipo de procesador", "Una marca de mouse"], "Reglas de escritura"),
        ("¿Dónde se guarda una variable?", ["En memoria", "En una carpeta", "En el monitor"], "En memoria"),
        ("¿Qué es el código fuente?", ["Instrucciones escritas", "Electricidad", "El cable de red"], "Instrucciones escritas"),
        ("¿El compilador lee comentarios?", ["No los lee", "Sí, siempre", "Solo al inicio"], "No los lee"),
        ("¿Qué es el hardware?", ["Parte física", "Los programas", "Las páginas web"], "Parte física"),
        ("¿Qué es el software?", ["Parte lógica", "El teclado", "La fuente de poder"], "Parte lógica")
    ],
    "UNIDAD II": [
        ("¿Qué guarda un 'int'?", ["Enteros", "Letras", "Imágenes"], "Enteros"),
        ("¿Qué guarda un 'float'?", ["Decimales", "Cadenas", "Enteros"], "Decimales"),
        ("¿Qué es un 'str'?", ["Texto", "Números", "Un error"], "Texto"),
        ("¿Valores del 'bool'?", ["True/False", "1 al 10", "A, B o C"], "True/False"),
        ("¿Qué es una lista?", ["Colección de datos", "Una sola variable", "Un cable"], "Colección de datos"),
        ("¿Qué es el símbolo '+'?", ["Operador", "Variable", "Comentario"], "Operador"),
        ("¿Símbolo de asignación?", ["=", "==", "->"], "="),
        ("¿Qué es 'if'?", ["Condicional", "Bucle infinito", "Tipo de dato"], "Condicional"),
        ("¿Qué es 'while'?", ["Bucle por condición", "Una salida", "Una variable"], "Bucle por condición"),
        ("¿Qué es 'for'?", ["Bucle iterativo", "Suma total", "Texto"], "Bucle iterativo")
    ],
    "UNIDAD III": [
        ("¿Para qué sirve Flet?", ["Interfaces UI", "Reparar discos", "Hackear redes"], "Interfaces UI"),
        ("¿Qué es un Widget?", ["Control visual", "Un virus", "Un cable"], "Control visual"),
        ("¿Qué muestra un Label?", ["Texto estático", "Videos HD", "Sonidos"], "Texto estático"),
        ("¿Qué es un Entry?", ["Entrada de texto", "Salida de audio", "Un botón"], "Entrada de texto"),
        ("¿Qué hace un Button?", ["Ejecuta acciones", "No hace nada", "Cierra el PC"], "Ejecuta acciones"),
        ("¿Qué es un Container?", ["Agrupador con estilo", "Una variable", "Un archivo"], "Agrupador con estilo"),
        ("¿Qué es un clic?", ["Un evento", "Un error", "Hardware"], "Un evento"),
        ("¿Qué es el Layout?", ["Diseño/Organización", "Color de fondo", "Nombre de app"], "Diseño/Organización"),
        ("¿Qué es el Mainloop?", ["Ciclo de ejecución", "Un cable", "Un icono"], "Ciclo de ejecución"),
        ("¿El color es un atributo?", ["Sí, es propiedad", "No, es un programa", "Solo en Linux"], "Sí, es propiedad")
    ]
}

# --- 5. FUNCIONES DE PERSISTENCIA (GOOGLE Y EXCEL) ---
def guardar_nota_remota(cedula, unidad, nota):
    if client:
        try:
            sh = client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
            celda = sh.find(str(cedula))
            col = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
            sh.update_cell(celda.row, col, nota)
        except Exception as e:
            print(f"Error en Sheets: {e}")

def guardar_nota_local(alumno, unidad, nota):
    if os.path.exists(EXCEL_PATH):
        try:
            wb = openpyxl.load_workbook(EXCEL_PATH)
            ws = wb.active
            col_ex = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
            for r in range(2, 51):
                if str(ws.cell(r, 3).value) == alumno:
                    ws.cell(r, col_ex).value = nota
                    break
            wb.save(EXCEL_PATH)
        except: pass

# --- 6. INTERFAZ GRÁFICA (CENTRADO ABSOLUTO Y ESTILO) ---
def main(page: ft.Page):
    page.title = "Portal Educativo UNERMB - Ing. Hedwar Urdaneta"
    page.window_maximized = True
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    def crear_contenedor_maestro(controles):
        return ft.Container(
            content=ft.Column(
                controles,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=25
            ),
            expand=True,
            image_src=FONDO_PATH,
            image_fit=ft.ImageFit.COVER,
            alignment=ft.alignment.center
        )

    def vista_login():
        page.clean()
        page.update()
        
        lista_alumnos = {"Admin": "1234"}
        if os.path.exists(EXCEL_PATH):
            try:
                wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
                ws = wb.active
                for r in range(2, 51):
                    nombre = ws.cell(r, 3).value
                    cedula = ws.cell(r, 2).value
                    if nombre: lista_alumnos[str(nombre)] = str(cedula)
            except: pass

        drop_usuario = ft.Dropdown(
            label="Seleccione su nombre",
            width=420,
            bgcolor="white",
            border_radius=10,
            options=[ft.dropdown.Option(n) for n in lista_alumnos.keys()]
        )
        txt_cedula = ft.TextField(
            label="Cédula de Identidad",
            password=True,
            can_reveal_password=True,
            width=420,
            bgcolor="white",
            border_radius=10
        )

        def realizar_ingreso(e):
            if drop_usuario.value in lista_alumnos and lista_alumnos[drop_usuario.value] == txt_cedula.value:
                state["alumno"] = drop_usuario.value
                state["cedula"] = txt_cedula.value
                vista_menu()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Datos Incorrectos. Verifique su cédula."))
                page.snack_bar.open = True
                page.update()

        page.add(crear_contenedor_maestro([
            ft.Text("PORTAL UNIVERSITARIO PNF", size=48, weight="bold", color="white", shadow=ft.BoxShadow(blur_radius=15, color="black")),
            drop_usuario,
            txt_cedula,
            ft.ElevatedButton("INGRESAR AL SISTEMA", on_click=realizar_ingreso, width=280, height=60, bgcolor="#1a4d7c", color="white")
        ]))

    def vista_menu():
        page.clean()
        page.add(crear_contenedor_maestro([
            ft.Text(f"Bienvenido, {state['alumno']}", size=32, color="white", weight="bold"),
            ft.ElevatedButton("📘 UNIDAD I: FUNDAMENTOS", on_click=lambda _: vista_unidad("UNIDAD I"), width=400, height=70),
            ft.ElevatedButton("🐍 UNIDAD II: PROGRAMACIÓN", on_click=lambda _: vista_unidad("UNIDAD II"), width=400, height=70),
            ft.ElevatedButton("💻 UNIDAD III: INTERFACES", on_click=lambda _: vista_unidad("UNIDAD III"), width=400, height=70),
            ft.TextButton("Cerrar Sesión", on_click=lambda _: vista_login(), style=ft.ButtonStyle(color="white"))
        ]))

    def vista_unidad(u):
        state["unidad"] = u
        page.clean()
        
        lista_temas = []
        for tema in contenido_estudio[u].keys():
            lista_temas.append(
                ft.ListTile(
                    title=ft.Text(tema, color="white", weight="bold"),
                    subtitle=ft.Text("Haga clic para ver definición", color="#CCCCCC"),
                    on_click=lambda e, t=tema: vista_definicion(t)
                )
            )

        page.add(crear_contenedor_maestro([
            ft.Text(f"Contenido de la {u}", size=30, color="white", weight="bold"),
            ft.Container(
                content=ft.Column(lista_temas, scroll="auto"),
                width=500, height=350, bgcolor="#77000000", border_radius=20, padding=15
            ),
            ft.ElevatedButton("✍️ EMPEZAR EXAMEN", on_click=lambda _: iniciar_evaluacion(), width=300, height=60, bgcolor="green", color="white"),
            ft.TextButton("Volver al Menú", on_click=lambda _: vista_menu(), style=ft.ButtonStyle(color="white"))
        ]))

    def vista_definicion(t):
        page.clean()
        texto_def = contenido_estudio[state["unidad"]].get(t)
        page.add(crear_contenedor_maestro([
            ft.Container(
                content=ft.Column([
                    ft.Text(t, size=40, color="white", weight="bold"),
                    ft.Divider(color="white"),
                    ft.Text(texto_def, size=24, color="white", text_align="center"),
                    ft.ElevatedButton("ENTENDIDO", on_click=lambda _: vista_unidad(state["unidad"]), width=200)
                ], horizontal_alignment="center"),
                padding=40, bgcolor="#88000000", border_radius=25, width=600
            )
        ]))

    def iniciar_evaluacion():
        state["idx"] = 0
        state["puntos"] = 0
        lanzar_pregunta()

    def lanzar_pregunta():
        page.clean()
        u = state["unidad"]
        banco = preguntas_evaluacion[u]

        if state["idx"] < len(banco):
            pregunta_act, opciones_orig, correcta = banco[state["idx"]]
            opciones = list(opciones_orig)
            random.shuffle(opciones)

            def verificar(eleccion):
                if eleccion == correcta:
                    state["puntos"] += 1
                state["idx"] += 1
                lanzar_pregunta()

            page.add(crear_contenedor_maestro([
                ft.Text(f"Evaluación {u} - {state['idx']+1}/10", size=20, color="white"),
                ft.Container(
                    content=ft.Text(pregunta_act, size=28, weight="bold", text_align="center"),
                    bgcolor="#EEFFFFFF", padding=30, border_radius=20, width=700
                ),
                *[ft.ElevatedButton(opt, on_click=lambda e, opt=opt: verificar(opt), width=500, height=60) for opt in opciones]
            ]))
        else:
            finalizar_sistema()

    def finalizar_sistema():
        page.clean()
        # Guardado en ambas plataformas
        guardar_nota_local(state["alumno"], state["unidad"], state["puntos"])
        guardar_nota_remota(state["cedula"], state["unidad"], state["puntos"])
        
        page.add(crear_contenedor_maestro([
            ft.Text("EVALUACIÓN COMPLETADA", size=35, color="white", weight="bold"),
            ft.Text(f"Tu calificación es:", size=24, color="white"),
            ft.Text(f"{state['puntos']} / 10", size=120, color="white", weight="bold"),
            ft.ElevatedButton("REGRESAR AL MENÚ PRINCIPAL", on_click=lambda _: vista_menu(), width=350, height=65)
        ]))
    
    vista_login()

if __name__ == "__main__":
    puerto_render = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=puerto_render)
