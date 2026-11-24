"""bouncer mascot: poses and expressions built from shared parts, written as standalone SVG files.

python3 assets/mascot.py assets  ->  assets/bouncer.svg, icon.svg, states/*.svg, sheet.svg (contact sheet, not committed)
"""
import sys
from pathlib import Path

INK, SUIT, SUIT_L, SUIT_D = "#17131F", "#2B2440", "#3D3459", "#211B33"
SKIN, SKIN_D, CORD, SHINE, WHITE = "#C98A5B", "#A86D42", "#EDE7FF", "#C8B6FF", "#FFFFFF"
ACCENT = "#D7FF3A"

HEAD = "M78 68 C78 36 97 18 120 18 C143 18 162 36 162 68 L162 90 C162 108 152 120 138 124 L102 124 C88 120 78 108 78 90 Z"
HEAD_SHADOW = "M148 26 C158 36 162 50 162 68 L162 90 C162 106 154 118 142 123 C150 110 153 98 153 84 L153 64 C153 48 152 36 148 26 Z"
EARS = ["M80 72 C66 70 64 96 80 94 Z", "M160 72 C174 70 176 96 160 94 Z"]
NECK = "M100 108 L100 142 L140 142 L140 108 Z"
BODY = ("M30 214 L30 186 C30 160 52 146 82 140 L104 135 L120 150 L136 135 L158 140 C188 146 210 160 210 186 "
        "L210 214 Q210 220 204 220 L36 220 Q30 220 30 214 Z")
CORD_D = "M167 90 C175 97 161 101 167 108 C173 115 159 119 165 126 C170 132 160 136 154 140"


def el(tag, **a):
    attrs = " ".join(f'{k.rstrip("_").replace("_", "-")}="{v}"' for k, v in a.items())
    return f"<{tag} {attrs}></{tag}>"


def path(d, **a):
    return el("path", d=d, **a)


def line(x1, y1, x2, y2, w, color, cap="round"):
    return path(f"M{x1} {y1} L{x2} {y2}", stroke=color, stroke_width=w, stroke_linecap=cap, fill="none")


def sleeve(x1, y1, x2, y2):
    return [line(x1, y1, x2, y2, 38, INK), line(x1, y1, x2, y2, 29, SUIT)]


def cuff(x1, y1, x2, y2, at=0.82):
    """White shirt cuff near the hand end of a sleeve."""
    dx, dy = x2 - x1, y2 - y1
    a, b = at, at + 0.06
    return line(round(x1 + dx * a, 1), round(y1 + dy * a, 1), round(x1 + dx * b, 1), round(y1 + dy * b, 1), 29, WHITE, "butt")


# ---------- silhouette (die-cut white outline + hard shadow) ----------
BASE_SIL = [("path", {"d": d}) for d in EARS + [NECK, HEAD, BODY]] + [
    ("path", {"d": CORD_D, "fill": "none", "stroke_width": 16}),
    ("ellipse", {"cx": 167, "cy": 84, "rx": 4.5, "ry": 6.5}),
]


def underlay(sil, color, dx=0, dy=0):
    t = f' transform="translate({dx} {dy})"' if dx or dy else ""
    inner = "".join(el(tag, **a) for tag, a in sil)
    return (f'<g{t} fill="{color}" stroke="{color}" stroke-width="18" stroke-linejoin="round" '
            f'stroke-linecap="round">{inner}</g>')


def sil_arm(x1, y1, x2, y2):
    return ("path", {"d": f"M{x1} {y1} L{x2} {y2}", "fill": "none", "stroke_width": 56})


