import PyInstaller.__main__
import os
from pathlib import Path

for f in os.listdir():
    if f.endswith('.pyw'):
        file_name = f
        conf_name = Path(f).stem + ".ini"
        break

PyInstaller.__main__.run([
    file_name,
    '--clean',
    '-y',
    '--icon=images/linkedin.ico',
    '--add-data=images/linkedin.ico;images/',
    '--add-data=resources/*;resources/',
    f'--add-data={conf_name};.',
])