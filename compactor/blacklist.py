from pathlib import Path

DEFAULT_BLACKLIST: frozenset[str] = frozenset({
    "the", "a", "an", "this", "that", "those", "these",
})

PUNCT_PRIORITY: dict[str, int] = {",": 0, ";": 1, ".": 2, "!": 3, "?": 4}


def _read_word_list(path: Path) -> set[str]:
    return {
        line.strip().lower()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def _load_blacklist(blacklist_file: str | None = None) -> set[str]:
    if blacklist_file is not None:
        path = Path(blacklist_file)
        if path.is_file():
            return _read_word_list(path)
    local = Path.cwd() / "blacklist.txt"
    if local.is_file():
        return _read_word_list(local)
    return set(DEFAULT_BLACKLIST)


def _extract_trailing_punct(token: str) -> tuple[str, str]:
    if token and token[-1] in PUNCT_PRIORITY:
        return token[:-1], token[-1]
    return token, ""


def _best_punct(puncts: list[str], existing: str = "") -> str:
    candidates: list[str] = []
    if existing:
        candidates.append(existing)
    candidates.extend(puncts)
    return max(candidates, key=lambda c: PUNCT_PRIORITY.get(c, -1))


def _apply_blacklist_line(line: str, blacklist: set[str]) -> str:
    tokens = line.split()

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
                    result[-1][1] = _best_punct(pending_puncts, existing=result[-1][1])
                else:
                    result.append(["", _best_punct(pending_puncts)])
                pending_puncts = []
            result.append([word, punct])

    # Handle trailing pending puncts (removals at end of text)
    if pending_puncts and result:
        result[-1][1] = _best_punct(pending_puncts, existing=result[-1][1])

    # Phase C — reconstruct
    return " ".join(w + p for w, p in result)


def apply_blacklist(text: str, blacklist_file: str | None = None) -> str:
    if not text:
        return ""

    blacklist = _load_blacklist(blacklist_file)
    # Preserve original line structure; punctuation merging stays line-local.
    return "\n".join(_apply_blacklist_line(line, blacklist) for line in text.split("\n"))
