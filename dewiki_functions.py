from threading import Thread
import json
import re
from html2text import html2text as htt
import wikitextparser as wtp

whole = list()


def dewiki(text):
    text = wtp.parse(text).plain_text()  # wiki to plaintext
    text = htt(text)  # remove any HTML
    text = text.replace('\\n', ' ')  # replace newlines
    text = re.sub('\s+', ' ', text)  # replace excess whitespace
    return text


def analyze_chunk(text):
    try:
        if '<redirect title="' in text:  # this is not the main article
            return None
        if '(disambiguation)' in text:  # this is not an article
            return None
        else:
            title = text.split('<title>')[1].split('</title>')[0]
            title = htt(title)
            if ':' in title:  # most articles with : in them are not articles we care about
                return None
        serial = text.split('<id>')[1].split('</id>')[0]
        content = text.split(
            '</text')[0].split('<text')[1].split('>', maxsplit=1)[1]
        content = dewiki(content)
        return {'title': title.strip(), 'text': content.strip(), 'id': serial.strip()}
    except Exception as oops:
        print(oops)
        return None


def save_article(article, savedir):
    doc = analyze_chunk(article)
    if doc:
        # print('SAVING:', doc['title'])
        whole.append(doc)
        # with open(savedir + filename, 'w', encoding='utf-8') as outfile:
        #    json.dump(doc, outfile, sort_keys=True, indent=1, ensure_ascii=False)


def process_file_text(filename, savedir):
    article = ''
    with open(filename, 'r', encoding='utf-8') as infile:
        print("counting lines...")
        num_lines = sum(1 for _ in open(filename, 'r', encoding='utf-8'))
        print("total lines:", num_lines)
        for i, line in enumerate(infile):
            if '<page>' in line:
                article = ''
            elif '</page>' in line:  # end of article
                if (i % 100 == 0):
                    prttxt = '{}/{} lines ({}%)'.format(i,
                                                        num_lines, round(i/num_lines*100, 2))
                    print(prttxt)
                Thread(target=save_article, args=(article, savedir)).start()
            else:
                article += line
    with open('wikiTR.json', 'w', encoding='utf-8') as output_file:
        print("saving...")
        json.dump(whole, output_file, sort_keys=True,
                  indent=1, ensure_ascii=False)
