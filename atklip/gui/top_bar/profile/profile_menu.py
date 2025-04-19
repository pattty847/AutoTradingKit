from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
)
from PySide6.QtCore import Qt
from atklip.gui.qfluentwidgets.components.dialog_box.message_box_base import (
    MessageBoxBase,
)
from atklip.gui.qfluentwidgets import (
    FluentIcon,
    PrimaryPushButton,
    PushButton,
    LineEdit as FluentLineEdit,
    CardWidget,
    TitleLabel,
    BodyLabel,
)
from atklip.gui.qfluentwidgets.window.stacked_widget import StackedWidget


class LoginPage(QWidget):
    def __init__(self, stack_widget):
        super().__init__()
        self.stack_widget = stack_widget

        self.setWindowTitle("Login Page")
        # self.setGeometry(100, 100, 600, 400)

        main_layout = QVBoxLayout()

        # Title label
        title_label = TitleLabel("Login")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px;")

        # Login form container
        form_container = CardWidget()
        form_container.setFixedSize(300, 350)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(5, 10, 5, 15)
        form_layout.setSpacing(10)

        form_layout.addWidget(title_label, alignment=Qt.AlignTop)

        # Username input
        username_label = BodyLabel("Username")
        self.username_input = FluentLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)

        # Password input
        password_label = BodyLabel("Password")
        self.password_input = FluentLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Login button
        login_button = PrimaryPushButton("Login")
        login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(login_button)

        # Social login buttons
        social_layout = QHBoxLayout()
        fb_login_button = PushButton("Facebook")
        fb_login_button.setIcon(FluentIcon.BOOK_SHELF)
        google_login_button = PushButton("Google")
        google_login_button.setIcon(FluentIcon.MAIL)
        social_layout.addWidget(fb_login_button)
        social_layout.addWidget(google_login_button)
        form_layout.addLayout(social_layout)

        # Register button
        register_button = PushButton("Go to Register Page")
        register_button.clicked.connect(self.go_to_register)
        form_layout.addWidget(register_button)

        # Center the form container
        main_layout.addStretch()
        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        # Handle login logic here
        print(f"Logging in with username: {username} and password: {password}")

    def go_to_register(self):
        self.stack_widget.setCurrentIndex(1)


class RegisterPage(QWidget):
    def __init__(self, stack_widget):
        super().__init__()
        self.stack_widget = stack_widget

        self.setWindowTitle("Register Page")
        # self.setGeometry(100, 100, 600, 500)

        main_layout = QVBoxLayout()

        # Title label
        title_label = TitleLabel("Register")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px;")

        # Register form container
        form_container = CardWidget()
        form_container.setFixedSize(300, 450)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(5, 10, 5, 35)
        form_layout.setSpacing(10)

        form_layout.addWidget(title_label, alignment=Qt.AlignTop)

        # Username input
        username_label = BodyLabel("Username")
        self.username_input = FluentLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)

        # Email input
        email_label = BodyLabel("Email")
        self.email_input = FluentLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.email_input)

        # Password input
        password_label = BodyLabel("Password")
        self.password_input = FluentLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)

        # Confirm Password input
        confirm_password_label = BodyLabel("Confirm Password")
        self.confirm_password_input = FluentLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm your password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(confirm_password_label)
        form_layout.addWidget(self.confirm_password_input)

        form_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Register button
        register_button = PrimaryPushButton("Register")
        register_button.clicked.connect(self.handle_register)
        form_layout.addWidget(register_button)

        # Login button
        login_button = PushButton("Go to Login Page")
        login_button.clicked.connect(self.go_to_login)
        form_layout.addWidget(login_button)

        # Center the form container
        main_layout.addStretch()
        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def handle_register(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        # Handle register logic here
        print(
            f"Registering with username: {username}, email: {email}, password: {password}, confirm_password: {confirm_password}"
        )

    def go_to_login(self):
        self.stack_widget.setCurrentIndex(0)


class ProfileWindow(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.resize(320, 350)

        self.stack_widget = QStackedWidget()

        self.login_page = LoginPage(self.stack_widget)
        self.register_page = RegisterPage(self.stack_widget)

        self.stack_widget.addWidget(self.login_page)
        self.stack_widget.addWidget(self.register_page)

        self.stack_widget.setCurrentIndex(0)

        self.viewLayout.addWidget(self.stack_widget)

        self.yesButton.setText("Done")
        self.cancelButton.setText("Cancel")
        self.hideYesButton()
        self.widget.setMinimumWidth(320)
        self.widget.setMinimumHeight(350)

    def validate(self):
        return True
