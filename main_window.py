from PyQt6 import uic, QtWidgets
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QFont, QResizeEvent, QPixmap
from PyQt6.QtWidgets import QGridLayout
from PyQt6.uic.properties import QtCore

import listing_widget
from user import User
from listing_widget import ListingWidget
from db_connection import connect_to_db


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, user):
        super().__init__()

        self.user = user

        uic.loadUi("uis/main.ui", self)

        self.setWindowTitle("Imobiliare")

        self.setWindowIcon(QIcon('icons/imobiliare-icon.png'))

        self.num_columns = 3
        self.aspect_ratio = 375 / 442

        self.dashboard_button.setVisible(False)
        self.agent_button.setVisible(False)
        self.favorites_button.setVisible(False)
        self.listings_button.setVisible(False)
        self.viewings_button.setVisible(False)
        self.setup_ui_by_roles()
        self.hello_setup()

        # self.pages.currentChanged.connect(self.buttons_handle)
        self.agent_button.clicked.connect(self.agent_handle)
        self.listings_button.clicked.connect(self.listings_handle)
        self.dashboard_button.clicked.connect(self.dashboard_handle)
        self.favorites_button.clicked.connect(self.favorites_handle)
        self.viewings_button.clicked.connect(self.viewings_handle)

        self.logout_button.setVisible(False)
        self.user_button.clicked.connect(self.toggle_logout)

        self.filters.setVisible(False)
        self.filter_button.clicked.connect(self.toggle_filters)

        self.logout_button.clicked.connect(self.logout_handle)

        self.load_listings_from_database()

        QTimer.singleShot(0, self.trigger_resize_event)

    def showEvent(self, event):
        super().showEvent(event)
        self.trigger_resize_event()

    def trigger_resize_event(self):
        self.resize(self.width() + 1, self.height())
        self.resize(self.width() - 1, self.height())

    def resizeEvent(self, event):
        window_width = self.scrollArea.width() - self.scrollArea.verticalScrollBar().width()

        widget_width = window_width // self.num_columns
        widget_width = max(widget_width, 50)

        widget_height = widget_width // self.aspect_ratio
        widget_height = max(widget_height, 50)

        widget_width = int(widget_width)
        widget_height = int(widget_height)
        aspect_ratio_photo = 290 / 181
        scalling_ratio_photo = widget_width / 333
        photo_height = int(widget_height // aspect_ratio_photo)
        photo_width = int(280 * scalling_ratio_photo)

        for i, widget in enumerate(self.findChildren(ListingWidget)):
            widget.setFixedSize(widget_width, widget_height)
            widget.main_photo.setFixedSize(photo_width, photo_height)

            pixmap = QPixmap(widget.pixmap_path)
            if pixmap:
                scaled_pixmap = pixmap.scaled(widget.main_photo.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                widget.main_photo.setPixmap(scaled_pixmap)
                widget.main_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)

            font_size_title = max(10, widget_width // 22)
            font_size_details = max(8, widget_width // 32)
            font_title = QFont("Century Gothic", font_size_title)
            font_details = QFont("Century Gothic", font_size_details)
            widget.title.setFont(font_title)
            widget.price.setFont(font_details)
            widget.date.setFont(font_details)
            widget.location.setFont(font_details)

            font_size_button = max(8, widget_width // 32)
            font_button = QFont("Century Gothic", font_size_button)
            widget.view_more.setFont(font_button)

            base_button_width = 122
            base_button_height = 32
            button_width = int(base_button_width * widget_width / 355)
            button_height = int(base_button_height * widget_height / 423)

            button_width = max(button_width, 50)
            button_height = max(button_height, 20)

            widget.view_more.setFixedSize(button_width, button_height)

            font_size_favorite = max(30, widget_width // 20)
            font_favorite = QFont("Segoe UI", font_size_favorite)
            widget.favorite.setFont(font_favorite)

            widget.layout().setSpacing(0)

        super().resizeEvent(event)

    def load_listings_from_database(self):
        db = connect_to_db()
        cursor = db.cursor()
        cursor.execute('''
                SELECT l.list_id, l.title, l.description, l.price, l.posted_date, GROUP_CONCAT(i.path) AS image_paths
                FROM listings l
                LEFT JOIN images i ON l.list_id = i.listing_id
                GROUP BY l.list_id
            ''')

        row, col = 0, 0
        for list_id, title, description, price, posted_date, image_paths in cursor:
            paths_array = image_paths.split(",") if image_paths else []
            listing_widget = ListingWidget(list_id, title, description, price, posted_date, paths_array)
            if self.user.role == 'admin' or self.user.role == 'agent':
                listing_widget.favorite.setVisible(False)
            self.listings_grid.addWidget(listing_widget, row, col)
            col += 1
            if col >= self.num_columns:
                row += 1
                col = 0

    def hello_setup(self):
        if self.user.role == 'admin':
            self.hello_label.setText('Hello, admin!')
        else:
            self.hello_label.setText(f"Hello, {self.user.first_name} {self.user.last_name}!")

    def logout_handle(self):
        self.user = None
        self.close()

    def toggle_logout(self):
        is_visible = self.logout_button.isVisible()

        self.logout_button.setVisible(not is_visible)
        self.hello_label.setVisible(is_visible)

    def toggle_filters(self):
        is_visible = self.filters.isVisible()
        self.filters.setVisible(not is_visible)
        self.trigger_resize_event()

    def setup_ui_by_roles(self):
        if self.user.role == 'admin':
            self.dashboard_button.setVisible(True)
            self.listings_button.setVisible(True)
        if self.user.role == 'client':
            self.listings_button.setVisible(True)
            self.favorites_button.setVisible(True)
            self.viewings_button.setVisible(True)
        if self.user.role == 'agent':
            self.listings_button.setVisible(True)
            self.agent_button.setVisible(True)
            self.viewings_button.setVisible(True)

    def agent_handle(self):
        self.pages.setCurrentIndex(5)

    def listings_handle(self):
        self.pages.setCurrentIndex(0)

    def view_listing_handle(self):
        self.pages.setCurrentIndex(1)

    def favorites_handle(self):
        self.pages.setCurrentIndex(2)

    def viewings_handle(self):
        self.pages.setCurrentIndex(3)

    def dashboard_handle(self):
        self.pages.setCurrentIndex(4)
