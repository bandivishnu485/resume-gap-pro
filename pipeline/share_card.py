"""
Share Card Generator — Creates a 1200x628px LinkedIn-ready shareable image.
"""
from __future__ import annotations
import io

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def _score_color(score: float) -> tuple:
    """Return RGB color based on match score."""
    if score >= 70:
        return (34, 197, 94)    # Green
    elif score >= 40:
        return (249, 115, 22)   # Orange
    else:
        return (239, 68, 68)    # Red


def _gap_pill_color(idx: int) -> tuple:
    colors = [(99, 102, 241), (236, 72, 153), (245, 158, 11)]
    return colors[idx % len(colors)]


class ShareCardGenerator:
    """Generates a 1200×628px PNG share card for LinkedIn."""

    WIDTH = 1200
    HEIGHT = 628

    def generate(
        self,
        name: str,
        role_title: str,
        match_score: float,
        top_gaps: list[str],
        days_in_plan: int,
    ) -> bytes:
        """
        Create a LinkedIn OG-standard share card image.

        Returns PNG bytes.
        """
        if not HAS_PIL:
            return b""

        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Background gradient effect (manual bands)
        for y in range(self.HEIGHT):
            ratio = y / self.HEIGHT
            r = int(248 - ratio * 20)
            g = int(250 - ratio * 15)
            b = int(252 - ratio * 10)
            draw.line([(0, y), (self.WIDTH, y)], fill=(r, g, b))

        # Left accent bar
        draw.rectangle([(0, 0), (8, self.HEIGHT)], fill=(99, 102, 241))

        # Top branding bar
        draw.rectangle([(0, 0), (self.WIDTH, 80)], fill=(17, 24, 39))
        self._draw_text(draw, "🎯 Resume Gap Pro", (30, 22), size=28, color=(255, 255, 255), bold=True)
        self._draw_text(draw, "AI-Powered Career Coaching", (self.WIDTH - 320, 30), size=18, color=(156, 163, 175))

        # Score circle (left half)
        score_color = _score_color(match_score)
        cx, cy = 280, 340
        r = 130
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=(220, 220, 220), width=3)
        draw.ellipse([(cx - r + 8, cy - r + 8), (cx + r - 8, cy + r - 8)], fill=(248, 250, 252))

        # Score arc (simplified — filled sector approximation)
        arc_r = r - 10
        filled_degrees = int((match_score / 100) * 360)
        draw.arc(
            [(cx - arc_r, cy - arc_r), (cx + arc_r, cy + arc_r)],
            start=-90,
            end=-90 + filled_degrees,
            fill=score_color,
            width=18,
        )

        # Score text inside circle
        score_str = f"{int(match_score)}%"
        self._draw_centered_text(draw, score_str, cx, cy - 22, size=52, color=score_color, bold=True)
        self._draw_centered_text(draw, "Match Score", cx, cy + 28, size=18, color=(100, 116, 139))

        # Divider
        draw.line([(460, 100), (460, self.HEIGHT - 40)], fill=(220, 220, 220), width=1)

        # Right panel — candidate info
        rx = 490
        self._draw_text(draw, name or "Your Name", (rx, 105), size=38, color=(17, 24, 39), bold=True)
        self._draw_text(draw, role_title, (rx, 158), size=22, color=(99, 102, 241))

        # Gap pills
        self._draw_text(draw, "Top Gaps to Close:", (rx, 215), size=18, color=(75, 85, 99))
        py = 248
        for i, gap in enumerate(top_gaps[:3]):
            pill_color = _gap_pill_color(i)
            gap_label = gap.title()
            pw = min(len(gap_label) * 11 + 32, 250)
            draw.rounded_rectangle([(rx, py), (rx + pw, py + 38)], radius=19, fill=(*pill_color, 220))
            self._draw_text(draw, gap_label, (rx + 16, py + 9), size=16, color=(255, 255, 255))
            py += 52

        # Plan banner
        banner_y = 455
        draw.rounded_rectangle([(rx, banner_y), (rx + 640, banner_y + 56)], radius=10, fill=(16, 185, 129))
        self._draw_text(
            draw,
            f"✅  {days_in_plan}-Day Upskilling Plan Activated",
            (rx + 20, banner_y + 15),
            size=20,
            color=(255, 255, 255),
            bold=True,
        )

        # Bottom branding
        draw.rectangle([(0, self.HEIGHT - 44), (self.WIDTH, self.HEIGHT)], fill=(17, 24, 39))
        self._draw_text(
            draw,
            "Built with Resume Gap Pro  •  Your AI Career Coach",
            (30, self.HEIGHT - 30),
            size=16,
            color=(156, 163, 175),
        )
        self._draw_text(
            draw,
            "github.com/resume-gap-pro",
            (self.WIDTH - 280, self.HEIGHT - 30),
            size=15,
            color=(99, 102, 241),
        )

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    # ------------------------------------------------------------------

    def _draw_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        pos: tuple,
        size: int = 16,
        color: tuple = (0, 0, 0),
        bold: bool = False,
    ) -> None:
        font_names = ["arialbd.ttf", "arial.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"] if bold else ["arial.ttf", "C:/Windows/Fonts/arial.ttf"]
        font = None
        for fn in font_names:
            try:
                font = ImageFont.truetype(fn, size)
                break
            except Exception:
                pass
        if font is None:
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None
        draw.text(pos, text, fill=color, font=font)

    def _draw_centered_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        cx: int,
        y: int,
        size: int = 20,
        color: tuple = (0, 0, 0),
        bold: bool = False,
    ) -> None:
        font_names = ["arialbd.ttf", "arial.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"] if bold else ["arial.ttf", "C:/Windows/Fonts/arial.ttf"]
        font = None
        for fn in font_names:
            try:
                font = ImageFont.truetype(fn, size)
                break
            except Exception:
                pass
        if font is None:
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None

        if font:
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                tw = bbox[2] - bbox[0]
            except Exception:
                tw = len(text) * size // 2
        else:
            tw = len(text) * size // 2

        draw.text((cx - tw // 2, y), text, fill=color, font=font)