# ---------- body ----------
def body(kind, accent):
    out = [path(d, fill=SKIN, stroke=INK, stroke_width=5, stroke_linejoin="round") for d in EARS]
    out += [path("M77 78 C71 80 71 88 77 89", fill="none", stroke=SKIN_D, stroke_width=3, stroke_linecap="round"),
            path("M163 78 C169 80 169 88 163 89", fill="none", stroke=SKIN_D, stroke_width=3, stroke_linecap="round"),
            path(NECK, fill=SKIN_D, stroke=INK, stroke_width=5, stroke_linejoin="round"),
            path(BODY, fill=SUIT, stroke=INK, stroke_width=5, stroke_linejoin="round")]
    thin = dict(stroke=INK, stroke_width=3.5, stroke_linejoin="round")
    if kind == "short":  # chest hidden by the arms
        out += [path("M104 135 L136 135 L128 170 L112 170 Z", fill=WHITE, **thin),
                path("M114 150 L126 150 L123 160 L117 160 Z", fill=accent, **thin),
                path("M117 160 L123 160 L128 186 L120 194 L112 186 Z", fill=accent, **thin),
                path("M100 132 L120 150 L108 156 L98 138 Z", fill=WHITE, **thin),
                path("M140 132 L120 150 L132 156 L142 138 Z", fill=WHITE, **thin),
                path("M82 140 L104 135 L118 182 L96 160 Z", fill=SUIT_L, **thin),
                path("M158 140 L136 135 L122 182 L144 160 Z", fill=SUIT_L, **thin)]
    else:  # full bust: closed jacket, buttons, pocket square
        out += [path("M48 214 L48 190 M192 214 L192 190", fill="none", stroke=SUIT_D, stroke_width=4, stroke_linecap="round"),
                path("M104 135 L136 135 L126 196 L114 196 Z", fill=WHITE, **thin),
                path("M114 150 L126 150 L123 160 L117 160 Z", fill=accent, **thin),
                path("M117 160 L123 160 L128 190 L120 198 L112 190 Z", fill=accent, **thin),
                path("M100 132 L120 150 L108 156 L98 138 Z", fill=WHITE, **thin),
                path("M140 132 L120 150 L132 156 L142 138 Z", fill=WHITE, **thin),
                path("M82 140 L104 135 L119 192 L94 164 Z", fill=SUIT_L, **thin),
                path("M158 140 L136 135 L121 192 L146 164 Z", fill=SUIT_L, **thin),
                path("M120 192 L120 218", fill="none", stroke=INK, stroke_width=3.5, stroke_linecap="round"),
                el("circle", cx=127, cy=202, r=3.2, fill=INK), el("circle", cx=127, cy=213, r=3.2, fill=INK),
                path("M152 177 L176 173", fill="none", stroke=INK, stroke_width=3.5, stroke_linecap="round"),
                path("M155 176 L159 166 L165 174 L170 165 L174 173 Z", fill=accent, stroke=INK, stroke_width=3, stroke_linejoin="round")]
    return out


# ---------- face ----------
BROWS = {
    "skeptic": ("M90 55 Q101 52 112 55", "M128 51 Q141 43 152 50"),
    "stern": ("M90 53 Q101 55 112 59", "M128 59 Q139 55 150 53"),
    "raised": ("M90 50 Q101 43 112 48", "M128 48 Q139 43 150 50"),
    "worried": ("M90 57 Q101 52 112 49", "M128 49 Q139 52 150 57"),
    "relaxed": ("M90 54 Q101 50 112 53", "M128 53 Q139 50 150 54"),
}
MOUTHS = {
    "smirk": "M106 108 Q118 113 132 103",
    "flat": "M108 107 L132 107",
    "smile": "M103 102 Q119 117 137 101",
    "meh": "M106 108 Q112 103 118 107 Q124 111 132 105",
    "wobbly": "M106 108 Q110 104 114 108 Q118 112 122 108 Q126 104 130 108",
    "hmm": "M112 109 Q120 106 128 109",
    "content": "M108 105 Q120 113 132 104",
}


def glasses(transform=""):
    t = f' transform="{transform}"' if transform else ""
    parts = [
        line(84, 61, 79, 70, 4, INK), line(156, 61, 161, 70, 4, INK), line(84, 60, 156, 60, 7, INK),
        path("M86 62 L115 62 L113 79 C112 86 108 89 101 89 L98 89 C91 89 88 85 87 79 Z", fill=INK),
        path("M125 62 L154 62 L153 79 C152 85 149 89 142 89 L139 89 C132 89 128 86 127 79 Z", fill=INK),
        path("M115 66 Q120 63 125 66", fill="none", stroke=INK, stroke_width=3.5),
        path("M92 66 L99 66 L93 80 L88 80 Z", fill=SHINE), path("M131 66 L138 66 L132 80 L127 80 Z", fill=SHINE),
    ]
    return f"<g{t}>{''.join(parts)}</g>"


