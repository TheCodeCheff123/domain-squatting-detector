class DomainVariationGenerator:
    """Generate common typo-squatting and spelling variants for a domain."""

    KEYBOARD_ADJACENTS = {
        "a": "qwsz", "b": "vghn", "c": "xdfv", "d": "erfcxs",
        "e": "rdsw", "f": "rtgvcd", "g": "tyhbvf", "h": "yujnbg",
        "i": "uojk", "j": "uikmnh", "k": "iolmj", "l": "opk",
        "m": "njk", "n": "bhjm", "o": "iplk", "p": "ol",
        "q": "wa", "r": "etfd", "s": "awedxz", "t": "rygf",
        "u": "yihj", "v": "cfgb", "w": "qesa", "x": "zsdc",
        "y": "tugh", "z": "asx",
    }
    HOMOGRAPHS = {"a": "4", "e": "3", "i": "1", "l": "1", "o": "0", "s": "5"}

    def __init__(self, replacement_tlds=None):
        self.replacement_tlds = replacement_tlds or ["com", "net", "org", "io", "co"]

    def generate(self, domain: str):
        domain = domain.lower().strip().rstrip(".")
        if "." not in domain:
            return

        labels = domain.split(".")
        base = ".".join(labels[:-1])
        original_tld = labels[-1]
        seen_bases = set()
        seen_candidates = set()

        def emit_base(value: str):
            if value and value not in seen_bases:
                seen_bases.add(value)
                return value
            return None

        def emit_candidate(value: str):
            labels = value.split(".")
            valid = (
                len(value) <= 253
                and len(labels) >= 2
                and all(
                    label
                    and len(label) <= 63
                    and label[0] != "-"
                    and label[-1] != "-"
                    and all(character.isalnum() or character == "-" for character in label)
                    for label in labels
                )
            )
            if valid and value not in seen_candidates:
                seen_candidates.add(value)
                return value
            return None

        base_variants = []
        if base:
            candidate_base = emit_base(base)
            if candidate_base:
                base_variants.append(candidate_base)

            for index in range(len(base)):
                omitted = emit_base(base[:index] + base[index + 1:])
                if omitted:
                    base_variants.append(omitted)

                character = base[index]
                for adjacent in self.KEYBOARD_ADJACENTS.get(character, ""):
                    substituted = emit_base(base[:index] + adjacent + base[index + 1:])
                    if substituted:
                        base_variants.append(substituted)

                substitute = self.HOMOGRAPHS.get(character)
                if substitute:
                    changed = emit_base(base[:index] + substitute + base[index + 1:])
                    if changed:
                        base_variants.append(changed)

                if index + 1 < len(base):
                    transposed = emit_base(base[:index] + base[index + 1] + character + base[index + 2:])
                    if transposed:
                        base_variants.append(transposed)

                for extra in "abcdefghijklmnopqrstuvwxyz0123456789-":
                    inserted = emit_base(base[:index + 1] + extra + base[index + 1:])
                    if inserted:
                        base_variants.append(inserted)

        tlds = list(dict.fromkeys([original_tld, *self.replacement_tlds]))
        for tld in tlds:
            if tld:
                for variant in base_variants:
                    candidate = emit_candidate(f"{variant}.{tld}")
                    if candidate:
                        yield candidate

        for hyphenated in (base.replace(".", "-"), "-".join(base)):
            for tld in tlds:
                candidate = emit_candidate(f"{hyphenated}.{tld}")
                if candidate:
                    yield candidate
