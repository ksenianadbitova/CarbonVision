import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def safe_load_csv(filename: str):
    """Безопасная загрузка CSV с понятной ошибкой."""
    path = DATA_DIR / filename
    try:
        if not path.exists():
            return None, f"Файл не найден: {path}"
        df = pd.read_csv(path)
        if df.empty:
            return None, f"Файл пуст: {path}"
        return df, None
    except Exception as e:
        return None, f"Ошибка чтения {filename}: {e}"


def load_locations():
    return safe_load_csv("locations.csv")


def load_biomass():
    return safe_load_csv("biomass_2019_2024.csv")


def load_baseline():
    return safe_load_csv("baseline.csv")


def load_parameters():
    df, err = safe_load_csv("parameters.csv")
    if err:
        return None, err
    params = dict(zip(df["parameter"], df["value"]))
    return params, None


def load_events():
    return safe_load_csv("events.csv")