def face(brows="skeptic", mouth="smirk", specs="normal", nose=True, extras=()):
    out = [path(HEAD, fill=SKIN), path(HEAD_SHADOW, fill=SKIN_D),
           el("ellipse", cx=102, cy=34, rx=12, ry=6, transform="rotate(-25 102 34)", fill=WHITE, opacity=0.4),
           path(HEAD, fill="none", stroke=INK, stroke_width=5, stroke_linejoin="round")]
    out += [path(d, fill="none", stroke=INK, stroke_width=4.5, stroke_linecap="round") for d in BROWS[brows]]
    if specs == "lowered":  # looking over the glasses
        for x in (101, 140):
            out += [el("ellipse", cx=x, cy=60, rx=7, ry=5.5, fill=WHITE, stroke=INK, stroke_width=2.5),
                    el("circle", cx=x, cy=62.5, r=2.8, fill=INK)]
        out.append(glasses("translate(0 14)"))
    elif specs == "crooked":
        out.append(glasses("rotate(-9 120 75) translate(0 3)"))
    else:
        out.append(glasses())
    if nose:
        out.append(path("M116 94 Q120 99 125 95", fill="none", stroke=INK, stroke_width=3.5, stroke_linecap="round"))
    out.append(path(MOUTHS[mouth], fill="none", stroke=INK, stroke_width=4.5, stroke_linecap="round", stroke_linejoin="round"))
    if "sweat" in extras:
        out.append(path("M160 30 C156 38 154 42 154 45 A6 6 0 0 0 166 45 C166 42 164 38 160 30 Z",
                        fill="#8FD3FF", stroke=INK, stroke_width=3, stroke_linejoin="round"))
    out += [path(CORD_D, fill="none", stroke=INK, stroke_width=6, stroke_linecap="round"),
            path(CORD_D, fill="none", stroke=CORD, stroke_width=3, stroke_linecap="round"),
            el("ellipse", cx=167, cy=84, rx=4.5, ry=6.5, fill=INK)]
    return out


def fist(cx, cy, r=14):
    return [el("circle", cx=cx, cy=cy, r=r, fill=SKIN, stroke=INK, stroke_width=4.5),
            path(f"M{cx-6} {cy-6} Q{cx} {cy-9} {cx+6} {cy-6}", fill="none", stroke=SKIN_D, stroke_width=2.5, stroke_linecap="round")]


# ---------- poses: (body kind, extra silhouette, layers between body and head) ----------
def pose_crossed(accent):
    sil = [sil_arm(196, 200, 74, 186), sil_arm(44, 200, 166, 186),
           ("circle", {"cx": 64, "cy": 178, "r": 14}), ("circle", {"cx": 172, "cy": 185, "r": 14})]
    lay = sleeve(196, 200, 74, 186) + fist(64, 178) + sleeve(44, 200, 166, 186) + [
        line(151, 187.7, 157, 187, 29, WHITE, "butt"),
        path("M60 194 Q100 186 140 186", fill="none", stroke=SUIT_L, stroke_width=3, stroke_linecap="round")] + fist(172, 185)
    return "short", sil, lay


def pose_stop(accent):  # raised palm: "not now"
    fingers = [el("rect", x=x, y=72, width=7.5, height=28, rx=3.75, fill=SKIN, stroke=INK, stroke_width=4) for x in (23, 31, 39, 47)]
    thumb = path("M50 110 C58 108 61 101 63 95 C64 90 58 88 56 93 C54 98 53 101 49 102 Z", fill=SKIN, stroke=INK, stroke_width=4, stroke_linejoin="round")
    palm = el("rect", x=22, y=90, width=33, height=32, rx=11, fill=SKIN, stroke=INK, stroke_width=4.5)
    sil = [sil_arm(50, 206, 40, 128), ("rect", {"x": 22, "y": 72, "width": 33, "height": 50, "rx": 10}),
           ("path", {"d": "M50 110 C58 108 61 101 63 95 C64 90 58 88 56 93 C54 98 53 101 49 102 Z"})]
    lay = sleeve(50, 206, 40, 128) + [cuff(50, 206, 40, 128, 0.8)] + fingers + [thumb, palm,
           path("M30 108 Q38 112 46 108", fill="none", stroke=SKIN_D, stroke_width=2.5, stroke_linecap="round")]
    return "bust", sil, lay


