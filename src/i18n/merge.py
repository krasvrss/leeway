"""Merge the translation tables into src/data/i18n.json ({"hr": {...}, "sl": {...}}).
Run after editing any t*.py file, then run build-www.py / build-web.py."""
import importlib.util, json, pathlib, sys
HERE = pathlib.Path(__file__).parent
out = {"hr": {}, "sl": {}}
seen = {}
for f in sorted(HERE.glob("t*.py")):
    spec = importlib.util.spec_from_file_location(f.stem, f); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    for row in m.T:
        en, hr, sl = row
        if en in seen and (seen[en] != (hr, sl)):
            print(f"note: {en!r} defined twice ({seen[en][0]!r} vs {hr!r}); keeping the later one", file=sys.stderr)
        seen[en] = (hr, sl)
        out["hr"][en] = hr; out["sl"][en] = sl
(HERE.parent / "data/i18n.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
print(len(out["hr"]), "strings")
