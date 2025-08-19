import re

def normalize_text(text: str) -> str:
    """Normalize text for comparison by lowercasing, stripping, and handling Uzbek characters."""
    if not text:
        return ""

    text = text.lower().strip()
    # Simple replacements for Uzbek specific characters for consistency
    replacements = {
        'ʻ': "'", '`': "'", 'ʼ': "'",
        'ғ': 'gʻ',
        'ў': 'oʻ',
        'ҳ': 'h',
        'қ': 'q',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove all punctuation except apostrophe
    text = re.sub(r"[^\w\s']", '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def semantic_similarity(text1: str, text2: str) -> float:
    """Calculate a simple similarity score based on Levenshtein distance."""
    if not text1 or not text2:
        return 0.0

    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)

    distance = levenshtein_distance(norm1, norm2)
    max_len = max(len(norm1), len(norm2))
    if max_len == 0:
        return 1.0  # Both are empty strings

    similarity = 1 - (distance / max_len)
    return similarity
