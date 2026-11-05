from pathlib import Path
import gzip, json
root = Path(__file__).resolve().parent
for name in json.loads((root / "compressed-files.json").read_text()):
    source = root / name
    target = source.with_suffix("")
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite {target}")
    target.write_bytes(gzip.decompress(source.read_bytes()))
print("JSON snapshots unpacked; full activity descriptions require original publisher XML.")
