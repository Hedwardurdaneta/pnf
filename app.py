import flet as ft
import gspread
import openpyxl
import os
import random
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# En la web, Flet busca los assets en la subcarpeta 'assets'
ICONO_PATH = "/icono.ico" 
FONDO_PATH = "/fondo.png"
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")
# Ajustado al nombre real visto en su GitHub (image_0ceda2.png)
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json.json")

# --- 2. PERSISTENCIA EN LA NUBE ---
def guardar_en_nube(nombre_alumno, unidad, puntos):
    alcance = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if not os.path.exists(CREDS_PATH):
            print(f"Error: No existe el archivo {CREDS_PATH}")
            return False

        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, alcance)
        cliente = gspread.authorize(creds)
        
        hoja_principal = cliente.open("Ingenieria de software II")
        hoja = hoja_principal.worksheet("Notas_PNF_UNERMB")
        
        # Columna C es donde están los nombres según su imagen image_0c7d60.png
        lista_nombres = hoja.col_values(3) 
        
        try:
            # Buscamos la fila exacta del alumno
            fila = lista_nombres.index(nombre_alumno) + 1
            # Mapeo de columnas: NOTA1=D(4), NOTA2=E(5), NOTA3=F(6)
            columna = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad)
            
            if columna:
                hoja.update_cell(fila, columna, puntos)
                return True
        except ValueError:
            return False
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False

# --- 3. ESTADO Y CONTENIDO ---
state = {"alumno": None, "unidad": None, "idx": 0, "puntos": 0}

contenido = {
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

preguntas = {
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

# --- 4. INTERFAZ ---
def main(page: ft.Page):
    page.title = "Portal Educativo UNERMB"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0

    def layout_con_fondo(contenido_vista):
        return ft.Container(
            content=ft.Column(contenido_vista, horizontal_alignment="center", alignment="center", spacing=20),
            expand=True,
            image=ft.DecorationImage(src=FONDO_PATH, fit=ft.ImageFit.COVER),
            alignment=ft.alignment.center,
        )

    def menu_principal():
        page.clean()
        page.add(layout_con_fondo([
            ft.Text(f"Bienvenido: {state['alumno']}", size=28, color="white", weight="bold"),
            ft.FilledButton("UNIDAD I", on_click=lambda _: mostrar_unidad("UNIDAD I"), width=320),
            ft.FilledButton("UNIDAD II", on_click=lambda _: mostrar_unidad("UNIDAD II"), width=320),
            ft.FilledButton("UNIDAD III", on_click=lambda _: mostrar_unidad("UNIDAD III"), width=320),
            ft.TextButton("Cerrar Sesión", on_click=lambda _: login_view(), style=ft.ButtonStyle(color="white"))
        ]))

    def lanzar_pregunta():
        page.clean()
        u = state["unidad"]
        if state["idx"] < len(preguntas[u]):
            p, opciones_orig, correcta = preguntas[u][state["idx"]]
            opciones = list(opciones_orig)
            random.shuffle(opciones)
            
            def validar(res):
                if res == correcta: state["puntos"] += 1
                state["idx"] += 1
                lanzar_pregunta()
                
            page.add(layout_con_fondo([
                ft.Text(f"Pregunta {state['idx']+1}/10", color="#a3e4d7"),
                ft.Text(p, size=26, color="white", text_align="center"),
                *[ft.FilledButton(o, on_click=lambda e, o=o: validar(o), width=350) for o in opciones]
            ]))
        else:
            guardar_en_nube(state["alumno"], state["unidad"], state["puntos"])
            page.add(layout_con_fondo([
                ft.Text("Evaluación Finalizada", size=24, color="white"),
                ft.Text(f"Nota: {state['puntos']}/10", size=70, color="white", weight="bold"),
                ft.FilledButton("VOLVER AL MENÚ", on_click=lambda _: menu_principal())
            ]))

    def mostrar_unidad(u):
        state["unidad"], state["idx"], state["puntos"] = u, 0, 0
        page.clean()
        temas = [ft.ListTile(title=ft.Text(t, color="white")) for t in contenido[u].keys()]
        page.add(layout_con_fondo([
            ft.Text(u, size=30, weight="bold", color="white"),
            ft.Container(content=ft.Column(temas, scroll="auto"), height=300, width=400, bgcolor="#66000000", border_radius=15),
            ft.FilledButton("INICIAR EVALUACIÓN", on_click=lambda _: lanzar_pregunta(), width=280)
        ]))

    def login_view():
        page.clean()
        datos = {"Admin": "1234"}
        if os.path.exists(EXCEL_PATH):
            wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
            sh = wb.active
            datos = {str(sh.cell(r, 3).value): str(sh.cell(r, 2).value) for r in range(2, 51) if sh.cell(r, 3).value}

        user_drop = ft.Dropdown(label="Usuario", width=320, options=[ft.dropdown.Option(n) for n in datos.keys()])
        pass_field = ft.TextField(label="Cédula", password=True, width=320, can_reveal_password=True)

        def ingresar(e):
            if user_drop.value in datos and datos[user_drop.value] == pass_field.value:
                state["alumno"] = user_drop.value
                menu_principal()
                page.update()

        page.add(layout_con_fondo([
            ft.Image(src=ICONO_PATH, width=100),
            ft.Text("PORTAL DE ACCESO", size=30, color="white", weight="bold"),
            user_drop, pass_field, 
            ft.FilledButton("INGRESAR", on_click=ingresar, width=220)
        ]))

    login_view()

if __name__ == "__main__":
    # Importante: assets_dir="assets" para que encuentre las imágenes
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", port=8080)
