from flask import current_app


def add_to_index(index: str, model: object) -> None:
    """Add the field(s) of a model specified in __searchable__ to the search index."""
    if not current_app.elasticsearch:
        return

    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, document=payload)


def remove_from_index(index: str, model: object) -> None:
    """Remove a model from the search index."""
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(
    index: str, query: str, page: int, per_page: int
) -> tuple[list[int], int]:
    """Query the search index and return a list of ids and the total number of results."""
    if not current_app.elasticsearch:
        return [], 0

    search = current_app.elasticsearch.search(
        index=index,
        query={"multi_match": {"query": query, "fields": ["*"]}},
        from_=(page - 1) * per_page,
        size=per_page,
    )
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]

    return ids, search["hits"]["total"]["value"]
