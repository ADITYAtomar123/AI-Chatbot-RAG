def detect_memory(text):

    if not text:
        return None

    text = text.lower()

    if "my name is" in text:
        name = text.split("my name is")[-1].strip()
        return ("name", name)

    if "i live in" in text:
        city = text.split("i live in")[-1].strip()
        return ("city", city)

    return None