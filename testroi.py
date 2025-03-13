import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush
from PySide6.QtCore import Qt

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login Here")
        self.setGeometry(100, 100, 400, 520)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#080710"))
        self.setPalette(palette)

        # Create a form layout
        form_layout = QVBoxLayout()

        # Add title
        title = QLabel("Login Here")
        title.setFont(QFont("Poppins", 32))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white;")
        form_layout.addWidget(title)

        # Add username field
        username_label = QLabel("Username")
        username_label.setFont(QFont("Poppins", 16))
        username_label.setStyleSheet("color: white; margin-top: 30px;")
        form_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Email or Phone")
        self.username_input.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.07);
            color: white;
            border-radius: 3px;
            padding: 10px;
            font-size: 14px;
            font-weight: 300;
        """)
        form_layout.addWidget(self.username_input)

        # Add password field
        password_label = QLabel("Password")
        password_label.setFont(QFont("Poppins", 16))
        password_label.setStyleSheet("color: white; margin-top: 30px;")
        form_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.07);
            color: white;
            border-radius: 3px;
            padding: 10px;
            font-size: 14px;
            font-weight: 300;
        """)
        form_layout.addWidget(self.password_input)

        # Add login button
        login_button = QPushButton("Log In")
        login_button.setStyleSheet("""
            background-color: white;
            color: #080710;
            padding: 15px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 5px;
            margin-top: 50px;
        """)
        form_layout.addWidget(login_button)

        # Add social buttons
        social_layout = QHBoxLayout()

        google_button = QPushButton("Google")
        google_button.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.27);
            color: #eaf0fb;
            padding: 5px 10px;
            border-radius: 3px;
            text-align: center;
        """)
        social_layout.addWidget(google_button)

        facebook_button = QPushButton("Facebook")
        facebook_button.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.27);
            color: #eaf0fb;
            padding: 5px 10px;
            border-radius: 3px;
            text-align: center;
            margin-left: 25px;
        """)
        social_layout.addWidget(facebook_button)

        form_layout.addLayout(social_layout)

        self.setLayout(form_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_page = LoginPage()
    login_page.show()

    sys.exit(app.exec())