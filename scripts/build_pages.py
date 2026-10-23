"""Empaqueta las mismas fuentes y adjuntos para Stlite sin duplicar la lógica."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = {name: (ROOT / name).read_text() for name in ('app.py', 'credito.py', 'motor_original.py')}
for path in (ROOT / 'documentos').iterdir():
    files[path.relative_to(ROOT).as_posix()] = path.read_text()
(ROOT / 'docs' / 'app-bundle.json').write_text(json.dumps(files, ensure_ascii=False))
(ROOT / 'docs' / '.nojekyll').touch()
print('Bundle Stlite generado con', len(files), 'archivos.')
