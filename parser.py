import threading
import time

import requests
import re

PHONE_TEMPLATE = r'[7|8]?[-|\s]?\(?\d{3}?\)?[-|\s]?\d{3}[-|\s]?\d{2}[-|\s]?\d{2}<'
links = [
    'https://masterdel.ru/',
    'https://repetitors.info/',
]


class PhoneParser(threading.Thread):
    """Class Phone Parser.
    Constructor takes url, regular expression template
    and list to store results phone numbers
    """

    def __init__(self, url, phone_template, out_phones, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        self.phone_template = phone_template
        self.out_phones = out_phones

    def run(self):
        """Parse phones from response and """
        try:
            response = requests.get(self.url)
            input_phones = re.findall(self.phone_template, response.text)
            self.out_phones.extend(self.normalize_phones(input_phones))
            with open('processed.txt', 'a', encoding='utf8') as file:
                file.write(f'{time.ctime(time.time())}   '
                           f'SUCCESS: {self.url} \n')
        except Exception as exc:
            with open('errors.txt', 'a', encoding='utf8') as file:
                file.write(f'{time.ctime(time.time())} \n'
                           f'{exc} \n')

    @staticmethod
    def normalize_phones(phones):
        """Convert phone number to 8KKKNNNNNNN"""
        normalized_phones = set()
        for phone in phones:
            normal_phone = re.sub(r'[^0-9]', '', phone)
            if len(normal_phone) == 7:
                normal_phone = f'8495{normal_phone}'
            if len(normal_phone) == 10:
                normal_phone = f'8{normal_phone}'
            if normal_phone[0] == '7':
                normal_phone = normal_phone.replace('7', '8', 1)
            normalized_phones.add(normal_phone)
        return normalized_phones


def time_track(func):
    def surrogate(*args, **kwargs):
        started_at = time.time()

        result = func(*args, **kwargs)

        ended_at = time.time()
        elapsed = round(ended_at - started_at, 4)
        print(f'Функция работала {elapsed} секунд(ы)')
        return result

    return surrogate


@time_track
def get_phones(urls):
    phones = []
    workers = [PhoneParser(url, PHONE_TEMPLATE, phones) for url in urls]

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()

    return phones


if __name__ == '__main__':
    get_phones(urls=links)
