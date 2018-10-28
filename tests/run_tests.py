import os

tests = [i for i in os.listdir(".") if i.startswith("test_") and i.endswith(".py")]

for t in tests:
    os.system(f"python -m unittest {t[:-3]}")
