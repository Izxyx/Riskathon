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

# --- Bloque de Ejecución Principal ---
if __name__ == "__main__":
    main()