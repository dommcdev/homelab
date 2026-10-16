# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools", "numpy"]
# ///
"""Generate the CathSocial wordmark SVG.

    uv run build.py                      # writes ../cathsocial-logo.svg
    uv run build.py --gap 40 -o /tmp/looser.svg

Design knobs live near the top (NAVY, GOLD, KEY keyline width) and in the
element builders under "layout": C_el (crown angle/scale), cross_el
(CB_HALF arm reach, bar height), heart_el (HW/HH size, heart cross), i_el (flame).
"""
import argparse
import math
import re
from pathlib import Path

import numpy as np
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("-o", "--out", default=str(HERE.parent / "cathsocial-logo.svg"))
ap.add_argument("--gap", type=float, default=30, help="outline-to-outline gap between letters (font units)")
ap.add_argument("--optical", type=float, default=0.6, help="strength of the white-space evening correction (0 = off)")
ap.add_argument("--weight", type=float, default=700, help="Cormorant Garamond weight (300-700)")
args = ap.parse_args()

NAVY = "#0F2F66"
GOLD = "#D6A23E"
KEY = 12          # gold keyline width (font units) outside navy shapes
TRACK = -12        # extra letterspacing

font = instantiateVariableFont(TTFont(HERE / "CormorantGaramond[wght].ttf"), {"wght": args.weight})
gs = font.getGlyphSet()
cmap = font.getBestCmap()
hmtx = font["hmtx"]

BASE = 900  # baseline y in SVG space; y_svg = BASE - y_font
OX = 120


def fx(x, y):
    return (round(x + OX, 1), round(BASE - y, 1))


class P:
    """Path builder in y-up font units, emitted in SVG y-down space."""

    def __init__(self, tf=None):
        self.d = []
        self.tf = tf or (lambda x, y: (x, y))

    def _p(self, *pts):
        out = []
        for i in range(0, len(pts), 2):
            x, y = self.tf(pts[i], pts[i + 1])
            sx, sy = fx(x, y)
            out.append(f"{sx:g},{sy:g}")
        return " ".join(out)

    def M(self, *p): self.d.append("M" + self._p(*p)); return self
    def L(self, *p): self.d.append("L" + self._p(*p)); return self
    def C(self, *p): self.d.append("C" + self._p(*p)); return self
    def Q(self, *p): self.d.append("Q" + self._p(*p)); return self
    def Z(self): self.d.append("Z"); return self
    def __str__(self): return "".join(self.d)


def glyph_d(name, x):
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    tp = TransformPen(pen, (1, 0, 0, -1, x + OX, BASE))
    gs[name].draw(tp)
    return pen.getCommands()


def bounds(name):
    bp = BoundsPen(gs)
    gs[name].draw(bp)
    return bp.bounds


def rot(cx, cy, ang_deg):
    a = math.radians(ang_deg)
    ca, sa = math.cos(a), math.sin(a)
    return lambda x, y: (cx + x * ca - y * sa, cy + x * sa + y * ca)


def circle(cx, cy, r, tf):
    x, y = tf(cx, cy)
    sx, sy = fx(x, y)
    return f'<circle cx="{sx:g}" cy="{sy:g}" r="{r:g}"/>'


# ---------- ornaments ----------

def bottony(cx, y0, y1, bar_y, bar_half, w, r, fl=12, fd=54, jewels=None, jr=0):
    """Latin cross bottony: trefoil ends on the upper three arms, flared foot."""
    h = w / 2
    e = h + fl
    out = []
    reach = r * 2.2  # how far back from each arm end the trefoil starts
    p = P()
    p.M(cx - h, y1 - reach).L(cx + h, y1 - reach)
    p.L(cx + h, bar_y + h).L(cx + bar_half - reach, bar_y + h)
    p.L(cx + bar_half - reach, bar_y - h).L(cx + h, bar_y - h)
    p.L(cx + h, y0 + fd).Q(cx + h, y0 + fd * 0.25, cx + e, y0).L(cx - e, y0)
    p.Q(cx - h, y0 + fd * 0.25, cx - h, y0 + fd)
    p.L(cx - h, bar_y - h).L(cx - bar_half + reach, bar_y - h)
    p.L(cx - bar_half + reach, bar_y + h).L(cx - h, bar_y + h).Z()
    out.append(str(p))
    ident = lambda x, y: (x, y)
    for ex, ey, ux, uy in ((cx, y1, 0, 1), (cx + bar_half, bar_y, 1, 0), (cx - bar_half, bar_y, -1, 0)):
        vx, vy = -uy, ux
        tip = (ex - ux * r, ey - uy * r)
        back = r * 1.02
        side = r * 1.06
        for c in (tip,
                  (tip[0] - ux * back + vx * side, tip[1] - uy * back + vy * side),
                  (tip[0] - ux * back - vx * side, tip[1] - uy * back - vy * side)):
            out.append(circle(c[0], c[1], r, ident))
        mid = (tip[0] - ux * back * 0.62, tip[1] - uy * back * 0.62)
        out.append(circle(mid[0], mid[1], r * 0.75, ident))
        if jewels is not None:
            jewels.append(circle(mid[0], mid[1], jr, ident))
    return out


