from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsTextItem, QFileDialog
from PyQt6.QtGui import QPainterPath, QPen, QColor, QFont, QFontDatabase, QImage, QPainter
from PyQt6.QtCore import Qt

class MapEditor(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.scene.setSceneRect(0, 0, 800, 600)
        self.scene.setBackgroundBrush(QColor("#f4e4bc"))
        layout.addWidget(self.view)
        tools = QHBoxLayout()
        brush_btn = QPushButton("Кисть")
        brush_btn.clicked.connect(lambda: setattr(self, "mode", "brush"))
        tools.addWidget(brush_btn)
        city_btn = QPushButton("Город")
        city_btn.clicked.connect(lambda: setattr(self, "mode", "marker_green"))
        tools.addWidget(city_btn)
        dungeon_btn = QPushButton("Логово")
        dungeon_btn.clicked.connect(lambda: setattr(self, "mode", "marker_red"))
        tools.addWidget(dungeon_btn)
        tavern_btn = QPushButton("Таверна")
        tavern_btn.clicked.connect(lambda: setattr(self, "mode", "marker_yellow"))
        tools.addWidget(tavern_btn)
        text_btn = QPushButton("Текст")
        text_btn.clicked.connect(lambda: setattr(self, "mode", "text"))
        tools.addWidget(text_btn)
        eraser_btn = QPushButton("Ластик")
        eraser_btn.clicked.connect(self.erase_last)
        tools.addWidget(eraser_btn)
        save_btn = QPushButton("Сохранить карту")
        save_btn.clicked.connect(self.save_map)
        tools.addWidget(save_btn)
        layout.addLayout(tools)
        self.setLayout(layout)
        self.mode = ""
        self.items = []
        self.path: Optional[QPainterPath] = None

        # try to load custom font and report to console
        font_id = QFontDatabase.addApplicationFont("assets/fonts/UncialAntiqua-Regular.ttf")
        if font_id != -1:
            print("Шрифт Uncial Antiqua успешно загружен!")
        else:
            print('qt.qpa.fonts: Cannot open "assets/fonts/UncialAntiqua-Regular.ttf" for reading.')
        self.font = QFont("Uncial Antiqua", 10)
        self.view.mousePressEvent = self.mouse_press
        self.view.mouseMoveEvent = self.mouse_move

    def mouse_press(self, event):
        pos = self.view.mapToScene(event.pos())
        if self.mode == "brush":
            self.path = QPainterPath()
            self.path.moveTo(pos)
            item = QGraphicsPathItem(self.path)
            item.setPen(QPen(QColor("brown"), 3))
            self.scene.addItem(item)
            self.items.append(item)
        elif self.mode.startswith("marker_"):
            color = self.mode.split("_")[1]
            item = QGraphicsEllipseItem(pos.x() - 5, pos.y() - 5, 10, 10)
            item.setBrush(QColor(color))
            self.scene.addItem(item)
            self.items.append(item)
            # persist location to DB if quest_id available
            try:
                parent = getattr(self, 'parent') and self.parent()
                quest_id = None
                if parent is not None and hasattr(parent, 'quest_wizard'):
                    qw = parent.quest_wizard
                    quest_id = getattr(qw, 'quest_id', None)
                if quest_id is not None:
                    import database
                    conn = database.create_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO quest_locations (quest_id, x, y, type) VALUES (?, ?, ?, ?)",
                        (quest_id, float(pos.x()), float(pos.y()), color),
                    )
                    conn.commit()
                    conn.close()
                    print(f"Локация сохранена для квеста {quest_id}: ({pos.x():.1f},{pos.y():.1f}) {color}")
            except Exception:
                pass
        elif self.mode == "text":
            item = QGraphicsTextItem("Локация")
            item.setFont(self.font)
            item.setPos(pos)
            self.scene.addItem(item)
            self.items.append(item)

    def mouse_move(self, event):
        if self.mode == "brush" and self.path:
            pos = self.view.mapToScene(event.pos())
            self.path.lineTo(pos)
            self.items[-1].setPath(self.path)

    def erase_last(self):
        if self.items:
            self.scene.removeItem(self.items.pop())
            print("Последний объект стерт.")

    def save_map(self):
        file = QFileDialog.getSaveFileName(self, "Сохранить карту", "", "PNG (*.png);;JPG (*.jpg)")[0]
        if file:
            image = QImage(800, 600, QImage.Format.Format_ARGB32)
            painter = QPainter(image)
            self.scene.render(painter)
            painter.end()
            image.save(file)
            print(f"Карта сохранена: {file}")
            if hasattr(self.parent(), "gamification_panel"):
                try:
                    self.parent().gamification_panel.add_xp(5, "SAVE_MAP")
                except Exception:
                    pass