def pose_thumbs(accent):  # thumbs up: "you're in"
    sil = [sil_arm(194, 212, 172, 166), ("rect", {"x": 156, "y": 122, "width": 32, "height": 52, "rx": 9})]
    lay = sleeve(194, 212, 172, 166) + [cuff(194, 212, 172, 166, 0.66),
           el("rect", x=161, y=122, width=13, height=32, rx=6.5, fill=SKIN, stroke=INK, stroke_width=4),
           el("rect", x=156, y=144, width=32, height=30, rx=9, fill=SKIN, stroke=INK, stroke_width=4.5)]
    lay += [path(f"M166 {y} L183 {y}", fill="none", stroke=SKIN_D, stroke_width=2.5, stroke_linecap="round") for y in (154, 161, 168)]
    return "bust", sil, lay


def pose_clipboard(accent):  # reading the list: handing over held messages
    sil = [sil_arm(44, 214, 84, 192), sil_arm(196, 214, 156, 192),
           ("rect", {"x": 78, "y": 140, "width": 84, "height": 82, "rx": 7})]
    lay = sleeve(44, 214, 84, 192) + sleeve(196, 214, 156, 192) + [
        el("rect", x=78, y=146, width=84, height=76, rx=7, fill="#D9B98C", stroke=INK, stroke_width=4.5),
        el("rect", x=86, y=157, width=68, height=60, rx=3, fill=WHITE, stroke=INK, stroke_width=2.5),
        el("rect", x=104, y=140, width=32, height=12, rx=4, fill="#9AA0B4", stroke=INK, stroke_width=3.5)]
    for i, y in enumerate((170, 184, 198, 210)):
        lay.append(path(f"M105 {y} L146 {y}", fill="none", stroke="#B9B3C9", stroke_width=3, stroke_linecap="round"))
        if i < 2:
            lay.append(path(f"M92 {y} l3.5 4 l6 -8", fill="none", stroke=INK, stroke_width=3, stroke_linecap="round", stroke_linejoin="round"))
        else:
            lay.append(el("circle", cx=96, cy=y, r=3.5, fill="none", stroke=INK, stroke_width=2.5))
    lay += fist(84, 192, 12) + fist(156, 192, 12)
    return "bust", sil, lay


def pose_shrug(accent):  # "fine, go in"
    hands = [("ellipse", {"cx": 26, "cy": 166, "rx": 13, "ry": 8, "transform": "rotate(-20 26 166)"}),
             ("ellipse", {"cx": 214, "cy": 166, "rx": 13, "ry": 8, "transform": "rotate(20 214 166)"})]
    sil = [sil_arm(48, 206, 32, 174), sil_arm(192, 206, 208, 174)] + hands
    lay = sleeve(48, 206, 32, 174) + sleeve(192, 206, 208, 174) + [cuff(48, 206, 32, 174, 0.72), cuff(192, 206, 208, 174, 0.72)]
    lay += [el(tag, **a, fill=SKIN, stroke=INK, stroke_width=4.5) for tag, a in hands]
    return "bust", sil, lay


def pose_coffee(accent):  # nothing to sort
    cup = "M60 150 L92 150 L88 186 Q87 192 81 192 L71 192 Q65 192 64 186 Z"
    sil = [sil_arm(44, 214, 60, 176), ("path", {"d": cup}), ("rect", {"x": 52, "y": 144, "width": 43, "height": 44, "rx": 6})]
    lay = sleeve(44, 214, 60, 176) + [
        path("M70 136 Q66 130 70 124 Q74 118 70 112", fill="none", stroke=INK, stroke_width=3, stroke_linecap="round", opacity=0.45),
        path("M82 134 Q78 128 82 122 Q86 116 82 110", fill="none", stroke=INK, stroke_width=3, stroke_linecap="round", opacity=0.45),
        path(cup, fill=WHITE, stroke=INK, stroke_width=4, stroke_linejoin="round"),
        path("M61.4 162 L90.6 162 L89.4 174 L62.6 174 Z", fill=accent, stroke=INK, stroke_width=3, stroke_linejoin="round"),
        el("rect", x=57, y=144, width=38, height=8, rx=3, fill="#E9E4F7", stroke=INK, stroke_width=4),
        el("rect", x=52, y=158, width=19, height=28, rx=8, fill=SKIN, stroke=INK, stroke_width=4.5),
        path("M57 167 L67 167 M57 175 L67 175", fill="none", stroke=SKIN_D, stroke_width=2.5, stroke_linecap="round")]
    return "bust", sil, lay


