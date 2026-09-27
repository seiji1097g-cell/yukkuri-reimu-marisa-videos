"""キャラクターの画像を用意する。
- オリジナルキャラ「こむぎ」「あずき」をPillowで描く（2倍で描いて縮小）
- 立ち絵画像が指定されていれば、その画像を読み込んで使う（描き直さない）
"""
import math, os, subprocess
from PIL import Image, ImageDraw, ImageFont

W = H = 320      # 最終サイズ
S = 2            # 描画倍率
LINE = (74, 48, 32, 255)
FACES = ["normal", "smile", "surprise", "trouble", "think"]
MOUTHS = ["closed", "half", "open"]
EYES = ["open", "closed"]
CHAR = {
    "komugi": {"body": (255, 241, 201, 255), "eye_r": 34, "eye_ry": 40, "eye_dx": 105},
    "azuki":  {"body": (220, 208, 244, 255), "eye_r": 26, "eye_ry": 30, "eye_dx": 100},
}


def find_font(weight="Bold"):
    """Noto Sans CJK JP を探す。.ttc は index=0 が日本語"""
    for d in ("/usr/share/fonts/opentype/noto", "/usr/share/fonts/noto-cjk", "/usr/share/fonts/google-noto-cjk",
              "/usr/share/fonts/truetype/noto", os.path.expanduser("~/.fonts"), os.path.expanduser("~/.local/share/fonts")):
        for name in (f"NotoSansCJK-{weight}.ttc", f"NotoSansCJKjp-{weight}.otf", f"NotoSansJP-{weight}.otf", f"NotoSansJP-{weight}.ttf"):
            if os.path.exists(os.path.join(d, name)):
                return os.path.join(d, name)
    out = subprocess.run(["fc-list", ":lang=ja", "file"], capture_output=True, text=True).stdout.split()
    files = [f.rstrip(":") for f in out if "Sans" in f] or [f.rstrip(":") for f in out]
    if not files:
        raise SystemExit("日本語フォントが見つかりません。fonts-noto-cjk を入れてください（例：apt-get install -y fonts-noto-cjk）")
    return files[0]


