# quest_master/gui/quest_wizard.py
from typing import Dict, Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QComboBox, QSpinBox, QTextEdit, QDateTimeEdit, QPushButton, QMessageBox, QLabel
from PyQt6.QtGui import QValidator, QPalette, QColor
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QKeySequence
from database import create_connection, save_quest

class TitleValidator(QValidator):
    def validate(self, input_text: str, pos: int) -> tuple:
        if len(input_text) > 50:
            return QValidator.State.Invalid, input_text, pos
        return QValidator.State.Acceptable, input_text, pos

class QuestWizard(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.title_edit = QLineEdit()
        self.title_edit.setValidator(TitleValidator())
        self.title_edit.textChanged.connect(self.autosave)
        layout.addWidget(self.title_edit)
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Легкий", "Средний", "Сложный", "Эпический"])
        self.difficulty_combo.currentTextChanged.connect(self.autosave)
        layout.addWidget(self.difficulty_combo)
        self.reward_spin = QSpinBox()
        self.reward_spin.setRange(10, 10000)
        self.reward_spin.valueChanged.connect(self.autosave)
        layout.addWidget(self.reward_spin)
        self.description_edit = QTextEdit()
        self.description_edit.textChanged.connect(self.on_description_changed)
        layout.addWidget(self.description_edit)
        # live counter for words/chars
        self.counter_label = QLabel("Слова: 0 / 50 — Символы: 0")
        layout.addWidget(self.counter_label)
        layout.addWidget(self.description_edit)
        self.deadline_edit = QDateTimeEdit()
        self.deadline_edit.setDateTime(QDateTime.currentDateTime())
        self.deadline_edit.dateTimeChanged.connect(self.autosave)
        layout.addWidget(self.deadline_edit)
        create_button = QPushButton("Создать квест")
        create_button.clicked.connect(self.create_quest)
        layout.addWidget(create_button)
        # Template engine selection and export buttons
        from PyQt6.QtWidgets import QHBoxLayout, QFileDialog
        te_layout = QHBoxLayout()
        self.template_combo = QComboBox()
        self.template_combo.addItems(["ancient_scroll.html", "guild_contract.html", "royal_decree.html"])
        te_layout.addWidget(self.template_combo)
        export_pdf_btn = QPushButton("Экспорт в PDF")
        export_pdf_btn.clicked.connect(self.export_pdf)
        te_layout.addWidget(export_pdf_btn)
        export_docx_btn = QPushButton("Экспорт в DOCX")
        export_docx_btn.clicked.connect(self.export_docx)
        te_layout.addWidget(export_docx_btn)
        layout.addLayout(te_layout)
        try:
            from PyQt6.QtWidgets import QShortcut
            QShortcut(QKeySequence("Ctrl+Return"), self, self.create_quest)
        except Exception:
            # QShortcut may be unavailable in some PyQt builds; ignore if so
            pass
        self.setLayout(layout)
        self.quest_id: Optional[int] = None

        # initial styles
        self.clear_error_style(self.title_edit)
        self.clear_error_style(self.description_edit)

    def autosave(self):
        data = self.get_data()
        try:
            prev_id = self.quest_id
            new_id = save_quest(self.quest_id, data)
            if new_id is not None:
                self.quest_id = new_id
                print(f"✅ Автосохранение: ID {self.quest_id}")
            # if record was created now (prev_id was None -> new_id assigned), award XP
            if prev_id is None and self.quest_id is not None:
                if hasattr(self.parent(), "gamification_panel"):
                    try:
                        self.parent().gamification_panel.add_xp(3, "CREATE_QUEST")
                    except Exception:
                        pass
        except Exception:
            # ignore autosave failures silently (could log)
            pass

    def on_description_changed(self):
        text = self.description_edit.toPlainText()
        words = len([w for w in text.split() if w.strip()])
        chars = len(text)
        self.counter_label.setText(f"Слова: {words} / 50 — Символы: {chars}")
        # autosave after updating counter
        self.autosave()

    def get_data(self) -> Dict[str, str | int]:
        return {
            "title": self.title_edit.text(),
            "difficulty": self.difficulty_combo.currentText(),
            "reward": self.reward_spin.value(),
            "description": self.description_edit.toPlainText(),
            "deadline": self.deadline_edit.dateTime().toString(Qt.DateFormat.ISODate),
        }

    def validate(self) -> bool:
        valid = True
        if not self.title_edit.text():
            self.highlight(self.title_edit, True)
            valid = False
        else:
            self.highlight(self.title_edit, False)
        if len([w for w in self.description_edit.toPlainText().split() if w.strip()]) < 50:
            self.highlight(self.description_edit, True)
            valid = False
        else:
            self.highlight(self.description_edit, False)
        return valid

    def highlight(self, widget: QWidget, error: bool):
        if error:
            widget.setStyleSheet("border: 2px solid red;")
        else:
            self.clear_error_style(widget)

    def clear_error_style(self, widget: QWidget):
        widget.setStyleSheet("")

    def create_quest(self):
        if not self.validate():
            return
        data = self.get_data()
        try:
            prev_id = self.quest_id
            new_id = save_quest(self.quest_id, data)
            if new_id is not None:
                self.quest_id = new_id
            QMessageBox.information(self, "Успех", "Квест создан!")
            # If the quest didn't exist before and wasn't created via autosave,
            # award XP now (avoid double-award if autosave already did it)
            if prev_id is None and hasattr(self.parent(), "gamification_panel"):
                try:
                    self.parent().gamification_panel.add_xp(3, "CREATE_QUEST")
                except Exception:
                    pass
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить квест: {e}")

    def _get_default_parchment_path(self, ext: str) -> str:
        import time, os
        ts = int(time.time())
        qid = self.quest_id or 0
        os.makedirs('parchments', exist_ok=True)
        return os.path.join('parchments', f'{qid}_{ts}.{ext}')

    def export_pdf(self):
        from PyQt6.QtWidgets import QFileDialog
        if self.quest_id is None:
            QMessageBox.warning(self, "Внимание", "Сначала создайте квест (сохраните).")
            return
        data = self.get_data()
        te = None
        try:
            from template_engine import TemplateEngine
            te = TemplateEngine()
        except Exception:
            QMessageBox.critical(self, "Ошибка", "TemplateEngine недоступен")
            return
        html = te.render(self.template_combo.currentText(), data)
        # embed QR if possible
        try:
            url = f"http://example.com/quest/{self.quest_id}"
            from base64 import b64encode
            img = te.generate_qr(url)
            b64 = b64encode(img).decode('ascii')
            html = f'<img src="data:image/png;base64,{b64}" alt="QR" />' + html
        except Exception:
            pass
        default = self._get_default_parchment_path('pdf')
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить PDF", default, "PDF Files (*.pdf)")
        if path:
            te.export_pdf(html, path, on_exported=self._on_exported)

    def export_docx(self):
        from PyQt6.QtWidgets import QFileDialog
        if self.quest_id is None:
            QMessageBox.warning(self, "Внимание", "Сначала создайте квест (сохраните).")
            return
        data = self.get_data()
        try:
            from template_engine import TemplateEngine
            te = TemplateEngine()
        except Exception:
            QMessageBox.critical(self, "Ошибка", "TemplateEngine недоступен")
            return
        html = te.render(self.template_combo.currentText(), data)
        default = self._get_default_parchment_path('docx')
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить DOCX", default, "Word Files (*.docx)")
        if path:
            te.export_docx(html, path, on_exported=self._on_exported)

    def _on_exported(self, xp: int, reason: str):
        if hasattr(self.parent(), 'gamification_panel'):
            try:
                self.parent().gamification_panel.add_xp(xp, reason)
            except Exception:
                pass
        