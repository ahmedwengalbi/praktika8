import sys, traceback
print('cwd:', __file__)
print('sys.path:')
for p in sys.path:
    print('  ', p)
print('\n-- Try import gui.main_window --')
try:
    import gui.main_window
    print('Imported gui.main_window OK')
except Exception:
    traceback.print_exc()

print('\n-- Try import main_window --')
try:
    import main_window
    print('Imported main_window OK')
except Exception:
    traceback.print_exc()
