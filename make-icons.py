"""Draw Leeway's launcher icons and splash screens into the Android project."""
from PIL import Image, ImageDraw, ImageFont
import pathlib, math

RES = pathlib.Path(__file__).parent / 'android/app/src/main/res'
BG = (12, 58, 128)
SEA = (40, 120, 130)
ORANGE = (255, 122, 61)
FOAM = (220, 238, 238)

def art(size, transparent_bg):
    """A cuttlefish eye (W-shaped pupil in a golden, mottled iris) on deep blue, drawn at 4x then reduced."""
    import random
    S = size * 4
    u = S / 108.0  # adaptive-icon units; the safe zone is the middle 66 units
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    if not transparent_bg:
        bg = Image.new('RGBA', (S, S))
        top, bot = (24, 118, 210), (10, 52, 120)
        for y in range(S):
            t = y / S
            ImageDraw.Draw(bg).line([(0, y), (S, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
        im = bg
    d = ImageDraw.Draw(im)
    cx, cy = 54 * u, 54 * u
    # skin around the eye: soft almond shape with a few mottled spots
    skin = Image.new('L', (S, S), 0); ImageDraw.Draw(skin).ellipse([cx - 31 * u, cy - 21 * u, cx + 31 * u, cy + 21 * u], fill=255)
    skincol = Image.new('RGBA', (S, S), (214, 160, 92, 255)); im.paste(skincol, (0, 0), skin); d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    for _ in range(14):
        a_ = rnd.uniform(0, 6.283); r = rnd.uniform(18, 29) * u
        x, y = cx + r * math.cos(a_), cy + r * math.sin(a_) * 0.66
        rr = rnd.uniform(0.9, 1.8) * u
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(176, 118, 64, 255))
    # iris: golden with radial streaks
    R = 19.5 * u
    d.ellipse([cx - R, cy - R * 0.92, cx + R, cy + R * 0.92], fill=(232, 196, 98, 255))
    for k in range(40):
        a_ = k / 40 * 6.283
        d.line([(cx + 7 * u * math.cos(a_), cy + 7 * u * math.sin(a_) * 0.92), (cx + R * 0.97 * math.cos(a_), cy + R * 0.9 * math.sin(a_))], fill=(196, 150, 60, 255), width=max(1, int(0.9 * u)))
    d.ellipse([cx - R, cy - R * 0.92, cx + R, cy + R * 0.92], outline=(120, 74, 30, 255), width=int(1.6 * u))
    # the W-shaped pupil of a cuttlefish: a smooth thick "W" with rounded lobes
    w, h = 12.5 * u, 6.5 * u
    ctrl = [(cx - w, cy - h * 0.9), (cx - w * 0.55, cy + h * 0.85), (cx, cy - h * 0.15), (cx + w * 0.55, cy + h * 0.85), (cx + w, cy - h * 0.9)]
    def cr(p0, p1, p2, p3, t):
        return tuple(0.5 * ((2 * p1[i]) + (-p0[i] + p2[i]) * t + (2 * p0[i] - 5 * p1[i] + 4 * p2[i] - p3[i]) * t * t + (-p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]) * t ** 3) for i in range(2))
    P = [ctrl[0]] + ctrl + [ctrl[-1]]
    curve = []
    for k in range(1, len(P) - 2):
        for j in range(20): curve.append(cr(P[k - 1], P[k], P[k + 1], P[k + 2], j / 20))
    curve.append(ctrl[-1])
    th = int(5.2 * u)
    d.line(curve, fill=(14, 18, 24, 255), width=th, joint='curve')
    for (x, y) in (curve[0], curve[-1]): d.ellipse([x - th / 2, y - th / 2, x + th / 2, y + th / 2], fill=(14, 18, 24, 255))
    for (x, y) in (ctrl[1], ctrl[3]): d.ellipse([x - th * 0.75, y - th * 0.7, x + th * 0.75, y + th * 0.55], fill=(14, 18, 24, 255))
    # highlight
    d.ellipse([cx + 6 * u, cy - 11 * u, cx + 10 * u, cy - 7.5 * u], fill=(255, 255, 255, 215))
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
