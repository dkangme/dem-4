from app.database.urls import increment_clicks

def record_click(short_code: str) -> None:
    increment_clicks(short_code)
