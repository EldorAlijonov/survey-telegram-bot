from math import ceil


def pages_count(total: int, page_size: int) -> int:
    return max(1, ceil(total / page_size))


def clamp_page(page: int, total: int, page_size: int) -> int:
    return max(0, min(page, pages_count(total, page_size) - 1))


def offset_for_page(page: int, page_size: int) -> int:
    return page * page_size
