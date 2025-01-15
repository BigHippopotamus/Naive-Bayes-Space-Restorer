from tamil import utf8

MAP_OFFSET = 40_000

mapping = {ch: chr(i + MAP_OFFSET) for i, ch in
           enumerate(sorted(utf8.tamil_letters.copy(), reverse=True, key=lambda x: len(x)))}
inverse_mapping = {v: k for k, v in mapping.items()}


def unify(text: str):
    # Tamil characters can be represented in various ways.
    # For example, கொ can be written as க + ொ, or
    # க + ெ + ா. The below lines unify these into
    # the representation used by the OpenTamil package

    text = (text.replace('ொ', 'ொ')
            .replace('ோ', 'ோ')
            .replace('ஔ', 'ஔ')
            .replace('ௌ', 'ௌ')
            .replace('ௌ்', 'ெள்'))

    return text


def map(text: str | list[str]):
    if type(text) is str:
        text = unify(text)

        for k in mapping:
            text = text.replace(k, mapping[k])
    elif type(text) is list:
        for index, char in enumerate(text):
            text[index] = mapping[char]

    return text


def unmap(text: str | list[str]):
    if type(text) is str:
        for k in inverse_mapping:
            text = text.replace(k, inverse_mapping[k])
    elif type(text) is list:
        for index, char in enumerate(text):
            text[index] = inverse_mapping[char]

    return text


def get_mapped_uyir():
    return map(utf8.uyir_letters.copy())


def get_mapped_mei():
    return map(utf8.mei_letters.copy())
