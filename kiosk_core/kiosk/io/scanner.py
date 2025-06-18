
import subprocess
import os
from datetime import datetime

SCAN_OUTPUT_DIR = "data/scans"

def scan_document(filename_prefix="scan"):
    """
    Сканы сохраняются в папку data/scans/ с уникальными именами.
    Требует установленного пакета `simple-scan` или `scanimage`.
    """
    if not os.path.exists(SCAN_OUTPUT_DIR):
        os.makedirs(SCAN_OUTPUT_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(SCAN_OUTPUT_DIR, f"{filename_prefix}_{timestamp}.png")

    try:
        subprocess.run([
            "scanimage",
            "--format=png",
            f"--output-file={output_file}"
        ], check=True)
        
        print(f"✅ Документ отсканирован: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print("❌ Ошибка при сканировании:", e)
        return None
