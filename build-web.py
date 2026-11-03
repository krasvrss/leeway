"""Build the single-file web version (published as a Claude artifact) from src/."""
import pathlib, sys
ROOT = pathlib.Path(__file__).parent
s = (ROOT / 'src/leeway.src.html').read_text()
s = s.replace('__I18N_JS__', (ROOT / 'src/i18n.js').read_text().replace('__I18N__', (ROOT / 'src/data/i18n.json').read_text().strip()))
for k, f in {'__LAND__':'land-adriatic.json','__LIVE__':'forecast-fallback.json','__HIRES__':'coast-porec-tar.json','__BATHY__':'depth-tarska.json','__SEAMARKS__':'seamarks.json'}.items():
    assert s.count(k) == 1, k
    s = s.replace(k, (ROOT / 'src/data' / f).read_text().strip())
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'leeway-web.html')
out.write_text(s); print('wrote', out, len(s))
