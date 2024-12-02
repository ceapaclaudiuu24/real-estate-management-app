from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QStackedLayout, QPushButton
import main_window


class ListingWidget(QWidget):
    def __init__(self, list_id, title, description, price, posted_date, image_paths):
        super().__init__()

        uic.loadUi("uis/listing_template.ui", self)

        self.title.setText(title)
        self.price.setText(f"{price} €")
        self.date.setText(f"{posted_date}")

        self.image_paths = image_paths

        if self.image_paths:
            self.pixmap_path = self.image_paths[0]
        else:
            self.pixmap_path = "assets/photos/Imobiliare.PNG"
