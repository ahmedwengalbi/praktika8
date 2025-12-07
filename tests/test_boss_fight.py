# simple boss-fight performance check for local TemplateEngine
import time
from core.template_engine import TemplateEngine

def test_100_quests_in_5_seconds():
    start = time.time()
    for _ in range(100):
        TemplateEngine()  # quick construction test
    elapsed = time.time() - start
    assert elapsed < 5
    print(f"Босс повержен за {elapsed:.2f} секунд! 20 XP")


if __name__ == '__main__':
    test_100_quests_in_5_seconds()