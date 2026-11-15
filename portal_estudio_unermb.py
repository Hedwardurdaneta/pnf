import flet as ft
import openpyxl
import os
import random
import asyncio
import json
import threading

# --- 1. CONFIGURACIÓN DE RUTAS Y PALETA INSTITUCIONAL UNERMB ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_UNERMB_PATH = "logo_unermb.png"  # Guardar el logo de la UNERMB en la carpeta 'assets'
FONDO_PATH = "fondo_v2.png"   # copiar assets/fondo.png como assets/fondo_v2.png (nombre nuevo evita la caché)
AUTOR = "Prof. MSc. Hedwar Urdaneta"
PROYECTO = "Innovación Digital como Herramienta en la Educación Universitaria:\nUna Visión Transformadora"
EXCEL_PATH = os.path.join(BASE_DIR, "Programacion.xlsx")

# Paleta de colores institucionales (Azul Marino UNERMB, Azul Académico, Dorado y Neutros)
COLOR_PRIMARIO = "#0A2540"       # Azul marino institucional profundo
COLOR_SECUNDARIO = "#1B4F72"     # Azul académico
COLOR_ACENTO = "#D4AC0D"         # Dorado institucional
COLOR_EXITO = "#1E8449"          # Verde esmeralda
COLOR_ERROR = "#922B21"          # Rojo carmesí
COLOR_TARJETA = "#F8F9F9"        # Blanco humo para tarjetas limpias
COLOR_TEXTO_OSCURO = "#1C2833"   # Gris carbón para alta legibilidad

# --- 2. REGISTRO DE ALUMNOS ACTUALIZADO (CÉDULA -> NOMBRE) ---
ADMIN_CEDULA = os.environ.get("ADMIN_CEDULA", "1234")  # en la nube: definir como secreto

def cargar_alumnos() -> dict:
    """Registro desde el secreto ALUMNOS_JSON (nube) o desde alumnos.json (local). Nunca va en el repositorio."""
    try:
        if os.environ.get("ALUMNOS_JSON"):
            datos = json.loads(os.environ["ALUMNOS_JSON"])
        else:
            with open(os.path.join(BASE_DIR, "alumnos.json"), encoding="utf-8") as f:
                datos = json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo cargar el registro de alumnos: {e}")
        datos = {}
    datos[ADMIN_CEDULA] = "ADMINISTRADOR"
    return datos

ALUMNOS = cargar_alumnos()

# --- 3. BANCO DE DATOS: INGENIERÍA DEL SOFTWARE II ---
contenido = {
    "Unidad 1: Modelado de Negocio": {
        "Procesos de negocio": "Conjunto estructurado de tareas y actividades relacionadas entre sí que producen un servicio o producto de valor para un cliente o usuario específico dentro de la organización.",
        "Actividades del negocio": "Pasos operativos concretos y atómicos que componen un proceso de negocio, ejecutados por personas o sistemas para transformar entradas en salidas.",
        "Reglas del Negocio": "Políticas, condiciones, restricciones o normativas que definen cómo debe operar la organización y qué decisiones son válidas dentro de sus procesos.",
        "Actores del Negocio": "Personas, cargos, departamentos o sistemas externos que interactúan con la organización participando o beneficiándose de sus procesos de negocio.",
        "Objetos del Negocio": "Entidades, documentos, recursos o información clave (como facturas, pedidos, expedientes o productos) que son creados, manipulados o consumidos durante los procesos."
    },
    "Unidad 2: Ingeniería de Requisitos": {
        "¿Qué son Requisitos?": "Condiciones, capacidades o características que debe cumplir un sistema de software para satisfacer una necesidad del usuario o cumplir con un contrato o estándar.",
        "Tipos de requisitos: funcionales, no- funcionales, otros": "Funcionales: describen qué debe hacer el sistema (funciones y servicios). No funcionales: definen restricciones y propiedades (rendimiento, seguridad, usabilidad). Otros: requisitos de dominio o legales.",
        "Atributos de calidad": "Propiedades medibles que determinan la excelencia del software más allá de sus funciones básicas, tales como confiabilidad, disponibilidad, mantenibilidad, portabilidad y eficiencia.",
        "Necesidades, objetivos y actores relacionados con los requisitos": "Los actores (stakeholders) expresan necesidades del problema; de ellas se derivan los objetivos del proyecto que luego se formalizan en requisitos técnicos.",
        "Fases de la ingeniería de requisitos: elicitación, modelado, análisis y gestión": "Elicitación (recolección con usuarios), Modelado (representación conceptual), Análisis (negociación y detección de fallos) y Gestión (control de cambios y trazabilidad).",
        "Técnicas para el levantamiento y recolección de requisitos (Joint Application Design, JAD)": "Métodos para obtener información de los interesados, destacando JAD: sesiones intensivas y estructuradas donde usuarios, analistas y desarrolladores definen juntos los requisitos."
    },
    "Unidad 3: Análisis y especificación de Requisitos": {
        "Características de requisitos: inspección, validación, completitud, detección de conflictos e inconsistencias": "Revisión rigurosa para asegurar que los requisitos sean completos, verificables y consistentes, detectando y resolviendo contradicciones entre lo que piden distintos usuarios.",
        "Tipos de especificación: textual, notación gráfica y lenguajes de representación (UML y URN)": "Formas de documentar requisitos: lenguaje natural estructurado (textual), diagramas visuales usando UML (Lenguaje Unificado de Modelado) y URN (Notación de Requerimientos de Usuario).",
        "Estándares para escribir requisitos de alta calidad": "Normativas internacionales (como IEEE 830 / ISO 29148) que establecen que cada requisito debe ser claro, no ambiguo, atómico, verificable, consistente y trazable.",
        "Documento de Requisitos (DRS)": "Documento oficial de Especificación de Requisitos de Software que consolida de forma ordenada todos los requisitos funcionales y no funcionales acordados con el cliente.",
        "Métricas de modelado de Análisis": "Indicadores cuantitativos que evalúan la complejidad, tamaño, calidad y estabilidad de los modelos de análisis antes de pasar a la fase de diseño y programación."
    }
}

