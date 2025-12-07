# quest_master/gui/gamification_panel.py
from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QListWidget, QLabel
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from gamification import Gamification
from pathlib import Path
from datetime import datetime


class GamificationPanel(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        # load persisted gamification state if present
        self.gamification = Gamification.load()
        layout = QVBoxLayout()
        self.level_label = QLabel()
        layout.addWidget(self.level_label)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)
        self.achievements = QListWidget()
        layout.addWidget(self.achievements)
        self.setLayout(layout)

        # try to load a bundled sound
        self.sound = QSoundEffect()
        sound_path = Path("assets/sounds/xp.wav")
        if sound_path.exists():
            try:
                self.sound.setSource(QUrl.fromLocalFile(str(sound_path)))
            except Exception:
                pass

        # initialize UI from current state
        self._update_ui()
        # populate achievements list from persisted state
        try:
            for a in getattr(self.gamification, 'achievements', []):
                self.achievements.addItem(a)
        except Exception:
            pass

    def _update_ui(self):
        level = self.gamification.get_level()
        xp = getattr(self.gamification, "xp", 0)
        self.level_label.setText(f"{level} — {xp} XP")
        self.progress.setValue(xp % 100)

    def add_xp(self, amount: int, reason: str | None = None):
        # forward to logic and update UI
        self.gamification.add_xp(amount, reason)
        # update UI elements
        try:
            self._update_ui()
            # add achievement entry with timestamp
            # the Gamification logic already appends a full timestamped entry; reuse it
            try:
                last = self.gamification.achievements[-1]
            except Exception:
                ts = datetime.now().strftime("%H:%M:%S")
                reason_text = reason or ""
                last = f"{ts}  +{amount} XP  ({reason_text})"
            self.achievements.addItem(last)
            # play sound if available
            try:
                src = None
                try:
                    src = self.sound.source()
                except Exception:
                    src = None
                if src is not None:
                    try:
                        if hasattr(src, 'isLocalFile'):
                            if src.isLocalFile():
                                self.sound.play()
                        else:
                            # fallback: try to play regardless
                            self.sound.play()
                    except Exception:
                        pass
            except Exception:
                pass
            # persist state
            try:
                self.gamification.save()
            except Exception:
                pass
        except Exception:
            pass