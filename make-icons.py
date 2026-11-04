"""Draw Leeway's launcher icons and splash screens into the Android project."""
from PIL import Image, ImageDraw, ImageFont
import pathlib, math

RES = pathlib.Path(__file__).parent / 'android/app/src/main/res'
BG = (12, 58, 128)
SEA = (40, 120, 130)
ORANGE = (255, 122, 61)
FOAM = (220, 238, 238)

def art(size, transparent_bg):
    """Top-down cuttlefish: short wavy arms, and its two long tentacles turned into wide hooks
    curving out left and right, so the outline reads as an anchor. Cream on deep blue."""
    S = size * 4
    u = S / 108.0
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    if not transparent_bg:
        bg = Image.new('RGBA', (S, S)); g = ImageDraw.Draw(bg)
        top, bot = (26, 124, 214), (9, 50, 118)
        for y in range(S):
            t = y / S; g.line([(0, y), (S, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
        im = bg
    d = ImageDraw.Draw(im)
    C = (246, 238, 220, 255); F = (206, 220, 238, 235); EYE = (12, 34, 70, 255); SPOT = (222, 206, 178, 255)
    k = 0.82  # the design is drawn in a 108-unit box, then scaled to sit inside the icon's safe zone
    T = lambda x, y: (X(54 + (x - 54) * k), X(54 + (y - 57) * k))
    X = lambda v: v * u
    W = lambda v: max(1, int(X(v * k)))
    def ell(x0, y0, x1, y1, fill):
        p0, p1 = T(x0, y0), T(x1, y1); d.ellipse([p0[0], p0[1], p1[0], p1[1]], fill=fill)
    def spline(ctrl, n=24):
        P = [ctrl[0]] + ctrl + [ctrl[-1]]; out = []
        for i in range(1, len(P) - 2):
            for j in range(n):
                t = j / n; p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
                out.append(tuple(0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t * t + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t ** 3) for c in range(2)))
        out.append(ctrl[-1]); return out
    cx = 54
    # mantle with its fin fringe (the anchor's shank)
    ell(cx - 14.5, 16.5, cx + 14.5, 61.5, F)
    ell(cx - 11.5, 19, cx + 11.5, 59, C)
    for i, yy in enumerate(range(25, 55, 5)):
        o = i % 2
        ell(cx - 6.5 + o, yy, cx - 3.5 + o, yy + 2, SPOT); ell(cx + 3.5 - o, yy + 1, cx + 6.5 - o, yy + 3, SPOT)
    # head and eyes
    ell(cx - 10, 57, cx + 10, 71, C)
    for sx in (-1, 1):
        ex = cx + sx * 8
        ell(ex - 3, 61, ex + 3, 67, C); ell(ex - 2, 62, ex + 2, 66, EYE)
    # two wide hooks: down from the head, out along the bottom, up the sides to barbed points
    th = 4.4
    for sx in (-1, 1):
        ctrl = [(cx + sx * 2, 70), (cx + sx * 6, 88), (cx + sx * 16, 95.5), (cx + sx * 28, 95), (cx + sx * 35, 87), (cx + sx * 37, 72), (cx + sx * 36, 54), (cx + sx * 34.5, 47)]
        pts = spline(ctrl, 90)
        for j, q in enumerate(pts):  # thin where it leaves the head, thickening toward the hook
            t = j / (len(pts) - 1); x, y = T(*q); r = X((0.55 + 3.0 * t ** 1.4) * k)
            d.ellipse([x - r, y - r, x + r, y + r], fill=C)
        tx, ty = 34.5, 47  # a bold barb pointing back down and inward, like a fish hook
        d.polygon([T(cx + sx * (tx + 3.0), ty - 1.5), T(cx + sx * (tx - 9.0), ty + 8.5), T(cx + sx * (tx - 1.0), ty + 9.5)], fill=C)
        ell(cx + sx * tx - 2.9, ty - 3.4, cx + sx * tx + 2.9, ty + 2.4, C)
    # eight short, wavy arms between the hooks
    for i in range(8):
        base = cx + (i - 3.5) * 1.9
        spread = (i - 3.5) * 1.1
        n = 80
        for j in range(n + 1):
            t = j / n; x, y = T(base + spread * t + 1.3 * math.sin(t * 7 + i), 69 + 18 * t)
            r = X((1.25 - 0.85 * t) * k); d.ellipse([x - r, y - r, x + r, y + r], fill=C)
    return im.resize((size, size), Image.LANCZOS)

DENS = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
for name, f in DENS.items():
    folder = RES / f'mipmap-{name}'
    legacy = int(48 * f)
    full = art(int(108 * f), False).resize((legacy, legacy), Image.LANCZOS)
    # legacy square icon with rounded corners
    mask = Image.new('L', (legacy, legacy), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, legacy - 1, legacy - 1], radius=int(legacy * 0.18), fill=255)
    sq = Image.new('RGBA', (legacy, legacy), (0, 0, 0, 0)); sq.paste(full, (0, 0), mask)
    sq.save(folder / 'ic_launcher.png')
    rmask = Image.new('L', (legacy, legacy), 0)
    ImageDraw.Draw(rmask).ellipse([0, 0, legacy - 1, legacy - 1], fill=255)
    rd = Image.new('RGBA', (legacy, legacy), (0, 0, 0, 0)); rd.paste(full, (0, 0), rmask)
    rd.save(folder / 'ic_launcher_round.png')
    art(int(108 * f), True).save(folder / 'ic_launcher_foreground.png')

(RES / 'values/ic_launcher_background.xml').write_text(
    '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#0C3A80</color>\n</resources>\n')
# the old vector foreground would shadow the PNGs on some API levels
v = RES / 'drawable-v24/ic_launcher_foreground.xml'
if v.exists(): v.unlink()

# splash screens: dark sea, the fish, and the name
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
for p in RES.glob('drawable*/splash.png'):
    w, h = Image.open(p).size
    im = Image.new('RGB', (w, h), BG)
    s = int(min(w, h) * 0.42)
    a = art(s, True)
    im.paste(a, ((w - s) // 2, int(h / 2 - s * 0.62)), a)
    d = ImageDraw.Draw(im)
    fs = max(14, int(min(w, h) * 0.075))
    try: font = ImageFont.truetype(font_path, fs)
    except OSError: font = ImageFont.load_default()
    t = 'LEEWAY'
    tw = d.textlength(t, font=font)
    d.text(((w - tw) / 2, h / 2 + s * 0.42), t, font=font, fill=FOAM)
    im.save(p)

# a preview of the icon for the README
art(512, False).save(pathlib.Path(__file__).parent / 'icon-512.png')
print('icons and splash screens written')

# ---- iOS app icon and splash (Capacitor iOS project) ----
IOS = pathlib.Path(__file__).parent / 'ios/App/App/Assets.xcassets'
if IOS.exists():
    art(1024, False).convert('RGB').save(IOS / 'AppIcon.appiconset/AppIcon-512@2x.png')  # iOS icons must not be transparent
    for p in IOS.glob('Splash.imageset/*.png'):
        w, h = Image.open(p).size
        im = Image.new('RGB', (w, h), BG); s = int(min(w, h) * 0.3); a = art(s, True)
        im.paste(a, ((w - s) // 2, int(h / 2 - s * 0.62)), a)
        d = ImageDraw.Draw(im); fs = int(min(w, h) * 0.05)
        try: font = ImageFont.truetype(font_path, fs)
        except OSError: font = ImageFont.load_default()
        tw = d.textlength('LEEWAY', font=font); d.text(((w - tw) / 2, h / 2 + s * 0.42), 'LEEWAY', font=font, fill=FOAM)
        im.save(p)

# ---- web app icons (home-screen install on iPhone and Android) ----
WEB = pathlib.Path(__file__).parent / 'web-icons'
WEB.mkdir(exist_ok=True)
for n in (180, 192, 512):
    art(n, False).convert('RGB').save(WEB / f'icon-{n}.png')
m = art(512, False).convert('RGB')  # maskable: keep the fish inside the safe circle
mk = Image.new('RGB', (512, 512), BG); small = m.resize((400, 400), Image.LANCZOS); mk.paste(small, (56, 56)); mk.save(WEB / 'icon-maskable-512.png')
print('iOS and web icons written')
