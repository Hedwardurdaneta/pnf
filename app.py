import flet as ft
import gspread
import openpyxl
import os
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURACIÓN E INFRAESTRUCTURA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Usamos el color de fondo sugerido anteriormente
COLOR_FONDO = "#8babf1" 
EXCEL_LOCAL = os.path.join(BASE_DIR, "Programacion.xlsx")
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")

# --- 2. GESTIÓN DE GOOGLE SHEETS ---
class UNERMB_Database:
    def __init__(self):
        self.sheet = self._conectar()

    def _conectar(self):
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        try:
            if os.path.exists(CREDS_JSON):
                creds = Credentials.from_service_account_file(CREDS_JSON, scopes=scope)
                client = gspread.authorize(creds)
                # Conexión directa a su hoja según captura
                return client.open("Ingenieria de software II").worksheet("Notas_PNF_UNERMB")
        except Exception as e:
            print(f"Error de conexión: {e}")
        return None

    def registrar_nota(self, cedula, unidad, nota):
        if not self.sheet: return False
        try:
            # Buscamos en Columna B (Cédulas)
            lista_cedulas = self.sheet.col_values(2)
            ced_buscar = str(cedula).strip()
            
            if ced_buscar in lista_cedulas:
                fila = lista_cedulas.index(ced_buscar) + 1
                # Mapeo: UNIDAD I -> D(4), II -> E(5), III -> F(6)
                columna = {"UNIDAD I": 4, "UNIDAD II": 5, "UNIDAD III": 6}.get(unidad, 4)
                self.sheet.update_cell(fila, columna, nota)
                return True
        except: pass
        return False

db_unermb = UNERMB_Database()

# --- 3. BANCO DE CONTENIDO ACADÉMICO COMPLETO ---
BANCO_DATOS = {
    "UNIDAD I: Fundamentos": {
        "material": {
            "Algoritmo": "Secuencia finita de instrucciones para resolver un problema.",
            "IDE": "Entorno de Desarrollo Integrado (ej. VS Code, PyCharm).",
            "Depuración": "Proceso de encontrar y corregir errores en el código.",
            "Compilación": "Traducción del código fuente a lenguaje máquina.",
            "Software": "Conjunto de programas, instrucciones y reglas informáticas."
        },
        "examen": [
            ("¿Qué es un algoritmo?", ["Pasos lógicos", "Hardware", "Un virus"], "Pasos lógicos"),
            ("¿Qué significa IDE?", ["Entorno de Desarrollo", "Internet", "Disco Duro"], "Entorno de Desarrollo"),
            ("¿La depuración sirve para?", ["Corregir errores", "Borrar archivos", "Instalar Office"], "Corregir errores"),
            ("¿Qué es el Software?", ["Parte lógica", "Teclado y Mouse", "Cables"], "Parte lógica"),
            ("¿La compilación traduce a?", ["Código máquina", "Español", "Imagen PNG"], "Código máquina"),
            ("¿Qué es la sintaxis?", ["Reglas de escritura", "Un procesador", "Una variable"], "Reglas de escritura"),
            ("¿El Hardware es?", ["Parte física", "Un algoritmo", "Un programa"], "Parte física"),
            ("¿Un comentario sirve para?", ["Documentar código", "Ejecutar procesos", "Sumar"], "Documentar código"),
            ("¿Dónde se aloja una variable?", ["Memoria RAM", "Monitor", "Impresora"], "Memoria RAM"),
            ("¿Qué es el código fuente?", ["Texto del programa", "Electricidad", "El BIOS"], "Texto del programa")
        ]
    },
    "UNIDAD II: Estructuras": {
        "material": {
            "int": "Tipo de dato para números enteros.",
            "float": "Tipo de dato para números con decimales.",
            "str": "Cadenas de caracteres o texto.",
            "bool": "Valores lógicos (Verdadero o Falso).",
            "Listas": "Colecciones ordenadas y mutables de elementos."
        },
        "examen": [
            ("¿Qué guarda el tipo 'int'?", ["Enteros", "Decimales", "Texto"], "Enteros"),
            ("¿Qué guarda 'float'?", ["Decimales", "Enteros", "Booleanos"], "Decimales"),
            ("¿Qué representa 'str'?", ["Texto", "Números", "Imágenes"], "Texto"),
            ("¿Valores de 'bool'?", ["True/False", "1 al 100", "A, B, C"], "True/False"),
            ("¿Una lista es?", ["Colección de datos", "Una sola variable", "Un error"], "Colección de datos"),
            ("¿Símbolo de asignación?", ["=", "==", "++"], "="),
            ("¿Qué hace 'if'?", ["Evalúa condición", "Repite código", "Suma"], "Evalúa condición"),
            ("¿Qué es 'while'?", ["Bucle condicional", "Una constante", "Un botón"], "Bucle condicional"),
            ("¿Qué es 'for'?", ["Bucle iterativo", "Una resta", "Un comentario"], "Bucle iterativo"),
            ("¿El símbolo '==' sirve para?", ["Comparar", "Asignar", "Dividir"], "Comparar")
        ]
    },
    "UNIDAD III: Interfaces": {
        "material": {
            "Flet": "Framework para crear apps interactivas en Python.",
            "Widget": "Componente básico de la interfaz de usuario.",
            "Container": "Elemento para agrupar y dar estilo a otros controles.",
            "Evento": "Acción que dispara un proceso (ej. on_click).",
            "UX": "Experiencia del usuario al interactuar con el sistema."
        },
        "examen": [
            ("¿Flet se basa en?", ["Flutter", "Java", "C++"], "Flutter"),
            ("¿Qué es un Widget?", ["Componente UI", "Un cable", "Un virus"], "Componente UI"),
            ("¿'on_click' es un?", ["Evento", "Tipo de dato", "Hardware"], "Evento"),
            ("¿Qué hace un TextField?", ["Recibe texto", "Muestra videos", "Apaga PC"], "Recibe texto"),
            ("¿El Container sirve para?", ["Agrupar y diseñar", "Sumar", "Navegar"], "Agrupar y diseñar"),
            ("¿Qué es un Label?", ["Texto estático", "Entrada de datos", "Imagen"], "Texto estático"),
            ("¿UX se refiere a?", ["Experiencia Usuario", "Unidad X", "Uso Externo"], "Experiencia Usuario"),
            ("¿Qué es el Layout?", ["Organización visual", "El color", "El código"], "Organización visual"),
            ("¿'page.update()' sirve para?", ["Refrescar cambios", "Cerrar app", "Borrar todo"], "Refrescar cambios"),
            ("¿Qué es un ElevatedButton?", ["Un botón", "Un texto", "Un fondo"], "Un botón")
        ]
    }
}

