from django.conf import settings


def _normalize_variants(raw_text: str, original_query: str) -> str:
    parts = []
    for piece in raw_text.replace("\n", ";").split(";"):
        cleaned = piece.strip(" \t\r\n-•.,")
        if cleaned:
            parts.append(cleaned)

    # Гарантируем, что исходный запрос всегда остается первым.
    ordered = [original_query.strip()] + parts
    unique = []
    seen = set()
    for item in ordered:
        key = item.casefold()
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return "; ".join(unique)


def expand_request_with_llm(search_query: str) -> str:
    query = (search_query or "").strip()
    if not query:
        return search_query

    try:
        from langchain_gigachat.chat_models import GigaChat
    except Exception:
        return search_query

    credentials = getattr(settings, "GIGACHAT_CREDENTIALS", "")
    if not credentials:
        return search_query

    try:
        llm = GigaChat(
            credentials=credentials,
            verify_ssl_certs=getattr(settings, "GIGACHAT_VERIFY_SSL_CERTS", False),
        )
        prompt = (
            "Ты эксперт по госзакупкам и КТРУ. "
            "Расширь пользовательский поисковый запрос синонимами и близкими формулировками, "
            "которые могут встречаться в закупках и наименованиях КТРУ. "
            "Верни только список фраз через ';' без пояснений и нумерации. "
            "Добавь 4-8 релевантных вариантов.\n\n"
            f"Исходный запрос: {query}"
        )
        response = llm.invoke(prompt)
        text = getattr(response, "content", str(response))
        expanded = _normalize_variants(str(text), query)
        return expanded if expanded else search_query
    except Exception:
        return search_query
