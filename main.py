from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap, QPainter, QCursor, QImage  
from PyQt5.QtCore import Qt, QPointF
import requests
import sys


class MapApplication(QWidget):
    def __init__(self):
        super().__init__()

        self.apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
        self.center = {'lon': 37.617635, 'lat': 55.755814}
        self.zoom = 10
        self.map_type = 'map'
        self.is_mouse_pressed = False
        self.map_markers = []

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
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            QLineEdit {
                border: 2px solid #4A90E2;
                border-radius: 5px;
                padding: 3px;
            }
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 5px;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #357AE8;
            }
            QListWidget {
                border: 2px solid #4A90E2;
                border-radius: 5px;
            }
            QListWidget::item {
                background-color: #ffffff;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
        """)


        self.map_type_combo.activated[str].connect(self.onMapTypeChange)

        self.search_edit = QLineEdit(self)
        self.search_edit.setGeometry(10, 480, 400, 30)

        self.search_button = QPushButton('Найти', self)
        self.search_button.setGeometry(420, 480, 80, 30)
        self.search_button.setStyleSheet('''
            QPushButton {
                background-color: #ff0000;
                color: white;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        ''')
        self.search_button.clicked.connect(self.searchObject)
        self.markers_list = QListWidget(self)
        self.markers_list.setGeometry(740, 100, 190, 300)
        self.markers_list.itemClicked.connect(self.onMarkerSelected)

        self.add_marker_button = QPushButton('Добавить метку', self)
        self.add_marker_button.setGeometry(740, 420, 190, 30)
        self.add_marker_button.clicked.connect(self.addMarker)

        self.remove_marker_button = QPushButton('Удалить метку', self)
        self.remove_marker_button.setGeometry(740, 460, 190, 30)
        self.remove_marker_button.clicked.connect(self.removeMarker)

        self.reset_search_button = QPushButton('Сброс поискового результата', self)
        self.reset_search_button.setGeometry(740, 10, 200, 30)
        self.reset_search_button.clicked.connect(self.resetSearchResult)
        
        self.address_label = QLabel('', self)
        self.address_label.setGeometry(740, 490, 190, 30)

        self.update_map()

    def resetSearchResult(self):
        self.address_label.setText('')
        self.removeAllMarkers()
        self.resetMapCenter()
        self.markers_list.clear()


    def removeAllMarkers(self):
        self.map_markers.clear()
        self.update_map()

    def resetMapCenter(self):
        self.center = {'lon': 37.617635, 'lat': 55.755814}
        self.update_map()
        
    def addMarker(self):
        lon, lat = self.center['lon'], self.center['lat']
        marker = {'lon': lon, 'lat': lat, 'address': 'Unknown Address'}
        self.map_markers.append(marker)

        address = self.getAddress(lon, lat)
        marker['address'] = address

        self.updateMapMarkersList()
        self.update_map()

    def getAddress(self, lon, lat):
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": self.apikey,
            "format": "json",
            "geocode": f"{lon},{lat}"
        }
        response = requests.get(url, params=params)
        data = response.json()

        try:
            real_address = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                'GeocoderMetaData']['text']
            return real_address
        except (KeyError, IndexError):
            return 'Unknown Address'

    def removeMarker(self):
        selected_item = self.markers_list.currentItem()
        if selected_item:
            index = self.markers_list.row(selected_item)
            del self.map_markers[index]
            self.updateMapMarkersList()
            self.update_map()

    def updateMapMarkersList(self):
        self.markers_list.clear()
        for marker in self.map_markers:
            address = marker['address']
            item = QListWidgetItem(f'{address}')
            self.markers_list.addItem(item)

    def onMarkerSelected(self):
        if self.map_markers:
            selected_item = self.markers_list.currentItem()
            if selected_item:
                index = self.markers_list.row(selected_item)
                if 0 <= index < len(self.map_markers):
                    marker = self.map_markers[index]
                    self.center['lon'], self.center['lat'] = marker['lon'], marker['lat']
                    self.update_map()

    def update_map(self):
        lon = self.center['lon']
        lat = self.center['lat']

        markers_list = []
        for marker in self.map_markers:
            markers_list.append(f"{marker['lon']},{marker['lat']},comma")

        map_params = {
            "ll": f"{lon},{lat}",
            "z": self.zoom,
            "l": self.map_type,
            "pt": "~".join(markers_list)
        }

        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=map_params)

        with open("map.png", "wb") as f:
            f.write(response.content)

        self.pixmap = QPixmap('map.png')
        pixmap = self.pixmap.scaled(780, 520, Qt.KeepAspectRatio)
        self.map_label.setPixmap(pixmap)

    def convert_geo_to_pixel(self, lon, lat):
        center_x = 780 / 2
        center_y = 520 / 2
        
        lon_diff = lon - self.center['lon']
        lat_diff = self.center['lat'] - lat
        
        lon_scale = 360 / (2 ** (self.zoom + 8))
        lat_scale = 170 / (2 ** (self.zoom + 8))
        
        pixel_x = center_x + lon_diff / lon_scale
        pixel_y = center_y + lat_diff / lat_scale
        
        return pixel_x, pixel_y


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
            print(self.map_markers)
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

    def searchObject(self):
        query = self.search_edit.text()
        if query:
            url = "https://geocode-maps.yandex.ru/1.x/"
            params = {
                "apikey": self.apikey,
                "format": "json",
                "geocode": query
            }
            response = requests.get(url, params=params)
            data = response.json()

            if data['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'] == '0':
                QMessageBox.warning(self, 'Поиск объекта', 'Объект не найден.')
                return

            address = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                'GeocoderMetaData']['text']
            self.address_label.setText(f'Адрес: {address}')

            coordinates_str = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point'][
                'pos']
            coordinates = [float(coord) for coord in coordinates_str.split()]

            marker = {'lon': coordinates[0], 'lat': coordinates[1], 'address': address}
            self.map_markers.append(marker)
            self.updateMapMarkersList()
            self.update_map()

            self.center['lon'], self.center['lat'] = coordinates
            self.update_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapApplication()
    ex.show()
    sys.exit(app.exec_())
