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

        # Configuración inicial
        self.setWindowTitle("Riskathon")
        try:
            self.setWindowIcon(QIcon("icon.png")) # Icono HSBC
        except Exception as e:
            print(f"Advertencia: No se pudo cargar icon.png - {e}")
        self.setGeometry(100, 100, 800, 600) # x, y, ancho, altura

        # Configurar Fondo
        self.pixmap = QPixmap("fondo.jpg")
        self.background_label = QLabel(self) # Cambiado a background_label para mayor claridad
        self.background_label.setPixmap(self.pixmap)
        # Ajustar geometría para ocupar toda la ventana. El auto-escalado se manejará con setScaledContents.
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setScaledContents(True) # Esto hace que la imagen se ajuste al tamaño del QLabel

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
        # Establece un layout principal para la ventana
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # HACK: Para que los widgets se superpongan al fondo, necesitamos que el fondo no sea parte del layout principal,
        # o que esté en un QGraphicsView, o simplemente lo redimensionamos en resizeEvent.
        # Por ahora, nos aseguramos de que el fondo se escale al tamaño de la ventana.

        # Título
        title_label = QLabel("🎲 Bienvenido, introduce tus datos:")
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20) # Más espacio

        # Campos de Usuario
        user_input_layout = QHBoxLayout()
        user_input_layout.addStretch(1) # Centrar

        self.registro_label = QLabel("Número de Registro:")
        self.registro_label.setFont(QFont("Arial", 12))
        self.registro_input = QLineEdit()
        self.registro_input.setPlaceholderText("Ejemplo: 45322652")
        self.registro_input.setMaxLength(8)
        self.registro_input.setFixedWidth(200)
        self.registro_input.setFont(QFont("Arial", 12))
        user_input_layout.addWidget(self.registro_label)
        user_input_layout.addWidget(self.registro_input)

        user_input_layout.addSpacing(30) # Espacio entre campos

        self.nombre_label = QLabel("Nombre de Usuario:")
        self.nombre_label.setFont(QFont("Arial", 12))
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ejemplo: Hugo Lopez")
        self.nombre_input.setFixedWidth(200)
        self.nombre_input.setFont(QFont("Arial", 12))
        user_input_layout.addWidget(self.nombre_label)
        user_input_layout.addWidget(self.nombre_input)
        user_input_layout.addStretch(1) # Centrar

        main_layout.addLayout(user_input_layout)
        main_layout.addSpacing(20) # Más espacio

        # Botón Lanzar Dados
        self.lanzar_dados_button = QPushButton("Lanzar Dados")
        self.lanzar_dados_button.setFont(QFont("Arial", 16, QFont.Bold))
        self.lanzar_dados_button.clicked.connect(self.validar_y_lanzar_dados)
        self.lanzar_dados_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px 20px; border-radius: 5px;")
        main_layout.addWidget(self.lanzar_dados_button)
        main_layout.addSpacing(20)

        # Puntos Acumulados
        self.puntos_label = QLabel(f"Puntos Acumulados: {self.puntos_totales}")
        self.puntos_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.puntos_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.puntos_label)
        main_layout.addSpacing(15)

        # Resultados de Dados (Información del último lanzamiento)
        self.dados_resultado_label = QLabel("")
        self.dados_resultado_label.setFont(QFont("Arial", 16))
        self.dados_resultado_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.dados_resultado_label)
        main_layout.addSpacing(20)

        # Contenedor de Preguntas
        self.preguntas_container_layout = QVBoxLayout()
        main_layout.addLayout(self.preguntas_container_layout)
        main_layout.addSpacing(20)

        # Botones de Tiro Extra
        self.extra_tiro_layout = QHBoxLayout() # Usar QHBoxLayout para los botones extra
        self.extra_tiro_layout.addStretch(1) # Centrar

        self.lanzar_extra_1_button = QPushButton(f"Lanzar 1 Dado Extra (Costo: {self.costo_tiro_extra_1} pts)")
        self.lanzar_extra_1_button.setFont(QFont("Arial", 14))
        self.lanzar_extra_1_button.clicked.connect(lambda: self.lanzar_dado_extra(1))
        self.lanzar_extra_1_button.setStyleSheet("background-color: #2196F3; color: white; padding: 8px 15px; border-radius: 5px;")
        self.lanzar_extra_1_button.hide() # Ocultar inicialmente
        self.extra_tiro_layout.addWidget(self.lanzar_extra_1_button)

        self.extra_tiro_layout.addSpacing(20)

        self.lanzar_extra_2_button = QPushButton(f"Lanzar 1 Dado Extra (Costo: {self.costo_tiro_extra_2} pts)")
        self.lanzar_extra_2_button.setFont(QFont("Arial", 14))
        self.lanzar_extra_2_button.clicked.connect(lambda: self.lanzar_dado_extra(2))
        self.lanzar_extra_2_button.setStyleSheet("background-color: #FF9800; color: white; padding: 8px 15px; border-radius: 5px;")
        self.lanzar_extra_2_button.hide() # Ocultar inicialmente
        self.extra_tiro_layout.addWidget(self.lanzar_extra_2_button)

        self.extra_tiro_layout.addStretch(1) # Centrar

        main_layout.addLayout(self.extra_tiro_layout)
        main_layout.addSpacing(30)

        # Contenedor del Jugador Líder
        self.leaderboard_label = QLabel("🏆 Jugador Top: N/A - 0 puntos")
        self.leaderboard_label.setFont(QFont("Arial", 18, QFont.StyleItalic))
        self.leaderboard_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.leaderboard_label)
        main_layout.addSpacing(20)

        # Botón Reiniciar Juego
        self.reset_game_button = QPushButton("Volver A Jugar")
        self.reset_game_button.setFont(QFont("Arial", 18, QFont.Bold))
        self.reset_game_button.setStyleSheet("background-color: #f44336; color: white; padding: 10px 20px; border-radius: 5px;")
        self.reset_game_button.clicked.connect(self.reiniciar_juego)
        main_layout.addWidget(self.reset_game_button)
        main_layout.addSpacing(15) # Espacio antes del último botón

        # Botón Descargar CSV (MOVIDO AQUÍ)
        self.download_button = QPushButton("Descargar Datos Globales")
        self.download_button.setFont(QFont("Arial", 16))
        self.download_button.setStyleSheet("background-color: #607D8B; color: white; padding: 8px 15px; border-radius: 5px;")
        self.download_button.clicked.connect(self.descargar_datos_csv_global)
        main_layout.addWidget(self.download_button)
        main_layout.addStretch(1) # Empujar todo hacia arriba

        # Label para el mensaje de fin de juego
        self.game_over_message_label = QLabel("")
        self.game_over_message_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.game_over_message_label.setAlignment(Qt.AlignCenter)
        self.game_over_message_label.setStyleSheet("color: #FF0000;") # Rojo para que se destaque
        main_layout.addWidget(self.game_over_message_label)

        self._actualizar_leaderboard() # Actualizar el leaderboard

    def resizeEvent(self, event):
        """
        Este evento se dispara cada vez que la ventana cambia de tamaño.
        Asegura que el fondo se ajuste a las nuevas dimensiones.
        """
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

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
                # The text for dados_resultado_label is now handled in update_ui_state
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
        # Clear existing questions from the layout
        for i in reversed(range(self.preguntas_container_layout.count())):
            widget = self.preguntas_container_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
            else: # Also handle nested layouts
                layout_item = self.preguntas_container_layout.itemAt(i)
                if layout_item and layout_item.layout():
                    for j in reversed(range(layout_item.layout().count())):
                        nested_widget = layout_item.layout().itemAt(j).widget()
                        if nested_widget:
                            nested_widget.setParent(None)
                    # Remove the nested layout once its widgets have been cleared
                    self.preguntas_container_layout.removeItem(layout_item)

        self.puntos_label.setText(f"Puntos Acumulados: {self.puntos_totales}")

        # Disable inputs after launching dice for the first time
        if self.credenciales_validas:
            self.registro_input.setEnabled(False)
            self.nombre_input.setEnabled(False)
            self.lanzar_dados_button.setEnabled(False)
        else:
            self.registro_input.setEnabled(True)
            self.nombre_input.setEnabled(True)
            self.lanzar_dados_button.setEnabled(True)

        # Determine if there are more unique questions available to be rolled
        more_questions_to_roll = len(self.preguntas_respondidas_sesion) < self.numero_preguntas_disponibles
        all_active_questions_answered = len(self.active_questions) == 0

        # Lógica para mostrar los botones de tiro extra
        if self.credenciales_validas and all_active_questions_answered:
            # Show extra roll button 1 if not taken and enough points
            if not self.tiro_extra_1_tomado and self.puntos_totales >= self.costo_tiro_extra_1 and more_questions_to_roll:
                self.lanzar_extra_1_button.show()
                self.lanzar_extra_1_button.setEnabled(True)
            else:
                self.lanzar_extra_1_button.hide()

            # Show extra roll button 2 if roll 1 was taken and enough points
            if self.tiro_extra_1_tomado and not self.tiro_extra_2_tomado and self.puntos_totales >= self.costo_tiro_extra_2 and more_questions_to_roll:
                self.lanzar_extra_2_button.show()
                self.lanzar_extra_2_button.setEnabled(True)
            else:
                self.lanzar_extra_2_button.hide()
        else:
            # Hide both buttons if conditions are not met
            self.lanzar_extra_1_button.hide()
            self.lanzar_extra_2_button.hide()

        # Check if the game is truly over (no more questions to roll and no more extra rolls can be afforded)
        can_afford_initial_roll = self.credenciales_validas and all_active_questions_answered and more_questions_to_roll
        can_afford_extra_roll_1 = (self.puntos_totales >= self.costo_tiro_extra_1 and not self.tiro_extra_1_tomado) and more_questions_to_roll
        can_afford_extra_roll_2 = (self.puntos_totales >= self.costo_tiro_extra_2 and self.tiro_extra_1_tomado and not self.tiro_extra_2_tomado) and more_questions_to_roll

        game_is_over = self.credenciales_validas and all_active_questions_answered and \
                       not (can_afford_initial_roll or can_afford_extra_roll_1 or can_afford_extra_roll_2)

        if game_is_over:
            self.dados_resultado_label.hide() # Hide the dice roll message
            self.game_over_message_label.setText("Se terminaron tus tiros. Gracias por participar")
            self.game_over_message_label.show()
            self.lanzar_dados_button.setEnabled(False)
            self.lanzar_extra_1_button.setEnabled(False)
            self.lanzar_extra_2_button.setEnabled(False)
        else:
            self.game_over_message_label.hide() # Hide the game over message if game is not over
            if self.active_questions: # If there are active questions, show them
                self.dados_resultado_label.setText(f"Preguntas actuales: {', '.join(map(str, self.active_questions))}")
                self.dados_resultado_label.show()
            elif self.credenciales_validas and all_active_questions_answered and more_questions_to_roll:
                # Only show "Lanza los dados" if logged in, active questions answered, and more questions to roll
                self.dados_resultado_label.setText("Lanza los dados para obtener preguntas.")
                self.dados_resultado_label.show()
            else: # If not logged in, or no active questions and no more rolls
                self.dados_resultado_label.setText("") # Clear the text
                self.dados_resultado_label.hide() # Hide the label


        # Display active questions if any
        if self.active_questions:
            for pregunta_num in self.active_questions:
                p_info = self.preguntas_base.get(pregunta_num)
                if p_info:
                    points_text = f"(Esta pregunta otorga {p_info['puntos']} puntos)" if p_info['puntos'] != 0 else ""
                    if p_info.get("accion_puntos") == "duplicar_acumulados":
                        points_text = "(¡Si aciertas, DUPLICAS tus puntos acumulados!)"

                    question_label = QLabel(f"Pregunta {pregunta_num}: {p_info['pregunta']}\n{points_text}")
                    question_label.setFont(QFont("Arial", 14, QFont.Bold))
                    self.preguntas_container_layout.addWidget(question_label)

                    options_layout = QHBoxLayout()
                    for i, opcion in enumerate(p_info['opciones']):
                        btn = QPushButton(opcion)
                        btn.setFont(QFont("Arial", 12))
                        btn.clicked.connect(lambda checked, pn=pregunta_num, op=opcion: self.handle_answer_selection(pn, op))
                        options_layout.addWidget(btn)
                    self.preguntas_container_layout.addLayout(options_layout)
                    self.preguntas_container_layout.addWidget(self.create_horizontal_line())


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