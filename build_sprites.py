"""たぬき式ゆっくりのパーツを重ねて、魔理沙と霊夢の表情ごとの立ち絵を作る（描き直さない）。
使い方：python3 build_sprites.py 素材フォルダ
  素材フォルダは、スキル同梱の assets/tanuki-yukkuri（英字のファイル名）か、
  配布ZIPを展開してできた「たぬき式ゆっくり」フォルダ（日本語のファイル名）のどちらでもよい。
出力：img/*.png と character_images.json（script.json の character_images にそのまま入れる）"""
import json, os, sys
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else "assets/tanuki-yukkuri"
OUT = "img"
ORDER = ["体", "顔色", "口", "目", "髪", "眉", "他"]   # 下から順に重ねる
# speaker：komugi＝霊夢（聞き役・右）、azuki＝魔理沙（解説役・左）
CHARS = {
    "komugi": {"name": "reimu",  "dir": "たぬき霊夢",   "fixed": {"体": "体_00", "髪": "髪_00", "他": "服_01"}, "min_w": 820},
    "azuki":  {"name": "marisa", "dir": "たぬき魔理沙", "fixed": {"体": "体_00", "髪": "髪_04", "他": "服_01"}, "min_w": 0},
}
# 表情ごとのパーツ：目（開・閉）、口（閉・半開き・全開）、眉、顔色
# 目_NN.0〜.4 はまばたき（.0＝閉）、口_NN.0〜.4 は口パク（.0＝閉、.4＝全開）のコマ
FACES = {
    "normal":   {"eyes": ("目_00", "目_00.0"), "mouth": ("口_00.1", "口_00.2", "口_00.4"), "眉": "眉_00", "顔色": "顔_00"},
    "smile":    {"eyes": ("目_19", "目_19"),   "mouth": ("口_07.0", "口_07.2", "口_07.4"), "眉": "眉_00", "顔色": "顔_01"},
    "surprise": {"eyes": ("目_15", "目_15.0"), "mouth": ("口_22", "口_03.2", "口_03.4"),   "眉": "眉_07", "顔色": "顔_00"},
    "trouble":  {"eyes": ("目_03", "目_03.0"), "mouth": ("口_20", "口_09.2", "口_09"),     "眉": "眉_06", "顔色": "顔_00"},
    "think":    {"eyes": ("目_13", "目_13.0"), "mouth": ("口_10", "口_02", "口_05"),       "眉": "眉_05", "顔色": "顔_00"},
}
VARIANTS = {"base": (0, 0), "mouth_half": (1, 0), "mouth_open": (2, 0), "eyes_closed": (0, 1)}
# スキル同梱版（英字名）での名前：たぬき霊夢/目/目_00.0.png → reimu/eye_00.0.png
PREFIX_EN = {"体_": "body_", "顔_": "face_", "口_": "mouth_", "目_": "eye_", "髪_": "hair_", "眉_": "brow_", "服_": "cloth_"}
JA = os.path.isdir(os.path.join(SRC, "たぬき霊夢"))


def part_path(c, cat, name):
    if JA:
        return f"{SRC}/{c['dir']}/{cat}/{name}.png"
    for ja, en in PREFIX_EN.items():
        if name.startswith(ja): name = en + name[len(ja):]; break
    return f"{SRC}/{c['name']}/{name}.png"


def needed(c):
    out = list(c["fixed"].items())
    for fc in FACES.values():
        out += [("眉", fc["眉"]), ("顔色", fc["顔色"])] + [("目", e) for e in fc["eyes"]] + [("口", m) for m in fc["mouth"]]
    return out


missing = sorted({part_path(c, k, v) for c in CHARS.values() for k, v in needed(c) if not os.path.exists(part_path(c, k, v))})
if missing:
    raise SystemExit("パーツが見つかりません（素材の版が変わった可能性があります。フォルダの中身を見て CHARS・FACES を直してください）：\n"
                     + "\n".join(missing))


def compose(c, layers):
    im = Image.new("RGBA", (1000, 860), (0, 0, 0, 0))
    for k in ORDER:
        if k in layers:
            im.alpha_composite(Image.open(part_path(c, k, layers[k])).convert("RGBA"))
    return im


os.makedirs(OUT, exist_ok=True)
spec = {}
for sp, c in CHARS.items():
    ims = {}
    for fname, fc in FACES.items():
        for vname, (mi, ei) in VARIANTS.items():
            layers = dict(c["fixed"], 眉=fc["眉"], 顔色=fc["顔色"], 口=fc["mouth"][mi], 目=fc["eyes"][ei])
            ims[(fname, vname)] = compose(c, layers)
    # 全差分を同じ枠で切り出す（chars.py が画像ごとに余白を切るので、四隅に透明度1の点を置いて位置ずれを防ぐ）
    boxes = [im.getbbox() for im in ims.values()]
    ub = (min(b[0] for b in boxes) - 4, min(b[1] for b in boxes) - 4, max(b[2] for b in boxes) + 4, max(b[3] for b in boxes) + 4)
    spec[sp] = {"faces": {}}
    for (fname, vname), im in ims.items():
        im = im.crop(ub)
        if im.width < c["min_w"]:   # 帽子で横に広い魔理沙と顔の大きさがそろうよう、霊夢の左右に透明な余白を足す
            pad = Image.new("RGBA", (c["min_w"], im.height), (0, 0, 0, 0))
            pad.alpha_composite(im, ((c["min_w"] - im.width) // 2, 0)); im = pad
        for xy in [(0, 0), (im.width - 1, 0), (0, im.height - 1), (im.width - 1, im.height - 1)]:
            im.putpixel(xy, (0, 0, 0, 1))
        p = f"{OUT}/{c['name']}_{fname}_{vname}.png"
        im.save(p)
        spec[sp]["faces"].setdefault(fname, {})[vname] = p
    spec[sp].update(spec[sp]["faces"]["normal"])
json.dump(spec, open("character_images.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"立ち絵を {OUT}/ に作りました（{sum(len(v['faces']) * 4 for v in spec.values())}枚）。character_images.json を script.json に入れてください")
