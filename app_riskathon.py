# Importar librerias
import sys
import random
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import re

# Datos de Preguntas y Opciones
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



numero_preguntas_disponibles = len(preguntas_base)

class TestConocimientoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎲 Riskathon")
        try:
            self.setWindowIcon(QIcon("icon.png")) # Asegúrate de tener un archivo icon.png si quieres un ícono
        except Exception as e:
            print(f"Advertencia: No se pudo cargar icon.png - {e}")
        self.setGeometry(100, 100, 800, 600) # x, y, ancho, altura

        # Estado del juego
        self.puntos_totales = 0
        self.preguntas_respondidas_sesion = [] # Tracks all unique questions answered in the current session (for CSV and overall game state)
        self.active_questions = [] # Stores the question numbers currently displayed on screen
        self.credenciales_validas = False
        self.costo_tiro_extra_1 = 100
        self.costo_tiro_extra_2 = 200
        self.tiro_extra_1_tomado = False # Flag to know if the first extra roll was used in the current round
        self.tiro_extra_2_tomado = False # Flag to know if the second extra roll was used in the current round
        self.nombre_staff = "Administrador" # Puede ser un input si es necesario
        # DataFrame para almacenar resultados
        self.data_df = self.obtener_df_inicial()

        self.init_ui()
        self.update_ui_state() # Llama a la actualización inicial

    def obtener_df_inicial(self):
        """
        Inicializa un DataFrame vacío para los datos.
        """
        print("Inicializando DataFrame vacío para la aplicación.")
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

    def insertar_fila_en_dataframe(self, nueva_fila_dict):
        """
        Inserta una nueva fila de datos en el DataFrame.
        """
        nueva_fila_df = pd.DataFrame([nueva_fila_dict])
        self.data_df = pd.concat([self.data_df, nueva_fila_df], ignore_index=True)

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # --- Título ---
        title_label = QLabel("🎲 Bienvenido, introduce tus datos:")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(10)

        # --- Campos de Usuario ---
        user_input_layout = QHBoxLayout()

        self.registro_label = QLabel("Número de Registro:")
        self.registro_input = QLineEdit()
        self.registro_input.setPlaceholderText("Ejemplo: 45322625")
        self.registro_input.setMaxLength(8)
        self.registro_input.setFixedWidth(200) # Ajusta el ancho
        user_input_layout.addWidget(self.registro_label)
        user_input_layout.addWidget(self.registro_input)
        user_input_layout.addStretch(1) # Empuja hacia la izquierda

        self.nombre_label = QLabel("Nombre de Usuario:")
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ejemplo: Hugo Perez")
        self.nombre_input.setFixedWidth(200) # Ajusta el ancho
        user_input_layout.addWidget(self.nombre_label)
        user_input_layout.addWidget(self.nombre_input)
        user_input_layout.addStretch(1) # Empuja hacia la izquierda

        main_layout.addLayout(user_input_layout)
        main_layout.addSpacing(10)

        # --- Botón Lanzar Dados ---
        self.lanzar_dados_button = QPushButton("Lanzar Dados y Obtener Preguntas")
        self.lanzar_dados_button.setFont(QFont("Arial", 12))
        self.lanzar_dados_button.clicked.connect(self.validar_y_lanzar_dados)
        main_layout.addWidget(self.lanzar_dados_button)
        main_layout.addSpacing(10)

        # --- Puntos Acumulados ---
        self.puntos_label = QLabel(f"Puntos Acumulados: {self.puntos_totales}")
        self.puntos_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.puntos_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.puntos_label)
        main_layout.addSpacing(10)

        # --- Resultados de Dados (Información del último lanzamiento) ---
        self.dados_resultado_label = QLabel("")
        self.dados_resultado_label.setFont(QFont("Arial", 18, QFont.Bold)) # Letra más grande
        self.dados_resultado_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.dados_resultado_label)
        main_layout.addSpacing(10)

        # --- Contenedor de Preguntas ---
        self.preguntas_container_layout = QVBoxLayout()
        main_layout.addLayout(self.preguntas_container_layout)
        main_layout.addSpacing(20)

        # --- Botones de Tiro Extra ---
        self.extra_tiro_layout = QVBoxLayout()
        self.lanzar_extra_1_button = QPushButton(f"Lanzar 1 Dado Extra (Costo: {self.costo_tiro_extra_1} puntos)")
        self.lanzar_extra_1_button.setFont(QFont("Arial", 12))
        self.lanzar_extra_1_button.clicked.connect(lambda: self.lanzar_dado_extra(1))
        self.extra_tiro_layout.addWidget(self.lanzar_extra_1_button)

        self.lanzar_extra_2_button = QPushButton(f"Lanzar 1 Dado Extra (Costo: {self.costo_tiro_extra_2} puntos)")
        self.lanzar_extra_2_button.setFont(QFont("Arial", 12))
        self.lanzar_extra_2_button.clicked.connect(lambda: self.lanzar_dado_extra(2))
        self.extra_tiro_layout.addWidget(self.lanzar_extra_2_button)

        main_layout.addLayout(self.extra_tiro_layout)
        main_layout.addSpacing(20)

        # --- Botón Descargar CSV ---
        self.download_button = QPushButton("Descargar Resultados en CSV")
        self.download_button.setFont(QFont("Arial", 12))
        self.download_button.clicked.connect(self.descargar_datos_csv)
        main_layout.addWidget(self.download_button)
        main_layout.addSpacing(10)

        # --- Botón Reiniciar Juego ---
        self.reset_game_button = QPushButton("Terminar Juego y Empezar Nuevo")
        self.reset_game_button.setFont(QFont("Arial", 12))
        self.reset_game_button.setStyleSheet("background-color: #f44336; color: white;") # Rojo para que destaque
        self.reset_game_button.clicked.connect(self.reiniciar_juego)
        main_layout.addWidget(self.reset_game_button)

        # Establecer la política de tamaño para que los layouts se expandan
        main_layout.addStretch(1)

    def lanzar_dados(self, num_dados=3):
        """
        Simula el lanzamiento de 'num_dados' dados, seleccionando 'num_dados' números únicos
        del rango 1 hasta numero_preguntas_disponibles, asegurándose de no repetir
        preguntas ya respondidas en la sesión actual.
        """
        # Las preguntas disponibles para una *nueva* tirada son aquellas que
        # no se han respondido en la sesión actual.
        preguntas_disponibles_para_nueva_tirada = [
            p for p in range(1, numero_preguntas_disponibles + 1)
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
            QMessageBox.critical(self, "Error de Validación", "❌ El Nombre de Usuario debe contener al menos un nombre y un apellido (ej. 'Hugo Perez').")

        if registro_valido and nombre_valido:
            self.credenciales_validas = True
            
            # Resetear los estados de los tiros extra para la nueva ronda
            self.tiro_extra_1_tomado = False
            self.tiro_extra_2_tomado = False

            # Generar nuevas preguntas y establecerlas como las activas
            self.active_questions = self.lanzar_dados(num_dados=3)

            if self.active_questions:
                QMessageBox.information(self, "Éxito", "¡Datos válidos! Resultados del lanzamiento inicial.")
                self.dados_resultado_label.setText(f"Dados lanzados (iniciales): {', '.join(map(str, self.active_questions))}")
            else:
                QMessageBox.warning(self, "Advertencia", "No se pudieron lanzar nuevos dados en este momento.")
        else:
            self.active_questions = [] # Clear active questions if validation fails

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
        p_info = preguntas_base.get(p_num)
        if not p_info:
            QMessageBox.critical(self, "Error", "Información de pregunta no encontrada.")
            return

        # Si la pregunta ya fue respondida (lo que no debería pasar si se borran bien, pero como precaución)
        if p_num in self.preguntas_respondidas_sesion:
            return

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        points_awarded = 0
        points_awarded_for_csv = 0 # Para el caso especial de duplicar puntos

        if selected_option == p_info['opciones_correctas']:
            if p_num == 28 and p_info.get("accion_puntos") == "duplicar_acumulados":
                points_awarded_for_csv = self.puntos_totales # Almacena los puntos actuales antes de duplicar para el CSV
                self.puntos_totales *= 2
                QMessageBox.information(self, "Respuesta Correcta", f"¡Respuesta CORRECTA para la pregunta {p_num}! Has DUPLICADO tus puntos a {self.puntos_totales}!")
            else:
                points_awarded = p_info['puntos']
                points_awarded_for_csv = points_awarded # Para el CSV
                self.puntos_totales += points_awarded
                QMessageBox.information(self, "Respuesta Correcta", f"¡Respuesta CORRECTA para la pregunta {p_num}! Has ganado {points_awarded} puntos.")
        else:
            QMessageBox.warning(self, "Respuesta Incorrecta", f"Respuesta INCORRECTA para la pregunta {p_num}. No has ganado puntos.")

        numero_registro_actual = self.registro_input.text()
        nombre_usuario_actual = self.nombre_input.text()

        nueva_fila = {
            "nombre_staff": self.nombre_staff,
            "hora_registro": current_time,
            "numero_usuario": numero_registro_actual,
            "nombre_usuario": nombre_usuario_actual,
            "pregunta_num": p_num,
            "pregunta": p_info['pregunta'],
            "opcion_seleccionada": selected_option,
            "puntos_obtenidos": points_awarded_for_csv,
            "puntos_acumulados": self.puntos_totales
        }
        self.insertar_fila_en_dataframe(nueva_fila)
        self.preguntas_respondidas_sesion.append(p_num) # Añadir a la lista de respondidas para seguimiento general

        # Eliminar la pregunta respondida de la lista de active_questions para que no se redibuje
        if p_num in self.active_questions:
            self.active_questions.remove(p_num)

        self.update_ui_state() # Crucial call to refresh the UI

    def update_ui_state(self):
        # Limpiar *todos* los widgets dentro del layout del contenedor de preguntas
        # Esto asegura que los contenedores de preguntas y opciones se borren por completo
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
            self.lanzar_dados_button.setEnabled(False) # Deshabilitar el botón principal después del primer lanzamiento válido
        else:
            self.registro_input.setEnabled(True)
            self.nombre_input.setEnabled(True)
            self.lanzar_dados_button.setEnabled(True)


        # Mostrar preguntas activas (las que quedan en self.active_questions)
        if self.active_questions:
            self.dados_resultado_label.setText(f"Preguntas actuales: {', '.join(map(str, self.active_questions))}")
            for pregunta_num in self.active_questions:
                p_info = preguntas_base.get(pregunta_num)
                if p_info:
                    question_label = QLabel(f"Pregunta {pregunta_num}: {p_info['pregunta']}\n*(Esta pregunta otorga {p_info['puntos']} puntos)")
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
                    self.preguntas_container_layout.addWidget(self.create_horizontal_line()) # Separador
        else:
            self.dados_resultado_label.setText("Lanza los dados para obtener preguntas.")


        # Controlar habilitación/deshabilitación de botones de tiro extra
        # Un tiro extra se habilita solo si todas las preguntas 'activas' actuales han sido respondidas
        # (es decir, self.active_questions está vacía)
        # y si el tiro extra correspondiente no se ha tomado todavía y el jugador tiene puntos suficientes.
        
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
            all_active_questions_answered and # Todas las preguntas activas deben estar respondidas
            self.tiro_extra_1_tomado and # El primer tiro extra ya se tomó
            not self.tiro_extra_2_tomado and # El segundo tiro extra no se ha tomado
            self.puntos_totales >= self.costo_tiro_extra_2
        )
        self.lanzar_extra_2_button.setEnabled(can_take_extra_2)


        # Lógica para el mensaje de "Fin del Juego"
        # El juego termina si no hay más preguntas únicas disponibles para lanzar.
        no_more_unique_questions_to_roll = len(self.preguntas_respondidas_sesion) == numero_preguntas_disponibles

        if self.credenciales_validas and no_more_unique_questions_to_roll and all_active_questions_answered:
            self.lanzar_dados_button.setEnabled(False) # No más lanzamientos iniciales
            self.lanzar_extra_1_button.setEnabled(False)
            self.lanzar_extra_2_button.setEnabled(False)
            if not hasattr(self, '_game_over_message_shown') or not self._game_over_message_shown:
                QMessageBox.information(self, "Fin del Juego", "¡Has respondido todas las preguntas únicas disponibles en el juego!")
                self._game_over_message_shown = True
        else:
            self._game_over_message_shown = False


    def descargar_datos_csv(self):
        if self.data_df.empty:
            QMessageBox.information(self, "Sin Datos", "Aún no hay datos para descargar en esta sesión.")
            return

        # Abre un diálogo para guardar el archivo
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Resultados CSV", "respuestas_sesion_actual.csv", "CSV Files (*.csv);;All Files (*)")

        if file_path:
            try:
                self.data_df.to_csv(file_path, index=False, encoding='utf-8')
                QMessageBox.information(self, "Descarga Exitosa", f"Datos guardados en: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error de Descarga", f"No se pudo guardar el archivo: {e}")

    def reiniciar_juego(self):
        """
        Reinicia todas las variables de la aplicación para comenzar un nuevo juego.
        """
        reply = QMessageBox.question(self, "Reiniciar Juego",
                                     "¿Estás seguro de que quieres terminar el juego actual y empezar uno nuevo?\nEsto borrará los datos de la sesión actual.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.puntos_totales = 0
            self.preguntas_respondidas_sesion = []
            self.active_questions = []
            self.credenciales_validas = False
            self.tiro_extra_1_tomado = False
            self.tiro_extra_2_tomado = False
            self.registro_input.clear()
            self.nombre_input.clear()

            # Limpiar el DataFrame para el nuevo juego
            self.data_df = self.obtener_df_inicial()

            QMessageBox.information(self, "Juego Reiniciado", "¡Juego reiniciado! Un nuevo jugador puede comenzar.")
            self.update_ui_state() # Actualizar la UI para reflejar el estado inicial
            self.dados_resultado_label.setText("") # Limpiar el texto de los dados
            if hasattr(self, '_game_over_message_shown'): # Reset game over flag
                del self._game_over_message_shown


    def create_horizontal_line(self):
        line = QLabel()
        line.setFrameShape(QLabel.HLine)
        line.setFrameShadow(QLabel.Sunken)
        line.setStyleSheet("margin: 5px 0;") # Espaciado
        return line

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Un estilo más moderno para la app

    window = TestConocimientoApp()
    window.show()
    sys.exit(app.exec_())