def _leaf(d, cx, cy, ang, length, width, fill):
    pts = [(t / 40 * length, math.sin(math.pi * t / 40) * width / 2) for t in range(41)]
    pts += [(x, -y) for x, y in reversed(pts)]
    ca, sa = math.cos(ang), math.sin(ang)
    d.polygon([(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts], fill=fill, outline=LINE, width=8)


def draw(name, face="normal", mouth="closed", eyes="open"):
    c = CHAR[name]
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W * S // 2
    d.ellipse((90, 590, 550, 632), fill=(0, 0, 0, 50))                       # 影
    if name == "komugi":                                                     # 双葉
        d.line((cx, 170, cx + 4, 110), fill=LINE, width=10)
        _leaf(d, cx + 2, 115, math.radians(-150), 95, 52, (150, 205, 90, 255))
        _leaf(d, cx + 2, 115, math.radians(-30), 95, 52, (150, 205, 90, 255))
    d.ellipse((40, 160, 600, 610), fill=c["body"], outline=LINE, width=10)  # 体
    d.ellipse((120, 210, 230, 260), fill=(255, 255, 255, 110))              # ハイライト
    ey = 360
    ex = [cx - c["eye_dx"], cx + c["eye_dx"]]
    r, ry = c["eye_r"], c["eye_ry"]
    if face == "surprise":
        r, ry = int(r * 1.25), int(ry * 1.25)
    if name == "komugi":                                                     # ほっぺ
        for x in ex:
            d.ellipse((x - 48, ey + 40, x + 48, ey + 78), fill=(255, 140, 140, 150))
    if name == "azuki" or face in ("trouble", "surprise", "think"):          # 眉
        bw = 14 if name == "azuki" else 9
        for i, x in enumerate(ex):
            s = -1 if i == 0 else 1
            if face == "trouble":      # 八の字（内側が上がる）
                d.line((x + s * 40, ey - 64, x - s * 26, ey - 90), fill=LINE, width=bw)
            elif face == "surprise":
                d.arc((x - 42, ey - 110, x + 42, ey - 60), 200, 340, fill=LINE, width=bw)
            else:
                d.line((x - 38, ey - 70, x + 38, ey - 70 - (8 if face == "think" and i == 1 else 0)), fill=LINE, width=bw)
    for x in ex:                                                             # 目
        if eyes == "closed":
            d.arc((x - r, ey - ry // 2, x + r, ey + ry), 20, 160, fill=LINE, width=9)
        elif face == "smile":
            d.arc((x - r, ey - ry // 2, x + r, ey + ry + 10), 200, 340, fill=LINE, width=11)
        else:
            d.ellipse((x - r, ey - ry, x + r, ey + ry), fill=LINE)
            hx = x - r // 3 + (r // 2 if face == "think" else 0)
            d.ellipse((hx - r // 3, ey - ry // 2 - r // 3, hx + r // 3, ey - ry // 2 + r // 3), fill=(255, 255, 255, 255))
    if name == "azuki":                                                      # 丸メガネ
        for x in ex:
            d.ellipse((x - 62, ey - 58, x + 62, ey + 58), outline=LINE, width=9)
        d.arc((cx - 40, ey - 25, cx + 40, ey + 25), 200, 340, fill=LINE, width=9)
    my = 470                                                                 # 口
    if mouth == "closed":
        if face == "trouble":
            d.line([(cx - 34 + i * 17, my + (6 if i % 2 else -6)) for i in range(5)], fill=LINE, width=8, joint="curve")
        elif face == "surprise":
            d.ellipse((cx - 14, my - 12, cx + 14, my + 16), outline=LINE, width=8)
        else:
            d.arc((cx - 32, my - 30, cx + 32, my + 16), 30, 150, fill=LINE, width=8)
    else:
        hw, hh = (30, 22) if mouth == "half" else (40, 42)
        d.ellipse((cx - hw, my - hh // 2, cx + hw, my + hh), fill=(150, 40, 50, 255), outline=LINE, width=7)
        if mouth == "open":
            d.chord((cx - 26, my + 4, cx + 26, my + hh - 4), 0, 180, fill=(235, 110, 120, 255))
    f = ImageFont.truetype(find_font("Black"), 110, index=0)                 # 記号
    if face == "surprise":
        d.text((545, 110), "！", font=f, fill=(230, 60, 60, 255), stroke_width=6, stroke_fill=(255, 255, 255, 255))
    elif face == "trouble":
        x0, y0 = 540, 230
        d.ellipse((x0 - 26, y0, x0 + 26, y0 + 60), fill=(120, 190, 255, 230), outline=LINE, width=5)
        d.polygon([(x0 - 22, y0 + 20), (x0, y0 - 30), (x0 + 22, y0 + 20)], fill=(120, 190, 255, 230))
    elif face == "think":
        d.rounded_rectangle((470, 90, 630, 170), 40, fill=(255, 255, 255, 240), outline=LINE, width=6)
        for k in range(3):
            d.ellipse((505 + k * 40, 122, 521 + k * 40, 138), fill=LINE)
    return im.resize((W, H), Image.LANCZOS)


def _fit_image(path, base_dir):
    """立ち絵画像を 320×320 の枠に、縦横比を保って下寄せで収める"""
    p = path if os.path.isabs(path) else os.path.join(base_dir, path)
    im = Image.open(p).convert("RGBA")
    bbox = im.getbbox()
    if bbox: im = im.crop(bbox)
    k = min(W / im.width, H / im.height)
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(im, ((W - im.width) // 2, H - im.height))
    return out


def build_all(character_images=None, base_dir="."):
    """(キャラ, 表情, 口, 目) → 画像 の辞書を作る。
    character_images の例：{"komugi": {"base": "a.png", "mouth_half": "b.png", "mouth_open": "c.png",
                                        "eyes_closed": "d.png", "faces": {"smile": "e.png"}}}
    差分がない組み合わせは base（または faces の画像）で代用する。
    （拡張）faces の値には、画像1枚のかわりに {"base", "mouth_half", "mouth_open", "eyes_closed"} の辞書も書ける。
    その表情でも口パクとまばたきをする。"""
    sp = {}
    for n in CHAR:
        imgs = (character_images or {}).get(n)
        cache = {}
        def load(key):
            if key and key not in cache: cache[key] = _fit_image(key, base_dir)
            return cache.get(key)
        for fc in FACES:
            for m in MOUTHS:
                for e in EYES:
                    if not imgs:
                        sp[(n, fc, m, e)] = draw(n, fc, m, e)
                        continue
                    src = imgs
                    fimg = imgs.get("faces", {}).get(fc)
                    if isinstance(fimg, dict): src, fimg = fimg, None     # 表情ごとの差分セット
                    key = src["base"]
                    if fimg: key = fimg
                    elif e == "closed" and src.get("eyes_closed"): key = src["eyes_closed"]
                    elif m == "open" and src.get("mouth_open"): key = src["mouth_open"]
                    elif m in ("half", "open") and (src.get("mouth_half") or src.get("mouth_open")):
                        key = src.get("mouth_half") or src["mouth_open"]
                    sp[(n, fc, m, e)] = load(key)
    return sp


def sheet(path, sprites):
    """全表情を1枚に並べた確認用画像"""
    im = Image.new("RGBA", (W * 5, H * 4), (190, 225, 250, 255))
    for j, n in enumerate(CHAR):
        for i, fc in enumerate(FACES):
            im.alpha_composite(sprites[(n, fc, "closed", "open")], (i * W, j * 2 * H))
            im.alpha_composite(sprites[(n, fc, "open" if i % 2 == 0 else "half", "closed" if i == 4 else "open")], (i * W, (j * 2 + 1) * H))
    im.convert("RGB").save(path)
