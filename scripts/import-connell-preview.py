"""Build an isolated NG preview: python3 scripts/import-connell-preview.py SOURCE_REPO."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

source = Path(sys.argv[1]).resolve()
target = Path(__file__).resolve().parents[1] / 'public' / 'connell'
with tempfile.TemporaryDirectory(prefix='connell-preview-') as directory:
    stage = Path(directory)
    for name in ('src', 'public'):
        shutil.copytree(source / name, stage / name)
    for name in ('package.json', 'index.html'):
        shutil.copyfile(source / name, stage / name)
    (stage / 'node_modules').symlink_to(source / 'node_modules', target_is_directory=True)
    for path in (stage / 'src').rglob('*'):
        if path.suffix in ('.jsx', '.js', '.css'):
            path.write_text(path.read_text().replace('/assets/', '/connell/assets/'))
    index = stage / 'index.html'
    index.write_text(index.read_text().replace('<head>', '<head>\n    <meta name="robots" content="noindex, nofollow" />'))
    subprocess.run([str(source / 'node_modules/.bin/vite'), 'build', '--base=/connell/'], cwd=stage, check=True)
    if target.exists():
        raise SystemExit(f'Remove the previous reviewed snapshot explicitly before replacing {target}')
    shutil.copytree(stage / 'dist', target)
print(f'Imported review snapshot to {target}')
