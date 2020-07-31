import os

from nltk.stem import WordNetLemmatizer

src_dir = os.path.relpath(os.path.dirname(__file__) or ".")
possible_tags_path = os.path.join(src_dir, "..", "docs/possible_tags.md")

TAG_OVERRIDES = {
    "flashbang": "stun-grenade",
    "flashbangs": "stun-grenade",
    "taze": "tase",
    "tazes": "tase",
    "tazer": "taser",
    "tazers": "taser",
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


def format_tag(wnl, tag_overrides, tag):
    tag_words = tag.split("-")
    new_tag_words = []
    for tag_word in tag_words:
        if tag_word in tag_overrides:
            new_tag_words.append(tag_overrides[tag_word])
            continue

        new_tag_words.append(wnl.lemmatize(tag_word))

    output_tag = "-".join(new_tag_words)

    return output_tag


if __name__ == "__main__":
    all_tags = read_tag_file(possible_tags_path)
