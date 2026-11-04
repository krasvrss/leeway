"""Draw Leeway's launcher icons and splash screens into the Android project."""
from PIL import Image, ImageDraw, ImageFont
import pathlib, math

RES = pathlib.Path(__file__).parent / 'android/app/src/main/res'
BG = (22, 104, 196)
SEA = (40, 120, 130)
ORANGE = (255, 122, 61)
FOAM = (220, 238, 238)

SPRITES = pathlib.Path(__file__).parent / 'src/icon'
BLUE = (22, 104, 196, 255)
def art(size, transparent_bg):
    """Pixel-art cuttlefish (cut out of a photo and reduced to a 32x32 grid) on blue.
    Square icons use the 26-pixel sprite; the transparent adaptive-icon layer uses a
    smaller 20-pixel sprite so Android's round/squircle masks don't clip it."""
    grid = Image.new('RGBA', (32, 32), (0, 0, 0, 0) if transparent_bg else BLUE)
    sp = Image.open(SPRITES / ('sprite20.png' if transparent_bg else 'sprite26.png')).convert('RGBA')
    o = (32 - sp.width) // 2
    grid.alpha_composite(sp, (o, o + (0 if transparent_bg else 1)))
    return grid.resize((size, size), Image.NEAREST)

DENS = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
for name, f in DENS.items():
    folder = RES / f'mipmap-{name}'
    legacy = int(48 * f)
    full = art(legacy, False)
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
    '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#1668C4</color>\n</resources>\n')
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
