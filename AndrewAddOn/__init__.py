import re
from bs4 import BeautifulSoup
from aqt import gui_hooks


def prepare(html, card, context):
    soup = BeautifulSoup(html, 'html.parser')
    spans = soup.find_all("span", "larger_font_size")
    for span in spans:
        unwrapped = span.unwrap()
    new_html = soup.prettify()

    pattern = r'([\u0F00-\u0FFF]+)'
    def replace_func(match):
        if match.group(0):
            return match[0]
        else if (matc):
            return rf'<span class="tibetan">{match.group(1)}</span>'
    new_html = re.sub(pattern, replace_func, new_html)

    print(new_html)
    return new_html

gui_hooks.ed
gui_hooks.card_will_show.append(prepare)