def pose_none(accent):
    return "bust", [], []


def mascot(pose, accent=ACCENT, size=240, label="", **face_kw):
    kind, sil, lay = pose(accent)
    s = BASE_SIL + sil
    parts = [underlay(s, INK, 5, 6), underlay(s, WHITE)] + body(kind, accent) + lay + face(**face_kw)
    aria = f' role="img" aria-label="{label}"' if label else ' aria-hidden="true"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 240 240"{aria}>'
            + "".join(parts) + "</svg>")


STATES = {  # file name: (pose, face, alt text)
    "let-in": (pose_thumbs, dict(brows="relaxed", mouth="smile"), "Thumbs up: the message gets in now"),
    "held": (pose_stop, dict(brows="stern", mouth="flat"), "Raised hand: the message waits"),
    "handover": (pose_clipboard, dict(brows="raised", mouth="hmm", specs="lowered", nose=False), "Reading the list: held messages handed over"),
    "resent": (pose_shrug, dict(brows="raised", mouth="meh"), "Shrug: sent twice, so it gets in"),
    "error": (pose_none, dict(brows="worried", mouth="wobbly", specs="crooked", extras=("sweat",)), "Crooked glasses: triage failed, message passes"),
    "idle": (pose_coffee, dict(brows="relaxed", mouth="content"), "Coffee break: nothing to sort"),
}


def icon(accent=ACCENT, size=512):
    """Head in a round badge (plugin icon)."""
    thin = dict(stroke=INK, stroke_width=3.5, stroke_linejoin="round")
    parts = [el("circle", cx=120, cy=120, r=104, fill=accent, stroke=INK, stroke_width=6),
             path("M100 134 L100 170 L140 170 L140 134 Z", fill=SKIN_D, stroke=INK, stroke_width=5, stroke_linejoin="round"),
             path("M48 195 C54 180 78 172 102 166 L120 180 L138 166 C162 172 186 180 192 195 A104 104 0 0 1 48 195 Z",
                  fill=SUIT, stroke=INK, stroke_width=5, stroke_linejoin="round"),
             path("M102 166 L138 166 L127 198 L113 198 Z", fill=WHITE, **thin),
             path("M114 172 L126 172 L123 181 L117 181 Z", fill=INK),
             path("M117 181 L123 181 L127 205 L120 212 L113 205 Z", fill=INK),
             path("M100 162 L120 180 L108 186 L98 168 Z", fill=WHITE, **thin),
             path("M140 162 L120 180 L132 186 L142 168 Z", fill=WHITE, **thin),
             path("M84 170 L102 166 L115 204 L96 186 Z", fill=SUIT_L, **thin),
             path("M156 170 L138 166 L125 204 L144 186 Z", fill=SUIT_L, **thin)]
    head = [path(d, fill=SKIN, stroke=INK, stroke_width=5, stroke_linejoin="round") for d in EARS] + face()
    parts.append(f'<g transform="translate(0 26)">{"".join(head)}</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 240 240" '
            f'role="img" aria-label="bouncer">' + "".join(parts) + "</svg>")


if __name__ == "__main__":
    out = Path(sys.argv[1])
    (out / "states").mkdir(parents=True, exist_ok=True)
    files = {"bouncer.svg": mascot(pose_crossed, size=480, label="bouncer, the mascot: a bouncer with arms crossed"),
             "icon.svg": icon()}
    for name, (pose, kw, alt) in STATES.items():
        files[f"states/{name}.svg"] = mascot(pose, label=alt, **kw)
    for name, svg in files.items():
        (out / name).write_text(svg)
    cells = [files["bouncer.svg"].replace('width="480" height="480"', 'width="240" height="240"')] + \
            [files[f"states/{n}.svg"] for n in STATES]
    sheet = "".join(c.replace("<svg ", f'<svg x="{(i % 4) * 250}" y="{(i // 4) * 250}" ', 1) for i, c in enumerate(cells))
    (out / "sheet.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="500" '
                                   f'style="background:#C8B6FF">{sheet}</svg>')
    print("\n".join(sorted(files)))
