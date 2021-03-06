from datetime import datetime
from datetime import timezone
from os.path import getmtime
from typing import List
from typing import Optional

from gutenberg.acquire import load_etext
from gutenberg.query import get_etexts
from gutenberg.query import get_metadata as _get_metadata

from gutenberg_http import config
from gutenberg_http.parameters import parse_include
from gutenberg_http.parameters import parse_search


def get_metadata(*args, **kwargs):
    value = _get_metadata(*args, **kwargs)
    return list(value) if value else None


def db_freshness() -> Optional[str]:
    if not config.DB_DIR:
        return None

    try:
        mtime = getmtime(config.DB_DIR)
    except FileNotFoundError:
        return None

    return str(datetime.fromtimestamp(mtime, timezone.utc))


def metadata(text_id: int, include: Optional[str] = None) -> dict:
    fields = parse_include(include)

    metadata_values = {field: get_metadata(field, text_id) for field in fields}

    return metadata_values


def body(text_id: int) -> str:
    return load_etext(text_id)


def search(query: str, include: Optional[str] = None) -> List[dict]:
    fields = parse_include(include) if include else []
    conjunction = parse_search(query)

    parts = iter(get_etexts(field, value) for field, value in conjunction)
    results = set(next(parts))
    [results.intersection_update(part) for part in parts]  # type: ignore

    return [dict([('text_id', text_id)] +
                 [(field, get_metadata(field, text_id)) for field in fields])
            for text_id in results]