# --- 3B. RESÚMENES DE ESTUDIO (mismo orden que 'contenido') ---
# (idea clave, [3 puntos], ejemplo)
RESUMEN = {
    "Unidad 1: Modelado de Negocio": [
        ("Secuencia de actividades que transforma entradas en un producto o servicio de valor.", ["Tiene inicio, fin y un cliente", "Se compone de actividades", "Se modela antes de diseñar el software"], "Proceso «Vender»: recibir pedido → cobrar → despachar."),
        ("Paso concreto e indivisible dentro de un proceso.", ["Lo ejecutan personas o sistemas", "Responde a: ¿qué se hace?", "Varias actividades forman un proceso"], "«Verificar inventario», «Empaquetar producto»."),
        ("Política o condición que define qué decisiones son válidas.", ["Suelen ser «si… entonces…»", "Restringen o guían el proceso", "Cambian con la política de la organización"], "Compras de más de 100$ tienen 10% de descuento."),
        ("Quien interactúa con el proceso o se beneficia de él.", ["Personas, cargos, departamentos o sistemas externos", "Internos (empleados) o externos (clientes)", "No son los objetos que se manipulan"], "Cliente, cajero, Departamento de Ventas."),
        ("Información o recurso que se crea, usa o transforma en los procesos.", ["Son los «sustantivos» del negocio", "Suelen ser documentos o entidades", "Pasan de actividad en actividad"], "Factura, pedido, expediente."),
    ],
    "Unidad 2: Ingeniería de Requisitos": [
        ("Condición o capacidad que el sistema debe cumplir para satisfacer una necesidad.", ["Nacen de necesidades de los usuarios", "También pueden venir de un contrato o estándar", "Deben ser claros y verificables"], "«El sistema debe emitir facturas en PDF»."),
        ("Funcional = QUÉ hace el sistema; no funcional = CÓMO lo hace.", ["Funcionales: funciones y servicios", "No funcionales: rendimiento, seguridad, usabilidad", "Otros: de dominio o legales"], "«Transferir fondos» (F) · «responder en < 2 s» (NF)."),
        ("Propiedades medibles que indican qué tan bien funciona el software.", ["Confiabilidad, disponibilidad, mantenibilidad", "Portabilidad y eficiencia", "Son requisitos no funcionales medibles"], "Disponibilidad del 99,5% mensual."),
        ("Necesidad → objetivo → requisito.", ["Actores (stakeholders): quienes tienen la necesidad", "Objetivo: lo que se quiere lograr", "Requisito: lo que el sistema debe cumplir"], "Cobrar más rápido → pago en línea → integrar pasarela de pago."),
        ("Cuatro fases: Elicitación → Modelado → Análisis → Gestión.", ["Elicitación: recolectar con usuarios; Modelado: representar", "Análisis: negociar y detectar fallos", "Gestión: control de cambios y trazabilidad"], "Tras las entrevistas dibujas diagramas (modelado) y luego buscas contradicciones (análisis)."),
        ("JAD: talleres intensivos donde usuarios y analistas definen juntos los requisitos.", ["Otras técnicas: entrevistas, encuestas, observación", "Usa un facilitador y sesiones estructuradas", "Acelera acuerdos y reduce malentendidos"], "3 días en una sala con gerentes, cajeros y programadores para definir un POS."),
    ],
    "Unidad 3: Análisis y especificación de Requisitos": [
        ("Un buen conjunto de requisitos es completo, consistente y verificable.", ["Inspección y validación: revisar con el cliente", "Completitud: no falta información", "Conflicto: dos requisitos que se contradicen"], "Req. 12 exige huella digital; Req. 45 prohíbe lectores biométricos."),
        ("Se documenta con texto, gráficos o lenguajes de modelado.", ["Textual: lenguaje natural estructurado", "Gráfica: diagramas", "UML (casos de uso, clases) y URN (objetivos y escenarios)"], "Diagrama de casos de uso del sistema de citas."),
        ("Cada requisito debe ser claro, atómico, verificable y trazable.", ["Referencias: IEEE 830 / ISO 29148", "Evitar palabras vagas: «rápido», «amigable»", "Una sola idea por requisito"], "Mal: «muy rápido». Bien: «responde en menos de 2 s»."),
        ("Documento oficial que reúne todos los requisitos acordados con el cliente.", ["Incluye funcionales y no funcionales", "Sirve de contrato técnico", "Es la base del diseño y las pruebas"], "Estructura típica: introducción, descripción general, requisitos específicos."),
        ("Números que miden tamaño, complejidad y calidad de los modelos de análisis.", ["Se aplican antes del diseño", "Ayudan a estimar esfuerzo", "Detectan modelos demasiado complejos"], "Contar casos de uso para estimar el tamaño del sistema."),
    ],
}
for _u in contenido:
    assert len(RESUMEN[_u]) == len(contenido[_u]), _u

MNEMO = {
    "Unidad 1: Modelado de Negocio": "PARAO = Procesos · Actividades · Reglas · Actores · Objetos. Actor = quién · Actividad = qué hace · Objeto = con qué · Regla = bajo qué condición.",
    "Unidad 2: Ingeniería de Requisitos": "EMAG = Elicitar · Modelar · Analizar · Gestionar. Funcional = QUÉ; No funcional = CÓMO.",
    "Unidad 3: Análisis y especificación de Requisitos": "Requisito de calidad = Claro + Atómico + Verificable + Trazable. Texto, gráfico, UML/URN.",
}

# --- 4. TALLER PRÁCTICO GUIADO ---
talleres = {
    "Unidad 1: Modelado de Negocio": [
        {
            "caso": "Caso de Estudio - Clínica: 'Un paciente solicita cita médica por la web; si tiene seguro activo, el sistema exonera el copago y emite un comprobante digital'. En este escenario, ¿qué elemento representa la condición 'si tiene seguro activo, se exonera el copago'?",
            "opciones": ["Regla del Negocio", "Actor del Negocio", "Objeto del Negocio"],
            "correcta": "Regla del Negocio",
            "explicacion": "Es una Regla del Negocio porque establece una política o condición operativa que gobierna la decisión dentro del proceso."
        },
        {
            "caso": "Caso de Estudio - Clínica: En el mismo escenario anterior, ¿qué representan el 'Paciente' y el 'Comprobante Digital' respectivamente?",
            "opciones": ["Actor del Negocio y Objeto del Negocio", "Proceso y Actividad", "Regla y Proceso"],
            "correcta": "Actor del Negocio y Objeto del Negocio",
            "explicacion": "El Paciente es un Actor externo que interactúa con el proceso, mientras que el Comprobante Digital es un Objeto de información generado."
        },
        {
            "caso": "Caso de Estudio - Almacén: 'Verificar inventario', 'Empaquetar producto' y 'Despachar pedido' son pasos operativos concretos realizados por el personal. ¿Cómo se clasifican?",
            "opciones": ["Actividades del negocio", "Objetos del negocio", "Actores del negocio"],
            "correcta": "Actividades del negocio",
            "explicacion": "Son Actividades del negocio: los pasos operativos específicos que en conjunto conforman el proceso completo de ventas."
        }
    ],
    "Unidad 2: Ingeniería de Requisitos": [
        {
            "caso": "Caso de Estudio - Banca Móvil: El cliente pide: 'La aplicación debe permitir transferir fondos entre cuentas y debe responder en menos de 2 segundos bajo 5.000 usuarios simultáneos'. ¿Cómo se dividen ambas exigencias?",
            "opciones": [
                "Transferir = Requisito Funcional | < 2 segundos = Requisito No Funcional",
                "Ambas son Requisitos Funcionales",
                "Transferir = Atributo de Calidad | < 2 segundos = Regla de Negocio"
            ],
            "correcta": "Transferir = Requisito Funcional | < 2 segundos = Requisito No Funcional",
            "explicacion": "Transferir fondos es una función del sistema (Funcional), mientras que el tiempo de respuesta mide rendimiento (No Funcional / Atributo de Calidad)."
        },
        {
            "caso": "Caso de Estudio - Levantamiento: El equipo de analistas reúne durante 3 días intensivos a gerentes, cajeros y programadores en una sala para consensuar pantallas y reglas de un nuevo POS. ¿Qué técnica aplican?",
            "opciones": ["Joint Application Design (JAD)", "Compilación incremental", "Métrica de complejidad ciclomática"],
            "correcta": "Joint Application Design (JAD)",
            "explicacion": "JAD consiste precisamente en talleres estructurados y colaborativos donde usuarios y desarrolladores definen juntos los requisitos."
        },
        {
            "caso": "Caso de Estudio - Ciclo de Requisitos: Ya recolectaste las entrevistas con los usuarios y dibujaste los diagramas conceptuales. Ahora debes detectar contradicciones y priorizar qué se construye primero. ¿En qué fase estás?",
            "opciones": ["Análisis de requisitos", "Elicitación de requisitos", "Codificación"],
            "correcta": "Análisis de requisitos",
            "explicacion": "En la fase de Análisis se evalúan, negocian y resuelven conflictos o inconsistencias entre los requisitos recolectados."
        }
    ],
    "Unidad 3: Análisis y especificación de Requisitos": [
        {
            "caso": "Auditoría DRS: Un analista escribe en el documento: 'El sistema debe ser muy rápido, intuitivo y agradable para cualquier usuario'. Según los estándares de calidad (IEEE 830 / ISO 29148), ¿cuál es el defecto principal?",
            "opciones": [
                "Es ambiguo y no es verificable cuantitativamente",
                "Es demasiado corto",
                "Usa lenguaje UML en lugar de texto"
            ],
            "correcta": "Es ambiguo y no es verificable cuantitativamente",
            "explicacion": "Palabras subjetivas como 'muy rápido' o 'agradable' impiden diseñar una prueba objetiva; un requisito de calidad debe ser medible y verificable."
        },
        {
            "caso": "Auditoría DRS: El Requisito #12 indica 'Todo usuario debe iniciar sesión con huella dactilar', pero el Requisito #45 indica 'El sistema operará exclusivamente en computadoras de escritorio sin lectores biométricos'. ¿Qué detectó la inspección?",
            "opciones": [
                "Un conflicto o inconsistencia entre requisitos",
                "Un atributo de portabilidad",
                "Una métrica de análisis exitosa"
            ],
            "correcta": "Un conflicto o inconsistencia entre requisitos",
            "explicacion": "Ambos requisitos se contradicen técnicamente; la inspección busca detectar estas inconsistencias antes de programar."
        },
        {
            "caso": "Documentación Técnica: Para representar visualmente los actores, casos de uso y flujos de interacción dentro del DRS utilizando un lenguaje estándar internacional, ¿qué herramienta empleas?",
            "opciones": ["Lenguaje Unificado de Modelado (UML)", "Hoja de cálculo de nómina", "Código binario puro"],
            "correcta": "Lenguaje Unificado de Modelado (UML)",
            "explicacion": "UML (y URN para objetivos/escenarios de usuario) es el estándar de notación gráfica para especificar modelos de análisis."
        }
    ]
}

