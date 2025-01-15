from tamil import utf8


mapping = {ch: chr(i + 40000) for i, ch in
           enumerate(sorted(utf8.tamil_letters.copy(), reverse=True, key=lambda x: len(x)))}
inverse_mapping = {v: k for k, v in mapping.items()}


def map(text: str | list[str]):
    if type(text) == str:
        # Tamil characters can be represented in various ways.
        # For example, கொ can be written as க + ொ, or
        # க + ெ + ா. The below lines unify these
        # representations into the one used by the tamil package
        text.replace('ொ', 'ொ')
        text.replace('ோ', 'ோ')
        text.replace('ஔ', 'ஔ')
        text.replace('ௌ', 'ௌ')
        text.replace('ௌ்', 'ெள்')

        for k in mapping:
            text = text.replace(k, mapping[k])
    elif type(text) == list:
        for index, char in enumerate(text):
            text[index] = mapping[char]

    return text


def unmap(text: str | list[str]):
    if type(text) == str:
        for k in inverse_mapping:
            text = text.replace(k, inverse_mapping[k])
    elif type(text) == list:
        for index, char in enumerate(text):
            text[index] = inverse_mapping[char]

    return text


def get_mapped_uyir():
    return map(utf8.uyir_letters.copy())


def get_mapped_mei():
    return map(utf8.mei_letters.copy())