def lozenge(cx, cy, rx, ry, tf=None):
    return str(P(tf).M(cx, cy + ry).L(cx + rx, cy).L(cx, cy - ry).L(cx - rx, cy).Z())


def heart(cx, cy, hw, hh):
    t = lambda x, y: (cx + x * hw, cy + y * hh)
    p = P(t)
    p.M(0, -1)
    p.C(-0.38, -0.62, -1, -0.22, -1, 0.36)
    p.C(-1, 0.78, -0.72, 1, -0.47, 1)
    p.C(-0.22, 1, -0.06, 0.86, 0, 0.66)
    p.C(0.06, 0.86, 0.22, 1, 0.47, 1)
    p.C(0.72, 1, 1, 0.78, 1, 0.36)
    p.C(1, -0.22, 0.38, -0.62, 0, -1).Z()
    return str(p)


def thorns(cx, cy, hw, amp, wl, bow):
    """Two counter-phase strands on a shallow arc, with thorns at the crests."""
    x0, x1 = cx - hw * 1.1, cx + hw * 1.1
    arc = lambda x: cy - bow * (1 - ((x - cx) / hw) ** 2)
    wave = lambda x, ph: amp * math.sin(2 * math.pi * (x - cx) / wl + ph)
    strands = []
    for ph in (0, math.pi):
        p = P()
        n = 160
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            (p.M if i == 0 else p.L)(x, arc(x) + wave(x, ph))
        strands.append(str(p))
    spikes = []
    j = 0
    xc = cx - wl * 0.25 - wl * math.ceil(hw / wl)
    while xc < x1:
        for ph, sgn in ((0, 1), (math.pi, -1)):
            if not (x0 < xc < x1):
                continue
            up = 1 if wave(xc, ph) > 0 else -1
            yb = arc(xc) + wave(xc, ph)
            lean = 8 * (1 if j % 2 else -1)
            ln = 26
            spikes.append(str(P().M(xc - 9, yb).L(xc + lean, yb + up * ln).L(xc + 9, yb).Z()))
            j += 1
        xc += wl / 2
    return strands, spikes


def crown(cx, cy, ang, s=1.0, arch=30):
    """Five-point crown on an arched band. (cx, cy) is the bottom-centre of the band."""
    tf = rot(cx, cy, ang)
    S = lambda v: v * s
    W, bh, A = S(168), S(52), S(arch)
    nk = S(9)  # half-width of the neck under each finial
    peaks = [(-W - S(10), S(150)), (-S(86), S(112)), (0, S(186)), (S(86), S(112)), (W + S(10), S(150))]
    dips = [S(66), S(70), S(70), S(66)]
    ys = lambda x: A * (1 - (x / W) ** 2)  # arch offset at x
    g = S(9)  # gap between band and crest
    band = P(tf).M(-W, 0).Q(0, 2 * A, W, 0).L(W + S(4), bh).Q(0, bh + 2 * A, -W - S(4), bh).Z()
    p = P(tf)
    p.M(-W + S(2), bh + g).Q(0, bh + g + 2 * A, W - S(2), bh + g)
    p.Q(W + S(6), bh + S(60), peaks[4][0] + nk, bh + peaks[4][1])
    p.L(peaks[4][0] - nk, bh + peaks[4][1])
    for i in range(3, -1, -1):
        (ax, ay), (bx, by) = peaks[i + 1], peaks[i]
        ctrl_y = 2 * (dips[i] + ys((ax + bx) / 2)) - (ay + by) / 2 - S(8)
        p.Q((ax + bx) / 2, bh + ctrl_y, bx + nk, bh + by)
        p.L(bx - nk, bh + by)
    p.Q(-W - S(6), bh + S(60), -W + S(2), bh + g).Z()
    body = str(band) + str(p)
    fin = []
    for i, (x, y) in enumerate(peaks):
        if i % 2 == 0:
            fin.append(lozenge(x, bh + y + S(16), S(20), S(30), tf))
        else:
            fin.append(circle(x, bh + y + S(10), S(16), tf))
    jy = bh / 2 + A * 0.5
    jewels = [
        lozenge(0, jy, S(22), S(16), tf),
        lozenge(-S(100), bh / 2 + ys(S(100)), S(14), S(11), tf),
        lozenge(S(100), bh / 2 + ys(S(100)), S(14), S(11), tf),
    ]
    return body, fin, jewels


