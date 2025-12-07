# quest_master/core/gamification.py
from typing import List, Optional
import json
from pathlib import Path

class Gamification:
    # User-requested LEVELS mapping (name -> threshold)
    LEVELS = {
        "Ученик": 0,
        "Мастер пергаментов": 50,
        "Архимаг документов": 100,
    }

    def __init__(self):
        self.xp: int = 0
        self.achievements: List[str] = []

    def add_xp(self, amount: int, reason: Optional[str] = None):
        """Add XP, record an achievement entry, and print a friendly message."""
        self.xp += amount
        reason_tag = reason if reason is not None else ""
        emoji = "🎉"
        ts = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{ts}  +{amount} XP  ({reason_tag})"
        try:
            self.achievements.append(entry)
        except Exception:
            pass
        print(f"{emoji} +{amount} XP ({reason_tag}). Всего: {self.xp} XP. Уровень: {self.get_level()}")

    def get_level(self) -> str:
        # choose the highest level whose threshold is <= xp
        try:
            items = sorted(self.LEVELS.items(), key=lambda kv: kv[1], reverse=True)
            for name, threshold in items:
                if self.xp >= threshold:
                    return name
        except Exception:
            pass
        return "Ученик"

    def to_dict(self) -> dict:
        return {"xp": self.xp, "achievements": self.achievements}

    @classmethod
    def from_dict(cls, data: dict) -> "Gamification":
        g = cls()
        try:
            g.xp = int(data.get("xp", 0))
            g.achievements = list(data.get("achievements", []))
        except Exception:
            pass
        return g

    def save(self, path: str | Path = "gamification.json") -> None:
        try:
            p = Path(path)
            p.write_text(json.dumps(self.to_dict(), ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    @classmethod
    def load(cls, path: str | Path = "gamification.json") -> "Gamification":
        try:
            p = Path(path)
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                return cls.from_dict(data)
        except Exception:
            pass
        return cls()