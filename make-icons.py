"""Draw Leeway's launcher icons and splash screens into the Android project."""
from PIL import Image, ImageDraw, ImageFont
import pathlib, math

RES = pathlib.Path(__file__).parent / 'android/app/src/main/res'
BG = (12, 58, 128)
SEA = (40, 120, 130)
ORANGE = (255, 122, 61)
FOAM = (220, 238, 238)

def art(size, transparent_bg):
    """Top-down cuttlefish whose two long tentacles are hooks curving out left and right,
    so the whole silhouette reads as an anchor. Cream on deep blue, drawn at 4x then reduced."""
    S = size * 4
    u = S / 108.0  # adaptive-icon units; keep the drawing inside the middle ~66
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    if not transparent_bg:
        bg = Image.new('RGBA', (S, S)); g = ImageDraw.Draw(bg)
        top, bot = (26, 124, 214), (9, 50, 118)
        for y in range(S):
            t = y / S; g.line([(0, y), (S, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
        im = bg
    d = ImageDraw.Draw(im)
    C = (246, 238, 220, 255); F = (214, 226, 240, 235); EYE = (12, 34, 70, 255)
    X = lambda v: v * u
    cx = 54
    # fin fringe all round the mantle (lighter), then the mantle itself (the anchor's shank)
    d.ellipse([X(cx - 13.5), X(19), X(cx + 13.5), X(63)], fill=F)
    d.ellipse([X(cx - 10.5), X(21), X(cx + 10.5), X(61)], fill=C)
    # subtle cuttlebone stripe and mottling for a little life
    for k, yy in enumerate(range(27, 57, 5)):
        d.ellipse([X(cx - 6 + (k % 2)), X(yy), X(cx - 3 + (k % 2)), X(yy + 2)], fill=(222, 206, 178, 255))
        d.ellipse([X(cx + 3 - (k % 2)), X(yy + 1), X(cx + 6 - (k % 2)), X(yy + 3)], fill=(222, 206, 178, 255))
    # head with eyes on the sides
    d.ellipse([X(cx - 9), X(58), X(cx + 9), X(71)], fill=C)
    for sx in (-1, 1):
        ex = cx + sx * 7.2
        d.ellipse([X(ex - 2.6), X(61.5), X(ex + 2.6), X(66.5)], fill=C)
        d.ellipse([X(ex - 1.8), X(62.4), X(ex + 1.8), X(65.6)], fill=EYE)
    # eight short arms, bunched and tapering forward
    for i in range(8):
        off = (i - 3.5) * 1.35
        d.polygon([(X(cx + off - 1.3), X(68)), (X(cx + off + 1.3), X(68)), (X(cx + off * 0.45 + 0.35), X(83)), (X(cx + off * 0.45 - 0.35), X(83))], fill=C)
    # the two long tentacles become hooks: down from the arm base, then curving out and up
    th = 3.6
    def hook(sign):
        # anchor crown: from the bottom centre, curving out to the side and up to a barbed point
        cy0, r = 71, 17
        pts = []
        for j in range(41):
            phi = math.radians(118 * j / 40)
            pts.append((X(cx + sign * r * math.sin(phi)), X(cy0 + r * math.cos(phi))))
        d.line(pts, fill=C, width=int(X(th)), joint='curve')
        for (x, y) in (pts[0], pts[-1]):
            d.ellipse([x - X(th / 2), y - X(th / 2), x + X(th / 2), y + X(th / 2)], fill=C)
        tx, ty = pts[-1]
        # barb: a small spur pointing back down and inward, like a fish hook
        d.polygon([(tx - sign * X(1.4), ty - X(0.8)), (tx - sign * X(5.2), ty + X(3.6)), (tx - sign * X(1.0), ty + X(3.0))], fill=C)
    # short stem from the arm tips down to the crown
    d.line([(X(cx), X(80)), (X(cx), X(88))], fill=C, width=int(X(th)))
    hook(-1); hook(1)
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