def seat(glyph, gx, ang, gap):
    """Point on a glyph's outline that supports a shape tilted by `ang`."""
    from fontTools.pens.basePen import BasePen

    pts = []

    class Flat(BasePen):
        def _moveTo(self, p): pts.append(p); self.cur = p
        def _lineTo(self, p): pts.append(p); self.cur = p
        def _curveToOne(self, a, b, c):
            p0 = self.cur
            for k in range(1, 25):
                t = k / 24
                u = 1 - t
                pts.append((u**3 * p0[0] + 3 * u * u * t * a[0] + 3 * u * t * t * b[0] + t**3 * c[0],
                            u**3 * p0[1] + 3 * u * u * t * a[1] + 3 * u * t * t * b[1] + t**3 * c[1]))
            self.cur = c

    gs[glyph].draw(Flat(gs))
    nx, ny = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
    px, py = max(pts, key=lambda q: q[0] * nx + q[1] * ny)
    return gx + px + nx * gap, py + ny * gap


def flame(cx, y0, h, w):
    """Gold flame with a navy core; returns (outer, inner)."""
    t = lambda x, y: (cx + x * w, y0 + y * h)
    o = P(t)
    o.M(0, 0)
    o.C(-0.64, 0, -1.0, 0.26, -0.94, 0.52)
    o.C(-0.88, 0.76, -0.52, 0.84, -0.3, 1.0)      # main tip, leaning left
    o.C(-0.32, 0.86, -0.18, 0.76, 0.02, 0.68)
    o.C(0.2, 0.7, 0.38, 0.74, 0.54, 0.82)         # secondary tongue
    o.C(0.5, 0.68, 0.98, 0.6, 0.94, 0.34)
    o.C(0.9, 0.12, 0.58, 0, 0, 0).Z()
    k = 0.5
    ti = lambda x, y: (cx + (x * k + 0.02) * w, y0 + (y * k * 1.04 + 0.12) * h)
    i = P(ti)
    i.M(0, 0)
    i.C(-0.64, 0, -1.0, 0.26, -0.94, 0.52)
    i.C(-0.88, 0.76, -0.52, 0.84, -0.3, 1.0)
    i.C(-0.2, 0.78, 0.98, 0.6, 0.94, 0.34)
    i.C(0.9, 0.12, 0.58, 0, 0, 0).Z()
    return str(o), str(i)



# ---------- layout ----------
GAP = args.gap


def glyph_pts(name, gx):
    from fontTools.pens.basePen import BasePen
    pts = []

    class Flat(BasePen):
        def _moveTo(self, p): self.cur = p; pts.append(p)
        def _lineTo(self, p):
            p0 = self.cur
            n = max(1, int(math.dist(p0, p) / 4))
            pts.extend((p0[0] + (p[0] - p0[0]) * k / n, p0[1] + (p[1] - p0[1]) * k / n) for k in range(1, n + 1))
            self.cur = p
        def _curveToOne(self, a, b, c):
            p0 = self.cur
            for k in range(1, 33):
                t = k / 32; u = 1 - t
                pts.append((u**3 * p0[0] + 3 * u * u * t * a[0] + 3 * u * t * t * b[0] + t**3 * c[0],
                            u**3 * p0[1] + 3 * u * u * t * a[1] + 3 * u * t * t * b[1] + t**3 * c[1]))
            self.cur = c

    gs[name].draw(Flat(gs))
    return [fx(px + gx, py) for px, py in pts]


