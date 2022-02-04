import re
import requests
import re


def extract_tags(wrapped_tags: list) -> list:
    return [element["tag"] for element in wrapped_tags]

def clean_str(str:str) -> str:
    
    str = str.replace("\t", " ")    # clear tabs
    str = str.replace("<h2>", "\n") # set newline after headline
    str = re.sub('<.*?>', '', str)  # clear html tags
    str = re.sub(' +', ' ', str)    # clear double spaces
    str = re.sub('\n+', '\n', str)  # clear double newlines
    
    return str



def fetch_content(details_url: str) -> str:

    print(f"fetching: {details_url}", end="")

    res = requests.get(details_url)

    if not res.ok:
        return "error while fetching content"

    content_array = res.json()["content"]

    type_blacklist = ["image_gallery", "box", "video", "audio"]
    content = ""

    for line in content_array:
        if line["type"] in type_blacklist:
            continue
        elif line["type"] == "quotation":
            content += line["quotation"]["text"]
        else:
            content += line["value"]

        content += " "

    content = clean_str(content)

    print("...done")
    return content