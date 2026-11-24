"""README visuals for bouncer: stickers.svg, flow.svg and demo.svg (animated).

python3 assets/readme.py
The fonts (SIL OFL, in assets/fonts) are embedded, so the visuals look the same everywhere, offline too.
The mascot comes from mascot.py. The demo honours "reduce motion": it then shows a single still frame.
"""
import base64
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mascot as M  # noqa: E402

INK, LILAC, LIME, WHITE, PINK, MINT = "#17131F", "#C8B6FF", "#D7FF3A", "#FFFFFF", "#FF8FD1", "#7CF5C8"
PANEL, TEXT, DIM = "#17131F", "#E9E4F7", "#A79FBF"
SANS, MONO = "'Bricolage Grotesque', system-ui, sans-serif", "'JetBrains Mono', ui-monospace, monospace"
T = 16.0  # demo loop, seconds


def font_css(mono=False):
    faces = [("Bricolage Grotesque", "BricolageGrotesque.woff2", "400 800")]
    if mono:
        faces.append(("JetBrains Mono", "JetBrainsMono.woff2", "400 700"))
    css = ""
    for family, file, weight in faces:
        data = base64.b64encode((HERE / "fonts" / file).read_bytes()).decode()
        css += f"@font-face{{font-family:'{family}';font-weight:{weight};src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    return css


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_w(s, size, weight=600, caps=False, spacing=0.0):
    """Rough width of Bricolage text, for layout (the renders were checked by eye)."""
    k = 0.64 if caps else (0.55 if weight >= 700 else 0.52)
    return len(s) * (size * k + spacing)


def svg(w, h, body, label, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(label)}"><style>{css}</style>{body}</svg>')


def nested(inner, x, y, size):
    """Place a standalone 240-box mascot SVG at (x, y)."""
    return inner.replace("<svg ", f'<svg x="{x}" y="{y}" ', 1).replace(
        'width="240" height="240"', f'width="{size}" height="{size}"', 1)


# ---------------------------------------------------------------- stickers
def ticket(x, y, w, h, fill, label, angle):
    cy, r = y + h / 2, 8
    d = (f"M{x} {y} H{x + w} V{cy - r} A{r} {r} 0 0 0 {x + w} {cy + r} V{y + h} H{x} "
         f"V{cy + r} A{r} {r} 0 0 0 {x} {cy - r} Z")
    cx = x + w / 2
    return (f'<g transform="rotate({angle} {cx} {cy})">'
            f'<path d="{d}" transform="translate(4 4)" fill="{INK}"/>'
            f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M{x + 30} {y + 7} V{y + h - 7}" stroke="{INK}" stroke-width="2" stroke-dasharray="4 4"/>'
            f'<circle cx="{x + 16}" cy="{cy}" r="4" fill="{INK}"/>'
            f'<text x="{x + 30 + (w - 30) / 2}" y="{cy + 5}" text-anchor="middle" font-family="{SANS}" '
            f'font-weight="800" font-size="14" letter-spacing="1" fill="{INK}">{esc(label)}</text></g>')


def stickers():
    items = [("YOUR WORDS, UNTOUCHED", LIME, -3), ("NEVER LOSES A MESSAGE", WHITE, 2),
             ("FAILS OPEN", PINK, -2), ("MADE WITH CLAUDE", MINT, 3)]
    widths = [text_w(s, 14, caps=True, spacing=1) + 58 for s, _, _ in items]
    gap = 22
    x = (1000 - sum(widths) - gap * (len(items) - 1)) / 2
    body = ""
    for (label, fill, angle), w in zip(items, widths):
        body += ticket(round(x, 1), 26, round(w, 1), 50, fill, label, angle)
        x += w + gap
    return svg(1000, 104, body, "your words, untouched · never loses a message · fails open · made with Claude", font_css())


# ---------------------------------------------------------------- flow
def card(x, y, w, h, fill=WHITE):
    return (f'<rect x="{x + 6}" y="{y + 6}" width="{w}" height="{h}" rx="20" fill="{INK}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="{fill}" stroke="{INK}" stroke-width="3"/>')


def lines(x, y, rows, size=15, weight=500, gap=21, anchor="start"):
    out = f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="{size}" font-weight="{weight}" fill="{INK}" text-anchor="{anchor}">'
    for i, row in enumerate(rows):
        out += f'<tspan x="{x}" dy="{0 if i == 0 else gap}">{esc(row)}</tspan>'
    return out + "</text>"