def shape_pts(d):
    """Sample an emitted path string or <circle> tag (SVG coordinates)."""
    if d.startswith("<circle"):
        cx, cy, r = (float(v) for v in re.findall(r'"([-\d.]+)"', d))
        return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 72)]
    pts, cur, start = [], None, None
    for cmd, args in re.findall(r"([MLQCZ])([^MLQCZ]*)", d):
        v = [tuple(map(float, p.split(","))) for p in args.split()]
        if cmd == "M":
            cur = start = v[0]; pts.append(cur); continue
        if cmd == "Z":
            v, cmd = [start], "L"
        if cmd == "L":
            for p in v:
                n = max(1, int(math.dist(cur, p) / 4))
                pts += [(cur[0] + (p[0] - cur[0]) * k / n, cur[1] + (p[1] - cur[1]) * k / n) for k in range(1, n + 1)]
                cur = p
        else:
            ctrl = [cur] + v
            for k in range(1, 25):
                t = k / 24
                if cmd == "Q":
                    a, b, c = ctrl
                    pts.append(((1-t)**2*a[0] + 2*(1-t)*t*b[0] + t*t*c[0], (1-t)**2*a[1] + 2*(1-t)*t*b[1] + t*t*c[1]))
                else:
                    a, b, c, e = ctrl
                    pts.append(((1-t)**3*a[0] + 3*(1-t)**2*t*b[0] + 3*(1-t)*t*t*c[0] + t**3*e[0],
                                (1-t)**3*a[1] + 3*(1-t)**2*t*b[1] + 3*(1-t)*t*t*c[1] + t**3*e[1]))
            cur = v[-1]
    return pts


def element(x):
    return {"navy": [], "gold": [], "navy_detail": [], "gold_detail": [], "npts": [], "gpts": [], "thorns": None}


def glyph_el(ch):
    def build(x):
        el = element(x)
        name = cmap[ord(ch)] if len(ch) == 1 else ch
        el["navy"].append(glyph_d(name, x))
        el["npts"] += glyph_pts(name, x)
        return el
    return build


def C_el(x):
    el = glyph_el("C")(x)
    ang, sc, arch = 12, 0.96, 26
    sx, sy = seat(cmap[ord("C")], x, ang, KEY - 3)
    ra = math.radians(ang)
    body, fins, jewels = crown(sx + arch * sc * math.sin(ra), sy - arch * sc * math.cos(ra), ang, s=sc, arch=arch)
    el["gold"].append(body)
    el["gold_detail"] += fins
    el["navy_detail"] += jewels
    return el


CB_HALF = 168


def cross_el(x):
    el = element(x)
    ccx = x + CB_HALF
    el["gold"] += bottony(ccx, 0, 728, 500, CB_HALF, 74, 30, jewels=el["navy_detail"], jr=10)
    el["navy_detail"].append(lozenge(ccx, 500, 18, 26))
    return el


HW, HH = 236, 222


def heart_el(x):
    el = element(x)
    hcx = x + HW
    hcy = (414 - 30) / 2
    d = heart(hcx, hcy, HW, HH)
    el["navy"].append(d)
    el["npts"] += shape_pts(d)
    el["clip"] = d
    cleft = hcy + 0.66 * HH
    el["gold"] += bottony(hcx, cleft + 4, 586, 528, 56, 30, 12, fl=9, fd=26)
    el["thorns"] = thorns(hcx, hcy + 64, HW, 18, 132, 24)
    return el


def i_el(x):
    el = glyph_el("dotlessi")(x)
    ib = bounds("dotlessi")
    fo, fi = flame(x + (ib[0] + ib[2]) / 2 + 4, 446, 236, 74)
    el["gold"].append(fo)
    el["navy_detail"].append(fi)
    return el


SEQ = [C_el, glyph_el("a"), cross_el, glyph_el("h"), glyph_el("S"), heart_el,
       glyph_el("c"), i_el, glyph_el("a"), glyph_el("l")]


def clouds(el):
    n = np.array(el["npts"]) if el["npts"] else np.empty((0, 2))
    g = [p for d in el["gold"] + el["gold_detail"] for p in shape_pts(d)]
    return n, (np.array(g) if g else np.empty((0, 2)))


def gap(A, B, dx):
    best = 1e9
    for pa, ra_ in ((A[0], KEY), (A[1], 0)):
        for pb, rb in ((B[0], KEY), (B[1], 0)):
            if not len(pa) or not len(pb):
                continue
            q = pb + np.array([dx, 0])
            # only points that can matter: overlapping vertical band
            dd = np.sqrt(((pa[:, None, :] - q[None, :, :]) ** 2).sum(-1)).min()
            best = min(best, dd - ra_ - rb)
    return best


def facing(c, side, width=420):
    if not len(c):
        return c
    return c[c[:, 0] > c[:, 0].max() - width] if side == "right" else c[c[:, 0] < c[:, 0].min() + width]


