def build_index_debug_report(payload: dict, index_id: str) -> dict:
    index_payload = payload["indices"][index_id]
    return {
        "id": index_payload["id"],
        "date": index_payload["date"],
        "features": index_payload["features"],
        "states": index_payload["states"],
        "pattern_tags": index_payload["pattern_tags"],
        "transition_tags": index_payload["transition_tags"],
        "salience": index_payload["salience"],
        "trace": index_payload["trace"],
    }


def build_market_debug_report(payload: dict) -> dict:
    return payload["market"]


def build_pair_debug_report(payload: dict, pair_id: str) -> dict:
    return payload["pairs"][pair_id]
