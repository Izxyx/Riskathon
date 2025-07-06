# --- Importaciones necesarias ---
import streamlit as st
import random
import pandas as pd
from datetime import datetime
import time
import re
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# --- Configuración de la Página de Streamlit ---
st.set_page_config(
    page_title="Test de Conocimiento",
    page_icon="🎲",
    layout="centered"
)

# --- Gestión de Datos en Caché ---
# La "base de datos" ahora será un DataFrame que vive en la caché de Streamlit
@st.cache_data(ttl=7200) # Cacha los datos por 7200 segundos (2 horas)
def obtener_df_inicial_cached():
    """
    Inicializa un DataFrame vacío para los datos.
    Esto solo se ejecutará la primera vez o cuando la caché expire.
    """
    print("Inicializando DataFrame vacío en caché.")
    return pd.DataFrame(columns=[
        "nombre_staff", "hora_registro", "numero_usuario", "nombre_usuario",
        "pregunta_num", "pregunta", "opcion_seleccionada",
        "puntos_obtenidos", "puntos_acumulados"
    ])

def insertar_fila_en_dataframe(nueva_fila_dict):
    """
    Inserta una nueva fila de datos en el DataFrame almacenado en st.session_state.
    """
    if 'data_df' not in st.session_state:
        st.session_state.data_df = obtener_df_inicial_cached() # O simplemente un DF vacío
    
    nueva_fila_df = pd.DataFrame([nueva_fila_dict])
    st.session_state.data_df = pd.concat([st.session_state.data_df, nueva_fila_df], ignore_index=True)

def eliminar_informacion_cached():
    """
    Elimina toda la información del DataFrame en st.session_state.
    """
    st.session_state.data_df = obtener_df_inicial_cached() # Reinicia el DataFrame
    st.cache_data.clear() # Limpiar caché si es necesario

# --- Función para reiniciar el juego ---
def reiniciar_juego():
    """
    Reinicia todas las variables de session_state para comenzar un nuevo juego.
    """
    st.session_state.respuestas_guardadas = []
    st.session_state.ultimos_dados = None
    st.session_state.puntos_totales = 0
    st.session_state['numero_registro'] = '' 
    st.session_state['nombre_usuario'] = ''
    st.session_state.preguntas_respondidas_sesion = []
    st.session_state.credenciales_validas = False
    st.session_state.preguntas_iniciales_completadas = False
    st.session_state.tiro_extra_1_tomado = False
    st.session_state.tiro_extra_2_tomado = False
    st.session_state.pregunta_extra_dado_1 = None
    st.session_state.pregunta_extra_dado_2 = None
    
    # Vaciar el DataFrame para el nuevo juego
    st.session_state.data_df = obtener_df_inicial_cached() 
    st.success("¡Juego reiniciado! Un nuevo jugador puede comenzar.")
    st.rerun() # Volver a ejecutar la aplicación para reflejar los cambios

# --- Inicialización de st.session_state ---
if 'respuestas_guardadas' not in st.session_state:
    st.session_state.respuestas_guardadas = []
if 'ultimos_dados' not in st.session_state:
    st.session_state.ultimos_dados = None
if 'puntos_totales' not in st.session_state:
    st.session_state.puntos_totales = 0
if 'numero_registro' not in st.session_state:
    st.session_state['numero_registro'] = ''
if 'nombre_usuario' not in st.session_state:
    st.session_state['nombre_usuario'] = ''
if 'nombre_staff' not in st.session_state:
    st.session_state['nombre_staff'] = 'Administrador'
if 'preguntas_respondidas_sesion' not in st.session_state:
    st.session_state.preguntas_respondidas_sesion = []
if 'credenciales_validas' not in st.session_state:
    st.session_state.credenciales_validas = False
if 'preguntas_iniciales_completadas' not in st.session_state:
    st.session_state.preguntas_iniciales_completadas = False
if 'costo_tiro_extra_1' not in st.session_state:
    st.session_state.costo_tiro_extra_1 = 100
if 'costo_tiro_extra_2' not in st.session_state:
    st.session_state.costo_tiro_extra_2 = 200
if 'tiro_extra_1_tomado' not in st.session_state:
    st.session_state.tiro_extra_1_tomado = False
if 'tiro_extra_2_tomado' not in st.session_state:
    st.session_state.tiro_extra_2_tomado = False
if 'pregunta_extra_dado_1' not in st.session_state:
    st.session_state.pregunta_extra_dado_1 = None
if 'pregunta_extra_dado_2' not in st.session_state:
    st.session_state.pregunta_extra_dado_2 = None

# Inicialización del DataFrame principal para almacenar datos
if 'data_df' not in st.session_state:
    st.session_state.data_df = obtener_df_inicial_cached()

