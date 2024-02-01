import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox
from PyQt5.QtGui import QPixmap, QPainter, QCursor
from PyQt5.QtCore import Qt, QPointF
import requests


class MapApplication(QWidget):
    def __init__(self):
        super().__init__()

        self.apikey = "Место_для_api"
        self.center = {'lon': 37.617635, 'lat': 55.755814}
        self.zoom = 10
        self.map_type = 'map'
        self.is_mouse_pressed = False

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1000, 520)
        self.setWindowTitle('Maps API')

        self.map_label = QLabel(self)
        self.map_label.setGeometry(0, 0, 780, 520)

        self.map_type_combo = QComboBox(self)
        self.map_type_combo.addItem("Схема")
        self.map_type_combo.addItem("Спутник")
        self.map_type_combo.addItem("Гибрид")
        self.map_type_combo.setGeometry(740, 50, 150, 30)

        self.map_type_combo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                border: 2px solid #4A90E2;
                border-radius: 5px;
                padding: 3px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 2px;
                border-left-color: #4A90E2;
                border-left-style: solid;
            }
        """)

        self.map_type_combo.activated[str].connect(self.onMapTypeChange)
        self.update_map()

    def update_map(self):
        lon = self.center['lon']
        lat = self.center['lat']

        map_params = {
            "ll": f"{lon},{lat}",
            "z": self.zoom,
            "l": self.map_type,
            "pt": f"{lon},{lat},pm2blm",
        }

        map_api_server = "https://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=map_params)

        with open("map.png", "wb") as f:
            f.write(response.content)

        pixmap = QPixmap('map.png')
        pixmap = pixmap.scaled(780, 520, Qt.KeepAspectRatio)
        self.map_label.setPixmap(pixmap)

    def onMapTypeChange(self, text):
        if text == "Схема":
            self.map_type = 'map'
        elif text == "Спутник":
            self.map_type = 'sat'
        elif text == "Гибрид":
            self.map_type = 'sat,skl'
        self.update_map()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.center['lat'] += 0.01
            self.update_map()
        elif event.key() == Qt.Key_Down:
            self.center['lat'] -= 0.01
            self.update_map()
        elif event.key() == Qt.Key_Left:
            self.center['lon'] -= 0.01
            self.update_map()
        elif event.key() == Qt.Key_Right:
            self.center['lon'] += 0.01
            self.update_map()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        if delta > 0:
            self.zoom += 1
            print(self.zoom)
            if self.zoom > 20:
                self.zoom = 20
        else:
            self.zoom -= 1
            if self.zoom < 1:
                self.zoom = 1
        self.update_map()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_mouse_pressed = True
            self.start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.is_mouse_pressed:
            delta = event.pos() - self.start_pos
            lon_scale = 360 / (2 ** (self.zoom + 8))
            lat_scale = 170 / (2 ** (self.zoom + 8))
            self.center['lon'] -= delta.x() * lon_scale
            self.center['lat'] += delta.y() * lat_scale
            self.update_map()
            self.start_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_mouse_pressed = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapApplication()
    ex.show()
    sys.exit(app.exec_())
