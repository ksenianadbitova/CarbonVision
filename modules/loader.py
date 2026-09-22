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
    """Загрузка участков из areas.csv."""
    df, err = safe_load_csv("areas.csv")
    if err:
        return None, err

    required = ["aoi_id", "name", "region", "area_ha",
                "bbox_west", "bbox_south", "bbox_east", "bbox_north"]
    for col in required:
        if col not in df.columns:
            return None, f"В areas.csv нет обязательной колонки: {col}"

    # Проверяем, что все координаты числовые
    for col in ["area_ha", "bbox_west", "bbox_south", "bbox_east", "bbox_north"]:
        try:
            df[col] = pd.to_numeric(df[col], errors="raise")
        except Exception:
            return None, f"Колонка {col} содержит нечисловые значения"

    # Считаем центр bbox — для отображения на карте
    df["lat"] = (df["bbox_south"] + df["bbox_north"]) / 2
    df["lon"] = (df["bbox_west"] + df["bbox_east"]) / 2

    return df, None


def load_baseline():
    return safe_load_csv("baseline.csv")


def load_parameters():
    df, err = safe_load_csv("parameters.csv")
    if err:
        return None, err
    try:
        params = dict(zip(df["parameter"], df["value"]))
    except Exception as e:
        return None, f"Не удалось собрать параметры: {e}"
    return params, None


def load_events():
    return safe_load_csv("events.csv")
