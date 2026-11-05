from pathlib import Path
import json,gzip
b=Path(__file__).resolve().parent
for n in json.loads((b/"compressed-files.json").read_text()):
 p=b/n;t=p.with_suffix("")
 if t.exists():raise FileExistsError(t)
 t.write_bytes(gzip.decompress(p.read_bytes()))
