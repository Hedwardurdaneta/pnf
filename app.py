import flet as ft
import gspread
import openpyxl
import os
import random
import time
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIGURACIÓN DE RUTAS Y CONSTANTES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONO_PATH = "icono.ico" 
FONDO_PATH = "fondo.png"
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json")

# --- 2. PERSISTENCIA EN GOOGLE SHEETS ---
def guardar_en_nube(nombre_alumno, unidad, puntos):
    """
    Registra la calificación en la hoja de cálculo de Google.
    Busca al alumno en la columna C y actualiza D, E o F.
    """
    alcance = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if not os.path.exists(CREDS_PATH):
            print("Error: credentials.json no encontrado.")
            return False

        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, alcance)
        cliente = gspread.authorize(creds)
        
        # Apertura del documento según sus capturas previas
        hoja_principal = cliente.open("Ingenieria de software II")
        hoja = hoja_principal.worksheet("Notas_PNF_UNERMB")
        
        # Obtención de nombres para localizar la fila
        lista_nombres = hoja.col_values(3) 
        
        if nombre_alumno in lista_nombres:
            fila = lista_nombres.index(nombre_alumno) + 1
            # Mapeo de columnas de evaluación
            mapeo_columnas = {
                "UNIDAD I": 4,   # Columna D
                "UNIDAD II": 5,  # Columna E
                "UNIDAD III": 6  # Columna F
            }
            columna = mapeo_columnas.get(unidad)
            
            if columna:
                hoja.update_cell(fila, columna, puntos)
                return True
        return False
            
    except Exception as e:
        print(f"Error en la conexión con la nube: {e}")
        return False

# --- 3. GESTIÓN DEL ESTADO Y BANCO DE PREGUNTAS ---
state = {
    "alumno": None, 
    "unidad": None, 
    "idx": 0, 
    "puntos": 0,
    "intentos": 0
}

# Banco de preguntas detallado para mantener la extensión y lógica del proyecto
preguntas = {
    "UNIDAD I": [
        ("¿Qué es un algoritmo?", ["Pasos lógicos", "Hardware", "Un error", "Virus"], "Pasos lógicos"),
        ("¿Qué es el Hardware?", ["Componentes físicos", "Programas", "Internet", "Nube"], "Componentes físicos"),
        ("¿Qué es el Software?", ["Sistemas y programas", "Cables", "Monitor", "Teclado"], "Sistemas y programas"),
        ("¿Qué significa IDE?", ["Entorno de desarrollo", "Disco duro", "Protocolo", "Puerto"], "Entorno de desarrollo"),
        ("¿Qué es la sintaxis?", ["Reglas del lenguaje", "Un cable", "Monitor", "Energía"], "Reglas del lenguaje"),
        ("¿Qué es un compilador?", ["Traductor de código", "Un virus", "Hardware", "Navegador"], "Traductor de código")
    ],
    "UNIDAD II": [
        ("¿Qué guarda el tipo 'int'?", ["Números enteros", "Texto", "Decimales", "Booleanos"], "Números enteros"),
        ("¿Qué guarda el tipo 'str'?", ["Cadenas de texto", "Números", "Listas", "Diccionarios"], "Cadenas de texto"),
        ("¿Qué guarda el tipo 'float'?", ["Números decimales", "Enteros", "Texto", "Binario"], "Números decimales"),
        ("¿Qué es un 'if'?", ["Estructura condicional", "Un bucle", "Una variable", "Una función"], "Estructura condicional"),
        ("¿Qué es un 'for'?", ["Bucle definido", "Una suma", "Un condicional", "Una constante"], "Bucle definido"),
        ("¿Qué es una función?", ["Bloque reutilizable", "Un error", "Un tipo de dato", "Una variable"], "Bloque reutilizable")
    ],
    "UNIDAD III": [
        ("¿Qué es Flet?", ["Framework de UI", "Base de datos", "Sistema operativo", "Hardware"], "Framework de UI"),
        ("¿Qué es un Widget?", ["Elemento de interfaz", "Un virus", "Un cable", "Un servidor"], "Elemento de interfaz"),
        ("¿Qué es el Layout?", ["Organización visual", "Un color", "Un tipo de letra", "Una base"], "Organización visual"),
        ("¿Qué es un evento?", ["Acción del usuario", "Un error", "Un proceso", "Un comando"], "Acción del usuario"),
        ("¿Qué es un TextField?", ["Campo de entrada", "Un botón", "Una imagen", "Un audio"], "Campo de entrada"),
        ("¿Qué es un Container?", ["Caja de diseño", "Un bucle", "Una red", "Un archivo"], "Caja de diseño")
    ]
}

