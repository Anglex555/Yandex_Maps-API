import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests


class MapApplication(QWidget):
    def __init__(self):
        super().__init__()

        self.apikey = "Место_для_api"
        self.center = {'lon': 37.617635, 'lat': 55.755814}
        self.zoom = 10

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1200, 900)
        self.setWindowTitle('Maps API')

        self.map_label = QLabel(self)
        self.map_label.setGeometry(0, 0, 1200, 900)

        self.update_map()

    def update_map(self):
        lon = self.center['lon']
        lat = self.center['lat']
        
        map_params = {
            "ll": f"{lon},{lat}",
            "z": self.zoom,
            "l": "map",
            "pt": f"{lon},{lat},pm2blm",
        }

        map_api_server = "https://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=map_params)

        with open("map.png", "wb") as f:
            f.write(response.content)

        pixmap = QPixmap('map.png')
        pixmap = pixmap.scaled(1200, 800, Qt.KeepAspectRatio)
        self.map_label.setPixmap(pixmap)

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
        else:
            self.zoom -= 1
            if self.zoom < 0:
                self.zoom = 0
        self.update_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapApplication()
    ex.show()
    sys.exit(app.exec_())
