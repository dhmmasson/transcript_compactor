import string
from pathlib import Path

DEFAULT_BLACKLIST: frozenset[str] = frozenset({
    "the", "a", "an", "of", "to", "and", "in", "is", "it", "that",
    "for", "on", "with", "as", "at", "by", "from", "be", "are", "was", "were",
})


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


def apply_blacklist(text: str, blacklist_file: str | None = None) -> str:
    if not text:
        return ""
    blacklist = _load_blacklist(blacklist_file)
    tokens = text.split()
    kept = []
    for token in tokens:
        bare = token.strip(string.punctuation).lower()
        if bare not in blacklist:
            kept.append(token)
    return " ".join(kept)