# --- 4. INTERFAZ GRÁFICA ---
def main(page: ft.Page):
    # Configuración de la ventana principal
    page.title = "Portal Académico PNF - UNERMB"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # CORRECCIÓN DE ALINEACIÓN: Se usan las constantes correctas para evitar el error 'center'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def layout_contenedor(elementos):
        """Genera la estructura visual con fondo para cada vista."""
        return ft.Container(
            content=ft.Column(
                elementos, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                alignment=ft.MainAxisAlignment.CENTER, 
                spacing=25
            ),
            expand=True,
            image_src=FONDO_PATH,
            image_fit=ft.ImageFit.COVER, # Corregido: Llamada directa al atributo
            alignment=ft.alignment.center,
        )

    def menu_principal():
        page.clean()
        page.add(layout_contenedor([
            ft.Text(f"SESIÓN INICIADA: {state['alumno']}", size=22, color="white", weight="bold"),
            ft.Text("SELECCIONE LA UNIDAD A EVALUAR", size=16, color="#d1d1d1"),
            ft.Divider(height=10, color="transparent"),
            ft.FilledButton("EVALUACIÓN: UNIDAD I", on_click=lambda _: ir_a_unidad("UNIDAD I"), width=350, height=50),
            ft.FilledButton("EVALUACIÓN: UNIDAD II", on_click=lambda _: ir_a_unidad("UNIDAD II"), width=350, height=50),
            ft.FilledButton("EVALUACIÓN: UNIDAD III", on_click=lambda _: ir_a_unidad("UNIDAD III"), width=350, height=50),
            ft.TextButton("CERRAR SESIÓN", on_click=lambda _: login_view(), style=ft.ButtonStyle(color="white"))
        ]))

    def ejecutar_examen():
        page.clean()
        u = state["unidad"]
        if state["idx"] < len(preguntas[u]):
            p, opciones, correcta = preguntas[u][state["idx"]]
            random.shuffle(opciones)
            
            def procesar_respuesta(seleccion):
                if seleccion == correcta:
                    state["puntos"] += 1
                state["idx"] += 1
                ejecutar_examen()

            page.add(layout_contenedor([
                ft.Text(f"{u} - PREGUNTA {state['idx'] + 1}", color="#aed6f1", size=18, weight="bold"),
                ft.Text(p, size=26, color="white", text_align="center", weight="w500"),
                ft.Column([
                    ft.FilledButton(opt, on_click=lambda e, opt=opt: procesar_respuesta(opt), width=400, height=45)
                    for opt in opciones
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ]))
        else:
            # Proceso de guardado al finalizar
            page.add(layout_contenedor([ft.ProgressRing(), ft.Text("Guardando nota...", color="white")]))
            exito = guardar_en_nube(state["alumno"], state["unidad"], state["puntos"])
            
            page.clean()
            resultado_texto = "Nota sincronizada con éxito" if exito else "Nota guardada localmente (Error de nube)"
            page.add(layout_contenedor([
                ft.Icon(ft.icons.CHECK_CIRCLE if exito else ft.icons.WARNING, color="white", size=80),
                ft.Text("EVALUACIÓN FINALIZADA", size=24, color="white", weight="bold"),
                ft.Text(f"PUNTUACIÓN: {state['puntos']} / {len(preguntas[u])}", size=50, color="white"),
                ft.Text(resultado_texto, color="#d1d1d1"),
                ft.FilledButton("VOLVER AL MENÚ", on_click=lambda _: menu_principal(), width=250)
            ]))

    def ir_a_unidad(u):
        state.update({"unidad": u, "idx": 0, "puntos": 0})
        page.clean()
        page.add(layout_contenedor([
            ft.Text(f"SISTEMA DE EVALUACIÓN: {u}", size=28, weight="bold", color="white"),
            ft.Text("Usted está por iniciar una prueba técnica.", color="white"),
            ft.Text("Las notas se enviarán automáticamente al docente.", color="#bdc3c7"),
            ft.FilledButton("COMENZAR AHORA", on_click=lambda _: ejecutar_examen(), width=300, height=55),
            ft.TextButton("Cancelar", on_click=lambda _: menu_principal(), style=ft.ButtonStyle(color="white"))
        ]))

    def login_view():
        page.clean()
        # Credenciales por defecto si el Excel falla
        usuarios_db = {"Admin": "1234"}
        
        if os.path.exists(EXCEL_PATH):
            try:
                workbook = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
                hoja_excel = workbook.active
                # Columna C (3) = Nombres, Columna B (2) = Cédula/Pass
                usuarios_db = {str(hoja_excel.cell(r, 3).value): str(hoja_excel.cell(r, 2).value) 
                               for r in range(2, 60) if hoja_excel.cell(r, 3).value}
            except Exception as e:
                print(f"Error cargando Excel: {e}")

        drop_user = ft.Dropdown(
            label="Seleccione su nombre",
            width=350,
            options=[ft.dropdown.Option(nombre) for nombre in usuarios_db.keys()],
            border_color="white",
            label_style=ft.TextStyle(color="white")
        )
        
        txt_pass = ft.TextField(
            label="Cédula de Identidad",
            password=True,
            can_reveal_password=True,
            width=350,
            border_color="white",
            label_style=ft.TextStyle(color="white")
        )

        def intentar_login(e):
            if drop_user.value in usuarios_db and usuarios_db[drop_user.value] == txt_pass.value:
                state["alumno"] = drop_user.value
                menu_principal()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Credenciales no coinciden. Intente de nuevo."))
                page.snack_bar.open = True
                page.update()

        page.add(layout_contenedor([
            ft.Image(src=ICONO_PATH, width=130),
            ft.Text("INGENIERÍA DE SOFTWARE II", size=30, weight="bold", color="white"),
            ft.Text("Portal UNERMB - Acceso Estudiantil", color="#d1d1d1"),
            drop_user,
            txt_pass,
            ft.FilledButton("INICIAR SESIÓN", on_click=intentar_login, width=250, height=50)
        ]))

    login_view()

# --- 5. LANZAMIENTO ---
if __name__ == "__main__":
    # Configuración de puerto y directorio de activos para Railway
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", port=8080)