# --- Datos de Preguntas y Opciones ---
preguntas_base = {
    1: {
        "pregunta": "¿Cuál es la capital de Francia?",
        "opciones": ["A) Madrid", "B) París", "C) Roma"],
        "opciones_correctas": "B) París",
        "puntos": 500
    },
    2: {
        "pregunta": "¿Qué planeta es conocido como el Planeta Rojo?",
        "opciones": ["A) Júpiter", "B) Marte", "C) Venus"],
        "opciones_correctas": "B) Marte",
        "puntos": 400
    },
    3: {
        "pregunta": "¿Quién escribió 'Cien años de soledad'?",
        "opciones": ["A) Mario Vargas Llosa", "B) Gabriel García Márquez", "C) Julio Cortázar"],
        "opciones_correctas": "B) Gabriel García Márquez",
        "puntos": 350
    },
    4: {
        "pregunta": "¿Cuál es el océano más grande del mundo?",
        "opciones": ["A) Atlántico", "B) Índico", "C) Pacífico"],
        "opciones_correctas": "C) Pacífico",
        "puntos": 300
    },
    5: {
        "pregunta": "¿En qué año llegó el hombre a la Luna?",
        "opciones": ["A) 1969", "B) 1959", "C) 1979"],
        "opciones_correctas": "A) 1969",
        "puntos": 30
    },
    6: {
        "pregunta": "¿Cuál es el animal terrestre más rápido?",
        "opciones": ["A) León", "B) Guepardo", "C) Halcón Peregrino"],
        "opciones_correctas": "B) Guepardo",
        "puntos": 250
    },
    7: {
        "pregunta": "¿Qué elemento químico tiene el símbolo 'O'?",
        "opciones": ["A) Oro", "B) Oxígeno", "C) Osmio"],
        "opciones_correctas": "B) Oxígeno",
        "puntos": 400
    },
    8: {
        "pregunta": "¿Cuál es la montaña más alta del mundo?",
        "opciones": ["A) K2", "B) Kangchenjunga", "C) Everest"],
        "opciones_correctas": "C) Everest",
        "puntos": 350
    },
    9: {
        "pregunta": "¿De qué país es originario el sushi?",
        "opciones": ["A) China", "B) Japón", "C) Corea del Sur"],
        "opciones_correctas": "B) Japón",
        "puntos": 300
    },
    10: {
        "pregunta": "¿Cuál es el río más largo del mundo?",
        "opciones": ["A) Amazonas", "B) Nilo", "C) Yangtsé"],
        "opciones_correctas": "B) Nilo",
        "puntos": 10
    },
    11: {
        "pregunta": "¿Quién pintó la Mona Lisa?",
        "opciones": ["A) Vincent van Gogh", "B) Leonardo da Vinci", "C) Pablo Picasso"],
        "opciones_correctas": "B) Leonardo da Vinci",
        "puntos": 250
    },
    12: {
        "pregunta": "¿Quién fue el primer presidente de los Estados Unidos?",
        "opciones": ["A) Thomas Jefferson", "B) John Adams", "C) George Washington"],
        "opciones_correctas": "C) George Washington",
        "puntos": 30
    },
    13: {
        "pregunta": "¿Cuál es el metal más abundante en la corteza terrestre?",
        "opciones": ["A) Hierro", "B) Oro", "C) Aluminio"],
        "opciones_correctas": "C) Aluminio",
        "puntos": 350
    },
    14: {
        "pregunta": "¿Qué instrumento se utiliza para medir la presión atmosférica?",
        "opciones": ["A) Termómetro", "B) Anemómetro", "C) Barómetro"],
        "opciones_correctas": "C) Barómetro",
        "puntos": 300
    },
    15: {
        "pregunta": "¿En qué continente se encuentra el desierto del Sahara?",
        "opciones": ["A) Asia", "B) América del Sur", "C) África"],
        "opciones_correctas": "C) África",
        "puntos": 100
    },
    16: {
        "pregunta": "¿Cuál es el hueso más largo del cuerpo humano?",
        "opciones": ["A) Tibia", "B) Radio", "C) Fémur"],
        "opciones_correctas": "C) Fémur",
        "puntos": 250
    },
    17: {
        "pregunta": "¿Qué ciudad es conocida como la 'Ciudad Eterna'?",
        "opciones": ["A) Atenas", "B) París", "C) Roma"],
        "opciones_correctas": "C) Roma",
        "puntos": 30
    },
    18: {
        "pregunta": "¿Cuál es el proceso por el cual las plantas producen su propio alimento?",
        "opciones": ["A) Respiración", "B) Transpiración", "C) Fotosíntesis"],
        "opciones_correctas": "C) Fotosíntesis",
        "puntos": 300
    },
    19: {
        "pregunta": "¿Quién fue el autor de la teoría de la relatividad?",
        "opciones": ["A) Isaac Newton", "B) Galileo Galilei", "C) Albert Einstein"],
        "opciones_correctas": "C) Albert Einstein",
        "puntos": 300
    },
    20: {
        "pregunta": "¿Cuál es el océano más pequeño del mundo?",
        "opciones": ["A) Atlántico", "B) Índico", "C) Ártico"],
        "opciones_correctas": "C) Ártico",
        "puntos": 100
    },
    21: {
        "pregunta": "¿Qué país es el más grande del mundo por área?",
        "opciones": ["A) Canadá", "B) China", "C) Rusia"],
        "opciones_correctas": "C) Rusia",
        "puntos": -500
    },
    22: {
        "pregunta": "¿Cuál es el sistema de escritura de los antiguos egipcios?",
        "opciones": ["A) Cuneiforme", "B) Alfabeto Fenicio", "C) Jeroglíficos"],
        "opciones_correctas": "C) Jeroglíficos",
        "puntos": 50
    },
    23: {
        "pregunta": "¿Cuántos huesos tiene un adulto humano promedio?",
        "opciones": ["A) 200", "B) 206", "C) 212"],
        "opciones_correctas": "B) 206",
        "puntos": 300
    },
    24: {
        "pregunta": "¿Cuál es el río más largo de América del Sur?",
        "opciones": ["A) Paraná", "B) Orinoco", "C) Amazonas"],
        "opciones_correctas": "C) Amazonas",
        "puntos": 350
    },
    25: {
        "pregunta": "¿Qué famoso científico formuló la ley de la gravitación universal?",
        "opciones": ["A) Charles Darwin", "B) Nikola Tesla", "C) Isaac Newton"],
        "opciones_correctas": "C) Isaac Newton",
        "puntos": 100
    },
    26: {
        "pregunta": "¿Qué país es conocido como la 'Tierra del Sol Naciente'?",
        "opciones": ["A) China", "B) Corea del Sur", "C) Japón"],
        "opciones_correctas": "C) Japón",
        "puntos": 250
    },
    27: {
        "pregunta": "¿Cuál es el planeta más grande de nuestro sistema solar?",
        "opciones": ["A) Tierra", "B) Saturno", "C) Júpiter"],
        "opciones_correctas": "C) Júpiter",
        "puntos": 50
    },
    28: {
        "pregunta": "¿Qué lengua se habla en Brasil?",
        "opciones": ["A) Español", "B) Inglés", "C) Portugués"],
        "opciones_correctas": "C) Portugués",
        "puntos": 0,
        "accion_puntos": "duplicar_acumulados"
    },
    29: {
        "pregunta": "¿Quién pintó la Capilla Sixtina?",
        "opciones": ["A) Donatello", "B) Leonardo da Vinci", "C) Miguel Ángel"],
        "opciones_correctas": "C) Miguel Ángel",
        "puntos": 350
    },
    30: {
        "pregunta": "¿Cuál es el país con la mayor población del mundo?",
        "opciones": ["A) Estados Unidos", "B) India", "C) Indonesia"],
        "opciones_correctas": "B) India",
        "puntos": 400
    },
    31: {
        "pregunta": "¿Qué gas es esencial para la combustión?",
        "opciones": ["A) Nitrógeno", "B) Dióxido de Carbono", "C) Oxígeno"],
        "opciones_correctas": "C) Oxígeno",
        "puntos": 250
    },
    32: {
        "pregunta": "¿Quién escribió 'Don Quijote de la Mancha'?",
        "opciones": ["A) Federico García Lorca", "B) Lope de Vega", "C) Miguel de Cervantes Saavedra"],
        "opciones_correctas": "C) Miguel de Cervantes Saavedra",
        "puntos": 50
    },
    33: {
        "pregunta": "¿Cuál es el deporte nacional de Japón?",
        "opciones": ["A) Judo", "B) Karate", "C) Sumo"],
        "opciones_correctas": "C) Sumo",
        "puntos": 300
    },
    34: {
        "pregunta": "¿Cuántos lados tiene un heptágono?",
        "opciones": ["A) 6", "B) 7", "C) 8"],
        "opciones_correctas": "B) 7",
        "puntos": 350
    },
    35: {
        "pregunta": "¿Cuántos lados tiene un pentágono?",
        "opciones": ["A) 5", "B) 7", "C) 8"],
        "opciones_correctas": "A) 5",
        "puntos": 400
    },
    36: {
        "pregunta": "¿Cuántos lados tiene un triangulo?",
        "opciones": ["A) 3", "B) 7", "C) 8"],
        "opciones_correctas": "A) 3",
        "puntos": 500
    },  
}

# Número de preguntas
numero_preguntas_disponibles = len(preguntas_base)

# --- Funciones de Lógica ---
def lanzar_dados(num_dados=3):
    """
    Simula el lanzamiento de 'num_dados' dados, seleccionando 'num_dados' números únicos
    del rango 1 hasta numero_preguntas_disponibles, asegurándose de no repetir
    preguntas ya respondidas en la sesión actual.
    """
    preguntas_no_respondidas = [p for p in range(1, numero_preguntas_disponibles + 1) if p not in st.session_state.preguntas_respondidas_sesion]

    if len(preguntas_no_respondidas) < num_dados:
        if len(st.session_state.preguntas_respondidas_sesion) < 3 and num_dados == 3:
            st.warning("No hay suficientes preguntas nuevas disponibles para el lanzamiento inicial. Reiniciando la lista de preguntas respondidas para esta sesión.")
            st.session_state.preguntas_respondidas_sesion = []
            preguntas_no_respondidas = [p for p in range(1, numero_preguntas_disponibles + 1)]
        elif num_dados == 1:
            if not preguntas_no_respondidas:
                st.warning("No hay preguntas nuevas disponibles para el tiro extra. ¡Has respondido todas las preguntas únicas!")
                return []
            return random.sample(preguntas_no_respondidas, 1)
        else:
            st.error(f"¡Necesitas al menos {num_dados} preguntas definidas para lanzar {num_dados} dados únicos!")
            return []

    return random.sample(preguntas_no_respondidas, num_dados)

