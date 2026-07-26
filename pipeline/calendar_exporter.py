"""
Calendar Exporter — Converts study roadmap to RFC-5545 .ics calendar file.
"""
from __future__ import annotations
import re
import uuid
from datetime import date, datetime, timedelta

try:
    from icalendar import Calendar, Event, vText
    HAS_ICAL = True
except ImportError:
    HAS_ICAL = False


class CalendarExporter:
    """Generates a downloadable .ics calendar from a roadmap markdown string."""

    def generate_ics(
        self,
        roadmap_text: str,
        start_date: date,
        daily_hours: int = 2,
    ) -> bytes:
        """
        Parse roadmap markdown and produce an RFC-5545 .ics file.

        Args:
            roadmap_text: Markdown string of the roadmap.
            start_date: The date to start scheduling from.
            daily_hours: Study hours per day (used for event duration).

        Returns:
            .ics file as bytes.
        """
        if not HAS_ICAL:
            return b"# icalendar library not installed. Run: pip install icalendar"

        cal = Calendar()
        cal.add("prodid", "-//Resume Gap Pro//Study Roadmap//EN")
        cal.add("version", "2.0")
        cal.add("calscale", "GREGORIAN")
        cal.add("method", "PUBLISH")
        cal.add("x-wr-calname", "Study Roadmap — Resume Gap Pro")
        cal.add("x-wr-timezone", "Asia/Kolkata")

        tasks = self._parse_roadmap_tasks(roadmap_text)

        if not tasks:
            # Fallback: one generic event per day for 30 days
            tasks = [
                {"day_offset": i, "title": f"Study Session — Day {i+1}", "description": "Study session from your roadmap.", "is_milestone": False}
                for i in range(30)
            ]

        for task in tasks:
            event_date = start_date + timedelta(days=task["day_offset"])
            event = Event()
            event.add("uid", str(uuid.uuid4()) + "@resumegappro")
            event.add("summary", vText(task["title"]))
            event.add("description", vText(task.get("description", "")))

            if task.get("is_milestone"):
                # All-day event for milestones
                event.add("dtstart", event_date)
                event.add("dtend", event_date + timedelta(days=1))
            else:
                # Timed event: 7 AM start
                start_dt = datetime(
                    event_date.year, event_date.month, event_date.day, 7, 0, 0
                )
                event.add("dtstart", start_dt)
                event.add("dtend", start_dt + timedelta(hours=daily_hours))
                event.add("categories", ["Study"])

            cal.add_component(event)

        return cal.to_ical()

    # ------------------------------------------------------------------

    def _parse_roadmap_tasks(self, text: str) -> list[dict]:
        """
        Extract daily tasks and milestones from roadmap markdown.

        Recognises:
        - ## Week N: ... → weekly milestone
        - ### Day N: ... → daily task
        - - ... bullet points → sub-tasks (aggregated under current day)
        """
        tasks = []
        current_week = 0
        current_day_offset = 0
        current_day_title = ""
        current_day_bullets: list[str] = []

        def flush_day():
            nonlocal current_day_title, current_day_bullets
            if current_day_title:
                tasks.append({
                    "day_offset": current_day_offset,
                    "title": current_day_title,
                    "description": "\n".join(current_day_bullets),
                    "is_milestone": False,
                })
                current_day_title = ""
                current_day_bullets = []

        for line in text.split("\n"):
            stripped = line.strip()

            # Week header → milestone
            week_match = re.match(r'^#{1,2}\s+Week\s+(\d+)[:\s]*(.*)', stripped, re.I)
            if week_match:
                flush_day()
                current_week = int(week_match.group(1))
                week_title = week_match.group(2).strip() or f"Week {current_week}"
                day_offset = (current_week - 1) * 7
                tasks.append({
                    "day_offset": day_offset,
                    "title": f"🏁 Milestone: {week_title}",
                    "description": f"Week {current_week} starts. Review progress and plan the week.",
                    "is_milestone": True,
                })
                current_day_offset = day_offset
                continue

            # Day header
            day_match = re.match(r'^#{2,4}\s+Day\s+(\d+)[:\s]*(.*)', stripped, re.I)
            if day_match:
                flush_day()
                day_num = int(day_match.group(1))
                day_topic = day_match.group(2).strip() or f"Day {day_num}"
                current_day_offset = (current_week - 1) * 7 + (day_num - 1)
                current_day_title = f"📚 Day {day_num}: {day_topic}"
                continue

            # Mon-Sun pattern
            dow_match = re.match(r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*[:\s–-]+(.*)', stripped, re.I)
            if dow_match:
                flush_day()
                dow = dow_match.group(1)
                topic = dow_match.group(2).strip()
                dow_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
                base = (current_week - 1) * 7
                current_day_offset = base + dow_map.get(dow[:3].capitalize(), 0)
                current_day_title = f"📅 {dow}: {topic}"
                continue

            # Bullet point
            bullet_match = re.match(r'^[-*•]\s+(.*)', stripped)
            if bullet_match and current_day_title:
                current_day_bullets.append(f"• {bullet_match.group(1)}")

        flush_day()
        return tasks
