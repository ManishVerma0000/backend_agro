import os
import re

def search():
    keywords = ["mobile_orders", "customer_addresses", "last_order"]
    pattern = re.compile("|".join(keywords), re.IGNORECASE)
    
    app_dir = r"c:\reading\A\backend\app"
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_no, line in enumerate(f, 1):
                        if pattern.search(line):
                            rel_path = os.path.relpath(path, app_dir)
                            print(f"{rel_path}:{line_no}: {line.strip()[:120]}")

if __name__ == "__main__":
    search()
