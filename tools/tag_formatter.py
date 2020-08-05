from nltk.stem import WordNetLemmatizer

TAG_OVERRIDES = {
    "flashbang": "stun-grenade",
    "flashbangs": "stun-grenade",
    "taze": "tase",
    "tazes": "tase",
    "tazer": "taser",
    "tazers": "taser",
    "kneck": "neck",
    "knee-on-kneck": "knee-on-neck",
    "bicycle": "bike",
    "beanbag": "bean-bag",
    "beanbags": "bean-bag",
    "shot": "shoot",
    "kneel": "knee",
    "pepper-bullet": "pepper-ball",
    "protestor": "protester",
    "real-bullet": "live-round",
}

WNL = WordNetLemmatizer()


def read_tag_file(tag_path):
    all_tags = set()
    with open(tag_path, "r") as tag_file:
        for line in tag_file.readlines():
            if line.startswith("```") or line.startswith("##") or len(line.strip()) == 0:
                continue

            all_tags.add(format_tag(WNL, TAG_OVERRIDES, line.strip()))

    return all_tags


def format_tags(wnl, all_tags, tag_overrides, tags):
    new_tags = []
    for tag in tags:
        if tag.strip() == "":
            continue
        new_tag = format_tag(wnl, tag_overrides, tag)
        if new_tag not in all_tags:
            raise ValueError(
                f"Unsupported tag: {tag}, formatted as {new_tag}. Please check against possible tags or add a new tag."
            )
        new_tags.append(new_tag)
    return ", ".join(new_tags)


def format_tag(wnl, tag_overrides, tag):
    tag_words = tag.strip().replace(".", "").split("-")
    new_tag_words = []

    for tag_word in tag_words:
        new_tag_words.append(wnl.lemmatize(tag_word))

    output_tag = "-".join(new_tag_words)

    if output_tag in tag_overrides:
        return tag_overrides[output_tag]

    return output_tag


if __name__ == "__main__":
    all_tags = read_tag_file(possible_tags_path)
