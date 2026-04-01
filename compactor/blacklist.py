from pathlib import Path

DEFAULT_BLACKLIST: frozenset[str] = frozenset({
    "the", "a", "an", "this", "that", "those", "these",
})

PUNCT_PRIORITY: dict[str, int] = {",": 0, ";": 1, ".": 2, "!": 3, "?": 4}


def _load_blacklist(blacklist_file: str | None = None) -> set[str]:
    if blacklist_file is not None:
        path = Path(blacklist_file)
        if path.is_file():
            return {
                line.strip().lower()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            }
    local = Path.cwd() / "blacklist.txt"
    if local.is_file():
        return {
            line.strip().lower()
            for line in local.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
    return set(DEFAULT_BLACKLIST)


def _extract_trailing_punct(token: str) -> tuple[str, str]:
    if token and token[-1] in PUNCT_PRIORITY:
        return token[:-1], token[-1]
    return token, ""


def apply_blacklist(text: str, blacklist_file: str | None = None) -> str:
    if not text:
        return ""
    blacklist = _load_blacklist(blacklist_file)
    tokens = text.split()

    # Phase A — classify tokens
    items: list[tuple[str, str, bool]] = []
    for token in tokens:
        word, punct = _extract_trailing_punct(token)
        is_kept = word.lower() not in blacklist or word == ""
        items.append((word, punct, is_kept))

    # Phase B — build result with punctuation merging
    result: list[list[str]] = []  # [[word, punct], ...]
    pending_puncts: list[str] = []

    for word, punct, kept in items:
        if not kept:
            if punct:
                pending_puncts.append(punct)
        else:
            if pending_puncts:
                if result:
                    prev_punct = result[-1][1]
                    all_puncts = []
                    if prev_punct:
                        all_puncts.append(prev_punct)
                    all_puncts.extend(pending_puncts)
                    best = max(all_puncts, key=lambda c: PUNCT_PRIORITY.get(c, -1))
                    result[-1][1] = best
                else:
                    best = max(pending_puncts, key=lambda c: PUNCT_PRIORITY.get(c, -1))
                    result.append(["", best])
                pending_puncts = []
            result.append([word, punct])

    # Handle trailing pending puncts (removals at end of text)
    if pending_puncts and result:
        prev_punct = result[-1][1]
        all_puncts = []
        if prev_punct:
            all_puncts.append(prev_punct)
        all_puncts.extend(pending_puncts)
        best = max(all_puncts, key=lambda c: PUNCT_PRIORITY.get(c, -1))
        result[-1][1] = best

    # Phase C — reconstruct
    return " ".join(w + p for w, p in result)
