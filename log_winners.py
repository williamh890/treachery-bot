import datetime
import uuid
from typing import NamedTuple
import gspread
from google.oauth2.service_account import Credentials
import os
import json


class PlayerLog(NamedTuple):
    game_id: int
    player_name: str
    is_winner: bool
    role_type: str
    role_name: str
    date: str
    id: str


def log_winners(winners: list[str], current_roles: dict[str, dict]) -> dict:
    game_id = str(uuid.uuid4())
    game_date = datetime.datetime.now().isoformat()

    game_logs = []
    for player, role in current_roles.items():
        player_log = PlayerLog(
            game_id=game_id,
            player_name=player,
            is_winner=player in winners,
            role_type=role['types']['subtype'],
            role_name=role['name'],
            date=game_date,
            id=str(uuid.uuid4())
        )

        game_logs.append(player_log)

    upload_to_sheets(game_logs)

    return game_logs


def upload_to_sheets(game_logs):
    SPREADSHEET_NAME = "MTG Treachery Games"
    WORKSHEET_NAME = "Game Log"

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    raw_json = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]

    service_account_info = json.loads(raw_json)

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

    sheet = gc.open(SPREADSHEET_NAME)
    worksheet = sheet.worksheet(WORKSHEET_NAME)

    worksheet.append_rows(game_logs, value_input_option="USER_ENTERED")

    print(f"Appended {len(game_logs)} rows to Google Sheet.")
