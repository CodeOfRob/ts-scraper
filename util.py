import re
import requests
import yake
from telegram.telegram import TelegramService


def extract_tags(wrapped_tags: list) -> list:
    return [element["tag"] for element in wrapped_tags]


def clean_str(str:str) -> str:
    
    str = str.replace("\t", " ")    # clear tabs
    str = str.replace("<h2>", "\n") # set newline after headline
    str = re.sub('<.*?>', '', str)  # clear html tags
    str = re.sub(' +', ' ', str)    # clear double spaces
    str = re.sub('\n+', '\n', str)  # clear double newlines
    
    return str


def fetch_content(details_url: str, tg: TelegramService) -> str:

    print(f"fetching: {details_url}", end="")

    try:
        res = requests.get(details_url)
    except Exception as e:
        tg.send_msg("Error while fetching details")
        print(e)

    if not res.ok:
        return "error while fetching content"

    content_array = res.json()["content"]

    type_blacklist = ["image_gallery", "box", "video", "audio", "related"]
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


def get_keywords(text: str):
      
    language = "de"
    max_ngram_size = 1
    deduplication_thresold = 0.9
    deduplication_algo = 'seqm'
    windowSize = 1
    word_count = len(text.split())
    numOfKeywords = int(word_count*0.03)

    custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
    return custom_kw_extractor.extract_keywords(text)