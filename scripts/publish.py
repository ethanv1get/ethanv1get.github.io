# -*- coding: utf-8 -*-
"""Create the public Pages artifact using only Python's standard library."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '_site'
# _site is a disposable, fixed build directory, never the source checkout.
if OUTPUT.is_symlink():
    raise ValueError('_site must not be a symbolic link')
# Validate editorial data before touching the last local preview.
from content import load_articles
load_articles(ROOT / 'articles.json')
mainframe_dist = ROOT / 'mainframe' / 'dist'
if not (mainframe_dist / 'index.html').is_file():
    raise ValueError('Mainframe build missing; run npm ci and npm run build in mainframe first')
if OUTPUT.exists():
    shutil.rmtree(OUTPUT)
OUTPUT.mkdir()
env = dict(os.environ, SITE_OUTPUT=str(OUTPUT))
subprocess.run([sys.executable, str(ROOT / 'scripts/build.py')], env=env, check=True)
for name in ('style.css', 'site.js', 'CNAME', '.nojekyll'):
    shutil.copy2(ROOT / name, OUTPUT / name)
for path in (ROOT / 'assets').rglob('*'):
    if path.is_symlink():
        raise ValueError('Public assets must not contain symbolic links')
shutil.copytree(ROOT / 'assets', OUTPUT / 'assets')
shutil.copy2(mainframe_dist / 'index.html', OUTPUT / 'index.html')
shutil.copytree(mainframe_dist / 'mainframe-assets', OUTPUT / 'mainframe-assets')
subprocess.run([sys.executable, str(ROOT / 'scripts/check.py')], env=env, check=True)
print(f'Public artifact ready: {OUTPUT}')
