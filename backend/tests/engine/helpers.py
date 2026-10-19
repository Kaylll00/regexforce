from itertools import product


def all_strings(alphabet: str, max_len: int) -> list[str]:
    values = [""]
    for length in range(1, max_len + 1):
        values.extend("".join(chars) for chars in product(alphabet, repeat=length))
    return values