OPTICAL = args.optical
DEPTH, MINGAP, AREA_REF = 40, GAP - 14, GAP + 27
BAND = np.arange(BASE - 396, BASE + 1, 6.0)


def top(c):
    return min(p[:, 1].min() for p in c if len(p))


def profile(c, side, BAND):
    """Per-scanline extreme x inside the x-height band, keyline-inflated, depth-capped."""
    n, g = c
    pts = [(n, KEY), (g, 0)]
    prof = np.full(len(BAND), np.nan)
    for p, r in pts:
        if not len(p):
            continue
        for k, y in enumerate(BAND):
            m = np.abs(p[:, 1] - y) < 3.5
            if not m.any():
                continue
            v = p[m, 0].max() + r if side == "right" else p[m, 0].min() - r
            if np.isnan(prof[k]):
                prof[k] = v
            else:
                prof[k] = max(prof[k], v) if side == "right" else min(prof[k], v)
    if side == "right":
        ext = np.nanmax(prof)
        return np.where(np.isnan(prof), ext - DEPTH, np.maximum(prof, ext - DEPTH))
    ext = np.nanmin(prof)
    return np.where(np.isnan(prof), ext + DEPTH, np.minimum(prof, ext + DEPTH))


XBAND = np.arange(BASE - 396, BASE + 1, 6.0)


def min_dist_pos(A, B, start, target):
    lo, hi = start - 200, start + 1500
    for _ in range(28):
        mid = (lo + hi) / 2
        if gap(A, B, mid) < target:
            lo = mid
        else:
            hi = mid
    return hi


local = [clouds(f(0)) for f in SEQ]
pos = [0.0]
for k in range(1, len(SEQ)):
    A = tuple(facing(c, "right") + np.array([pos[-1], 0]) for c in local[k - 1])
    B = tuple(facing(c, "left") for c in local[k])
    dx = min_dist_pos(A, B, pos[-1], GAP)
    if SEQ[k] is not cross_el and SEQ[k - 1] is not cross_el and OPTICAL:
        Ar = profile(tuple(c + np.array([pos[-1], 0]) for c in local[k - 1]), "right", XBAND)
        Bl = profile(local[k], "left", XBAND)
        area = Bl.mean() + dx - Ar.mean()
        floor = min_dist_pos(A, B, pos[-1], MINGAP)
        dx = max(floor, dx + OPTICAL * (AREA_REF - area))
    pos.append(round(dx, 1))

els = [f(p) for f, p in zip(SEQ, pos)]
navy = [d for e in els for d in e["navy"]]
gold = [d for e in els for d in e["gold"]]
gold_detail = [d for e in els for d in e["gold_detail"]]
navy_detail = [d for e in els for d in e["navy_detail"]]
heart_d = next(e["clip"] for e in els if "clip" in e)
st, sp = next(e["thorns"] for e in els if e["thorns"])
allp = np.vstack([np.vstack([c for c in clouds(e) if len(c)]) for e in els])
x = allp[:, 0].max() - OX + KEY

# ---------- emit ----------
pad = 50
minx, maxx = allp[:, 0].min() - KEY - pad, OX + x + pad
miny, maxy = BASE - 900, BASE + 70
vb_w, vb_h = maxx - minx, maxy - miny

out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{minx:g} {miny:g} {vb_w:g} {vb_h:g}">')
out.append("<title>CathSocial</title>")
out.append(f'<defs><clipPath id="heart"><path d="{heart_d}"/></clipPath>')
out.append("</defs>")
ink = "".join(f'<path d="{d}"/>' for d in navy)
out.append(f'<g fill="{GOLD}" stroke="{GOLD}" stroke-width="{KEY*2}" stroke-linejoin="round">{ink}</g>')
out.append(f'<g fill="{NAVY}">{ink}</g>')
out.append(f'<g clip-path="url(#heart)" fill="{GOLD}"><g fill="none" stroke="{GOLD}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round">'
           + "".join(f'<path d="{d}"/>' for d in st) + "</g>" + "".join(f'<path d="{d}"/>' for d in sp) + "</g>")
out.append(f'<g fill="{GOLD}">' + "".join(d if d.startswith("<") else f'<path d="{d}"/>' for d in gold) + "".join(d if d.startswith("<") else f'<path d="{d}"/>' for d in gold_detail) + "</g>")
out.append(f'<g fill="{NAVY}">' + "".join(d if d.startswith("<") else f'<path d="{d}"/>' for d in navy_detail) + "</g>")
out.append("</svg>")
Path(args.out).write_text("\n".join(out))
print("wrote", args.out)
