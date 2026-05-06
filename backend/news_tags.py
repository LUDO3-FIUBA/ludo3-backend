NEWS_TAGS = [
    {"key": "deportes", "label": "Deportes", "color": "#22c55e"},
    {"key": "institucional", "label": "Institucional", "color": "#3b82f6"},
    {"key": "laboratorio", "label": "Laboratorio", "color": "#f59e0b"},
]

NEWS_TAG_CHOICES = [(tag["key"], tag["label"]) for tag in NEWS_TAGS]

NEWS_TAGS_BY_KEY = {tag["key"]: tag for tag in NEWS_TAGS}
