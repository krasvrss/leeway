"""Build www/index.html for the Android app from the Leeway page source.

The app version fetches fresh forecasts from Open-Meteo every time it opens,
caches the last good download for offline use, and keeps the catch log on the phone.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / 'src' / 'leeway.src.html'
DATA = {
    '__LAND__': ROOT / 'src/data/land-adriatic.json',      # Natural Earth 1:10m coastline, Adriatic
    '__LIVE__': ROOT / 'src/data/forecast-fallback.json',  # Open-Meteo snapshot used only when offline on first launch
    '__HIRES__': ROOT / 'src/data/coast-porec-tar.json',   # OpenStreetMap coastline, Poreč to Novigrad
    '__BATHY__': ROOT / 'src/data/depth-tarska.json',      # EMODnet depth grid, Červar to Tarska uvala
    '__SEAMARKS__': ROOT / 'src/data/seamarks.json',      # OpenStreetMap seamarks: lights, beacons, reefs, shellfish beds
    '__SEABED__': ROOT / 'src/data/seabed.json',          # EMODnet EUSeaMap 2025 seabed type, 0.001° grid (run-length coded)
}

s = SRC.read_text()
s = s.replace('__I18N_JS__', (ROOT / 'src/i18n.js').read_text().replace('__I18N__', (ROOT / 'src/data/i18n.json').read_text().strip()))

def R(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)

R('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
R('const LIVE = __LIVE__;', 'let LIVE = __LIVE__; // offline fallback: forecast bundled at build time')
R('const HOURS = 120;', 'const HOURS = (() => { const n = new Date(); n.setMinutes(0,0,0); const off = Math.round((n - new Date(LIVE.t0))/3600e3); return Math.max(24, Math.min(156, LIVE.pts[0].spd.length - off - 1)); })();')
R('(() => {\n"use strict";', 'function main(){\n(() => {\n"use strict";')

LOADER = r'''
/* ---------- live data loader (app build) ---------- */
const SPOT_LL = [[45.2775,13.5980],[45.2280,13.5880],[45.3097,13.5937]]; // Červar Porat, Poreč, Tarska uvala
let LIVE_SOURCE = "bundled";
function ymd(d){ return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0"); }
async function fetchJSON(u, ms){
  const c = new AbortController(), t = setTimeout(()=>c.abort(), ms);
  try { const r = await fetch(u, {signal:c.signal}); if (!r.ok) throw new Error("HTTP "+r.status); return await r.json(); }
  finally { clearTimeout(t); }
}
async function fetchLive(){
  const la = SPOT_LL.map(p=>p[0]).join(","), lo = SPOT_LL.map(p=>p[1]).join(",");
  const q = `latitude=${la}&longitude=${lo}&timezone=Europe%2FZagreb&past_days=3&forecast_days=7`;
  const [a, b] = await Promise.all([
    fetchJSON(`https://api.open-meteo.com/v1/forecast?${q}&hourly=wind_speed_10m,wind_direction_10m,wind_gusts_10m,temperature_2m,cloud_cover,precipitation&wind_speed_unit=kn`, 15000),
    fetchJSON(`https://marine-api.open-meteo.com/v1/marine?${q}&hourly=wave_height,wave_period,sea_level_height_msl,sea_surface_temperature`, 15000)
  ]);
  const today = ymd(new Date()) + "T00:00";
  const ti = a[0].hourly.time.indexOf(today), tj = b[0].hourly.time.indexOf(today);
  if (ti < 0 || tj < 0) throw new Error("forecast does not start today");
  const back = Math.min(ti, tj, 72), i0 = ti - back, j0 = tj - back; // keep the last 3 days for the catch log
  const n = Math.min(a[0].hourly.time.length - i0, b[0].hourly.time.length - j0);
  const r1 = v => v==null ? null : Math.round(v*10)/10, r2 = v => v==null ? null : Math.round(v*100)/100;
  const A = (arr,f) => arr.slice(i0, i0+n).map(f), B = (arr,f) => arr.slice(j0, j0+n).map(f);
  const pts = a.map((x,k) => { const h = x.hourly, m = b[k].hourly; return {
    glat:x.latitude, glon:x.longitude, mlat:b[k].latitude, mlon:b[k].longitude,
    spd:A(h.wind_speed_10m,r1), dir:A(h.wind_direction_10m,v=>v==null?null:Math.round(v)), gust:A(h.wind_gusts_10m,r1), tmp:A(h.temperature_2m,r1),
    hs:B(m.wave_height,r2), tp:B(m.wave_period,r1), sl:B(m.sea_level_height_msl,r2), sst:B(m.sea_surface_temperature,r1) }; });
  const T = a[2].hourly;
  const rainBefore = T.precipitation.slice(Math.max(0,i0-72), i0).reduce((s,v)=>s+(v||0), 0);
  const now = new Date();
  return {t0: a[0].hourly.time[i0], fetched: ymd(now)+"T"+String(now.getHours()).padStart(2,"0")+":"+String(now.getMinutes()).padStart(2,"0"),
    pts, wx:{cc:A(T.cloud_cover,v=>v==null?0:v), pr:A(T.precipitation,r1), rainBefore: Math.round(rainBefore*10)/10}};
}
// Weather, sea and tide for a past catch (Open-Meteo history), used by the catch log.
window.LW_FETCH_PAST = async function(date, lat, lon){
  const age = (Date.now() - date.getTime())/864e5;
  if (age < -14) return null;
  const d0 = new Date(date.getTime() - 3*864e5), d1 = new Date(date.getTime() + 864e5);
  const q = `latitude=${lat.toFixed(4)}&longitude=${lon.toFixed(4)}&timezone=Europe%2FZagreb&start_date=${ymd(d0)}&end_date=${ymd(d1)}`;
  const base = age > 80 ? "https://archive-api.open-meteo.com/v1/archive" : "https://api.open-meteo.com/v1/forecast";
  const wx = await fetchJSON(`${base}?${q}&hourly=wind_speed_10m,wind_direction_10m,wind_gusts_10m,temperature_2m,cloud_cover,precipitation&wind_speed_unit=kn`, 15000);
  let mar = null;
  try { mar = await fetchJSON(`https://marine-api.open-meteo.com/v1/marine?${q}&hourly=wave_height,sea_level_height_msl,sea_surface_temperature`, 15000); } catch(e) {}
  const key = ymd(date) + "T" + String(date.getHours()).padStart(2,"0") + ":00";
  const h = wx.hourly, i = h.time.indexOf(key); if (i < 0) return null;
  const r1 = v => v==null ? null : Math.round(v*10)/10, r2 = v => v==null ? null : Math.round(v*100)/100;
  const rain = h.precipitation.slice(Math.max(0,i-72), i).reduce((s,v)=>s+(v||0), 0);
  const out = {spd:r1(h.wind_speed_10m[i]), dir:h.wind_direction_10m[i]==null?null:Math.round(h.wind_direction_10m[i]), gust:r1(h.wind_gusts_10m[i]),
    cc:h.cloud_cover[i], tmp:r1(h.temperature_2m[i]), clarity: rain>15 ? "murky" : rain>4 ? "stained" : "clear"};
  if (mar && mar.hourly){
    const m = mar.hourly, j = m.time.indexOf(key);
    if (j >= 0){ out.hs = r2(m.wave_height[j]); out.sst = r1(m.sea_surface_temperature[j]); out.sl = r2(m.sea_level_height_msl[j]);
      if (window.LW_STAGE && m.sea_level_height_msl.some(v=>v!=null)) out.stage = window.LW_STAGE(m.sea_level_height_msl)(j); }
  }
  return out;
};
async function boot(){
  let cached = null;
  try { cached = JSON.parse(localStorage.getItem("lw.live") || "null"); } catch(e) {}
  try {
    const L = await fetchLive();
    LIVE = L; LIVE_SOURCE = "live";
    try { localStorage.setItem("lw.live", JSON.stringify(L)); } catch(e) {}
  } catch(e) {
    if (cached && cached.t0 && cached.pts) { LIVE = cached; LIVE_SOURCE = "cached"; }
  }
  const b = document.getElementById("boot"); if (b) b.remove();
  main();
  const note = document.querySelector(".notice");
  const when = new Date(LIVE.fetched);
  const stamp = when.toLocaleString(window.LW_I18N ? window.LW_I18N.locale() : undefined, {weekday:"short", hour:"2-digit", minute:"2-digit"});
  note.innerHTML = (LIVE_SOURCE==="live" ? `Forecast updated <span>${stamp}</span>` : `Offline · forecast from <span>${stamp}</span>`) +
    ` · <button id="refresh" class="refresh">Refresh</button> · not for navigation · map © OpenStreetMap, depth EMODnet, forecast Open-Meteo`;
  document.getElementById("refresh").onclick = () => location.reload();
  let hiddenAt = 0;
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) hiddenAt = Date.now();
    else if (hiddenAt && Date.now() - hiddenAt > 60*60e3) location.reload();
  });
}
'''

# close main() after the app IIFE and start the loader
idx = s.rindex('})();\n</script>')
s = s[:idx] + '})();\n}\n' + LOADER + '\nboot();\n' + pathlib.Path('src/update-banner.js').read_text() + '\nif ("serviceWorker" in navigator && location.protocol==="https:" && location.hostname!=="localhost") navigator.serviceWorker.register("sw.js").catch(()=>{});\n</script>' + s[idx + len('})();\n</script>'):]

for k, f in DATA.items():
    assert s.count(k) == 1, k
    s = s.replace(k, pathlib.Path(f).read_text().strip())

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0f2128">
<title>Leeway</title>
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Leeway">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<style>
:root{color-scheme:light}
body{margin:0;font:14px system-ui,-apple-system,"Segoe UI",sans-serif}
img{max-width:100%}
[hidden]{display:none!important}
#boot{position:fixed;inset:0;display:grid;place-items:center;background:#0f2128;color:#e2eded;font:600 15px system-ui,sans-serif;z-index:100}
#boot b{display:block;font:700 34px "Barlow Condensed","Arial Narrow",sans-serif;letter-spacing:.04em;text-align:center}
.refresh{border:0;background:none;padding:0;font:inherit;color:var(--accent);text-decoration:underline;cursor:pointer}
html{-webkit-tap-highlight-color:transparent}
</style>
</head>
<body>
<div id="boot"><div><b>LEEWAY</b>Loading the latest forecast…</div></div>
'''
out = HEAD + s + '\n</body>\n</html>\n'
(ROOT / 'www').mkdir(exist_ok=True)
(ROOT / 'www' / 'index.html').write_text(out)
print('wrote www/index.html', len(out))

# ---- web app (add to home screen on iPhone / Android) ----
import shutil
for f in (ROOT / 'web-icons').glob('*.png'):
    shutil.copy(f, ROOT / 'www' / f.name)
(ROOT / 'www' / 'manifest.webmanifest').write_text(json.dumps({
    "name": "Leeway – marine wind & fishing", "short_name": "Leeway", "start_url": "./", "scope": "./",
    "display": "standalone", "orientation": "any", "background_color": "#0f2128", "theme_color": "#0f2128",
    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
              {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]
}, ensure_ascii=False, indent=1))
(ROOT / 'www' / 'sw.js').write_text("""// Keeps Leeway opening offline. The page itself saves the last forecast.
const CACHE = 'leeway-v1';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icon-180.png', './icon-192.png', './icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (u.origin !== location.origin || e.request.method !== 'GET') return;   // forecasts go straight to the network
  e.respondWith(fetch(e.request).then(r => { const c = r.clone(); caches.open(CACHE).then(k => k.put(e.request, c)); return r; })
    .catch(() => caches.match(e.request).then(r => r || caches.match('./index.html'))));
});
""")
print('wrote web app files')
