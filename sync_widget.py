import datetime as dt
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


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


def build_payload(config: dict) -> dict:
    widget = config.get("widget", {})
    dynamic = widget.get("dynamic", [])
    fields = validate_dynamic(dynamic)

    if not fields:
        raise ValueError("widget.dynamic is empty or invalid")

    now_utc = dt.datetime.now(dt.timezone.utc)
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

    app_id = os.getenv("DISCORD_APP_ID", "").strip() or str(discord.get("app_id", "")).strip()
    user_id = os.getenv("DISCORD_USER_ID", "").strip() or str(discord.get("user_id", "")).strip()
    identity_id_env = os.getenv("DISCORD_IDENTITY_ID", "").strip()
    identity_id = int(identity_id_env) if identity_id_env else int(discord.get("identity_id", 0))

    if not app_id or not user_id:
        raise RuntimeError("Missing Discord app/user ids")

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