# --- 5. BANCO DE EVALUACIÓN CRONOMETRADA ---
preguntas = {
    "Unidad 1: Modelado de Negocio": [
        ("¿Qué es un proceso de negocio?", ["Conjunto de tareas que generan valor", "Un lenguaje de programación", "Un cable de red"], "Conjunto de tareas que generan valor", "Un proceso de negocio articula tareas relacionadas para entregar un producto o servicio de valor."),
        ("¿Qué representan las actividades del negocio?", ["Pasos operativos concretos dentro de un proceso", "Los clientes externos", "El hardware del servidor"], "Pasos operativos concretos dentro de un proceso", "Las actividades son los pasos específicos que ejecutan personas o sistemas dentro de un proceso."),
        ("¿Cuál es la función de las reglas del negocio?", ["Definir políticas y restricciones operativas", "Diseñar la interfaz gráfica", "Compilar el código fuente"], "Definir políticas y restricciones operativas", "Las reglas del negocio establecen condiciones, normativas y límites en la toma de decisiones."),
        ("¿Quiénes son los actores del negocio?", ["Personas, cargos o sistemas que interactúan", "Solo los programadores", "Los archivos de base de datos"], "Personas, cargos o sistemas que interactúan", "Todo ente interno o externo que participa o se beneficia de un proceso es un Actor del Negocio."),
        ("¿Qué son los objetos del negocio?", ["Entidades o información manipulada en procesos", "Los monitores de la oficina", "Los errores de sintaxis"], "Entidades o información manipulada en procesos", "Los objetos de negocio son los recursos, documentos o datos que fluyen y se transforman."),
        ("¿Cuál es un ejemplo de objeto del negocio?", ["Una factura o pedido", "El teclado del analista", "Un bucle while"], "Una factura o pedido", "Una factura o pedido es un documento/entidad de información generada y procesada en el negocio."),
        ("¿Cuál es un ejemplo de regla del negocio?", ["Aplicar 10% de descuento a compras mayores a 100$", "Usar Python 3 para programar", "Guardar datos en memoria RAM"], "Aplicar 10% de descuento a compras mayores a 100$", "Es una política comercial condicionada que rige cómo debe ejecutarse una operación."),
        ("¿Para qué sirve el modelado de negocio?", ["Comprender cómo opera la organización", "Instalar el sistema operativo", "Formatear el disco duro"], "Comprender cómo opera la organización", "Permite mapear la estructura y dinámica actual de la empresa antes de diseñar software."),
        ("¿De qué está compuesto un proceso de negocio?", ["De actividades relacionadas entre sí", "De variables globales", "De tarjetas gráficas"], "De actividades relacionadas entre sí", "Un proceso se descompone en secuencias de actividades interconectadas."),
        ("¿Un departamento o cliente externo se considera?", ["Actor del negocio", "Objeto del negocio", "Atributo de calidad"], "Actor del negocio", "Tanto unidades organizativas internas como clientes externos actúan sobre los procesos.")
    ],
    "Unidad 2: Ingeniería de Requisitos": [
        ("¿Qué son los requisitos en ingeniería de software?", ["Condiciones y capacidades que debe cumplir el sistema", "Solo los colores de la pantalla", "Los manuales de hardware"], "Condiciones y capacidades que debe cumplir el sistema", "Definen lo que el software debe hacer y las restricciones bajo las cuales debe operar."),
        ("¿Qué describen los requisitos funcionales?", ["Las funciones y servicios que hace el sistema", "La velocidad del procesador", "El precio de venta del software"], "Las funciones y servicios que hace el sistema", "Especifican las acciones, cálculos, transformaciones y respuestas del sistema."),
        ("¿Qué definen los requisitos no funcionales?", ["Restricciones como seguridad y rendimiento", "El menú de opciones del usuario", "Los nombres de los alumnos"], "Restricciones como seguridad y rendimiento", "Establecen criterios de operación y calidad como seguridad, tiempos de respuesta y disponibilidad."),
        ("¿Qué son los atributos de calidad?", ["Propiedades medibles como confiabilidad y usabilidad", "Los botones de la interfaz", "Las tablas de Excel"], "Propiedades medibles como confiabilidad y usabilidad", "Son características no funcionales evaluables que determinan el nivel de excelencia del software."),
        ("¿Cuál es el orden lógico de las fases de requisitos?", ["Elicitación, modelado, análisis y gestión", "Programación, venta y borrado", "Diseño, hardware y cableado"], "Elicitación, modelado, análisis y gestión", "Primero se recolectan (elicitación), luego se representan, se depuran y se controlan sus cambios."),
        ("¿En qué consiste la fase de elicitación?", ["Recolección y descubrimiento de requisitos", "Escribir el código en Python", "Probar el sistema en producción"], "Recolección y descubrimiento de requisitos", "Es el proceso de investigar y extraer necesidades mediante entrevistas, talleres u observación."),
        ("¿Qué significan las siglas JAD?", ["Joint Application Design", "Java Application Data", "Junior Analyst Developer"], "Joint Application Design", "JAD (Diseño Conjunto de Aplicaciones) es una técnica grupal para levantar requisitos."),
        ("¿En qué consiste la técnica JAD?", ["Sesiones estructuradas entre usuarios y analistas", "Un lenguaje de consulta SQL", "Un antivirus corporativo"], "Sesiones estructuradas entre usuarios y analistas", "Reúne a los involucrados clave en talleres facilitados para acelerar la definición de requisitos."),
        ("¿De dónde se derivan los requisitos técnicos?", ["De las necesidades y objetivos de los actores", "De la memoria caché", "Del azar"], "De las necesidades y objetivos de los actores", "Los requisitos traducen las necesidades de negocio y objetivos de los stakeholders en especificaciones."),
        ("¿De qué se encarga la gestión de requisitos?", ["Del control de cambios y trazabilidad", "De apagar los servidores", "De diseñar logotipos"], "Del control de cambios y trazabilidad", "Asegura el seguimiento de cada requisito y administra las modificaciones a lo largo del proyecto.")
    ],
    "Unidad 3: Análisis y especificación de Requisitos": [
        ("¿Qué busca la inspección y validación de requisitos?", ["Asegurar completitud y detectar inconsistencias", "Aumentar el tamaño del archivo", "Eliminar a los usuarios"], "Asegurar completitud y detectar inconsistencias", "Verifica que los requisitos reflejen lo que el cliente quiere y no tengan errores ni omisiones."),
        ("¿Qué ocurre cuando dos requisitos se contradicen?", ["Hay un conflicto o inconsistencia", "El código compila más rápido", "Se completa la entrega"], "Hay un conflicto o inconsistencia", "Una inconsistencia ocurre cuando cumplir un requisito impide cumplir otro."),
        ("¿Qué significan las siglas UML?", ["Lenguaje Unificado de Modelado", "Unidad de Memoria Lógica", "Usuario Múltiple Local"], "Lenguaje Unificado de Modelado", "UML es el lenguaje visual estándar para especificar y documentar artefactos de software."),
        ("¿Qué significan las siglas URN?", ["Notación de Requerimientos de Usuario", "Unidad Regional Nacional", "Uso Rápido de Navegador"], "Notación de Requerimientos de Usuario", "URN combina el modelado de objetivos (GRL) y escenarios (UCM) en ingeniería de requisitos."),
        ("¿Cuáles son los tipos de especificación de requisitos?", ["Textual, notación gráfica y lenguajes UML/URN", "Audio, video y fotografía", "Binario, octal y hexadecimal"], "Textual, notación gráfica y lenguajes UML/URN", "Los requisitos se documentan combinando lenguaje natural estructurado y modelos visuales."),
        ("¿Qué característica exige un estándar de alta calidad?", ["Que sea claro, verificable y no ambiguo", "Que tenga muchas metáforas", "Que sea secreto para el cliente"], "Que sea claro, verificable y no ambiguo", "Un requisito bien escrito debe tener una única interpretación y poder comprobarse con pruebas."),
        ("¿Qué es el Documento de Requisitos (DRS)?", ["Especificación oficial que consolida los requisitos", "Un recibo de pago bancario", "Una hoja de cálculo vacía"], "Especificación oficial que consolida los requisitos", "El DRS (o SRS) es el contrato técnico formal entre el cliente y el equipo de desarrollo."),
        ("¿Qué evalúan las métricas de modelado de análisis?", ["Complejidad, tamaño y calidad de los modelos", "La velocidad del internet", "La temperatura del procesador"], "Complejidad, tamaño y calidad de los modelos", "Permiten estimar el esfuerzo y detectar modelos excesivamente complejos antes de programar."),
        ("¿Qué significa que un requisito sea verificable?", ["Que se puede comprobar mediante pruebas", "Que está escrito en inglés", "Que ocupa más de una página"], "Que se puede comprobar mediante pruebas", "Debe existir un método objetivo (inspección, demostración o test) para confirmar que se cumple."),
        ("¿Qué significa la completitud en los requisitos?", ["Que no falte información necesaria para desarrollar", "Que el programa ya esté vendido", "Que no tenga comentarios"], "Que no falte información necesaria para desarrollar", "Un documento es completo cuando incluye todas las funciones, restricciones y respuestas esperadas.")
    ]
}