# --- Función Principal de la Aplicación Streamlit ---
def main():
    st.title("🎲 Bienvenido, introduce tus datos:")
    st.markdown("---")

    # Campos de entrada para Número de Usuario y Nombre de Usuario
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['numero_registro'] = st.text_input("Número de Registro", value=st.session_state['numero_registro'], key="user_id_input", placeholder="Ejemplo: 45322625")
    with col2:
        st.session_state['nombre_usuario'] = st.text_input("Nombre de Usuario", value=st.session_state['nombre_usuario'], key="user_name_input", placeholder="Ejemplo: Hugo Perez")

    st.markdown("---")

    # Botón para validar y luego lanzar dados (solo para las 3 preguntas iniciales)
    if st.button("Lanzar Dados y Obtener Preguntas", use_container_width=True,
                 disabled=st.session_state.preguntas_iniciales_completadas or st.session_state.tiro_extra_1_tomado):
        
        st.session_state.credenciales_validas = False
        registro_valido = False
        nombre_valido = False

        if len(st.session_state['numero_registro']) == 8 and st.session_state['numero_registro'].isdigit():
            registro_valido = True
        else:
            st.error("❌ El **Número de Registro** debe contener exactamente 8 dígitos numéricos.")

        if re.match(r"^\b\w+\b(?:\s+\b\w+\b)+$", st.session_state['nombre_usuario'].strip()):
            nombre_valido = True
        else:
            st.error("❌ El **Nombre de Usuario** debe contener al menos un nombre y un apellido (ej. 'Hugo Perez').")

        if registro_valido and nombre_valido:
            st.session_state.credenciales_validas = True
            st.session_state.ultimos_dados = lanzar_dados(num_dados=3)
            st.session_state.pregunta_extra_dado_1 = None
            st.session_state.pregunta_extra_dado_2 = None
            st.session_state.tiro_extra_1_tomado = False
            st.session_state.tiro_extra_2_tomado = False

            if st.session_state.ultimos_dados:
                st.success("¡Datos válidos! Resultados del lanzamiento inicial:")
                st.write(f"### **Dados lanzados (iniciales):** {', '.join(map(str, st.session_state.ultimos_dados))}")
                st.markdown("---")
            else:
                st.warning("No se pudieron lanzar nuevos dados en este momento.")
        else:
            st.session_state.ultimos_dados = None

    # Mostrar el acumulado de puntos
    st.subheader(f"Puntos Acumulados: {st.session_state.puntos_totales}")
    st.markdown("---")

    def handle_answer_selection(p_num, p_info, selected_option, is_extra_question_type=None):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        points_awarded = 0

        if selected_option == p_info['opciones_correctas']:
            # Lógica para duplicar puntos en la pregunta 28
            if p_num == 28 and p_info.get("accion_puntos") == "duplicar_acumulados":
                # Si la pregunta es la 28 y tiene la acción de duplicar
                points_awarded = st.session_state.puntos_totales
                st.session_state.puntos_totales *= 2 
                st.success(f"¡Respuesta CORRECTA para la pregunta {p_num}! Has DUPLICADO tus puntos a {st.session_state.puntos_totales}!")
            else:
                # Comportamiento estándar para otras preguntas
                points_awarded = p_info['puntos']
                st.session_state.puntos_totales += points_awarded
                st.success(f"¡Respuesta CORRECTA para la pregunta {p_num}! Has ganado {points_awarded} puntos.")
            st.balloons()
        else:
            st.error(f"Respuesta INCORRECTA para la pregunta {p_num}. No has ganado puntos.")
            st.snow()

        time.sleep(2)

        numero_registro_actual = st.session_state['numero_registro']
        nombre_usuario_actual = st.session_state['nombre_usuario']

        # Almacenar la respuesta en el DataFrame de session_state
        nueva_fila = {
            "nombre_staff": st.session_state['nombre_staff'],
            "hora_registro": current_time,
            "numero_usuario": numero_registro_actual,
            "nombre_usuario": nombre_usuario_actual,
            "pregunta_num": p_num,
            "pregunta": p_info['pregunta'],
            "opcion_seleccionada": selected_option,
            "puntos_obtenidos": points_awarded,
            "puntos_acumulados": st.session_state.puntos_totales
        }
        insertar_fila_en_dataframe(nueva_fila) # Usamos la función modificada

        st.session_state.preguntas_respondidas_sesion.append(p_num)

        if is_extra_question_type is None:
            if p_num in st.session_state.ultimos_dados:
                st.session_state.ultimos_dados.remove(p_num)
        elif is_extra_question_type == 1:
            st.session_state.pregunta_extra_dado_1 = None
        elif is_extra_question_type == 2:
            st.session_state.pregunta_extra_dado_2 = None

        st.rerun()

    # Mostrar las preguntas y opciones solo si ya se lanzaron los dados Y las credenciales son válidas
    if st.session_state.ultimos_dados is not None and st.session_state.credenciales_validas:
        st.subheader("Preguntas seleccionadas:")

        # Preguntas iniciales
        for i, pregunta_num in enumerate(list(st.session_state.ultimos_dados)):
            if pregunta_num not in st.session_state.preguntas_respondidas_sesion:
                pregunta_info = preguntas_base.get(
                    pregunta_num,
                    {
                        "pregunta": f"Pregunta {pregunta_num} (no definida):",
                        "opciones": [f"A) Opción {pregunta_num}-1", f"B) Opción {pregunta_num}-2", f"C) Opción {pregunta_num}-3"],
                        "opciones_correctas": "",
                        "puntos": 0
                    }
                )

                st.info(f"""
                    ### Pregunta {pregunta_num}: {pregunta_info['pregunta']}
                    *(Esta pregunta otorga {pregunta_info['puntos']} puntos)*
                """)

                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    if st.button(pregunta_info['opciones'][0], key=f"btn_A_{pregunta_num}", use_container_width=True):
                        handle_answer_selection(pregunta_num, pregunta_info, pregunta_info['opciones'][0])
                with col_b:
                    if st.button(pregunta_info['opciones'][1], key=f"btn_B_{pregunta_num}", use_container_width=True):
                        handle_answer_selection(pregunta_num, pregunta_info, pregunta_info['opciones'][1])
                with col_c:
                    if st.button(pregunta_info['opciones'][2], key=f"btn_C_{pregunta_num}", use_container_width=True):
                        handle_answer_selection(pregunta_num, pregunta_info, pregunta_info['opciones'][2])

                st.markdown("---")

        # Verificar si todas las preguntas iniciales han sido respondidas
        if st.session_state.ultimos_dados == [] and len([q for q in st.session_state.preguntas_respondidas_sesion if q in [p for p in range(1, numero_preguntas_disponibles + 1)]]) >= 3 and not st.session_state.tiro_extra_1_tomado:
            st.session_state.preguntas_iniciales_completadas = True
            st.success("¡Has respondido las 3 preguntas iniciales!")
            st.markdown("---")

            # Opción para lanzar el primer dado extra, solo si hay puntos > 0
            if st.session_state.puntos_totales > 0:
                st.subheader("¡Oportunidad de Puntos Extra (1 de 2)!")
                st.write(f"¿Quieres lanzar un dado más para obtener una pregunta adicional? **Costo: {st.session_state.costo_tiro_extra_1} puntos**")
                if st.button(f"Lanzar 1 Dado Extra (Costo: {st.session_state.costo_tiro_extra_1} puntos)", use_container_width=True, key="lanzar_dado_extra_1", 
                             disabled=st.session_state.tiro_extra_1_tomado or st.session_state.puntos_totales < st.session_state.costo_tiro_extra_1):
                    if st.session_state.puntos_totales >= st.session_state.costo_tiro_extra_1:
                        preguntas_obtenidas = lanzar_dados(num_dados=1)
                        if preguntas_obtenidas:
                            st.session_state.puntos_totales -= st.session_state.costo_tiro_extra_1
                            st.session_state.pregunta_extra_dado_1 = preguntas_obtenidas[0]
                            st.session_state.tiro_extra_1_tomado = True
                            st.success(f"¡Dado extra lanzado! Se restaron {st.session_state.costo_tiro_extra_1} puntos. Pregunta adicional: {st.session_state.pregunta_extra_dado_1}")
                        else:
                            st.warning("No se pudo lanzar el dado extra. No hay más preguntas disponibles o ya las respondiste todas.")
                    else:
                        st.error(f"¡No tienes suficientes puntos para este tiro extra! Necesitas {st.session_state.costo_tiro_extra_1} puntos y tienes {st.session_state.puntos_totales}.")
                    st.rerun()
            else:
                st.info("No tienes puntos acumulados para optar por tiros extra en este momento.")


    # Mostrar la pregunta extra 1 si se lanzó el dado extra y aún no ha sido respondida
    if st.session_state.pregunta_extra_dado_1 is not None and st.session_state.pregunta_extra_dado_1 not in st.session_state.preguntas_respondidas_sesion:
        st.subheader("Pregunta Extra 1:")
        pregunta_num_extra = st.session_state.pregunta_extra_dado_1
        pregunta_info_extra = preguntas_base.get(
            pregunta_num_extra,
            {
                "pregunta": f"Pregunta Extra {pregunta_num_extra} (no definida):",
                "opciones": [f"A) Opción {pregunta_num_extra}-1", f"B) Opción {pregunta_num_extra}-2", f"C) Opción {pregunta_num_extra}-3"],
                "opciones_correctas": "",
                "puntos": 0
            }
        )

        st.warning(f"""
            ### Pregunta Extra 1: {pregunta_info_extra['pregunta']}
            *(Esta pregunta otorga {pregunta_info_extra['puntos']} puntos)*
        """)

        col_a_extra, col_b_extra, col_c_extra = st.columns(3)

        with col_a_extra:
            if st.button(pregunta_info_extra['opciones'][0], key=f"btn_A_extra_1_{pregunta_num_extra}", use_container_width=True):
                handle_answer_selection(pregunta_num_extra, pregunta_info_extra, pregunta_info_extra['opciones'][0], is_extra_question_type=1)
        with col_b_extra:
            if st.button(pregunta_info_extra['opciones'][1], key=f"btn_B_extra_1_{pregunta_num_extra}", use_container_width=True):
                handle_answer_selection(pregunta_num_extra, pregunta_info_extra, pregunta_info_extra['opciones'][1], is_extra_question_type=1)
        with col_c_extra:
            if st.button(pregunta_info_extra['opciones'][2], key=f"btn_C_extra_1_{pregunta_num_extra}", use_container_width=True):
                handle_answer_selection(pregunta_num_extra, pregunta_info_extra, pregunta_info_extra['opciones'][2], is_extra_question_type=1)

        st.markdown("---")
    # Si la pregunta extra 1 fue lanzada y ya no está en la variable (porque se respondió)
    elif st.session_state.tiro_extra_1_tomado and st.session_state.pregunta_extra_dado_1 is None and not st.session_state.tiro_extra_2_tomado:
        st.success("¡Has respondido la primera pregunta extra!")
        st.markdown("---")
        # Mostrar opción para el segundo tiro extra si el primero ya fue respondido y el segundo no ha sido tomado, solo si hay puntos > 0
        if st.session_state.puntos_totales > 0:
            st.subheader("¡Oportunidad de Puntos Extra (2 de 2)!")
            st.write(f"¿Quieres lanzar un dado más para obtener otra pregunta adicional? **Costo: {st.session_state.costo_tiro_extra_2} puntos**")
            if st.button(f"Lanzar 1 Dado Extra (Costo: {st.session_state.costo_tiro_extra_2} puntos)", use_container_width=True, key="lanzar_dado_extra_2", 
                         disabled=st.session_state.tiro_extra_2_tomado or st.session_state.puntos_totales < st.session_state.costo_tiro_extra_2):
                if st.session_state.puntos_totales >= st.session_state.costo_tiro_extra_2:
                    preguntas_obtenidas = lanzar_dados(num_dados=1)
                    if preguntas_obtenidas:
                        st.session_state.puntos_totales -= st.session_state.costo_tiro_extra_2
                        st.session_state.pregunta_extra_dado_2 = preguntas_obtenidas[0]
                        st.session_state.tiro_extra_2_tomado = True
                        st.success(f"¡Dado extra lanzado! Se restaron {st.session_state.costo_tiro_extra_2} puntos. Pregunta adicional: {st.session_state.pregunta_extra_dado_2}")
                    else:
                        st.warning("No se pudo lanzar el dado extra. No hay más preguntas disponibles o ya las respondiste todas.")
                else:
                    st.error(f"¡No tienes suficientes puntos para este tiro extra! Necesitas {st.session_state.costo_tiro_extra_2} puntos y tienes {st.session_state.puntos_totales}.")
                st.rerun()
        else:
            st.info("No tienes puntos acumulados para optar por más tiros extra en este momento.")

    # Mostrar la pregunta extra 2 si se lanzó el dado extra 2 y aún no ha sido respondida
    if st.session_state.pregunta_extra_dado_2 is not None and st.session_state.pregunta_extra_dado_2 not in st.session_state.preguntas_respondidas_sesion:
        st.subheader("Pregunta Extra 2:")
        pregunta_num_extra = st.session_state.pregunta_extra_dado_2
        pregunta_info_extra = preguntas_base.get(
            pregunta_num_extra,
            {
                "pregunta": f"Pregunta Extra {pregunta_num_extra} (no definida):",
                "opciones": [f"A) Opción {pregunta_num_extra}-1", f"B) Opción {pregunta_num_extra}-2", "C) Opción {pregunta_num_extra}-3"],
                "opciones_correctas": "",
                "puntos": 0
            }
        )

        st.warning(f"""
            ### Pregunta Extra 2: {pregunta_info_extra['pregunta']}
            *(Esta pregunta otorga {pregunta_info_extra['puntos']} puntos)*
        """)

        col_a_extra, col_b_extra, col_c_extra = st.columns(3)

        with col_a_extra:
            if st.button(pregunta_info_extra['opciones'][0], key=f"btn_A_extra_2_{pregunta_num_extra}", use_container_width=True):
                handle_answer_selection(pregunta_num_extra, pregunta_info_extra, pregunta_info_extra['opciones'][0], is_extra_question_type=2)
        with col_b_extra:
            if st.button(pregunta_info_extra['opciones'][1], key=f"btn_B_extra_2_{pregunta_num_extra}", use_container_width=True):
                handle_answer_selection(pregunta_num_extra, pregunta_info_extra, pregunta_info_extra['opciones'][1], is_extra_question_type=2)
        with col_c_extra:
            if st.button(pregunta_info_extra['opciones'][2], key=f"btn_C_extra_2_{pregunta_num_extra}", use_container_width=True):
                handle_answer_selection(pregunta_num_extra, pregunta_info_extra, pregunta_info_extra['opciones'][2], is_extra_question_type=2)

        st.markdown("---")
    # Si la pregunta extra 2 fue lanzada y ya no está en la variable (porque se respondió)
    elif st.session_state.tiro_extra_2_tomado and st.session_state.pregunta_extra_dado_2 is None:
        st.success("¡Has respondido la segunda pregunta extra!")
        st.info("¡No hay más tiros extra disponibles en esta sesión!")
    
    # --- Sección de Descarga de Resultados ---
    st.markdown("---")
    st.subheader("Descargar Resultados en CSV")
    col_descargar, _ = st.columns([3, 3])
    with col_descargar:
        # Aquí usamos st.session_state.data_df directamente, ya que es donde
        # almacenamos los datos en memoria en esta versión.
        df_to_download = st.session_state.data_df
        df_to_download = df_to_download[['hora_registro','numero_usuario','nombre_usuario','puntos_acumulados']]
        df_to_download.drop_duplicates(subset=['numero_usuario','nombre_usuario'], inplace=True, keep='last')
        
        # Solo permite descargar si hay datos en el DataFrame
        if not df_to_download.empty:
            st.download_button(
                label="Descargar datos de la sesión actual",
                data=df_to_download.to_csv(index=False).encode('utf-8'),
                file_name='respuestas_sesion_actual.csv',
                mime='text/csv',
                key="download_responses_btn"
            )
        else:
            st.info("Aún no hay datos para descargar en esta sesión.")

    # --- Botón para reiniciar el juego ---
    st.markdown("---")
    st.subheader("Finalizar Juego Actual")
    st.info("Al presionar este botón, se borrarán todos los datos del juego actual para que un nuevo jugador pueda participar.")
    if st.button("Terminar Juego y Empezar Nuevo", use_container_width=True, key="reset_game_btn"):
        reiniciar_juego()

