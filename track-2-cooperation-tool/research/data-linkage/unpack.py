from pathlib import Path
import gzip
for p in Path(__file__).resolve().parent.rglob('*.json.gz'):
    target=p.with_suffix('')
    if not target.exists():
        target.write_bytes(gzip.decompress(p.read_bytes()))
