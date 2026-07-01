import datetime as dt
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_dynamic(dynamic: list) -> list:
    validated: list = []
    for entry in dynamic:
        if not isinstance(entry, dict):
            continue

        value_type = int(entry.get("type", 1))
        name = str(entry.get("name", "")).strip()
        value = entry.get("value", "")

        if not name:
            continue

        if value_type == 3:
            if not isinstance(value, dict) or not str(value.get("url", "")).strip():
                continue
            validated.append({"type": 3, "name": name, "value": {"url": str(value["url"]).strip()}})
        elif value_type == 2:
            try:
                validated.append({"type": 2, "name": name, "value": int(value)})
            except Exception:
                continue
        else:
            validated.append({"type": 1, "name": name, "value": str(value)})

    return validated


def parse_hhmm(value: str, fallback_hour: int, fallback_minute: int) -> tuple[int, int]:
    try:
        hour_text, minute_text = str(value).strip().split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return hour, minute
    except Exception:
        pass
    return fallback_hour, fallback_minute


def resolve_timezone(name: str) -> dt.tzinfo:
    try:
        return ZoneInfo(name)
    except Exception:
        return dt.timezone.utc


def find_next_shift_start(
    now_local: dt.datetime,
    weekdays: set[int],
    start_hour: int,
    start_minute: int,
) -> dt.datetime:
    for offset in range(0, 8):
        candidate_date = now_local.date() + dt.timedelta(days=offset)
        candidate_start = dt.datetime(
            year=candidate_date.year,
            month=candidate_date.month,
            day=candidate_date.day,
            hour=start_hour,
            minute=start_minute,
            tzinfo=now_local.tzinfo,
        )

        if candidate_start.weekday() not in weekdays:
            continue

        if candidate_start > now_local:
            return candidate_start

    return now_local


