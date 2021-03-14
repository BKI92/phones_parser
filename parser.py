import re
import threading
import time
from typing import List, Set

import requests

MAX_THREADS_LOCKER = threading.BoundedSemaphore(100)
PHONE_TEMPLATE = r'([7|8]?[-|\s]?\(?\d{3}?\)?[-|\s]?\d{3}[-|\s]?\d{2}[-|\s]?\d{2}|\d{3}[-|\s]?\d{2}[-|\s]?\d{2})\s?<'

links = [
    'https://masterdel.ru/',
    'https://repetitors.info/',

]


class PageLoader(threading.Thread):
    """Class Page Loader.
    Load html pages from given url
    """

    def __init__(self, url: str, pages: list, *args: tuple,
                 **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self.url = url
        self.pages = pages

    def get_page(self):
        return requests.get(self.url)

    def run(self) -> None:
        MAX_THREADS_LOCKER.acquire()
        try:
            response = self.get_page()
            self.pages.append(response.text)
            with open('processed.txt', 'a', encoding='utf8') as file:
                file.write(f'{time.ctime(time.time())}   '
                           f'SUCCESS: {self.url} \n')
        except (requests.exceptions.MissingSchema,
                requests.exceptions.InvalidSchema,
                requests.exceptions.InvalidURL,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                ) as exc:
            with open('errors.txt', 'a', encoding='utf8') as file:
                file.write(f'{time.ctime(time.time())} \n'
                           f'{exc} \n')
        except Exception as exc:
            with open('other_errors.txt', 'a', encoding='utf8') as file:
                file.write(f'{time.ctime(time.time())} \n'
                           f'{exc} \n')
        finally:
            MAX_THREADS_LOCKER.release()


class PageParser(threading.Thread):
    """Class Phone Parser.
    Constructor takes url, regular expression template
    and list to store results phone numbers
    """

    def __init__(self, page: str, phone_template: str, out_phones: List[str],
                 *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self.page = page
        self.phone_template = phone_template
        self.out_phones = out_phones

    def find_phones(self) -> List[str]:
        return re.findall(self.phone_template, self.page)

    def run(self) -> None:
        """Parse phones from loaded pages """
        MAX_THREADS_LOCKER.acquire()
        input_phones = self.find_phones()
        self.out_phones.extend(self.normalize_phones(input_phones))
        MAX_THREADS_LOCKER.release()

    @staticmethod
    def normalize_phones(phones: List[str]) -> Set[str]:
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


def get_pages(urls: List[str]) -> List[str]:
    """Create threads, which load pages"""
    loaded_pages = []
    loaders = [PageLoader(url, loaded_pages) for url in urls]
    for loader in loaders:
        loader.start()
    for loader in loaders:
        loader.join()

    return loaded_pages


@time_track
def get_phones(urls: List[str]) -> List[str]:
    """Create threads, which find phones from string"""
    out_phones = []
    parsers = [PageParser(page, PHONE_TEMPLATE, out_phones) for page in
               get_pages(urls)]

    for parser in parsers:
        parser.start()
    for parser in parsers:
        parser.join()

    return out_phones


if __name__ == '__main__':
    get_phones(urls=links)
