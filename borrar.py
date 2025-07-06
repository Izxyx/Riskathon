from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventana con Imagen Completa")
        self.setGeometry(100, 100, 800, 600) # Initial window size

        # Load the pixmap
        self.pixmap = QPixmap("icon.png")
        if self.pixmap.isNull():
            print("Error: No se pudo cargar 'icon.png'. Asegúrate de que el archivo existe en la misma carpeta.")
            # Create a dummy pixmap if the file is not found
            self.pixmap = QPixmap(200, 200)
            self.pixmap.fill(self.palette().window().color())


        # Create the label
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)
        self.label.setScaledContents(True) # This is crucial for scaling the image

        # Create a vertical layout and add the label to it
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0) # Remove any margins around the image

        # Set the layout for the window
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())