# --- 4. LÓGICA DE LA APLICACIÓN (UI) ---
def main(page: ft.Page):
    page.title = "Portal Educativo UNERMB - Ing. Hedwar Urdaneta"
    page.bgcolor = COLOR_FONDO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 20
    
    state = {"user": None, "ced": None, "uni": None, "pts": 0, "idx": 0}

    def login():
        page.clean()
        alumnos = {}
        if os.path.exists(EXCEL_LOCAL):
            try:
                wb = openpyxl.load_workbook(EXCEL_LOCAL, data_only=True)
                ws = wb.active
                for r in range(2, 60):
                    n = ws.cell(r, 3).value
                    c = ws.cell(r, 2).value
                    if n: alumnos[str(n)] = str(c)
            except: pass

        dd = ft.Dropdown(label="Seleccione su Nombre", width=400, bgcolor="white",
                         options=[ft.dropdown.Option(n) for n in alumnos.keys()])
        tf = ft.TextField(label="Cédula", password=True, width=400, bgcolor="white")

        def ingresar(e):
            if dd.value in alumnos and alumnos[dd.value] == tf.value:
                state.update({"user": dd.value, "ced": tf.value})
                menu()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Datos Incorrectos"))
                page.snack_bar.open = True
                page.update()

        page.add(ft.Text("PORTAL ACADÉMICO UNERMB", size=32, weight="bold", color="white"),
                 dd, tf, ft.ElevatedButton("ENTRAR", on_click=ingresar, width=200, height=50))

    def menu():
        page.clean()
        page.add(ft.Text(f"Bienvenido: {state['user']}", size=24, color="white"),
                 *[ft.ElevatedButton(u, on_click=lambda e, u=u: unidad(u), width=350, height=50) 
                   for u in BANCO_DATOS.keys()],
                 ft.TextButton("Cerrar Sesión", on_click=lambda _: login(), style=ft.ButtonStyle(color="white")))

    def unidad(u):
        state["uni"] = u
        page.clean()
        material = BANCO_DATOS[u]["material"]
        items = [ft.ListTile(title=ft.Text(t, color="white"), subtitle=ft.Text(d, color="#eeeeee")) 
                 for t, d in material.items()]
        
        page.add(ft.Text(u, size=28, color="white", weight="bold"),
                 ft.Container(content=ft.Column(items, scroll="auto"), height=300, width=550, 
                              bgcolor="#44000000", border_radius=15, padding=10),
                 ft.ElevatedButton("INICIAR EXAMEN (10 Preguntas)", on_click=lambda _: empezar_test(), 
                                   bgcolor="green", color="white", width=300, height=50))

    def empezar_test():
        state.update({"idx": 0, "pts": 0})
        mostrar_pregunta()

    def mostrar_pregunta():
        page.clean()
        preguntas = BANCO_DATOS[state["uni"]]["examen"]
        if state["idx"] < len(preguntas):
            p, opts, corr = preguntas[state["idx"]]
            
            def verificar(opcion):
                if opcion == corr: state["pts"] += 1
                state["idx"] += 1
                mostrar_pregunta()

            page.add(ft.Text(f"Pregunta {state['idx']+1} de 10", color="white"),
                     ft.Container(content=ft.Text(p, size=22, weight="bold", text_align="center"),
                                  bgcolor="white", padding=20, border_radius=10, width=600),
                     *[ft.ElevatedButton(o, on_click=lambda e, o=o: verificar(o), width=400) for o in opts])
        else:
            finalizar()

    def finalizar():
        page.clean()
        res_text = ft.Text("Sincronizando con la nube...", color="white", italic=True)
        page.add(ft.Text("EVALUACIÓN FINALIZADA", size=26, color="white"),
                 ft.Text(f"Nota: {state['pts']}/10", size=70, color="yellow", weight="bold"),
                 res_text)
        page.update()

        # Guardado en Google Sheets
        exito = db_unermb.registrar_nota(state["ced"], state["uni"].split(":")[0], state["pts"])
        res_text.value = "✅ Nota registrada con éxito" if exito else "⚠️ Error al conectar con Google Sheets"
        res_text.color = "green" if exito else "red"
        page.add(ft.ElevatedButton("VOLVER AL MENÚ", on_click=lambda _: menu(), width=250))
        page.update()

    login()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)
