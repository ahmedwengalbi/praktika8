# quest_master/core/template_engine.py
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Callable, Optional
import qrcode
from io import BytesIO
from datetime import datetime
import os

class TemplateEngine:
    def __init__(self):
        templates_path = "templates"
        if not os.path.exists(templates_path):
            raise RuntimeError(f"Папка шаблонов '{templates_path}' не найдена. Убедитесь, что она существует в корне проекта.")
        if not os.listdir(templates_path):
            raise RuntimeError(f"Папка шаблонов '{templates_path}' пуста. Добавьте необходимые файлы шаблонов.")
        try:
            self.env = Environment(loader=FileSystemLoader(templates_path))
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки шаблонов: {e}")

    @staticmethod
    def generate_dummy_quest(i: int) -> dict:
        return {
            "id": i,
            "title": f"Автоматический квест #{i}",
            "difficulty": ["Легкий", "Средний", "Сложный", "Эпический"][i % 4],
            "reward": 100 + i * 10,
            "description": "Это автоматически сгенерированное описание. " * 10,
            "deadline": datetime.now().isoformat(),
        }

    class BatchExporter:
        @staticmethod
        def generate_100_quests(export_html: bool = False, on_complete: Optional[Callable[[int, str], None]] = None):
            """
            Generate 100 dummy quests using the TemplateEngine. If `export_html` is True,
            write HTML files to `parchments/`. If generation finishes in under 5 seconds
            and `on_complete` callback is provided, call it with (20, 'BOSS_FIGHT').
            """
            import time
            te = TemplateEngine()
            out = []
            start = time.time()
            for i in range(1, 101):
                q = TemplateEngine.generate_dummy_quest(i)
                # render to HTML but do not write heavy PDFs unless requested
                html = te.render('ancient_scroll.html', q)
                out.append(html)
            elapsed = time.time() - start
            if export_html:
                os.makedirs('parchments', exist_ok=True)
                for idx, html in enumerate(out, start=1):
                    path = os.path.join('parchments', f'quest_{idx}.html')
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(html)
            # Boss fight: reward if completed under threshold
            try:
                if elapsed < 5 and on_complete:
                    try:
                        on_complete(20, "BOSS_FIGHT")
                    except Exception:
                        pass
            except Exception:
                pass
            return out

    def render(self, template_name: str, data: Dict):
        try:
            template = self.env.get_template(template_name)
            return template.render(data)
        except Exception as e:
            raise RuntimeError(f"Ошибка рендеринга шаблона '{template_name}': {e}")

    def export_pdf(self, html: str, path: str, on_exported: Optional[Callable[[int, str], None]] = None):
        try:
            # weasyprint is an optional, heavy dependency (requires native libs on Windows).
            # Pylance may report a missing import in environments where it's not installed;
            # silence that specific warning while keeping the runtime import behavior.
            from weasyprint import HTML  # type: ignore[reportMissingImports]
        except Exception:
            print("WeasyPrint не доступен — экспорт в PDF невозможен в этой среде.")
            return
        HTML(string=html).write_pdf(path)
        # report export event (2 XP) and call optional callback
        print(f"+2 XP (EXPORT_DOC). Файл: {path}")
        if on_exported:
            try:
                on_exported(2, "EXPORT_DOC")
            except Exception:
                pass

    def export_docx(self, html: str, path: str, on_exported: Optional[Callable[[int, str], None]] = None):
        try:
            # python-docx may be absent in some environments; silence static analysis warning
            from docx import Document  # type: ignore[reportMissingImports]
        except Exception:
            print("python-docx не установлен — экспорт в DOCX невозможен в этой среде.")
            return
        doc = Document()
        doc.add_paragraph(html)  # Упрощённо
        doc.save(path)
        print(f"+2 XP (EXPORT_DOC). Файл: {path}")
        if on_exported:
            try:
                on_exported(2, "EXPORT_DOC")
            except Exception:
                pass

    def generate_qr(self, url: str) -> bytes:
        try:
            qr = qrcode.QRCode()
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return buffer.getvalue()
        except Exception as e:
            raise RuntimeError(f"Ошибка генерации QR-кода: {e}")


# expose BatchExporter at module level for convenience
BatchExporter = TemplateEngine.BatchExporter