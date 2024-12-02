import re
import sys
import bcrypt

import mysql.connector
from PyQt6 import uic, QtWidgets
from PyQt6.QtGui import QIntValidator, QIcon
from PyQt6.QtWidgets import QLineEdit

from db_connection import connect_to_db
from main_window import MainWindow

from user import User

import rc_icons


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def check_password(stored_hash, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash)


class RegisterWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        uic.loadUi("uis/login_registration2.ui", self)

        self.setWindowTitle("Imobiliare")

        self.setWindowIcon(QIcon('icons/imobiliare-icon.png'))

        self.loginMain.clicked.connect(lambda: window.stackedWidget.setCurrentIndex(1))
        self.registerMain.clicked.connect(lambda: window.stackedWidget.setCurrentIndex(2))

        self.cancel_login.clicked.connect(self.cancel_login_handle)
        self.cancel_register.clicked.connect(self.cancel_register_handle)
        self.back_option.clicked.connect(lambda: window.stackedWidget.setCurrentIndex(0))

        self.loginSubmit.clicked.connect(self.perform_login)
        self.passwordLogIn.setEchoMode(QLineEdit.EchoMode.Password)

        self.agentButton.clicked.connect(self.agent_connect)

        self.clientButton.clicked.connect(self.client_connect)

        self.submitButton.clicked.connect(self.submit_form)

        self.selected_role = ""

        self.emailInput.textChanged.connect(self.on_text_changed)

        self.password_req1.setVisible(False)
        self.password_req2.setVisible(False)
        self.password_req3.setVisible(False)
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordInput.textChanged.connect(self.validate_password)
        self.passwordInput.focusInEvent = self.password_focus_in
        self.passwordInput.focusOutEvent = self.password_focus_out

        self.phoneInput.setValidator(QIntValidator())

        self.return_handle()
        self.stackedWidget.currentChanged.connect(self.update_default_button)
        self.update_default_button(self.stackedWidget.currentIndex())

    def return_handle(self):
        self.emailLogIn.returnPressed.connect(self.loginSubmit.click)
        self.passwordLogIn.returnPressed.connect(self.loginSubmit.click)

        self.firstNameInput.returnPressed.connect(self.submitButton.click)
        self.lastNameInput.returnPressed.connect(self.submitButton.click)
        self.emailInput.returnPressed.connect(self.submitButton.click)
        self.passwordInput.returnPressed.connect(self.submitButton.click)
        self.phoneInput.returnPressed.connect(self.submitButton.click)

    def update_default_button(self, index):
        self.submitButton.setAutoDefault(False)
        self.loginSubmit.setAutoDefault(False)
        if index == 1:
            self.loginSubmit.setAutoDefault(True)
        elif index == 3:
            self.submitButton.setAutoDefault(True)

    def cancel_login_handle(self):
        self.stackedWidget.setCurrentIndex(0)
        self.emailLogIn.clear()
        self.passwordLogIn.clear()

    def cancel_register_handle(self):
        self.stackedWidget.setCurrentIndex(0)
        self.firstNameInput.clear()
        self.lastNameInput.clear()
        self.emailInput.clear()
        self.passwordInput.clear()
        self.phoneInput.clear()
        self.emailInput.setStyleSheet("border: 2px solid transparent; border-radius: 15px; padding: 5px;")
        self.passwordInput.setStyleSheet("border: 2px solid transparent; border-radius: 15px; padding: 5px;")

    def agent_connect(self):
        self.stackedWidget.setCurrentIndex(3)
        self.show_agent_register()
        self.select_agent()

    def client_connect(self):
        self.stackedWidget.setCurrentIndex(3)
        self.show_client_register()
        self.select_client()

    def show_agent_register(self):
        self.titleRegister.setText("Agent Register")

    def show_client_register(self):
        self.titleRegister.setText("Client Register")

    def select_agent(self):
        self.selected_role = "agent"

    def select_client(self):
        self.selected_role = "client"

    def on_text_changed(self):
        email_text = self.emailInput.text()

        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        if re.match(email_pattern, email_text):
            self.emailInput.setStyleSheet("border: 2px solid green; border-radius: 15px; padding: 5px;")
        else:
            self.emailInput.setStyleSheet("border: 2px solid red; border-radius: 15px; padding: 5px;")

    def password_focus_in(self, event):
        self.password_req1.setVisible(True)
        self.password_req2.setVisible(True)
        self.password_req3.setVisible(True)
        super(QLineEdit, self.passwordInput).focusInEvent(event)

    def password_focus_out(self, event):
        self.password_req1.setVisible(False)
        self.password_req2.setVisible(False)
        self.password_req3.setVisible(False)
        super(QLineEdit, self.passwordInput).focusInEvent(event)

    def validate_password_length(self, password):
        return len(password) >= 8

    def password_has_digit(self, password):
        return bool(re.search(r'\d', password))

    def password_has_special_char(self, password):
        return bool(re.search(r'[^A-Za-z0-9]', password))

    def validate_password(self):
        password_input = self.passwordInput.text()
        length_valid = self.validate_password_length(password_input)
        has_digit = self.password_has_digit(password_input)
        has_special_char = self.password_has_special_char(password_input)

        if length_valid:
            self.password_req1.setStyleSheet("color: green;")
        else:
            self.password_req1.setStyleSheet("color: black;")

        if has_digit:
            self.password_req2.setStyleSheet("color: green;")
        else:
            self.password_req2.setStyleSheet("color: black;")

        if has_special_char:
            self.password_req3.setStyleSheet("color: green;")
        else:
            self.password_req3.setStyleSheet("color: black;")

        if length_valid and has_digit and has_special_char:
            self.passwordInput.setStyleSheet("border: 2px solid green; border-radius: 15px; padding: 5px;")
            return True
        else:
            self.passwordInput.setStyleSheet("border: 2px solid red; border-radius: 15px; padding: 5px;")
            return False

    def submit_form(self):

        first_name = self.firstNameInput.text()
        last_name = self.lastNameInput.text()
        email = self.emailInput.text()
        password = self.passwordInput.text()
        phone = self.phoneInput.text()

        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        if (not first_name.strip() or not last_name.strip() or not re.match(email_pattern, email)
                or not self.validate_password() or not phone.strip() or not self.selected_role):
            QtWidgets.QMessageBox.warning(self, "Error", "Please fill all the fields!")
            return

        db = connect_to_db()
        cursor = db.cursor()
        try:
            query = """
                INSERT INTO users (email, first_name, last_name, password, phone, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (email, first_name, last_name, hash_password(password), phone, self.selected_role)
            cursor.execute(query, values)
            db.commit()

            self.firstNameInput.clear()
            self.lastNameInput.clear()
            self.emailInput.clear()
            self.passwordInput.clear()
            self.phoneInput.clear()
            self.emailInput.setStyleSheet("border: 2px solid transparent; border-radius: 15px; padding: 5px;")
            self.passwordInput.setStyleSheet("border: 2px solid transparent; border-radius: 15px; padding: 5px;")
            self.stackedWidget.setCurrentIndex(1)

        except mysql.connector.Error as err:
            QtWidgets.QMessageBox.warning(self, "Error", f"Error: {err}")
        finally:
            cursor.close()
            db.close()

    def perform_login(self):
        email = self.emailLogIn.text()
        password = self.passwordLogIn.text()

        if not email or not password:
            QtWidgets.QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        try:
            connection = connect_to_db()
            cursor = connection.cursor()

            query = """
            SELECT * FROM users WHERE email = %s
            """
            cursor.execute(query, (email,))
            result = cursor.fetchone()

            if result and check_password(result[3].encode('utf-8'), password):
                user = User(result[0], result[1], result[2], result[3], result[4], result[5], result[6])
                self.close()
                self.main_window = MainWindow(user)
                self.main_window.show()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Invalid credentials")

            cursor.close()
            connection.close()

        except mysql.connector.Error as err:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error: {err}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec())