# --- 5B. PLANILLA Y RESPALDO PERSISTENTE (Hugging Face Dataset privado) ---
_LOCK = threading.Lock()
HF_TOKEN = os.environ.get("HF_TOKEN")
HF_DATASET = os.environ.get("HF_DATASET")  # ej: "usuario/notas-isw2" (dataset PRIVADO)

def _hf_descargar():
    if HF_TOKEN and HF_DATASET:
        try:
            from huggingface_hub import hf_hub_download
            hf_hub_download(repo_id=HF_DATASET, filename="Programacion.xlsx", repo_type="dataset",
                            token=HF_TOKEN, local_dir=BASE_DIR)
            print("[OK] Planilla restaurada desde Hugging Face.")
        except Exception as e:
            print(f"[AVISO] No se restauró planilla remota: {e}")

def _hf_subir():
    if HF_TOKEN and HF_DATASET:
        try:
            from huggingface_hub import HfApi
            with _LOCK:
                with open(EXCEL_PATH, "rb") as f:
                    datos = f.read()
            HfApi(token=HF_TOKEN).upload_file(path_or_fileobj=datos, path_in_repo="Programacion.xlsx",
                                              repo_id=HF_DATASET, repo_type="dataset")
        except Exception as e:
            print(f"[AVISO] No se pudo respaldar la planilla: {e}")

def asegurar_planilla():
    _hf_descargar()
    if os.path.exists(EXCEL_PATH):
        return
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Notas"
    ws.append(["N°", "Cédula", "Nombre", "Unidad I", "Unidad II", "Unidad III"])
    n = 0
    for ced, nom in ALUMNOS.items():
        if ced != ADMIN_CEDULA:
            n += 1
            ws.append([n, ced, nom])
    wb.save(EXCEL_PATH)

asegurar_planilla()

# --- 6. PERSISTENCIA Y ANALÍTICA DOCENTE EN EXCEL ---
def guardar_datos(cedula_alumno: str, nombre_alumno: str, unidad: str, puntos: int, historial_respuestas: list) -> tuple[bool, str]:
    if cedula_alumno == ADMIN_CEDULA:
        return True, "Modo Administrador: Nota y analítica no registradas en planilla."

    if not os.path.exists(EXCEL_PATH):
        return False, "No se encontró el archivo Programacion.xlsx en el servidor."

    col = {
        "Unidad 1: Modelado de Negocio": 4,
        "Unidad 2: Ingeniería de Requisitos": 5,
        "Unidad 3: Análisis y especificación de Requisitos": 6
    }.get(unidad)

    if not col:
        return False, "Unidad académica no válida."

    try:
        wb = openpyxl.load_workbook(EXCEL_PATH)
        sheet = wb.active
        encontrado = False

        for row in range(2, sheet.max_row + 1):
            celda_cedula = sheet.cell(row=row, column=2).value
            val_cedula = str(celda_cedula).strip().replace(".", "") if celda_cedula else ""

            if val_cedula == cedula_alumno:
                sheet.cell(row=row, column=col).value = puntos
                encontrado = True
                break

        if not encontrado:
            wb.close()
            return False, f"Cédula {cedula_alumno} ({nombre_alumno}) no localizada en el Excel."

        if "Analitica" not in wb.sheetnames:
            ws_ana = wb.create_sheet(title="Analitica")
            ws_ana.append(["Unidad", "Pregunta / Tema Evaluado", "Aciertos", "Fallos / Tiempo Agotado", "% Dominio"])
        else:
            ws_ana = wb["Analitica"]

        for preg_texto, acerto in historial_respuestas:
            fila_encontrada = None
            for r in range(2, ws_ana.max_row + 1):
                if ws_ana.cell(r, 1).value == unidad and ws_ana.cell(r, 2).value == preg_texto:
                    fila_encontrada = r
                    break

            if fila_encontrada:
                aciertos_act = int(ws_ana.cell(fila_encontrada, 3).value or 0) + (1 if acerto else 0)
                fallos_act = int(ws_ana.cell(fila_encontrada, 4).value or 0) + (0 if acerto else 1)
                total = aciertos_act + fallos_act
                porcentaje = round((aciertos_act / total) * 100, 1) if total > 0 else 0
                ws_ana.cell(fila_encontrada, 3).value = aciertos_act
                ws_ana.cell(fila_encontrada, 4).value = fallos_act
                ws_ana.cell(fila_encontrada, 5).value = f"{porcentaje}%"
            else:
                aciertos_ini = 1 if acerto else 0
                fallos_ini = 0 if acerto else 1
                porcentaje = 100.0 if acerto else 0.0
                ws_ana.append([unidad, preg_texto, aciertos_ini, fallos_ini, f"{porcentaje}%"])

        wb.save(EXCEL_PATH)
        wb.close()
        return True, f"Calificación ({puntos}/10) y analítica guardadas exitosamente."
    except PermissionError:
        return False, "Error: Cierra el archivo Excel antes de guardar la nota."
    except Exception as e:
        print(f"[ERROR ESCRITURA EXCEL]: {e}")
        return False, f"Error inesperado al guardar: {e}"


