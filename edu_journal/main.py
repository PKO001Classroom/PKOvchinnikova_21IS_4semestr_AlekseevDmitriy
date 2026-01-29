import sys
from PyQt5.QtWidgets import QApplication
from database import Database
from ui.login_window import LoginWindow
from ui.student_window import StudentWindow
from ui.teacher_window import TeacherWindow


class EduJournalApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.db = Database()
        self.login_window = None
        self.main_window = None
        
    def show_login(self):
        """Показать окно входа"""
        self.login_window = LoginWindow(self.db, self.on_login_success)
        self.login_window.show()

    def on_login_success(self, user):
        """Обработка успешного входа"""
        if user.role == 'student':
            self.main_window = StudentWindow(user, self.db)
        else:
            self.main_window = TeacherWindow(user, self.db)
        
        self.main_window.show()

    def run(self):
        """Запуск приложения"""
        self.show_login()
        return self.app.exec_()


if __name__ == '__main__':
    app = EduJournalApp()
    sys.exit(app.run())