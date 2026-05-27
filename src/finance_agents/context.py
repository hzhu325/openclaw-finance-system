from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_market_context(memory_dir: Path) -> dict[str, Any]:
    events_path = memory_dir / "market_events.md"
    events: list[str] = []
    if events_path.exists():
        for line in events_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                events.append(stripped[2:])

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(events_path),
        "event_count": len(events),
        "events": events,
        "staleness_note": "External browser/news automation is not connected in this local MVP.",
    }
