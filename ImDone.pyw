import os
import shutil

def delete_silently():
    target = r"C:\devinsprogram"
    try:
        if os.path.exists(target):
            shutil.rmtree(target)
    except Exception:
        pass  # Silently ignore all errors

delete_silently()
