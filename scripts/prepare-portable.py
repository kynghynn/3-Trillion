"""Make every source page usable directly from disk, without a web server."""
from pathlib import Path
from urllib.parse import urlsplit
import re
root=Path(__file__).resolve().parents[1]/'site'
for page in root.rglob('*.html'):
    prefix='../'*(len(page.relative_to(root).parts)-1) or './'
    def localize(match):
        attr,url=match.groups();u=urlsplit(url);path=u.path.lstrip('/')
        if not path or path.endswith('/'):path+='index.html'
        return f'{attr}="{prefix}{path}'+('?' + u.query if u.query else '')+('#' + u.fragment if u.fragment else '')+'"'
    text=re.sub(r'(href|src)="(/[^\"]*)"',localize,page.read_text())
    text=re.sub(r'\sdata-file-root="[^"]*"','',text)
    text=text.replace('<body ',f'<body data-file-root="{prefix}" ',1)
    page.write_text(text)
print('All page links use local relative paths.')