st.code(
        """
# Importar librerias
import sys
import random
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt
import re
import os

# Nombre del archivo CSV donde estarán las preguntas
archivo_preguntas = "preguntas.csv"
# Nuevo archivo CSV usado como base de datos
base_datos = "base_datos.csv"

# Clase Widget
class TestConocimientoApp(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar Fondo
        self.pixmap = QPixmap("fondo.jpg")
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)
        self.label.setGeometry(0, 0, 800, 600) # x, y, ancho, altura
        self.label.setScaledContents(True)

        # Configuración inicial
        self.setWindowTitle("Riskathon")
        try:
            self.setWindowIcon(QIcon("icon.png")) # Icono HSBC
        except Exception as e:
            print(f"Advertencia: No se pudo cargar icon.png - {e}")
        self.setGeometry(100, 100, 800, 600) # x, y, ancho, altura

        # Cargar las preguntas al iniciar la aplicación
        self.preguntas_base = self._cargar_preguntas_desde_csv(archivo_preguntas)
        self.numero_preguntas_disponibles = len(self.preguntas_base)

        if not self.preguntas_base:
            QMessageBox.critical(self, "Error Fatal", "No se pudieron cargar las preguntas. El juego no puede iniciar.")
            sys.exit(1) # Salir si no hay preguntas

        # Estado del juego de la sesión actual
        self.puntos_totales = 0
        self.preguntas_respondidas_sesion = []
        self.active_questions = []
        self.credenciales_validas = False
        self.costo_tiro_extra_1 = 100
        self.costo_tiro_extra_2 = 200
        self.tiro_extra_1_tomado = False
        self.tiro_extra_2_tomado = False
        self.nombre_staff = "Administrador"
        self.numero_registro_actual_sesion = ""
        self.nombre_usuario_actual_sesion = ""
        # DataFrame para almacenar resultados de la sesión actual
        self.data_df_sesion = self.obtener_df_inicial_sesion()
        # DataFrame para almacenar todos los resultados de todos los jugadores y sesiones
        self.data_df_global = self._cargar_registros_globales()
        # Llama a la actualización inicial
        self.init_ui()
        self.update_ui_state() 

    def _cargar_preguntas_desde_csv(self, filename):
        """
        Carga las preguntas desde un archivo CSV usando pandas y las devuelve como un diccionario
        """
        preguntas_cargadas = {}
        try:
            # Leer el CSV con pandas
            df = pd.read_csv(filename, encoding='utf-8')

            # Validar que las columnas necesarias existan
            required_columns = ['pregunta', 'opciones', 'respuesta_correctas', 'puntos']
            if not all(col in df.columns for col in required_columns):
                missing_cols = [col for col in required_columns if col not in df.columns]
                QMessageBox.critical(None, "Error de CSV", f"El archivo '{filename}' no tiene todas las columnas requeridas. Faltan: {', '.join(missing_cols)}.")
                return {}

            # Iterar sobre las filas del DataFrame
            for index, row in df.iterrows():
                try:
                    p_num = index + 1
                    pregunta_texto = str(row['pregunta']).strip()

                    # Parsear las opciones de la columna 'opciones'
                    raw_opciones = str(row['opciones']).strip()
                    opciones_list = [opt.strip() for opt in raw_opciones.split(',') if opt.strip()]

                    if len(opciones_list) < 2:
                         QMessageBox.warning(None, "Error de Formato CSV", f"La pregunta '{pregunta_texto}' (fila {index+2}) no tiene suficientes opciones válidas en la columna 'opciones'. Se requieren al menos 2.")
                         continue

                    puntos = int(row['puntos'])
                    respuesta_correcta = str(row['respuesta_correctas']).strip()
                    accion_puntos = str(row.get('accion_puntos', '')).strip()

                    # Validar que la respuesta_correcta esté entre las opciones
                    if respuesta_correcta not in opciones_list:
                        QMessageBox.warning(None, "Error de Formato CSV", f"La respuesta correcta '{respuesta_correcta}' para la pregunta '{pregunta_texto}' (fila {index+2}) no se encuentra entre las opciones proporcionadas.")
                        continue

                    pregunta_data = {
                        "pregunta": pregunta_texto,
                        "opciones": opciones_list,
                        "opciones_correctas": respuesta_correcta,
                        "puntos": puntos
                    }
                    if accion_puntos:
                        pregunta_data["accion_puntos"] = accion_puntos
                    preguntas_cargadas[p_num] = pregunta_data
                except ValueError as ve:
                    print(f"Error de formato en fila {index} del CSV: {row.to_dict()} - {ve}")
                    QMessageBox.warning(None, "Error de Formato CSV", f"Error en el formato de una fila (fila {index+2} si incluye encabezado) en el CSV. Asegúrate de que 'puntos' sea un número válido y que las opciones estén correctamente formateadas.")
                    continue
            return preguntas_cargadas
        except FileNotFoundError:
            QMessageBox.critical(None, "Error de Archivo", f"El archivo '{filename}' no se encontró. Por favor, asegúrate de que esté en la misma carpeta que el script.")
            return {}
        except pd.errors.EmptyDataError:
            QMessageBox.critical(None, "Error de CSV", f"El archivo '{filename}' está vacío o corrupto.")
            return {}
        except Exception as e:
            QMessageBox.critical(None, "Error de Lectura CSV", f"Ocurrió un error inesperado al leer el archivo CSV: {e}")
            return {}

    def obtener_df_inicial_sesion(self):
        """
        Inicializa un DataFrame vacío para los datos de la sesión actual
        """
        print("Inicializando DataFrame vacío para la sesión actual.")
        return pd.DataFrame(columns=[
            "nombre_staff",
            "hora_registro",
            "numero_usuario",
            "nombre_usuario",
            "pregunta_num",
            "pregunta",
            "opcion_seleccionada",
            "puntos_obtenidos",
            "puntos_acumulados"
        ])

    def _cargar_registros_globales(self):
        """
        Carga el DataFrame de registros globales desde el archivo CSV
        """
        try:
            if os.path.exists(base_datos) and os.path.getsize(base_datos) > 0:
                df = pd.read_csv(base_datos, encoding='utf-8')
                print(f"Registros globales cargados desde {base_datos}.")
                return df
            else:
                print(f"Archivo {base_datos} no encontrado o vacío. Creando DataFrame global vacío.")
                return pd.DataFrame(columns=[
                    "nombre_staff",
                    "hora_registro",
                    "numero_usuario",
                    "nombre_usuario",
                    "puntos_acumulados_finales"
                ])
        except Exception as e:
            QMessageBox.warning(self, "Error de Carga", f"No se pudieron cargar los registros globales desde '{base_datos}': {e}. Se iniciará con un registro vacío.")
            return pd.DataFrame(columns=[
                "nombre_staff",
                "hora_registro",
                "numero_usuario",
                "nombre_usuario",
                "puntos_acumulados_finales"
            ])

    def _guardar_registros_globales(self):
        """
        Guarda el DataFrame de registros globales en el archivo CSV
        """
        try:
            self.data_df_global.to_csv(base_datos, index=False, encoding='utf-8')
            print(f"Registros globales guardados en {base_datos}.")
        except Exception as e:
            QMessageBox.critical(self, "Error al Guardar", f"No se pudieron guardar los registros globales en '{base_datos}': {e}")


    def insertar_fila_en_dataframe_sesion(self, nueva_fila_dict):
        """
        Inserta una nueva fila de datos en el DataFrame de la sesión actual.
        """
        nueva_fila_df = pd.DataFrame([nueva_fila_dict])
        self.data_df_sesion = pd.concat([self.data_df_sesion, nueva_fila_df], ignore_index=True)


    def init_ui(self):
        """
        Codigo de la App
        """
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Título
        title_label = QLabel("🎲 Bienvenido, introduce tus datos:")
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(10)

        # Campos de Usuario
        user_input_layout = QHBoxLayout()

        self.registro_label = QLabel("Número de Registro:")
        self.registro_input = QLineEdit()
        self.registro_input.setPlaceholderText("Ejemplo: 45322652")
        self.registro_input.setMaxLength(8)
        self.registro_input.setFixedWidth(200) # Ajusta el ancho
        user_input_layout.addWidget(self.registro_label)
        user_input_layout.addWidget(self.registro_input)
        user_input_layout.addStretch(1) # Empuja hacia la izquierda

        self.nombre_label = QLabel("Nombre de Usuario:")
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ejemplo: Hugo Lopez")
        self.nombre_input.setFixedWidth(200) # Ajusta el ancho
        user_input_layout.addWidget(self.nombre_label)
        user_input_layout.addWidget(self.nombre_input)
        user_input_layout.addStretch(1) # Empuja hacia la izquierda

        main_layout.addLayout(user_input_layout)
        main_layout.addSpacing(10)

        # Botón Lanzar Dados
        self.lanzar_dados_button = QPushButton("Lanzar Dados")
        self.lanzar_dados_button.setFont(QFont("Arial", 16))
        self.lanzar_dados_button.clicked.connect(self.validar_y_lanzar_dados)
        main_layout.addWidget(self.lanzar_dados_button)
        main_layout.addSpacing(10)

        # Puntos Acumulados
        self.puntos_label = QLabel(f"Puntos Acumulados: {self.puntos_totales}")
        self.puntos_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.puntos_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.puntos_label)
        main_layout.addSpacing(10)

        # Resultados de Dados (Información del último lanzamiento)
        self.dados_resultado_label = QLabel("")
        self.dados_resultado_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.dados_resultado_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.dados_resultado_label)
        main_layout.addSpacing(10)

        # Contenedor de Preguntas
        self.preguntas_container_layout = QVBoxLayout()
        main_layout.addLayout(self.preguntas_container_layout)
        main_layout.addSpacing(20)

        # Botones de Tiro Extra
        self.extra_tiro_layout = QVBoxLayout()
        self.lanzar_extra_1_button = QPushButton(f"Lanzar 1 Dado Extra (Costo: {self.costo_tiro_extra_1} puntos)")
        self.lanzar_extra_1_button.setFont(QFont("Arial", 16))
        self.lanzar_extra_1_button.clicked.connect(lambda: self.lanzar_dado_extra(1))
        self.extra_tiro_layout.addWidget(self.lanzar_extra_1_button)

        self.lanzar_extra_2_button = QPushButton(f"Lanzar 1 Dado Extra (Costo: {self.costo_tiro_extra_2} puntos)")
        self.lanzar_extra_2_button.setFont(QFont("Arial", 16))
        self.lanzar_extra_2_button.clicked.connect(lambda: self.lanzar_dado_extra(2))
        self.extra_tiro_layout.addWidget(self.lanzar_extra_2_button)

        main_layout.addLayout(self.extra_tiro_layout)
        main_layout.addSpacing(20)

        # Contenedor del Jugador Líder
        self.leaderboard_label = QLabel("🏆 Jugador Top: N/A - 0 puntos")
        self.leaderboard_label.setFont(QFont("Arial", 18))
        self.leaderboard_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.leaderboard_label)
        main_layout.addSpacing(10)

        # Botón Descargar CSV
        self.download_button = QPushButton("Descargar Datos")
        self.download_button.setFont(QFont("Arial", 18))
        self.download_button.clicked.connect(self.descargar_datos_csv_global)
        main_layout.addWidget(self.download_button)
        main_layout.addSpacing(10)

        # Botón Reiniciar Juego
        self.reset_game_button = QPushButton("Volver A Jugar")
        self.reset_game_button.setFont(QFont("Arial", 18))
        self.reset_game_button.setStyleSheet("background-color: #f44336; color: white;")
        self.reset_game_button.clicked.connect(self.reiniciar_juego)
        main_layout.addWidget(self.reset_game_button)
        main_layout.addStretch(1)

        self._actualizar_leaderboard() # Actualizar el leaderboard

    def lanzar_dados(self, num_dados=3):
        """
        Simula el lanzamiento de un dado
        """
        # Las preguntas disponibles para una nueva tirada son aquellas que no se han respondido en la sesión actual.
        preguntas_disponibles_para_nueva_tirada = [
            p for p in self.preguntas_base.keys()
            if p not in self.preguntas_respondidas_sesion
        ]

        if len(preguntas_disponibles_para_nueva_tirada) < num_dados:
            QMessageBox.information(self, "Información", "¡No hay suficientes preguntas únicas disponibles para lanzar más dados en esta sesión!")
            return []

        return random.sample(preguntas_disponibles_para_nueva_tirada, num_dados)

    def validar_y_lanzar_dados(self):
        numero_registro = self.registro_input.text()
        nombre_usuario = self.nombre_input.text()

        registro_valido = False
        nombre_valido = False

        if len(numero_registro) == 8 and numero_registro.isdigit():
            registro_valido = True
        else:
            QMessageBox.critical(self, "Error de Validación", "❌ El Número de Registro debe contener exactamente 8 dígitos numéricos.")

        if re.match(r"^\b\w+\b(?:\s+\b\w+\b)+$", nombre_usuario.strip()):
            nombre_valido = True
        else:
            QMessageBox.critical(self, "Error de Validación", "❌ El Nombre de Usuario debe contener al menos un nombre y un apellido (Ejrmplo: 'Hugo Lopez').")

        if registro_valido and nombre_valido:
            self.credenciales_validas = True
            # Guardar el número de registro y nombre para la sesión actual
            self.numero_registro_actual_sesion = numero_registro
            self.nombre_usuario_actual_sesion = nombre_usuario

            # Resetear los estados de los tiros extra para la nueva ronda
            self.tiro_extra_1_tomado = False
            self.tiro_extra_2_tomado = False

            # Generar nuevas preguntas y establecerlas como las activas
            self.active_questions = self.lanzar_dados(num_dados=3)

            if self.active_questions:
                QMessageBox.information(self, "Éxito", "¡Datos válidos! Resultados del lanzamiento inicial.")
                self.dados_resultado_label.setText(f"Preguntas seleccionadas: {', '.join(map(str, self.active_questions))}")
            else:
                QMessageBox.warning(self, "Advertencia", "No se pudieron lanzar nuevos dados en este momento.")
        else:
            self.active_questions = []

        self.update_ui_state()

    def lanzar_dado_extra(self, tiro_num):
        costo = self.costo_tiro_extra_1 if tiro_num == 1 else self.costo_tiro_extra_2
        if self.puntos_totales >= costo:
            preguntas_obtenidas = self.lanzar_dados(num_dados=1)
            if preguntas_obtenidas:
                self.puntos_totales -= costo

                # Borrar las preguntas activas actuales y mostrar solo la nueva pregunta extra
                self.active_questions = preguntas_obtenidas

                if tiro_num == 1:
                    self.tiro_extra_1_tomado = True
                    QMessageBox.information(self, "Tiro Extra", f"¡Dado extra 1 lanzado! Se restaron {costo} puntos. Pregunta adicional: {self.active_questions[0]}")
                else:
                    self.tiro_extra_2_tomado = True
                    QMessageBox.information(self, "Tiro Extra", f"¡Dado extra 2 lanzado! Se restaron {costo} puntos. Pregunta adicional: {self.active_questions[0]}")
            else:
                QMessageBox.warning(self, "Advertencia", "No se pudo lanzar el dado extra. No hay más preguntas disponibles o ya las respondiste todas.")
        else:
            QMessageBox.warning(self, "Puntos Insuficientes", f"¡No tienes suficientes puntos para este tiro extra! Necesitas {costo} puntos y tienes {self.puntos_totales}.")
        self.update_ui_state()

    def handle_answer_selection(self, p_num, selected_option):
        p_info = self.preguntas_base.get(p_num)
        if not p_info:
            QMessageBox.critical(self, "Error", "Información de pregunta no encontrada.")
            return

        if p_num in self.preguntas_respondidas_sesion:
            return

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        points_awarded = 0
        points_awarded_for_csv = 0

        if selected_option == p_info['opciones_correctas']:
            if p_info.get("accion_puntos") == "duplicar_acumulados":
                points_awarded_for_csv = self.puntos_totales
                self.puntos_totales *= 2
                QMessageBox.information(self, "Respuesta Correcta", f"¡Respuesta CORRECTA para la pregunta {p_num}! Has DUPLICADO tus puntos a {self.puntos_totales}!")
            else:
                points_awarded = p_info['puntos']
                points_awarded_for_csv = points_awarded
                self.puntos_totales += points_awarded
                QMessageBox.information(self, "Respuesta Correcta", f"¡Respuesta CORRECTA para la pregunta {p_num}! Has ganado {points_awarded} puntos.")
        else:
            QMessageBox.warning(self, "Respuesta Incorrecta", f"Respuesta INCORRECTA para la pregunta {p_num}. No has ganado puntos.")

        # Guardar cada acción en el DataFrame de la sesión
        nueva_fila_sesion = {
            "nombre_staff": self.nombre_staff,
            "hora_registro": current_time,
            "numero_usuario": self.numero_registro_actual_sesion,
            "nombre_usuario": self.nombre_usuario_actual_sesion,
            "pregunta_num": p_num,
            "pregunta": p_info['pregunta'],
            "opcion_seleccionada": selected_option,
            "puntos_obtenidos": points_awarded_for_csv,
            "puntos_acumulados": self.puntos_totales
        }
        self.insertar_fila_en_dataframe_sesion(nueva_fila_sesion)
        self.preguntas_respondidas_sesion.append(p_num)

        # Eliminar la pregunta respondida de la lista de active_questions para que no se redibuje
        if p_num in self.active_questions:
            self.active_questions.remove(p_num)

        self.update_ui_state() # Actualizar la UI
        self._actualizar_leaderboard() # Actualizar el leaderboard al responder una pregunta

    def update_ui_state(self):
        for i in reversed(range(self.preguntas_container_layout.count())):
            widget = self.preguntas_container_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
            else: # También manejar layouts anidados
                layout_item = self.preguntas_container_layout.itemAt(i)
                if layout_item and layout_item.layout():
                    for j in reversed(range(layout_item.layout().count())):
                        nested_widget = layout_item.layout().itemAt(j).widget()
                        if nested_widget:
                            nested_widget.setParent(None)
                    # Eliminar el layout anidado una vez que sus widgets han sido limpiados
                    self.preguntas_container_layout.removeItem(layout_item)


        self.puntos_label.setText(f"Puntos Acumulados: {self.puntos_totales}")

        # Deshabilitar inputs después de lanzar dados por primera vez
        if self.credenciales_validas:
            self.registro_input.setEnabled(False)
            self.nombre_input.setEnabled(False)
            self.lanzar_dados_button.setEnabled(False)
        else:
            self.registro_input.setEnabled(True)
            self.nombre_input.setEnabled(True)
            self.lanzar_dados_button.setEnabled(True)

        # Mostrar preguntas activas
        if self.active_questions:
            self.dados_resultado_label.setText(f"Preguntas actuales: {', '.join(map(str, self.active_questions))}")
            for pregunta_num in self.active_questions:
                p_info = self.preguntas_base.get(pregunta_num)
                if p_info:
                    # Mostrar puntos directamente si no son 0 para evitar 0 puntos
                    points_text = f"(Esta pregunta otorga {p_info['puntos']} puntos)" if p_info['puntos'] != 0 else ""
                    # Si hay acción de puntos (como duplicar), añadirla al texto
                    if p_info.get("accion_puntos") == "duplicar_acumulados":
                        points_text = "(¡Si aciertas, DUPLICAS tus puntos acumulados!)"

                    question_label = QLabel(f"Pregunta {pregunta_num}: {p_info['pregunta']}\n{points_text}")
                    question_label.setFont(QFont("Arial", 14, QFont.Bold))
                    self.preguntas_container_layout.addWidget(question_label)

                    options_layout = QHBoxLayout()
                    # Los botones siempre estarán habilitados para las preguntas que están en active_questions
                    for i, opcion in enumerate(p_info['opciones']):
                        btn = QPushButton(opcion)
                        btn.setFont(QFont("Arial", 12))
                        btn.clicked.connect(lambda checked, pn=pregunta_num, op=opcion: self.handle_answer_selection(pn, op))
                        options_layout.addWidget(btn)
                    self.preguntas_container_layout.addLayout(options_layout)
                    self.preguntas_container_layout.addWidget(self.create_horizontal_line())
        else:
            self.dados_resultado_label.setText("Lanza los dados para obtener preguntas.")

        all_active_questions_answered = len(self.active_questions) == 0 # Todas las preguntas activas se han eliminado (respondido)

        # Botón de Dado Extra 1
        can_take_extra_1 = (
            self.credenciales_validas and
            all_active_questions_answered and
            not self.tiro_extra_1_tomado and
            self.puntos_totales >= self.costo_tiro_extra_1
        )
        self.lanzar_extra_1_button.setEnabled(can_take_extra_1)

        # Botón de Dado Extra 2
        can_take_extra_2 = (
            self.credenciales_validas and
            all_active_questions_answered and
            self.tiro_extra_1_tomado and
            not self.tiro_extra_2_tomado and
            self.puntos_totales >= self.costo_tiro_extra_2
        )
        self.lanzar_extra_2_button.setEnabled(can_take_extra_2)


        # Lógica para el mensaje de "Fin del Juego"
        no_more_unique_questions_to_roll = len(self.preguntas_respondidas_sesion) == self.numero_preguntas_disponibles

        if self.credenciales_validas and no_more_unique_questions_to_roll and all_active_questions_answered:
            self.lanzar_dados_button.setEnabled(False) # No más lanzamientos iniciales
            self.lanzar_extra_1_button.setEnabled(False)
            self.lanzar_extra_2_button.setEnabled(False)
            if not hasattr(self, '_game_over_message_shown') or not self._game_over_message_shown:
                QMessageBox.information(self, "Fin del Juego", "¡Has respondido todas las preguntas únicas disponibles en el juego!")
                self._game_over_message_shown = True
        else:
            self._game_over_message_shown = False

    def _actualizar_leaderboard(self):
        """
        Actualiza el QLabel para mostrar al jugador con la puntuación más alta
        """
        if self.data_df_global.empty:
            self.leaderboard_label.setText("🏆 Jugador Top: N/A - 0 puntos")
            return

        # Agrupar por usuario (usando numero_usuario y nombre_usuario para unicidad) y obtener el último registro de puntos_acumulados_finales
        df_ultimos_resultados_por_jugador = self.data_df_global.groupby(
            ['numero_usuario', 'nombre_usuario']
        ).last().reset_index()

        # Encontrar el jugador con la puntuación más alta
        if 'puntos_acumulados_finales' in df_ultimos_resultados_por_jugador.columns:
            # Asegurarse de que los puntos sean numéricos y manejar NaNs si los hay
            df_ultimos_resultados_por_jugador['puntos_acumulados_finales'] = pd.to_numeric(
                df_ultimos_resultados_por_jugador['puntos_acumulados_finales'], errors='coerce'
            ).fillna(0) # Rellenar cualquier NaN con 0

            # Encontrar el índice del valor máximo
            idx_max_puntos = df_ultimos_resultados_por_jugador['puntos_acumulados_finales'].idxmax()
            jugador_en_cabeza = df_ultimos_resultados_por_jugador.loc[idx_max_puntos]

            nombre_lider = jugador_en_cabeza['nombre_usuario']
            numero_registro_lider = jugador_en_cabeza['numero_usuario'] # Obtener el número de registro
            puntos_lider = int(jugador_en_cabeza['puntos_acumulados_finales'])

            self.leaderboard_label.setText(
                f"🏆 Jugador Top: {nombre_lider} - {numero_registro_lider} - {puntos_lider} puntos"
            )
        else:
            self.leaderboard_label.setText("🏆 Jugador Top: N/A - 0 puntos (Columna de puntos finales no encontrada)")


    def descargar_datos_csv_global(self):
        """
        Descarga TODOS los registros acumulados de todos los jugadores en el CSV global
        """
        if self.data_df_global.empty:
            QMessageBox.information(self, "Sin Datos", "Aún no hay datos acumulados para descargar.")
            return

        # Abre un diálogo para guardar el archivo
        # Se sugiere el nombre del archivo global
        suggested_filename = base_datos
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Todos los Resultados", suggested_filename, "CSV Files (*.csv);;All Files (*)")

        if file_path:
            try:
                self.data_df_global.to_csv(file_path, index=False, encoding='utf-8')
                QMessageBox.information(self, "Descarga Exitosa", f"Todos los datos acumulados guardados en: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error de Descarga", f"No se pudo guardar el archivo: {e}")

    def reiniciar_juego(self):
        """
        Reinicia todas las variables de la aplicación para comenzar un nuevo juego.
        """
        reply = QMessageBox.question(self, "Terminar Sesión y Empezar Nuevo Jugador",
                                     "¿Estás seguro de que quieres terminar la sesión actual y empezar un nuevo jugador?\nEsto guardará tus resultados finales en la base de datos.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Guardar el registro final del jugador actual en el DataFrame global
            if self.credenciales_validas and self.numero_registro_actual_sesion and self.nombre_usuario_actual_sesion:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                fila_final_jugador = {
                    "nombre_staff": self.nombre_staff,
                    "hora_registro": current_time,
                    "numero_usuario": self.numero_registro_actual_sesion,
                    "nombre_usuario": self.nombre_usuario_actual_sesion,
                    "puntos_acumulados_finales": self.puntos_totales # Puntos finales del juego del jugador
                }
                # Asegurarse de que el DataFrame global tenga todas las columnas necesarias
                for col in fila_final_jugador.keys():
                    if col not in self.data_df_global.columns:
                        self.data_df_global[col] = None # Añadir columna si no existe

                nueva_fila_df = pd.DataFrame([fila_final_jugador])
                self.data_df_global = pd.concat([self.data_df_global, nueva_fila_df], ignore_index=True)
                self._guardar_registros_globales() # Guardar en el archivo CSV
                QMessageBox.information(self, "Sesión Finalizada", "¡Tus resultados han sido guardados en el registro global!")
            else:
                QMessageBox.warning(self, "Advertencia", "No se guardaron resultados ya que no se inició una sesión válida de juego.")

            # Reiniciar el estado de la sesión actual
            self.puntos_totales = 0
            self.preguntas_respondidas_sesion = []
            self.active_questions = []
            self.credenciales_validas = False
            self.tiro_extra_1_tomado = False
            self.tiro_extra_2_tomado = False
            self.registro_input.clear()
            self.nombre_input.clear()
            self.numero_registro_actual_sesion = "" 
            self.nombre_usuario_actual_sesion = ""

            # Limpiar el DataFrame de la sesión para el nuevo juego
            self.data_df_sesion = self.obtener_df_inicial_sesion()

            # Recargar preguntas para asegurar que un nuevo juego empiece con todas las preguntas disponibles
            self.preguntas_base = self._cargar_preguntas_desde_csv(archivo_preguntas)
            self.numero_preguntas_disponibles = len(self.preguntas_base)
            if not self.preguntas_base: # Verificar si la recarga falló
                QMessageBox.critical(self, "Error Fatal", "No se pudieron recargar las preguntas. Por favor, reinicia la aplicación.")
                sys.exit(1)

            QMessageBox.information(self, "Juego Reiniciado", "¡Juego reiniciado! Un nuevo jugador puede comenzar.")
            self.update_ui_state() # Actualizar la UI
            self.dados_resultado_label.setText("") # Limpiar el texto de los dados
            if hasattr(self, '_game_over_message_shown'): # Reset game over flag
                del self._game_over_message_shown
            self._actualizar_leaderboard() # Actualizar el leaderboard después de reiniciar

    def create_horizontal_line(self):
        line = QLabel()
        line.setFrameShape(QLabel.HLine)
        line.setFrameShadow(QLabel.Sunken)
        line.setStyleSheet("margin: 20px 0;")
        return line

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = TestConocimientoApp()
    window.show()
    sys.exit(app.exec_())
        """
    )

# --- Bloque de Ejecución Principal ---
if __name__ == "__main__":
    main()