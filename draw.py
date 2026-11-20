#!/usr/bin/env python3
"""Paint the front page for news-image-20261120.

Friday 20 November 2026, summed up on one page: "THE WORLD TODAY",
a newspaper front page drawn with Pillow. Masthead, three lead
stories, a strip with a schematic world map next to a photo of the
summit city, six continent sections and an also-today strip -- thirty
stories in all.

The skyline photo is an AI-made illustration of Shenzhen at dusk
(hero.png, shipped in this repo). It is cropped into its panel here,
so rendering is deterministic: run this file twice and entry.png
comes out byte-identical.

Run:  python3 draw.py    (writes entry.png next to this file)
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

INK = (22, 22, 22)
GREY = (70, 70, 70)
FAINT = (96, 96, 96)
PAPER = (250, 244, 226)
RULE = (118, 108, 88)
NAVY = (28, 55, 92)
BRICK = (158, 30, 30)
TEAL = (36, 88, 118)
SEA = (210, 228, 236)
LAND = (46, 96, 124)
SEAM = (202, 192, 166)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
FONT_FILE = {
    "serif_b": "DejaVuSerif-Bold.ttf",
    "serif": "DejaVuSerif.ttf",
    "sans_b": "DejaVuSans-Bold.ttf",
    "sans": "DejaVuSans.ttf",
}
_cache = {}


def font(face, size):
    """One DejaVu face at the given size, cached."""
    key = (face, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONT_DIR + FONT_FILE[face], size)
    return _cache[key]


class Sheet:
    """The page and the small set of marks a front page needs."""

    def __init__(self):
        self.img = Image.new("RGB", (W, H), PAPER)
        self.d = ImageDraw.Draw(self.img)

    def put(self, x, y, s, face, size, color):
        self.d.text((x, y), s, font=font(face, size), fill=color)

    def block(self, x, y, s, face, size, width, leading, color=None):
        """Wrap text into lines that fit `width`; return the y below."""
        if color is None:
            color = INK
        f = font(face, size)
        lines, cur = [], ""
        for word in s.split():
            nxt = (cur + " " + word).strip()
            if self.d.textlength(nxt, font=f) <= width:
                cur = nxt
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        for ln in lines:
            self.d.text((x, y), ln, font=f, fill=color)
            y += leading
        return y

    def rule(self, x0, x1, y, color=None, width=1):
        self.d.line([(x0, y), (x1, y)], fill=color or INK, width=width)

    def frame(self, box, color=FAINT):
        self.d.rectangle(box, outline=color, width=1)

    def fill(self, box, color):
        self.d.rectangle(box, fill=color)


def fit(s, face, size, max_w, pen):
    """Largest size at or under `size` whose width fits `max_w`."""
    while size > 10:
        f = font(face, size)
        if pen.textlength(s, font=f) <= max_w:
            return f
        size -= 2
    return font(face, size)


def lead(sh, x, y, w, h, tag, tint, head, body):
    """One of the three lead stories: tag, headline, short body."""
    sh.frame((x, y, x + w, y + h))
    sh.fill((x, y, x + w, y + 3), tint)
    sh.put(x + 10, y + 12, tag, "sans_b", 12, tint)
    after = sh.block(x + 10, y + 34, head, "sans_b", 20, w - 20, 24)
    sh.block(x + 10, after + 4, body, "sans", 13, w - 20, 17, GREY)


# Schematic world map: rough landmass polygons, a red pin on each,
# and where its label sits. All coordinates are local to the strip.
MAP = [
    # North America
    ([(28, 36), (105, 28), (150, 36), (138, 58), (88, 66), (38, 54)],
     (88, 46), "N. AMERICA", (52, 70)),
    # South America
    ([(158, 56), (180, 50), (192, 62), (178, 74), (162, 68)],
     (176, 62), "S. AMERICA", (132, 78)),
    # Europe
    ([(330, 32), (372, 26), (392, 36), (372, 48), (342, 44)],
     (362, 36), "EUROPE", (256, 34)),
    # Africa
    ([(342, 50), (372, 48), (384, 64), (366, 80), (348, 68)],
     (364, 64), "AFRICA", (392, 62)),
    # Asia
    ([(420, 30), (520, 24), (560, 34), (538, 54), (460, 58), (428, 44)],
     (498, 40), "ASIA", (470, 62)),
    # Oceania
    ([(566, 62), (588, 58), (596, 68), (576, 74), (568, 70)],
     (582, 66), "OCEANIA", (540, 80)),
]


def map_panel(sh, x, y, w, h):
    """The schematic world map with one pin per continent."""
    sh.fill((x, y, x + w, y + h), SEA)
    sh.frame((x, y, x + w, y + h))
    sh.put(x + 10, y + 6, "WHERE IT HAPPENED", "sans_b", 13, NAVY)
    sh.put(x + w - 252, y + 6, "30 STORIES ON 6 CONTINENTS", "sans_b", 13,
           NAVY)
    for poly, pin, tag, at in MAP:
        pts = [(x + px, y + py) for px, py in poly]
        sh.d.polygon(pts, fill=LAND)
        dx, dy = pin
        sh.d.ellipse([x + dx - 4, y + dy - 4, x + dx + 4, y + dy + 4],
                     fill=BRICK, outline=WHITE, width=1)
        lx, ly = at
        sh.put(x + lx, y + ly, tag, "sans_b", 10, INK)


def photo_panel(sh, x, y, w, h, caption):
    """Crop hero.png into its panel, caption along the bottom."""
    here = os.path.dirname(os.path.abspath(__file__))
    photo = Image.open(os.path.join(here, "hero.png")).convert("RGB")
    pw, ph = photo.size
    band = int(pw * h / w)
    top = int(ph * 0.16)
    top = max(0, min(top, ph - band))
    photo = photo.crop((0, top, pw, top + band)).resize((w, h))
    sh.img.paste(photo, (x, y))
    sh.frame((x, y, x + w, y + h))
    sh.fill((x, y + h - 18, x + w, y + h), NAVY)
    sh.put(x + 8, y + h - 15, caption, "sans_b", 10, WHITE)


def region(sh, x, y, w, h, name, tint, stories):
    """A continent section: coloured header, then four stories."""
    sh.frame((x, y, x + w, y + h))
    sh.fill((x, y, x + w, y + 26), tint)
    sh.put(x + 10, y + 5, name, "sans_b", 14, WHITE)
    sh.put(x + w - 90, y + 5, "4 STORIES", "sans_b", 12, WHITE)
    cy = y + 34
    for pos, (head, body) in enumerate(stories):
        cy = sh.block(x + 10, cy, head, "sans_b", 13, w - 20, 14)
        cy = sh.block(x + 10, cy + 1, body, "sans", 11, w - 20, 12, GREY)
        cy += 5
        if pos < len(stories) - 1:
            sh.rule(x + 10, x + w - 10, cy - 3, SEAM)


TITLE = "THE WORLD TODAY"
DATE_LINE = "FRIDAY, 20 NOVEMBER 2026  \u2022  30 STORIES  \u2022  6 CONTINENTS"

LEADS = [
    ("SUMMIT  |  LEAD 1", BRICK,
     "Trump, Xi and Putin issue 'peace declaration'",
     "First-ever trilateral summit ends in Shenzhen; the three say a "
     "nuclear war 'cannot be won and must never be fought'."),
    ("UKRAINE  |  LEAD 2", NAVY,
     "Russia's overnight barrage batters Kyiv",
     "Missiles and drones hit three Dnipro bridges; four killed, the "
     "Qatar embassy damaged; the EU summons Russia's envoy."),
    ("WEATHER  |  LEAD 3", TEAL,
     "Cyclone Akvan makes landfall in India",
     "The storm crosses the Odisha-Andhra coast at 70-80 km/h, the "
     "third cyclone to hit India in under a month."),
]

REGIONS = [
    ("NORTH AMERICA", NAVY, [
        ("Anthropic shares soar 34% on debut",
         "The Claude maker is the first frontier AI firm to go public; "
         "its value tops $2tn on day one. (BBC)"),
        ("Pentagon puts Iran war cost at $48.3bn",
         "The tally excludes base damage as Tehran widens its Gulf "
         "attacks on shipping and bases. (Reports)"),
        ("Senate rejects Iran war-powers resolution",
         "The 51-48 vote leaves the president's war powers intact "
         "after the House passed the measure. (Reports)"),
        ("Trump posthumously pardons Pete Rose",
         "The late baseball legend is pardoned decades after his ban "
         "from the game. (Reports)"),
    ]),
    ("EUROPE", (120, 60, 18), [
        ("UK and EU agree youth mobility scheme",
         "Young people will be able to live and work across the "
         "Channel under the new deal. (BBC)"),
        ("Europe ready to join new Ukraine talks",
         "Chancellor Merz says talks including Europe will be held "
         "soon; Putin invites EU leaders to Moscow. (Reports)"),
        ("UK pledges 1,000+ drones for Ukraine",
         "The \u00a3260m package of long-range drones was announced "
         "in Berlin. (Reports)"),
        ("Bulgaria says hackers stole 62m pages",
         "Government documents were taken in a major breach, Sofia "
         "says. (Reports)"),
    ]),
    ("ASIA", (94, 42, 120), [
        ("ICJ rules Myanmar committed genocide",
         "Thursday's ruling finds Myanmar responsible for genocide "
         "against the Rohingya in its 2017 crackdown. (ICJ)"),
        ("Taiwan stocks plunge 2,200 points",
         "The index breaks below 37,000 intraday in its worst week "
         "in months. (Reports)"),
        ("Tanker hit by mine near Hormuz strait",
         "A tanker catches fire east of the strait as Houthis claim "
         "strikes on four Saudi targets. (Reports)"),
        ("Samsung names new mobile chief",
         "Won-Joon Choi takes over the Galaxy business in a senior "
         "reshuffle. (Reports)"),
    ]),
    ("AFRICA", (22, 108, 60), [
        ("Migrant boat capsizes off Senegal",
         "Dozens missing after a boat carrying about 50 people sinks "
         "off Yenne, south of Dakar. (Reuters)"),
        ("UNHCR launches global appeal to save lives",
         "Nearly 2,500 people have died or gone missing on sea routes "
         "to Europe in nine months. (PANA)"),
        ("AU condemns drone strikes in Sudan",
         "The African Union chair decries deadly attacks in Sudan and "
         "the disputed Abyei area. (PANA)"),
        ("Djibouti shipwreck toll rises to 139",
         "A further 84 people remain missing after the boat capsized, "
         "officials say. (PANA)"),
    ]),
    ("SOUTH AMERICA", (120, 86, 16), [
        ("Haiti police kill 34 in gang raid",
         "At least 34 suspected gang members are killed in a raid on "
         "the capital. (Reports)"),
        ("Bukele set to seek a third term",
         "El Salvador's president is expected to formalise his bid "
         "for another term. (Reports)"),
        ("Venezuela touts AI at COP31",
         "Caracas pitches AI as a path to cleaner oil production at "
         "the Antalya talks. (Reports)"),
        ("US backs Colombia coca spraying return",
         "Washington backs plans to resume aerial spraying despite "
         "lawmakers' concerns. (Reports)"),
    ]),
    ("OCEANIA", (126, 50, 82), [
        ("5.6-magnitude quake near New Caledonia",
         "The tremor strikes off the Pacific territory; no tsunami "
         "warning follows. (Reports)"),
        ("Cyclone Xavier track updated",
         "Fiji's weather service updates its forecasts; island "
         "warning levels hold. (RSMC Nadi)"),
        ("Van Gogh sells for $190.4m",
         "A leafy 'Blossoming Chestnut Trees' sets a big price at "
         "auction. (Reports)"),
        ("'Human' is Word of the Year",
         "Cambridge Dictionary picks 'human' as its word of 2026. "
         "(Reports)"),
    ]),
]

ALSO = ("ALSO TODAY:  COP31 draft deal drops fossil-fuel language, "
        "drawing fire in Antalya  \u2022  US sanctions Comancheros and "
        "'Ndrangheta crime groups  \u2022  Greenland security deal wins "
        "unanimous Danish approval.")
CREDITS = ("Sources, all reported 19-20 Nov 2026: AP, Reuters, AFP, "
           "BBC, WSJ, CNN, ICJ, IMD, PANA, RSMC Nadi, DFAT. Claims are "
           "labelled as claims; Thursday-evening events are those in "
           "Friday's editions.")
PHOTO_CAP = "SHENZHEN AT DUSK \u2014 THE SUMMIT CITY"


def build():
    """Compose the whole front page and return the image."""
    sh = Sheet()
    sh.d.rectangle([16, 14, W - 16, H - 14], outline=RULE, width=2)

    title_f = fit(TITLE, "serif_b", 58, W - 60, sh.d)
    title_w = sh.d.textlength(TITLE, font=title_f)
    sh.d.text(((W - title_w) / 2, 22), TITLE, font=title_f, fill=NAVY)
    date_f = font("sans_b", 17)
    date_w = sh.d.textlength(DATE_LINE, font=date_f)
    sh.d.text(((W - date_w) / 2, 94), DATE_LINE, font=date_f, fill=BRICK)
    sh.rule(28, W - 28, 120, width=2)

    lead_w, gap = 316, 12
    for slot, (tag, tint, head, body) in enumerate(LEADS):
        lead(sh, 26 + slot * (lead_w + gap), 130, lead_w, 138,
             tag, tint, head, body)

    map_panel(sh, 26, 278, 600, 94)
    photo_panel(sh, 638, 278, 360, 94, PHOTO_CAP)

    region_w, region_h = 316, 270
    for row in range(2):
        for col in range(3):
            name, tint, stories = REGIONS[row * 3 + col]
            region(sh, 26 + col * (region_w + gap),
                   382 + row * (region_h + 10), region_w, region_h,
                   name, tint, stories)

    y = 382 + 2 * region_h + 10 + 6
    y = sh.block(26, y, ALSO, "sans_b", 12, W - 52, 16)
    sh.rule(26, W - 26, y + 4, RULE)
    sh.block(26, y + 10, CREDITS, "sans", 10, W - 52, 13, FAINT)
    return sh.img


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    build().save(os.path.join(here, "entry.png"), "PNG", optimize=True)
    print("wrote entry.png")