def build_runtime_tokens(config: dict, now_utc: dt.datetime) -> dict[str, str | int]:
    widget = config.get("widget", {})
    tokens: dict[str, str | int] = {
        "unix_now": int(now_utc.timestamp()),
        "now_utc_iso": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    work = widget.get("work_schedule", {})
    if not isinstance(work, dict):
        return tokens

    timezone_name = str(work.get("timezone", "Europe/London")).strip() or "Europe/London"
    tz = resolve_timezone(timezone_name)
    now_local = now_utc.astimezone(tz)

    configured_days = work.get("weekdays", [0, 1, 2, 3, 4])
    weekdays = {day for day in configured_days if isinstance(day, int) and 0 <= day <= 6}
    if not weekdays:
        weekdays = {0, 1, 2, 3, 4}

    start_hour, start_minute = parse_hhmm(str(work.get("start", "08:00")), 8, 0)
    end_hour, end_minute = parse_hhmm(str(work.get("end", "18:00")), 18, 0)

    bar_length = int(work.get("progress_bar_length", 12) or 12)
    if bar_length < 5:
        bar_length = 5
    if bar_length > 30:
        bar_length = 30

    fill_char = str(work.get("progress_fill_char", "#"))[:1] or "#"
    empty_char = str(work.get("progress_empty_char", "-"))[:1] or "-"

    today_start = now_local.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    today_end = now_local.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    if today_end <= today_start:
        today_end = today_end + dt.timedelta(days=1)

    is_workday = now_local.weekday() in weekdays
    next_shift_start = find_next_shift_start(now_local, weekdays, start_hour, start_minute)
    next_shift_end = next_shift_start.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    if next_shift_end <= next_shift_start:
        next_shift_end = next_shift_end + dt.timedelta(days=1)

    active_start = today_start if is_workday else next_shift_start
    active_end = today_end if is_workday else next_shift_end

    if not is_workday:
        progress_fraction = 0.0
        status = "Off shift"
    elif now_local < today_start:
        progress_fraction = 0.0
        status = "Before shift"
    elif now_local >= today_end:
        progress_fraction = 1.0
        status = "After shift"
    else:
        total_seconds = max((today_end - today_start).total_seconds(), 1.0)
        elapsed_seconds = max((now_local - today_start).total_seconds(), 0.0)
        progress_fraction = min(max(elapsed_seconds / total_seconds, 0.0), 1.0)
        status = "At work"

    percent = int(round(progress_fraction * 100))
    filled = int(round(progress_fraction * bar_length))
    filled = min(max(filled, 0), bar_length)
    bar = (fill_char * filled) + (empty_char * (bar_length - filled))

    tokens.update(
        {
            "work_timezone": timezone_name,
            "work_status": status,
            "work_progress_percent": percent,
            "progress_current_value": percent,
            "progress_max_value": 100,
            "work_progress_bar": bar,
            "work_progress_text": f"{bar} {percent}%",
            "work_unix_start": int(active_start.timestamp()),
            "work_unix_end": int(active_end.timestamp()),
            "work_unix_next_start": int(next_shift_start.timestamp()),
            "work_unix_next_end": int(next_shift_end.timestamp()),
            "work_local_now": now_local.strftime("%Y-%m-%d %H:%M"),
        }
    )

    return tokens


def apply_runtime_tokens(fields: list, tokens: dict[str, str | int]) -> list:
    updated: list = []

    for field in fields:
        if not isinstance(field, dict):
            continue

        next_field = dict(field)
        name = str(next_field.get("name", "")).strip()
        field_type = int(next_field.get("type", 1))

        if field_type == 2 and name in tokens:
            try:
                next_field["value"] = int(tokens[name])
            except Exception:
                pass
            updated.append(next_field)
            continue

        if field_type == 1:
            if name in tokens:
                next_field["value"] = str(tokens[name])
            else:
                value = str(next_field.get("value", ""))
                for token_name, token_value in tokens.items():
                    value = value.replace(f"{{{{{token_name}}}}}", str(token_value))
                next_field["value"] = value

        updated.append(next_field)

    return updated


def build_payload(config: dict) -> dict:
    widget = config.get("widget", {})
    dynamic = widget.get("dynamic", [])
    fields = validate_dynamic(dynamic)

    if not fields:
        raise ValueError("widget.dynamic is empty or invalid")

    now_utc = dt.datetime.now(dt.timezone.utc)
    tokens = build_runtime_tokens(config, now_utc)
    fields = apply_runtime_tokens(fields, tokens)
    sync_label = str(widget.get("sync_timezone_label", "UTC")).strip() or "UTC"
    fields.append(
        {
            "type": 1,
            "name": "last_sync",
            "value": now_utc.strftime("%Y-%m-%d %H:%M") + f" {sync_label}",
        }
    )

    return {
        "username": str(widget.get("display_name", "Custom Widget")),
        "data": {
            "dynamic": fields,
        },
    }


def patch_discord_widget(config: dict, payload: dict) -> tuple[bool, int, str]:
    discord = config.get("discord", {})

    app_id_env = str(discord.get("app_id_env", "DISCORD_APP_ID")).strip() or "DISCORD_APP_ID"
    user_id_env = str(discord.get("user_id_env", "DISCORD_USER_ID")).strip() or "DISCORD_USER_ID"

    app_id = os.getenv(app_id_env, "").strip() or str(discord.get("app_id", "")).strip()
    user_id = os.getenv(user_id_env, "").strip() or str(discord.get("user_id", "")).strip()
    identity_id_env = os.getenv("DISCORD_IDENTITY_ID", "").strip()
    identity_id = int(identity_id_env) if identity_id_env else int(discord.get("identity_id", 0))

    if not app_id or not user_id:
        raise RuntimeError(
            f"Missing Discord app/user ids in env vars {app_id_env}/{user_id_env} and config values"
        )

    token_env = str(discord.get("bot_token_env", "DISCORD_BOT_TOKEN")).strip()
    bot_token = os.getenv(token_env, "").strip()
    if not bot_token:
        raise RuntimeError(f"Missing bot token in env var {token_env}")

    url = f"https://discord.com/api/v9/applications/{app_id}/users/{user_id}/identities/{identity_id}/profile"
    request = urllib.request.Request(
        url=url,
        method="PATCH",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bot {bot_token}",
            "User-Agent": "DiscordBot (https://github.com/discord/discord-api-docs, 1.0.0)",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8", errors="replace")
            return 200 <= response.status < 300, response.status, body
    except urllib.error.HTTPError as http_error:
        body = http_error.read().decode("utf-8", errors="replace") if http_error.fp else ""
        return False, http_error.code, body
    except Exception as error:
        return False, 0, str(error)


def main() -> int:
    base_dir = Path(__file__).resolve().parent
    config_name = os.getenv("CONFIG_PATH", "config.example.json")
    config_path = Path(config_name)
    if not config_path.is_absolute():
        config_path = base_dir / config_name

    if not config_path.exists():
        print(f"Missing config file: {config_path}")
        return 1

    config = read_json(config_path)
    payload = build_payload(config)
    success, status, body = patch_discord_widget(config, payload)

    if success:
        print(f"Widget sync OK status={status} fields={len(payload['data']['dynamic'])}")
        return 0

    print(f"Widget sync failed status={status} body={body}")
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted")
        raise SystemExit(130)
