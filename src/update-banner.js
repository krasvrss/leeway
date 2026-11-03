// ---- update banner (Android app only): compares this build with the newest GitHub release ----
// __LW_BUILD__ is replaced with the GitHub build number when the APK is built.
(function(){
const LW_BUILD = parseInt("__LW_BUILD__", 10) || 0;
const RELEASES = "https://api.github.com/repos/krasvrss/leeway/releases/latest";
function checkUpdate(){
  const C = window.Capacitor;
  const native = C && C.isNativePlatform && C.isNativePlatform();
  if (!native || !LW_BUILD || !navigator.onLine) return;
  let last = 0; try { last = +localStorage.getItem("lw.updChecked") || 0; } catch(e){}
  if (Date.now() - last < 3*3600e3) return;
  fetch(RELEASES, {headers:{Accept:"application/vnd.github+json"}})
    .then(r => r.ok ? r.json() : null).then(rel => {
      try { localStorage.setItem("lw.updChecked", String(Date.now())); } catch(e){}
      if (!rel) return;
      const n = parseInt(String(rel.tag_name).replace(/\D/g, ""), 10) || 0;
      let skip = 0; try { skip = +localStorage.getItem("lw.updSkip") || 0; } catch(e){}
      if (n <= LW_BUILD || n <= skip) return;
      const apk = (rel.assets || []).find(a => /\.apk$/.test(a.name));
      if (apk) showUpdate(n, (rel.body || "").split("\n")[0].slice(0, 90), apk.browser_download_url);
    }).catch(() => {});
}
function showUpdate(n, note, url){
  if (document.getElementById("lwUpd")) return;
  const b = document.createElement("div");
  b.id = "lwUpd"; b.setAttribute("role", "status");
  b.style.cssText = "position:fixed;left:12px;right:12px;bottom:calc(14px + env(safe-area-inset-bottom));z-index:50;max-width:460px;margin:0 auto;background:var(--panel);color:var(--ink);border:1px solid var(--accent);border-radius:12px;padding:12px 14px;box-shadow:0 6px 24px rgba(0,0,0,.35);font:14px/1.35 system-ui,sans-serif;display:flex;gap:10px;align-items:center";
  const t = document.createElement("div"); t.style.flex = "1";
  const h = document.createElement("strong"); h.textContent = "Leeway " + n + " is available";
  t.appendChild(h);
  if (note){ const p = document.createElement("div"); p.style.cssText = "opacity:.8;font-size:13px;margin-top:2px"; p.textContent = note; t.appendChild(p); }
  const go = document.createElement("a"); go.href = url; go.textContent = "Download";
  go.style.cssText = "background:var(--accent);color:var(--accent-ink);padding:8px 12px;border-radius:8px;text-decoration:none;font-weight:600;white-space:nowrap";
  const x = document.createElement("button"); x.type = "button"; x.textContent = "Later";
  x.style.cssText = "background:none;border:0;color:inherit;opacity:.7;font:inherit;padding:8px 4px;cursor:pointer";
  x.onclick = () => { try { localStorage.setItem("lw.updSkip", String(n)); } catch(e){} b.remove(); };
  b.append(t, go, x); document.body.appendChild(b);
}
window.LW_SHOW_UPDATE = showUpdate; // for testing
setTimeout(checkUpdate, 4000);
document.addEventListener("visibilitychange", () => { if (!document.hidden) checkUpdate(); });
})();
