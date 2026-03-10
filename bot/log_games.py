import datetime
import pathlib
import uuid
from typing import NamedTuple
import gspread
from google.oauth2.service_account import Credentials
import os
import json


class PlayerLog(NamedTuple):
    event_id: str
    game_id: int
    player_name: str
    is_winner: bool
    role_type: str
    role_name: str
    game_start: str
    game_end: str
    note: str


class RerollLog(NamedTuple):
    player_name: str
    role_type: str
    role_name: str
    date: str
    id: str


def log_game(winners: list[str], current_roles: dict[str, dict], start_time: datetime.datetime, notes: dict) -> dict:
    if notes is None:
        notes = {}

    game_id = str(uuid.uuid4())
    game_end = datetime.datetime.now().isoformat()

    if start_time:
        start_time = start_time.isoformat()
    else:
        start_time = 'NULL'

    game_logs = []
    for player, role in current_roles.items():
        player_log = PlayerLog(
            event_id=str(uuid.uuid4()),
            game_id=game_id,
            player_name=player,
            is_winner=player in winners,
            role_type=role['types']['subtype'],
            role_name=role['name'],
            game_start=start_time,
            game_end=game_end,
            note=notes.get(player, 'NULL'),
        )

        game_logs.append(player_log)

    upload_to_sheets(game_logs)

    return game_logs


def log_reroll(role, player_name):
    reroll_id = str(uuid.uuid4())
    reroll_date = datetime.datetime.now().isoformat()

    reroll = [
            RerollLog(
                player_name=player_name,
                role_type=role['types']['subtype'],
                role_name=role['name'],
                date=reroll_date,
                id=reroll_id,
                )
            ]

    upload_reroll(reroll)

    return reroll


def upload_to_sheets(game_logs):
    gc = _login_to_sheet()

    SPREADSHEET_NAME = "MTG Treachery Games"
    WORKSHEET_NAME = "Game Log"

    sheet = gc.open(SPREADSHEET_NAME)
    worksheet = sheet.worksheet(WORKSHEET_NAME)
    print(game_logs)
    worksheet.append_rows(game_logs, value_input_option="USER_ENTERED")

    print(f"Appended {len(game_logs)} rows to Google Sheet.")


def upload_reroll(reroll_log: list[RerollLog]) -> None:
    SPREADSHEET_NAME = "MTG Treachery Games"
    WORKSHEET_NAME = "Reroll Log"

    gc = _login_to_sheet()
    sheet = gc.open(SPREADSHEET_NAME)
    worksheet = sheet.worksheet(WORKSHEET_NAME)
    print(reroll_log)
    worksheet.append_rows(reroll_log, value_input_option="USER_ENTERED")

    print(f"Appended {len(reroll_log)} rows to Google Sheet.")


def _login_to_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    raw_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", default=None)
    if raw_json:
        service_account_info = json.loads(raw_json)
    else:
        with (pathlib.Path(__file__).parent / 'creds.json').open() as f:
            service_account_info = json.load(f)

    # Fix escaped newlines (common in env vars)
    service_account_info["private_key"] = (
        service_account_info["private_key"]
        .replace("\\n", "\n")
    )

    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes=scopes,
    )

    gc = gspread.authorize(credentials)

    return gc
