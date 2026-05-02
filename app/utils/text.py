ANSWER_LABELS = {
    "good": "Yaxshi",
    "bad": "Unchalik emas",
    "yes": "Ha",
    "no": "Yo‘q",
    "morning": "08:00 dan 12:00 gacha",
    "afternoon": "12:00 dan 18:00 gacha",
    "web": "Web dasturlash",
    "robotics": "Robototexnika",
    "ai": "Sun’iy intellekt",
    "design": "Grafik dizayn",
    "computer": "Kompyuter savodxonligi",
    "english": "Ingliz tili",
}


def answer_label(value: str | None) -> str:
    if value is None:
        return "-"
    return ANSWER_LABELS.get(value, value)
