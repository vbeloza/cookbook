import sys
import sqlite3
from fileinput import close

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox, QListWidget
)
from PyQt6.QtCore import Qt

def create_database():
    conn = sqlite3.connect('cookbook.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

create_database()


class CookbookApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Кулинарная книга')
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Название рецепта")
        self.layout.addWidget(self.name_input)

        self.ingredients_input = QTextEdit(self)
        self.ingredients_input.setPlaceholderText("Ингредиенты (один на строку)")
        self.layout.addWidget(self.ingredients_input)

        self.instructions_input = QTextEdit(self)
        self.instructions_input.setPlaceholderText("Инструкции по приготовлению")
        self.layout.addWidget(self.instructions_input)

        self.category_input = QLineEdit(self)
        self.category_input.setPlaceholderText("Категория")
        self.layout.addWidget(self.category_input)

        self.save_button = QPushButton("Сохранить рецепт", self)
        self.layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_recipe)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Поиск рецептов")
        self.layout.addWidget(self.search_input)

        self.search_button = QPushButton("Найти рецепт", self)
        self.layout.addWidget(self.search_button)
        self.search_button.clicked.connect(self.search_recipes)

        self.results_list = QListWidget(self)
        self.layout.addWidget(self.results_list)

        self.results_list.itemDoubleClicked.connect(self.display_recipe)


    def save_recipe(self):
        name = self.name_input.text()
        ingredients = self.ingredients_input.toPlainText()
        instructions = self.instructions_input.toPlainText()
        category = self.category_input.text()

        if not all([name, ingredients, instructions, category]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля")
            return

        conn = sqlite3.connect('cookbook.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO recipes (name, ingredients, instructions, category)
            VALUES (?, ?, ?, ?)
        ''', (name, ingredients, instructions, category))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Успех", "Рецепт успешно сохранён!")
        self.clear_inputs()


    def clear_inputs(self):
        self.name_input.clear()
        self.ingredients_input.clear()
        self.instructions_input.clear()
        self.category_input.clear()


    def search_recipes(self):
        search_term = self.search_input.text()
        conn = sqlite3.connect('cookbook.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT name FROM recipes WHERE name LIKE ?
        ''', ('%' + search_term + '%',))

        results = cursor.fetchall()
        conn.close()

        self.results_list.clear()
        for row in results:
            self.results_list.addItem(row[0])

        if not results:
            QMessageBox.information(self, "Результаты поиска", "Рецепты не найдены.")


    def display_recipe(self, item):
        name = item.text()
        conn = sqlite3.connect('cookbook.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM recipes WHERE name = ?
        ''', (name,))

        recipe = cursor.fetchone()
        conn.close()

        if recipe:
            details = f"Название: {recipe[1]}\n\nИнгредиенты:\n{recipe[2]}\n\nИнструкции:\n{recipe[3]}\n\nКатегория: {recipe[4]}"
            QMessageBox.information(self, "Рецепт", details)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось найти рецепт.")


class Database:
    def __init__(self):
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        self.connection.commit()

    def add_user(self, username, password):
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists

    def check_user(self, username, password):
        self.cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        if result is not None:
            stored_password = result[0]
            return stored_password == password
        return False  # User does not exist

    def close(self):
        self.connection.close()


class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите имя пользователя")
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Вход", self)
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("Нет аккаунта? Зарегистрируйтесь!", self)
        self.register_button.clicked.connect(self.show_register)

        layout.addWidget(QLabel("Вход пользователя"))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)
        self.setWindowTitle("Вход")


    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.db.check_user(username, password):
            QMessageBox.information(self, "Успех", "Вы успешно вошли в систему!")
            self.open_main()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль.")
            self.username_input.clear()
            self.password_input.clear()

    def show_register(self):
        self.hide()
        self.register_window = RegisterWindow(self.db)
        self.register_window.show()

    def open_main(self):
        self.main_window = CookbookApp()
        self.main_window.show()

    def closeEvent(self, event):
        if event.key() == Qt.Key_Return:  # Проверка нажатия клавиши Enter
            self.open_main()



class RegisterWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите имя пользователя")
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.register_button = QPushButton("Регистрация", self)
        self.register_button.clicked.connect(self.register)

        self.back_button = QPushButton("Назад", self)
        self.back_button.clicked.connect(self.show_login)

        layout.addWidget(QLabel("Регистрация пользователя"))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.register_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)
        self.setWindowTitle("Регистрация")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.db.add_user(username, password):
            QMessageBox.information(self, "Успех", "Вы успешно зарегистрированы!")
            self.show_login()
        else:
            QMessageBox.warning(self, "Ошибка", "Имя пользователя уже существует.")
            self.username_input.clear()
            self.password_input.clear()

    def show_login(self):
        self.hide()
        self.login_window = LoginWindow(self.db)
        self.login_window.show()

    def closeEvent(self, event):
        self.db.close()  # Закрываем базу данных при закрытии окна
        event.accept()


def main():
    app = QApplication(sys.argv)
    db = Database()
    login_window = LoginWindow(db)
    login_window.show()
    sys.exit(app.exec_())
    db.close()


if __name__ == "__main__":
    main()
