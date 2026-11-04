/* Leeway translations: English source text is looked up in a dictionary per language.
   The app keeps writing English; this layer translates text nodes, a few attributes and canvas
   labels as they appear, so every panel is covered without threading a t() call through it.
   Text the user typed (notes, lure names) sits under translate="no" and is left alone. */
(function(){
const DICT = __I18N__;
const LANGS = [["en","English","EN"],["sl","Slovenščina","SL"],["hr","Hrvatski","HR"]];
const LOCALE = {en:undefined, sl:"sl-SI", hr:"hr-HR"};
let lang = "";
try { lang = localStorage.getItem("lw.lang") || ""; } catch(e){}
if (lang!=="en" && !DICT[lang]){
  const n = (navigator.language||"").toLowerCase();
  lang = n.startsWith("sl") ? "sl" : /^(hr|bs|sr)/.test(n) ? "hr" : "en";
}
let D = null, U = null, cache = new Map();
const NUM = /\d+(?:[.,:]\d+)*/g;
function setDict(){
  D = DICT[lang] || null; U = {}; cache = new Map();
  if (D) for (const k in D) U[k.toUpperCase()] = D[k].toLocaleUpperCase(LOCALE[lang]);
}
const isUpper = s => /[A-Z]/.test(s) && s===s.toUpperCase();
function look(s){
  let v = D[s]; if (v!=null) return v;
  const up = isUpper(s);
  if (up){ v = U[s]; if (v!=null) return v; }
  if (s.length>3 && /^[a-z]/.test(s)){ v = D[s[0].toUpperCase()+s.slice(1)]; if (v!=null) return v[0].toLocaleLowerCase(LOCALE[lang])+v.slice(1); }
  const nums = s.match(NUM);
  if (nums){
    const key = s.replace(NUM, "{n}");
    v = D[key]; if (v==null && up) v = U[key.toUpperCase()] != null ? U[key.toUpperCase()].replace(/\{N\}/g,"{n}") : null;
    if (v!=null){ let i=0; return v.replace(/\{(n|\d)\}/g, (m,g)=> g==="n" ? (nums[i++] ?? "") : (nums[+g-1] ?? "")); }
  }
  return null;
}
const SEPS = ["; ", ", ", ": ", " and ", " or ", " / "];
function tr(s, depth){
  if (!D || typeof s!=="string" || !/[A-Za-z]/.test(s)) return s;
  const hit = cache.get(s); if (hit!=null) return hit;
  const m = s.match(/^(\s*)([\s\S]*?)(\s*)$/), core = m[2];
  let v = look(core);
  if (v==null){
    const p = core.match(/^([·•,:;(\[–—\-+×←→↑↓✓●○◐◑\s]*)([\s\S]*?)([·•,:;)\]–—\-…\s]*)$/);
    if (p && p[2] && p[2]!==core){ const w = look(p[2]); if (w!=null) v = p[1]+w+p[3]; }
  }
  if (v==null && (depth||0) < 3){
    for (const sep of [" · ", " — "]){
      if (!core.includes(sep)) continue;
      const parts = core.split(sep), out = parts.map(x => tr(x, (depth||0)+1));
      if (out.some((x,i)=>x!==parts[i])){ v = out.join(sep); break; }
    }
  }
  if (v==null && (depth||0) < 3){
    const sent = core.split(/(?<=[.!?…])(?<!\b(?:Sv|Rt|St|npr|e\.g)\.)\s+(?=[A-Z0-9„"(])/);
    if (sent.length>1){ const out = sent.map(x => tr(x, (depth||0)+1)); if (out.some((x,i)=>x!==sent[i])) v = out.join(" "); }
  }
  if (v==null && (depth||0) < 3){
    for (const sep of SEPS){
      if (!core.includes(sep)) continue;
      const parts = sep===": " ? [core.slice(0, core.indexOf(sep)), core.slice(core.indexOf(sep)+2)] : core.split(sep);
      const out = parts.map(x => tr(x, (depth||0)+1));
      if (out.some((x,i)=>x!==parts[i])){ const js = sep.trim() && /[a-z]/.test(sep) ? " "+(D[sep.trim()]||sep.trim())+" " : sep; v = out.join(js); break; }
    }
  }
  if (v==null && (depth||0) < 3){ const pm = core.match(/^(.*\S) \(([^()]+)\)$/); if (pm){ const b=tr(pm[1],(depth||0)+1), q=tr(pm[2],(depth||0)+1); if (b!==pm[1] || q!==pm[2]) v = b+" ("+q+")"; } }
  if (v==null && window.LW_I18N_MISS) window.LW_I18N_MISS.add(core);
  const res = v==null ? s : m[1]+v+m[3];
  if (cache.size < 5000) cache.set(s, res);
  return res;
}

/* ---- DOM ---- */
const SKIP = new Set(["SCRIPT","STYLE","TEXTAREA","NOSCRIPT"]);
const ATTRS = ["placeholder","aria-label","title","alt"];
const seen = new WeakMap();
function skipped(el){ return !el || SKIP.has(el.nodeName) || (el.closest && el.closest('[translate="no"]')); }
function doText(n){
  const cur = n.nodeValue, r = seen.get(n);
  const en = r && cur===r.out ? r.en : cur;
  const out = lang==="en" ? en : tr(en);
  seen.set(n, {en, out});
  if (out!==cur) n.nodeValue = out;
}
function doAttrs(el){
  let r = seen.get(el); if (!r){ r = {}; seen.set(el, r); }
  for (const a of ATTRS){
    if (!el.hasAttribute(a)) continue;
    const cur = el.getAttribute(a), x = r[a];
    const en = x && cur===x.out ? x.en : cur, out = lang==="en" ? en : tr(en);
    r[a] = {en, out}; if (out!==cur) el.setAttribute(a, out);
  }
}
function walk(node){
  if (node.nodeType===3){ if (!skipped(node.parentNode)) doText(node); return; }
  if (node.nodeType!==1 || skipped(node)) return;
  doAttrs(node);
  for (let c=node.firstChild; c; c=c.nextSibling) walk(c);
}
const mo = new MutationObserver(list=>{
  for (const m of list){
    if (m.type==="childList") m.addedNodes.forEach(walk);
    else if (m.type==="characterData"){ if (!skipped(m.target.parentNode)) doText(m.target); }
    else if (m.type==="attributes" && !skipped(m.target)) doAttrs(m.target);
  }
  mo.takeRecords();
});
function start(){
  walk(document.body);
  mo.observe(document.body, {childList:true, subtree:true, characterData:true, attributes:true, attributeFilter:ATTRS});
}

/* ---- canvas labels ---- */
const CP = CanvasRenderingContext2D.prototype;
for (const f of ["fillText","strokeText","measureText"]){
  const orig = CP[f];
  CP[f] = function(t, ...a){ return orig.call(this, lang!=="en" && typeof t==="string" ? tr(t) : t, ...a); };
}

/* ---- picker ---- */
const listeners = [];
function setLang(l){
  if (l!=="en" && !DICT[l]) l = "en";
  lang = l; setDict();
  try { localStorage.setItem("lw.lang", l); } catch(e){}
  document.documentElement.lang = l;
  walk(document.body);
  listeners.forEach(fn=>{ try { fn(l); } catch(e){} });
  const sel = document.getElementById("langsel"); if (sel && sel.value!==l) sel.value = l;
  const lc = document.getElementById("lcode"); if (lc) lc.textContent = l.toUpperCase();
}
function mountPicker(){
  const sel = document.getElementById("langsel"); if (!sel) return;
  sel.innerHTML = LANGS.map(([k,n,s])=>`<option value="${k}">${n}</option>`).join("");
  sel.value = lang;
  const lc = document.getElementById("lcode"); if (lc) lc.textContent = lang.toUpperCase();
  sel.onchange = () => setLang(sel.value);
}

setDict();
document.documentElement.lang = lang;
window.LW_I18N = {
  tr: s => lang==="en" ? s : tr(s),
  get lang(){ return lang; },
  locale: () => LOCALE[lang],
  setLang, onChange: fn => listeners.push(fn)
};
if (document.readyState==="loading") document.addEventListener("DOMContentLoaded", ()=>{ mountPicker(); start(); });
else { mountPicker(); start(); }
})();