def badge(x, y, n):
    return (f'<circle cx="{x}" cy="{y}" r="17" fill="{LIME}" stroke="{INK}" stroke-width="3"/>'
            f'<text x="{x}" y="{y + 6}" text-anchor="middle" font-family="{SANS}" font-size="17" font-weight="800" fill="{INK}">{n}</text>')


def arrow(x1, y1, x2, y2):
    return (f'<path d="M{x1} {y1} L{x2 - 10} {y2}" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
            f'<path d="M{x2 - 16} {y2 - 9} L{x2} {y2} L{x2 - 16} {y2 + 9}" fill="none" stroke="{INK}" stroke-width="4" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def flow():
    b = f'<rect width="960" height="340" rx="28" fill="{LILAC}"/>'
    # 1. you type
    b += card(28, 46, 250, 250) + badge(52, 70, 1)
    b += (f'<path d="M78 112 H226 Q240 112 240 126 V170 Q240 184 226 184 H112 L92 202 L96 184 H78 Q64 184 64 170 V126 '
          f'Q64 112 78 112 Z" fill="{WHITE}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
    b += lines(84, 145, ["stay on Python 3.9", "no match/case"], size=15, weight=600)
    b += lines(52, 236, ["You type while", "Claude works."], size=19, weight=800, gap=24)
    # 2. bouncer looks
    b += card(355, 46, 250, 250) + badge(379, 70, 2)
    b += nested(M.icon(size=240), 420, 74, 120)
    b += lines(379, 236, ["bouncer takes", "a look."], size=19, weight=800, gap=24)
    b += lines(379, 282, ["Haiku reads it next to the task."], size=13, weight=500)
    # 3. in or the line
    b += card(682, 46, 250, 112, LIME) + badge(706, 70, 3)
    b += lines(706, 112, ["IN, right away"], size=19, weight=800)
    b += lines(706, 136, ["It changes the task: Claude", "gets it at its next step."], size=13, weight=500, gap=18)
    b += card(682, 184, 250, 112)
    b += lines(706, 226, ["THE LINE, for later"], size=19, weight=800)
    b += lines(706, 250, ["It can wait: handed over", "when the task is done."], size=13, weight=500, gap=18)
    b += arrow(290, 171, 345, 171) + arrow(617, 150, 672, 104) + arrow(617, 192, 672, 238)
    return svg(960, 340, b, "1. You type while Claude works. 2. bouncer takes a look: Haiku reads your message "
               "next to the task. 3. If it changes the task, it gets in right away; if it can wait, it waits in "
               "line and is handed over when the task is done.", font_css())


# ---------------------------------------------------------------- demo (animated)
def pct(t):
    return f"{max(0.0, min(100.0, t / T * 100)):.2f}%"


def keyframes(name, steps):
    """steps: [(seconds, css)] -> @keyframes, first and last frames added."""
    steps = sorted(steps, key=lambda s: s[0])
    if steps[0][0] > 0:
        steps = [(0, steps[0][1])] + steps
    if steps[-1][0] < T:
        steps = steps + [(T, steps[-1][1])]
    return f"@keyframes {name}{{" + "".join(f"{pct(t)}{{{css}}}" for t, css in steps) + "}"


def windows(name, wins, ease=0.08):
    """Opacity 1 inside each (start, end) window, 0 elsewhere."""
    st = [(0, "opacity:0")]
    for a, b in wins:
        st += [(a - ease, "opacity:0"), (a, "opacity:1"), (b, "opacity:1")]
        if b < T:
            st.append((b + ease, "opacity:0"))
    return keyframes(name, st)


def bubble_w(text):
    return round(text_w(text, 15) + 30)


def bubble(name, text, stamp, stamp_fill, x0, y0, static_t, static_op, static_stamp):
    w = bubble_w(text)
    sw = round(text_w(stamp, 13, caps=True, spacing=1) + 22)
    g = (f'<g transform="translate({x0 - w} {y0})"><g class="b {name}" transform="translate({static_t[0]} {static_t[1]})" opacity="{static_op}">'
         f'<path d="M16 0 H{w - 16} Q{w} 0 {w} 16 V24 Q{w} 40 {w - 16} 40 H30 L14 52 L18 40 H16 Q0 40 0 24 V16 Q0 0 16 0 Z" '
         f'fill="{WHITE}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
         f'<text x="15" y="26" font-family="{SANS}" font-size="15" font-weight="600" fill="{INK}">{esc(text)}</text>'
         f'<g transform="translate({w - 24} -16) rotate(-7)"><g class="{name}s st" opacity="{static_stamp}">'
         f'<rect x="3" y="3" width="{sw}" height="26" rx="7" fill="{INK}"/>'
         f'<rect width="{sw}" height="26" rx="7" fill="{stamp_fill}" stroke="{INK}" stroke-width="3"/>'
         f'<text x="{sw / 2}" y="18" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="800" '
         f'letter-spacing="1" fill="{INK}">{esc(stamp)}</text></g></g></g></g>')
    return g, w


def demo():
    door_x, arrive_y = 330, 176           # bubbles stop with their right edge at door_x
    line_x, line_y = 44, 356               # where held messages wait, just above the rope
    css = font_css(mono=True)
    css += (f".m,.b,.l{{animation-duration:{T}s;animation-iteration-count:infinite;animation-timing-function:ease-in-out}}"
            ".st{transform-box:fill-box;transform-origin:center}"
            "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    body = f'<rect width="900" height="440" rx="28" fill="{LILAC}"/>'
    body += (f'<text x="34" y="52" font-family="{SANS}" font-size="13" font-weight="800" letter-spacing="2" '
             f'fill="{INK}" opacity="0.75">OUTSIDE</text>')
    # door, sign, floor
    body += (f'<rect x="352" y="52" width="136" height="28" rx="8" fill="{INK}"/>'
             f'<text x="420" y="71" text-anchor="middle" font-family="{SANS}" font-size="12" font-weight="800" '
             f'letter-spacing="1.5" fill="{LIME}">CLAUDE AT WORK</text>'
             f'<rect x="342" y="88" width="156" height="262" rx="10" fill="#2B2440" stroke="{INK}" stroke-width="4"/>'
             f'<rect x="358" y="104" width="124" height="246" rx="4" fill="#3D3459"/>'
             f'<path d="M24 350 H530" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    # the line: label, posts, rope (drawn after the bubbles, see below)
    body += (f'<text x="356" y="420" font-family="{SANS}" font-size="12" font-weight="800" letter-spacing="1.5" '
             f'fill="{INK}" opacity="0.75">THE LINE</text>')
    # mascot poses, one visible at a time
    poses = [("m0", M.mascot(M.pose_crossed, size=240), 1), ("m1", M.mascot(M.pose_thumbs, size=240, brows="relaxed", mouth="smile"), 0),
             ("m2", M.mascot(M.pose_stop, size=240, brows="stern", mouth="flat"), 0),
             ("m3", M.mascot(M.pose_clipboard, size=240, brows="raised", mouth="hmm", specs="lowered", nose=False), 0)]
    for cls, art, op in poses:
        body += f'<g class="m {cls}" opacity="{op}">{nested(art, 326, 166, 188)}</g>'
    # bubbles: (class, text, stamp, fill, arrive, stamp_t, leave, to_line, back)
    w1, w2, w3 = (bubble_w(t) for t in ("stay on Python 3.9", "what's the capital of Australia?", "only from 1 to 15"))
    b1, _ = bubble("b1", "stay on Python 3.9", "IN", LIME, door_x, arrive_y, (0, 0), 0, 0)
    b2, _ = bubble("b2", "what's the capital of Australia?", "LATER", WHITE, door_x, arrive_y,
                   (line_x - (door_x - w2), line_y - arrive_y), 1, 1)
    b3, _ = bubble("b3", "only from 1 to 15", "IN", LIME, door_x, arrive_y, (0, 0), 0, 0)
    body += b1 + b2 + b3
    body += (f'<path d="M30 406 Q185 430 340 406" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
             f'<path d="M30 406 Q185 430 340 406" fill="none" stroke="{PINK}" stroke-width="4" stroke-linecap="round"/>')
    for px in (30, 340):
        body += (f'<rect x="{px - 4}" y="400" width="8" height="30" rx="4" fill="{INK}"/>'
                 f'<rect x="{px - 12}" y="427" width="24" height="7" rx="3.5" fill="{INK}"/>'
                 f'<circle cx="{px}" cy="400" r="7" fill="{LIME}" stroke="{INK}" stroke-width="2.5"/>')
    # Claude's panel
    body += (f'<rect x="548" y="40" width="328" height="360" rx="18" fill="{PANEL}" stroke="{INK}" stroke-width="3"/>'
             + "".join(f'<circle cx="{570 + 16 * i}" cy="62" r="5" fill="#3D3459"/>' for i in range(3))
             + f'<text x="622" y="66" font-family="{MONO}" font-size="12" fill="{DIM}">claude · ~/shop</text>'
             f'<path d="M549 82 H875" stroke="#2B2440" stroke-width="2"/>')
    rows = [  # (appears at, text, color, tag)
        (0.2, "> refactor the payment module", TEXT, None),
        (0.9, "  · Edit payment.py", DIM, None),
        (3.6, "+ stay on Python 3.9", TEXT, "IN"),
        (4.6, "  · Edit payment.py", DIM, None),
        (9.6, "+ only from 1 to 15", TEXT, "IN"),
        (10.2, "  · Bash pytest -q   42 passed", DIM, None),
        (10.8, "  task done", LIME, None),
        (12.3, "-> 1 held message handed over", TEXT, None),
        (12.9, "  Canberra. Refactor done.", TEXT, None),
    ]
    anim = ""
    for i, (t, txt, color, tag) in enumerate(rows):
        y = 114 + i * 30
        static = 1 if t < 11 else 0
        row = f'<text x="566" y="{y}" font-family="{MONO}" font-size="13" fill="{color}" xml:space="preserve">{esc(txt)}</text>'
        if tag:
            tx = 566 + len(txt) * 7.8 + 10
            row += (f'<rect x="{tx}" y="{y - 13}" width="28" height="18" rx="4" fill="{LIME}"/>'
                    f'<text x="{tx + 14}" y="{y}" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="700" fill="{INK}">{tag}</text>')
        body += f'<g class="l l{i}" opacity="{static}">{row}</g>'
        anim += keyframes(f"l{i}", [(0, "opacity:0"), (t, "opacity:0"), (t + 0.3, "opacity:1"), (15.3, "opacity:1"), (15.8, "opacity:0")])
        anim += f".l{i}{{animation-name:l{i}}}"
    # mascot timing
    anim += windows("m0", [(0, 2.2), (3.7, 5.4), (6.9, 8.4), (9.9, 10.9), (13.7, T)]) + ".m0{animation-name:m0}"
    anim += windows("m1", [(2.3, 3.6), (8.5, 9.8)]) + ".m1{animation-name:m1}"
    anim += windows("m2", [(5.5, 6.8)]) + ".m2{animation-name:m2}"
    anim += windows("m3", [(11.0, 13.6)]) + ".m3{animation-name:m3}"

    # bubble motion: offsets from the arrival spot
    def through_door(x0):
        return 470 - x0

    def move(name, x0, w, arrive, stamp_t, leave, line=None, back=None):
        off = -(x0 + w + 20)
        st = [(0, f"transform:translate({off}px,0);opacity:0"), (arrive - 1.0, f"transform:translate({off}px,0);opacity:1"),
              (arrive, "transform:translate(0,0);opacity:1"), (leave, "transform:translate(0,0);opacity:1")]
        if line is None:
            st += [(leave + 0.7, f"transform:translate({through_door(x0)}px,0);opacity:0")]
        else:
            lx, ly = line
            st += [(leave + 0.9, f"transform:translate({lx}px,{ly}px);opacity:1"),
                   (back, f"transform:translate({lx}px,{ly}px);opacity:1"),
                   (back + 1.0, f"transform:translate({through_door(x0)}px,0);opacity:0")]
        k = keyframes(name, st) + f".{name}{{animation-name:{name}}}"
        k += keyframes(name + "s", [(0, "opacity:0;transform:scale(0)"), (stamp_t - 0.01, "opacity:0;transform:scale(0)"),
                                    (stamp_t, "opacity:1;transform:scale(0.2)"), (stamp_t + 0.15, "opacity:1;transform:scale(1.25)"),
                                    (stamp_t + 0.3, "opacity:1;transform:scale(1)"), (T - 0.4, "opacity:1;transform:scale(1)"),
                                    (T, "opacity:0;transform:scale(1)")])
        return k + f".{name}s{{animation-name:{name}s;animation-duration:{T}s;animation-iteration-count:infinite}}"

    x1, x2, x3 = door_x - w1, door_x - w2, door_x - w3
    anim += move("b1", x1, w1, 2.0, 2.25, 2.9)
    anim += move("b2", x2, w2, 5.2, 5.45, 6.1, line=(line_x - x2, line_y - arrive_y), back=11.3)
    anim += move("b3", x3, w3, 8.2, 8.45, 8.9)
    label = ("Animated demo. Claude works on a task behind a door guarded by bouncer. Three messages arrive. "
             "'stay on Python 3.9' is stamped IN and goes straight to Claude. 'what's the capital of Australia?' is stamped "
             "LATER and waits in line. 'only from 1 to 15' is stamped IN. When the task is done, bouncer reads his list "
             "and hands the held message over.")
    return svg(900, 440, body, label, css + anim)


if __name__ == "__main__":
    files = {"stickers.svg": stickers(), "flow.svg": flow(), "demo.svg": demo()}
    for name, content in files.items():
        (HERE / name).write_text(content)
        print(f"{name}: {len(content) // 1024} KB")
