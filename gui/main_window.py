# quest_master/gui/main_window.py
from typing import Optional
from PyQt6.QtWidgets import QMainWindow, QTabWidget
from quest_wizard import QuestWizard
from map_editor import MapEditor
# Gamification panel removed per user request

class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QMainWindow] = None):
        super().__init__(parent)
        self.setWindowTitle("Квест-мастер: Генератор приключений")
        self.setGeometry(100, 100, 1200, 800)
        tab_widget = QTabWidget()
        self.quest_wizard = QuestWizard(self)
        tab_widget.addTab(self.quest_wizard, "Генератор квестов")
        self.map_editor = MapEditor(self)
        tab_widget.addTab(self.map_editor, "Редактор карт")
        # gamification tab intentionally omitted
        self.setCentralWidget(tab_widget)