_guardar_interno = guardar_datos

def guardar_datos(*args, **kwargs):
    """Guarda con bloqueo (evita choques entre alumnos) y respalda en segundo plano."""
    with _LOCK:
        resultado = _guardar_interno(*args, **kwargs)
    if resultado[0] and args[0] != ADMIN_CEDULA:
        threading.Thread(target=_hf_subir, daemon=True).start()
    return resultado


# --- 7. INTERFAZ GRÁFICA PROFESIONAL (IDENTIDAD UNERMB) ---
def main(page: ft.Page):
    page.title = "UNERMB • Portal de Estudio Digital • Ingeniería del Software II"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    estado = {
        "cedula": None,
        "alumno": None,
        "unidad": None,
        "idx": 0,
        "puntos": 0,
        "historial": [],
        "timer_task": None
    }

    def cancelar_cronometro():
        tarea = estado.get("timer_task")
        if tarea and not tarea.done():
            tarea.cancel()
        estado["timer_task"] = None

    page.on_disconnect = lambda e: cancelar_cronometro()

    def mostrar_alerta(mensaje: str, es_error: bool = True):
        page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR_OUTLINE if es_error else ft.Icons.CHECK_CIRCLE_OUTLINE, color="white"),
                ft.Text(mensaje, color="white", weight="bold", expand=True)
            ]),
            bgcolor=COLOR_ERROR if es_error else COLOR_EXITO
        )
        page.snack_bar.open = True
        page.update()

    def logo_institucional(tamano: int = 105):
        return ft.Container(
            content=ft.Image(
                src=LOGO_UNERMB_PATH,
                width=tamano,
                height=tamano,
                fit="contain",
                error_content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ACCOUNT_BALANCE, size=tamano * 0.5, color=COLOR_PRIMARIO),
                        ft.Text("UNERMB", size=11, weight="bold", color=COLOR_PRIMARIO)
                    ], alignment="center", horizontal_alignment="center", spacing=2),
                    width=tamano,
                    height=tamano,
                    bgcolor="white",
                    border_radius=14,
                    border=ft.Border.all(2, COLOR_ACENTO),
                    alignment=ft.Alignment(0, 0)
                )
            ),
            padding=8,
            bgcolor="white",
            border_radius=14,
            border=ft.Border.all(2, COLOR_ACENTO),
            shadow=ft.BoxShadow(blur_radius=10, color="#33000000")
        )

    def barra_superior():
        alumno = estado.get("alumno")
        cedula = estado.get("cedula")
        return ft.Container(
            content=ft.Row(
                [
                    ft.Row([
                        logo_institucional(48),
                        ft.Column([
                            ft.Text("UNIVERSIDAD NACIONAL EXPERIMENTAL RAFAEL MARÍA BARALT", size=13, weight="bold", color="white"),
                            ft.Text("PNF en Informática • Ingeniería del Software II (ISC339)", size=12, color="#D6EAF8")
                        ], spacing=1)
                    ], spacing=12),
                    ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.PERSON, color=COLOR_ACENTO, size=18),
                                ft.Text(f"{alumno} (C.I. {cedula})", color="white", size=13, weight="bold")
                            ], spacing=6),
                            bgcolor="#1A3A5A",
                            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                            border_radius=20
                        ),
                        ft.Button(
                            "Salir",
                            icon=ft.Icons.LOGOUT,
                            on_click=lambda _: login_view(),
                            style=ft.ButtonStyle(
                                bgcolor=COLOR_ERROR,
                                color="white",
                                shape=ft.RoundedRectangleBorder(radius=10)
                            )
                        )
                    ], spacing=10) if alumno else ft.Container()
                ],
                alignment="spaceBetween"
            ),
            bgcolor=COLOR_PRIMARIO,
            padding=ft.Padding.symmetric(horizontal=24, vertical=10),
            border=ft.Border.only(bottom=ft.BorderSide(3, COLOR_ACENTO))
        )

    def layout_academico(contenido_central: list, mostrar_header: bool = True):
        cuerpo = ft.Container(
            content=ft.Column(
                contenido_central,
                horizontal_alignment="center",
                alignment="center",
                spacing=18,
                scroll="auto"
            ),
            expand=True,
            alignment=ft.Alignment(0, 0),
            padding=25
        )

        estructura = [barra_superior(), cuerpo] if mostrar_header else [cuerpo]

        # Capas: imagen de fondo + velo azul marino semitransparente + contenido
        return ft.Stack([
            ft.Container(image=ft.DecorationImage(src=FONDO_PATH, fit="cover"), left=0, top=0, right=0, bottom=0),
            ft.Container(
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=["#E60A2540", "#D9154360", "#CC1F618D"]
                ),
                left=0, top=0, right=0, bottom=0
            ),
            ft.Container(content=ft.Column(estructura, spacing=0, expand=True), left=0, top=0, right=0, bottom=0)
        ], expand=True)

    def boton_estilizado(texto: str, icono, on_click, ancho: int = 320, color_bg: str = COLOR_SECUNDARIO, color_txt: str = "white"):
        return ft.Button(
            content=ft.Row([
                ft.Icon(icono, color=color_txt, size=20),
                ft.Text(texto, size=15, weight="bold", color=color_txt, text_align="center")
            ], alignment="center", spacing=10),
            on_click=on_click,
            width=ancho,
            height=48,
            style=ft.ButtonStyle(
                bgcolor=color_bg,
                shape=ft.RoundedRectangleBorder(radius=12),
                elevation=4
            )
        )

    def menu_principal():
        cancelar_cronometro()
        page.clean()
        if not estado["alumno"]:
            login_view()
            return

        tarjetas_unidades = [
            ("Unidad 1: Modelado de Negocio", "Procesos, actividades, reglas, actores y objetos del negocio.", ft.Icons.ACCOUNT_TREE, "UNIDAD I"),
            ("Unidad 2: Ingeniería de Requisitos", "Tipos de requisitos, atributos de calidad, fases y técnica JAD.", ft.Icons.FACT_CHECK, "UNIDAD II"),
            ("Unidad 3: Análisis y especificación de Requisitos", "Inspección, validación, UML/URN, estándares y documento DRS.", ft.Icons.ARCHITECTURE, "UNIDAD III")
        ]

        cards = []
        for titulo_u, desc_u, icono_u, etiqueta_u in tarjetas_unidades:
            cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Text(etiqueta_u, size=11, weight="bold", color="white"),
                                bgcolor=COLOR_PRIMARIO,
                                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                border_radius=8
                            ),
                            ft.Icon(icono_u, color=COLOR_SECUNDARIO, size=28)
                        ], alignment="spaceBetween"),
                        ft.Text(titulo_u, size=18, weight="bold", color=COLOR_TEXTO_OSCURO),
                        ft.Text(desc_u, size=13, color="#566573", expand=True),
                        boton_estilizado("Ingresar a la Unidad", ft.Icons.ARROW_FORWARD, lambda e, u=titulo_u: mostrar_unidad(u), ancho=260, color_bg=COLOR_SECUNDARIO)
                    ], spacing=8),
                    width=310,
                    height=245,
                    bgcolor=COLOR_TARJETA,
                    padding=20,
                    border_radius=16,
                    border=ft.Border.all(1, "#D5D8DC"),
                    shadow=ft.BoxShadow(blur_radius=15, color="#33000000")
                )
            )

        page.add(layout_academico([
            ft.Container(
                content=ft.Column([
                    ft.Text("CONTENIDO PROGRAMÁTICO • TRAYECTO III", size=13, weight="bold", color=COLOR_ACENTO),
                    ft.Text("Seleccione una Unidad Curricular", size=28, weight="bold", color="white", text_align="center"),
                    ft.Text("Explore los saberes teóricos, practique con casos reales y presente su evaluación.", size=14, color="#EBF5FB", text_align="center")
                ], horizontal_alignment="center", spacing=4),
                margin=ft.Margin.only(bottom=10)
            ),
            ft.Row(cards, alignment="center", wrap=True, spacing=20)
        ]))
        page.update()

    def mostrar_unidad(unidad: str):
        cancelar_cronometro()
        estado["unidad"] = unidad
        estado["idx"] = 0
        estado["puntos"] = 0
        estado["historial"] = []
        page.clean()

        temas = [
            ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.MENU_BOOK, color=COLOR_SECUNDARIO),
                    title=ft.Text(t, color=COLOR_TEXTO_OSCURO, size=14, weight="w600"),
                    trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=COLOR_SECUNDARIO),
                    on_click=lambda e, t=t: mostrar_def(t)
                ),
                bgcolor="white",
                border_radius=10,
                border=ft.Border.all(1, "#E5E8E8"),
                margin=ft.Margin.only(bottom=6)
            )
            for t in contenido.get(unidad, {}).keys()
        ]

        panel_unidad = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LIBRARY_BOOKS, color=COLOR_PRIMARIO, size=28),
                    ft.Text(unidad, size=22, weight="bold", color=COLOR_PRIMARIO, expand=True)
                ], spacing=10),
                ft.Divider(height=1, color="#D5D8DC"),
                ft.Text("Haga clic sobre cada saber para estudiar su definición antes de evaluar:", size=13, color="#566573"),
                ft.Container(
                    content=ft.Column(temas, scroll="auto"),
                    height=280,
                    padding=4
                ),
                ft.Row([
                    boton_estilizado("Modo Estudio (resumen)", ft.Icons.AUTO_STORIES, lambda _: estudiar(0), ancho=275, color_bg=COLOR_SECUNDARIO),
                    boton_estilizado("Taller Práctico (Sin nota)", ft.Icons.BUILD_CIRCLE, lambda _: iniciar_taller(0), ancho=275, color_bg=COLOR_EXITO),
                    boton_estilizado("Evaluación", ft.Icons.QUIZ, lambda _: iniciar_evaluacion(), ancho=275, color_bg=COLOR_PRIMARIO)
                ], alignment="center", wrap=True, spacing=12),
                ft.TextButton(
                    "← Volver al Menú de Unidades",
                    on_click=lambda _: menu_principal(),
                    style=ft.ButtonStyle(color=COLOR_SECUNDARIO)
                )
            ], horizontal_alignment="center", spacing=12),
            width=640,
            bgcolor=COLOR_TARJETA,
            padding=25,
            border_radius=20,
            shadow=ft.BoxShadow(blur_radius=20, color="#40000000")
        )

        page.add(layout_academico([panel_unidad]))
        page.update()

    def mostrar_def(tema: str):
        estudiar(list(contenido[estado["unidad"]]).index(tema))

    def estudiar(i: int = 0):
        cancelar_cronometro()
        page.clean()
        unidad = estado["unidad"]
        temas = list(contenido.get(unidad, {}).keys())
        i = max(0, min(i, len(temas) - 1))
        tema = temas[i]
        clave, puntos_clave, ejemplo = RESUMEN[unidad][i]
        ultimo = i == len(temas) - 1

        completo = ft.Container(
            content=ft.Text(contenido[unidad][tema], size=13, color=COLOR_TEXTO_OSCURO),
            visible=False, padding=12, bgcolor="white", border_radius=10, border=ft.Border.all(1, "#D5D8DC")
        )

        def alternar(e):
            completo.visible = not completo.visible
            page.update()

        tarjeta = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"Tema {i + 1} de {len(temas)}", size=13, weight="bold", color=COLOR_SECUNDARIO),
                    ft.Icon(ft.Icons.AUTO_STORIES, color=COLOR_ACENTO, size=26)
                ], alignment="spaceBetween"),
                ft.ProgressBar(value=(i + 1) / len(temas), color=COLOR_ACENTO, bgcolor="#D5D8DC"),
                ft.Text(tema, size=18, color=COLOR_PRIMARIO, weight="bold", text_align="center"),
                ft.Container(
                    content=ft.Text("💡 " + clave, size=16, weight="bold", color="white", text_align="center"),
                    padding=14, bgcolor=COLOR_SECUNDARIO, border_radius=12, width=560
                ),
                ft.Column([ft.Text("•  " + p, size=14, color=COLOR_TEXTO_OSCURO) for p in puntos_clave], spacing=4, width=560),
                ft.Container(
                    content=ft.Text("Ejemplo: " + ejemplo, size=13, italic=True, color=COLOR_TEXTO_OSCURO),
                    padding=12, bgcolor="#FEF9E7", border_radius=10, border=ft.Border.all(1, COLOR_ACENTO), width=560
                ),
                ft.TextButton("Ver definición completa", icon=ft.Icons.EXPAND_MORE, on_click=alternar, style=ft.ButtonStyle(color=COLOR_SECUNDARIO)),
                completo,
                ft.Text("🧠 " + MNEMO[unidad], size=12, color="#566573", text_align="center"),
                ft.Row([
                    ft.TextButton("← Anterior", on_click=lambda _: estudiar(i - 1), disabled=(i == 0)),
                    boton_estilizado("Ir al Taller" if ultimo else "Siguiente", ft.Icons.BUILD_CIRCLE if ultimo else ft.Icons.ARROW_FORWARD,
                                     (lambda _: iniciar_taller(0)) if ultimo else (lambda _: estudiar(i + 1)), ancho=200, color_bg=COLOR_EXITO if ultimo else COLOR_PRIMARIO),
                ], alignment="spaceBetween", width=560),
                ft.TextButton("Volver a la Unidad", on_click=lambda _: mostrar_unidad(unidad), style=ft.ButtonStyle(color=COLOR_SECUNDARIO))
            ], horizontal_alignment="center", spacing=12),
            width=640, bgcolor=COLOR_TARJETA, padding=25, border_radius=20,
            shadow=ft.BoxShadow(blur_radius=20, color="#40000000")
        )
        page.add(layout_academico([tarjeta]))
        page.update()

    def iniciar_evaluacion():
        banco = list(preguntas.get(estado["unidad"], []))
        random.shuffle(banco)
        estado.update({"banco": banco, "idx": 0, "puntos": 0, "historial": []})
        lanzar_pregunta()

    def iniciar_taller(indice_caso: int = 0):
        cancelar_cronometro()
        page.clean()
        unidad = estado["unidad"]
        casos_unidad = talleres.get(unidad, [])

        if indice_caso >= len(casos_unidad):
            tarjeta_fin_taller = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.EMOJI_EVENTS, color=COLOR_ACENTO, size=60),
                    ft.Text("¡Taller Práctico Completado!", size=26, color=COLOR_PRIMARIO, weight="bold", text_align="center"),
                    ft.Text(
                        "Has analizado todos los casos prácticos de esta unidad. Ya estás preparado para presentar la evaluación cronometrada.",
                        color=COLOR_TEXTO_OSCURO, size=16, text_align="center"
                    ),
                    boton_estilizado("Iniciar Evaluación (40s)", ft.Icons.QUIZ, lambda _: iniciar_evaluacion(), ancho=290, color_bg=COLOR_PRIMARIO),
                    ft.TextButton("Volver a los Saberes", on_click=lambda _: mostrar_unidad(unidad), style=ft.ButtonStyle(color=COLOR_SECUNDARIO))
                ], horizontal_alignment="center", spacing=16),
                padding=30, bgcolor=COLOR_TARJETA, border_radius=20, width=600,
                shadow=ft.BoxShadow(blur_radius=20, color="#40000000")
            )
            page.add(layout_academico([tarjeta_fin_taller]))
            page.update()
            return

        datos_caso = casos_unidad[indice_caso]
        opciones = list(datos_caso["opciones"])
        random.shuffle(opciones)

        caja_feedback = ft.Container(visible=False, padding=15, border_radius=12, width=580)
        boton_siguiente = boton_estilizado(
            "Siguiente Caso",
            ft.Icons.ARROW_FORWARD,
            lambda _: iniciar_taller(indice_caso + 1),
            ancho=240,
            color_bg=COLOR_PRIMARIO
        )
        boton_siguiente.visible = False
        botones_opciones = []

        def verificar_taller(seleccion: str):
            es_correcto = (seleccion == datos_caso["correcta"])
            for btn in botones_opciones:
                btn.disabled = True

            caja_feedback.bgcolor = COLOR_EXITO if es_correcto else COLOR_ERROR
            titulo_fb = "¡Excelente análisis!" if es_correcto else f"Respuesta esperada: {datos_caso['correcta']}"
            caja_feedback.content = ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE if es_correcto else ft.Icons.INFO, color="white", size=28),
                ft.Column([
                    ft.Text(titulo_fb, size=16, weight="bold", color="white"),
                    ft.Text(datos_caso["explicacion"], size=14, color="white")
                ], spacing=4, expand=True)
            ], spacing=12)
            caja_feedback.visible = True
            boton_siguiente.visible = True
            page.update()

        for op in opciones:
            botones_opciones.append(
                ft.Button(
                    content=ft.Text(op, size=14, weight="w600", color=COLOR_PRIMARIO, text_align="center"),
                    on_click=lambda e, o=op: verificar_taller(o),
                    width=560,
                    height=48,
                    style=ft.ButtonStyle(
                        bgcolor="white",
                        shape=ft.RoundedRectangleBorder(radius=10),
                        side=ft.BorderSide(1.5, COLOR_SECUNDARIO)
                    )
                )
            )

        panel_taller = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text("MODO PRÁCTICA GUIADA", size=11, weight="bold", color="white"),
                        bgcolor=COLOR_EXITO, padding=ft.Padding.symmetric(horizontal=10, vertical=4), border_radius=8
                    ),
                    ft.Text(f"Caso {indice_caso + 1} de {len(casos_unidad)}", size=14, weight="bold", color=COLOR_SECUNDARIO)
                ], alignment="spaceBetween"),
                ft.Container(
                    content=ft.Text(datos_caso["caso"], size=16, color=COLOR_TEXTO_OSCURO, weight="w500"),
                    padding=16, bgcolor="white", border_radius=12, border=ft.Border.all(1, "#D5D8DC")
                ),
                *botones_opciones,
                caja_feedback,
                boton_siguiente,
                ft.TextButton("Salir del Taller", on_click=lambda _: mostrar_unidad(unidad), style=ft.ButtonStyle(color=COLOR_SECUNDARIO))
            ], horizontal_alignment="center", spacing=12),
            width=640, bgcolor=COLOR_TARJETA, padding=25, border_radius=20,
            shadow=ft.BoxShadow(blur_radius=20, color="#40000000")
        )

        page.add(layout_academico([panel_taller]))
        page.update()

    def lanzar_pregunta():
        cancelar_cronometro()
        page.clean()
        unidad = estado["unidad"]
        idx = estado["idx"]
        puntos = estado["puntos"]
        lista_preguntas = estado.get("banco") or preguntas.get(unidad, [])

        if idx < len(lista_preguntas):
            p, opciones_originales, correcta, explicacion = lista_preguntas[idx]
            opciones = list(opciones_originales)
            random.shuffle(opciones)

            respondido = {"hecho": False}
            texto_tiempo = ft.Text("40s", size=16, weight="bold", color="white")
            badge_tiempo = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.TIMER, color="white", size=18),
                    texto_tiempo
                ], spacing=6),
                bgcolor=COLOR_SECUNDARIO,
                padding=ft.Padding.symmetric(horizontal=14, vertical=6),
                border_radius=20
            )
            caja_feedback = ft.Container(visible=False, padding=15, border_radius=12, width=580)
            botones_opciones = []

            def avanzar(e=None):
                estado["idx"] += 1
                lanzar_pregunta()

            boton_sig = boton_estilizado(
                "Siguiente pregunta" if idx + 1 < len(lista_preguntas) else "Ver resultado",
                ft.Icons.ARROW_FORWARD, avanzar, ancho=260, color_bg=COLOR_PRIMARIO)
            boton_sig.visible = False

            async def mostrar_feedback_y_avanzar(respuesta_usuario: str | None):
                if respondido["hecho"]:
                    return
                respondido["hecho"] = True
                cancelar_cronometro()

                for btn in botones_opciones:
                    btn.disabled = True

                acerto = (respuesta_usuario == correcta)
                if acerto:
                    estado["puntos"] += 1

                estado["historial"].append((p, acerto))

                if respuesta_usuario is None:
                    titulo_fb = f"Tiempo agotado • Respuesta correcta: {correcta}"
                    caja_feedback.bgcolor = COLOR_ERROR
                elif acerto:
                    titulo_fb = "¡Respuesta Correcta!"
                    caja_feedback.bgcolor = COLOR_EXITO
                else:
                    titulo_fb = f"Incorrecto • La correcta era: {correcta}"
                    caja_feedback.bgcolor = COLOR_ERROR

                caja_feedback.content = ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE if acerto else ft.Icons.ERROR, color="white", size=28),
                    ft.Column([
                        ft.Text(titulo_fb, size=15, weight="bold", color="white"),
                        ft.Text(explicacion, size=13, color="white")
                    ], spacing=4, expand=True)
                ], spacing=12)
                caja_feedback.visible = True
                boton_sig.visible = True
                page.update()

            async def cuenta_regresiva(indice_actual: int):
                try:
                    for segundos in range(39, -1, -1):
                        await asyncio.sleep(1)
                        if respondido["hecho"] or estado["idx"] != indice_actual:
                            return
                        texto_tiempo.value = f"{segundos}s"
                        if segundos <= 10:
                            badge_tiempo.bgcolor = COLOR_ERROR
                        page.update()

                    if not respondido["hecho"] and estado["idx"] == indice_actual:
                        await mostrar_feedback_y_avanzar(None)
                except asyncio.CancelledError:
                    pass

            for op in opciones:
                botones_opciones.append(
                    ft.Button(
                        content=ft.Text(op, size=15, weight="w600", color=COLOR_PRIMARIO, text_align="center"),
                        on_click=lambda e, o=op: page.run_task(mostrar_feedback_y_avanzar, o),
                        width=560,
                        height=50,
                        style=ft.ButtonStyle(
                            bgcolor="white",
                            shape=ft.RoundedRectangleBorder(radius=10),
                            side=ft.BorderSide(1.5, COLOR_SECUNDARIO)
                        )
                    )
                )

            panel_examen = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"Pregunta {idx + 1} de {len(lista_preguntas)}", color=COLOR_PRIMARIO, size=16, weight="bold"),
                        badge_tiempo
                    ], alignment="spaceBetween"),
                    ft.ProgressBar(value=(idx + 1) / len(lista_preguntas), color=COLOR_ACENTO, bgcolor="#D5D8DC"),
                    ft.Container(
                        content=ft.Text(p, size=19, color=COLOR_TEXTO_OSCURO, weight="bold", text_align="center"),
                        padding=20,
                        bgcolor="white",
                        border_radius=12,
                        border=ft.Border.all(1, "#D5D8DC"),
                        width=580
                    ),
                    *botones_opciones,
                    caja_feedback,
                    boton_sig
                ], horizontal_alignment="center", spacing=14),
                width=640,
                bgcolor=COLOR_TARJETA,
                padding=25,
                border_radius=20,
                shadow=ft.BoxShadow(blur_radius=20, color="#40000000")
            )

            page.add(layout_academico([panel_examen]))
            page.update()
            estado["timer_task"] = page.run_task(cuenta_regresiva, idx)
        else:
            cedula = estado["cedula"]
            alumno = estado["alumno"]
            nota = round(puntos * 10 / max(len(lista_preguntas), 1), 1)
            exito, mensaje = guardar_datos(cedula, alumno, unidad, nota, estado["historial"])

            aprobado = nota >= 6
            fallos = [(q[0], q[2], q[3]) for q, (_, ok) in zip(estado.get("banco", []), estado["historial"]) if not ok]
            bloque_repaso = [ft.Text(f"Aciertos: {puntos} de {len(lista_preguntas)}", size=14, weight="bold", color=COLOR_TEXTO_OSCURO)]
            if fallos:
                bloque_repaso.append(ft.Text("Repasa estos puntos:", size=14, weight="bold", color=COLOR_PRIMARIO))
                bloque_repaso += [
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f, size=13, weight="bold", color=COLOR_TEXTO_OSCURO),
                            ft.Text("✔ " + c + " — " + e, size=12, color="#566573")
                        ], spacing=2),
                        padding=10, bgcolor="white", border_radius=10, border=ft.Border.all(1, "#D5D8DC"), width=460)
                    for f, c, e in fallos
                ]
            tarjeta_resultado = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.VERIFIED if aprobado else ft.Icons.SCHOOL, size=64, color=COLOR_EXITO if aprobado else COLOR_SECUNDARIO),
                    ft.Text("Evaluación Finalizada", size=24, weight="bold", color=COLOR_PRIMARIO),
                    ft.Text(unidad, size=14, color="#566573", weight="bold"),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("CALIFICACIÓN OBTENIDA", size=12, weight="bold", color="#566573"),
                            ft.Text(f"{nota} / 10", size=54, weight="bold", color=COLOR_EXITO if aprobado else COLOR_ERROR)
                        ], horizontal_alignment="center", spacing=2),
                        padding=ft.Padding.symmetric(horizontal=40, vertical=15),
                        bgcolor="white",
                        border_radius=16,
                        border=ft.Border.all(2, COLOR_EXITO if aprobado else COLOR_ERROR)
                    ),
                    *bloque_repaso,
                    ft.Text(mensaje, size=14, color=COLOR_EXITO if exito else COLOR_ERROR, weight="bold", text_align="center"),
                    boton_estilizado("Repetir evaluación", ft.Icons.REPLAY, lambda _: iniciar_evaluacion(), ancho=280, color_bg=COLOR_SECUNDARIO),
                    boton_estilizado("Volver al Menú Principal", ft.Icons.HOME, lambda _: menu_principal(), ancho=280, color_bg=COLOR_PRIMARIO)
                ], horizontal_alignment="center", spacing=14),
                width=520,
                bgcolor=COLOR_TARJETA,
                padding=30,
                border_radius=20,
                shadow=ft.BoxShadow(blur_radius=20, color="#40000000")
            )

            page.add(layout_academico([tarjeta_resultado]))
            mostrar_alerta(mensaje, es_error=not exito)
            page.update()

    def login_view():
        cancelar_cronometro()
        estado.update({"cedula": None, "alumno": None, "unidad": None, "idx": 0, "puntos": 0, "historial": []})
        page.clean()

        cedula_field = ft.TextField(
            label="Número de Cédula de Identidad",
            hint_text="Ej: 12345678",
            prefix_icon=ft.Icons.BADGE,
            width=340,
            color=COLOR_TEXTO_OSCURO,
            bgcolor="white",
            border_color=COLOR_SECUNDARIO,
            focused_border_color=COLOR_PRIMARIO,
            keyboard_type=ft.KeyboardType.NUMBER,
            autofocus=True,
            on_submit=lambda e: ingresar(e)
        )

        def ingresar(e):
            raw_val = cedula_field.value.strip() if cedula_field.value else ""
            cedula_limpia = "".join(filter(str.isdigit, raw_val))

            if not cedula_limpia:
                mostrar_alerta("Por favor, ingrese su número de cédula.")
                return

            if cedula_limpia in ALUMNOS:
                estado["cedula"] = cedula_limpia
                estado["alumno"] = ALUMNOS[cedula_limpia]
                menu_principal()
            else:
                mostrar_alerta("Cédula no registrada en la sección. Verifique e intente de nuevo.")

        tarjeta_login = ft.Container(
            content=ft.Column([
                logo_institucional(110),
                ft.Text("UNERMB", size=26, weight="bold", color=COLOR_PRIMARIO),
                ft.Text("Programa Nacional de Formación en Informática", size=13, weight="bold", color=COLOR_SECUNDARIO, text_align="center"),
                ft.Container(
                    content=ft.Text("Ingeniería del Software II • Trayecto III", size=12, weight="bold", color="white"),
                    bgcolor=COLOR_PRIMARIO,
                    padding=ft.Padding.symmetric(horizontal=14, vertical=5),
                    border_radius=12
                ),
                ft.Divider(height=10, color="#D5D8DC"),
                ft.Text("Ingrese su cédula para acceder al aula virtual", size=14, color="#566573", text_align="center"),
                cedula_field,
                boton_estilizado("Ingresar al Portal", ft.Icons.LOGIN, ingresar, ancho=340, color_bg=COLOR_PRIMARIO),
                ft.Text(PROYECTO, size=10, italic=True, color="#566573", text_align="center"),
                ft.Text(f"{AUTOR} • © UNERMB", size=11, color="#808B96", text_align="center")
            ], horizontal_alignment="center", spacing=12),
            width=440,
            bgcolor=COLOR_TARJETA,
            padding=32,
            border_radius=24,
            border=ft.Border.only(top=ft.BorderSide(6, COLOR_ACENTO)),
            shadow=ft.BoxShadow(blur_radius=25, color="#59000000")
        )

        page.add(layout_academico([tarjeta_login], mostrar_header=False))
        page.update()

    login_view()

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 8550))
    es_nube = "PORT" in os.environ

    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir=os.path.join(BASE_DIR, "assets"),
        host="0.0.0.0" if es_nube else "127.0.0.1",
        port=puerto
    )
