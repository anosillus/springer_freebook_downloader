#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# File name: test.py
# First Edit: 2020-04-11
# Last Change: 12-Apr-2020.
"""
This scrip is for test

"""
#
import pickle
import urllib.request
from collections import OrderedDict
from time import sleep

import bs4
import mechanicalsoup
from tqdm import tqdm

# from tqdm.auto import trange

# import sys

# TEST_BOOK_PAGE = 'https://link.springer.com/book/10.1007/978-1-4612-4360-1'
BASE_URL = "https://link.springer.com/"
START_URL = 'https://link.springer.com/search?facet-language="En"&facet-content-type="Book"&package=openaccess&showAll=false'
# SECOIND_URL = 'https://link.springer.com/search/page/2?package=openaccess&showAll=false&facet-language="En"&facet-content-type="Book"'
UNKNOWN_URL = 'https://link.springer.com/search/page/{}?package=openaccess&showAll=false&facet-language="En"&facet-content-type="Book"'
MAX_RANGE = 46
TITLE_SELECTOR_IN_BOOK_INFO = "#main-content > article.main-wrapper.main-wrapper--no-gradient.main-wrapper--dual-main > div > div > div.main-body__content > div > div > div:nth-child(1) > div.page-title > h1"
PDF_LINK_SELECTOR_IN_BOOK_INFO = "#main-content > article.main-wrapper.main-wrapper--no-gradient.main-wrapper--dual-main > div > div > div.cta-button-container.cta-button-container--stacked.u-pt-36 > div > div > a"
EPUB_LINK_SELECTOR_IN_BOOK_INFO = "#main-content > article.main-wrapper.main-wrapper--no-gradient.main-wrapper--dual-main > div > div > div.cta-button-container.cta-button-container--inline.cta-button-container--stacked.u-pt-36.test-download-book-separate-buttons > div:nth-child(2) > a"


FIRST_NEXT_PAGE_SELECTOR = (
    "#kb-nav--main > div.functions-bar.functions-bar-bottom > form > a"
)
NEXT_PAGE_SELECTOR = (
    "#kb-nav--main > div.functions-bar.functions-bar-bottom > form > a.next"
)


def write_history(filename, data):
    with open(filename, mode="a") as f:
        f.write(data)


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


class Scraper:
    def __init__(self, url, data_directory="./../pdfs/", sleep_time=10):
        self.start_url = url
        self.detail_page_urls = []
        self.pdf_urls = []
        self.top_page_urls = [url]
        self.data_directory = data_directory
        self.browser = mechanicalsoup.StatefulBrowser()
        self.file_detail_d = OrderedDict()
        self.sleep_time = sleep_time
        self.debug = ""
        self.count = 1

    def collect_detail_page_urls(self, url=""):
        print(len(self.detail_page_urls))

        if not url:
            url = self.start_url
        result_list_page_bs = self.get_page_information(url)
        self.detail_page_urls += self.get_detail_page_urls(result_list_page_bs)

        if self.count < 46:
            self.count += 1

            self.top_page_urls.append(UNKNOWN_URL.format(self.count))
            # if self.get_next_page_link(result_list_page_bs):
            #     next_page_url = self.get_next_page_link(result_list_page_bs)
            #     self.top_page_urls.append(next_page_url)
            self.collect_detail_page_urls(UNKNOWN_URL.format(self.count))
        #     # sys.exit()
        # else:
        #     print("Finish")
        #     print(len(self.detail_page_urls))

    def collect_pdf_file_urls(self, init_n=0, range_n=60):
        if init_n + range_n > len(self.detail_page_urls):
            max_range = len(self.detail_page_urls)

            if init_n > range_n > len(self.detail_page_urls):
                raise "Finished!"
        else:
            max_range = init_n + range_n

        for detail_page_link in tqdm(self.detail_page_urls[init_n:max_range]):
            detail_page_bs = self.get_page_information(detail_page_link)

            if detail_page_bs.select(EPUB_LINK_SELECTOR_IN_BOOK_INFO):
                name = self.get_epub_name(detail_page_bs)
                url = self.get_epub_url_link(detail_page_bs)
                self.file_detail_d.update({name: url})
            else:
                name = self.get_pdf_name(detail_page_bs)
                url = self.get_pdf_url_link(detail_page_bs)
                self.file_detail_d.update({name: url})

            write_history(
                "./../log/pdf_data_working", str(name + ", " + str(url))
            )

    def download_pdfs(self):
        for output_path, url in tqdm(
            self.file_detail_d.items(), desc="file-loop"
        ):
            sleep(self.sleep_time)
            self.download_url(url, output_path)

    def download_url(self, url, output_path):
        """download_url.

        :param url:
        https://~.pdf
        # https://link.springer.com/book/10.1007/978-1-4612-4360-1/content/pdf/10.1007%2F978-1-4612-4360-1.pdf'

        :param output_path:
        'file save target directory'
        """

        with DownloadProgressBar(
            unit="B", unit_scale=True, miniters=1, desc=url.split("/")[-1]
        ) as t:
            urllib.request.urlretrieve(
                url, filename=output_path, reporthook=t.update_to
            )

    def get_page_information(self, url):
        self.browser.open(url)
        sleep(self.sleep_time)

        return self.browser.get_current_page()

    def get_next_page_link(self, result_list_page_bs: bs4.BeautifulSoup):
        if len(self.top_page_urls == 1):
            target_css = result_list_page_bs.select(FIRST_NEXT_PAGE_SELECTOR)

            if target_css[0]["class"][0] == "next":  # Is it start case?
                return BASE_URL + target_css[0]["href"]

        else:
            try:
                target_css = result_list_page_bs.select(NEXT_PAGE_SELECTOR)
            except:
                print("Maybe Finished")

                return False

            return BASE_URL + target_css[0]["href"]

    def get_detail_page_urls(self, result_list_page_bs):
        return [
            BASE_URL + target_css["href"]
            for target_css in result_list_page_bs.select("#results-list")[
                0
            ].find_all("a", {"class": "title"})
        ]

    def get_pdf_url_link(self, detail_page_html_bs):
        return (
            BASE_URL
            + detail_page_html_bs.select(PDF_LINK_SELECTOR_IN_BOOK_INFO)[0][
                "href"
            ]
        )

    def get_epub_url_link(self, detail_page_html_bs):
        return (
            BASE_URL
            + detail_page_html_bs.select(EPUB_LINK_SELECTOR_IN_BOOK_INFO)[0][
                "href"
            ]
        )

    def get_pdf_name(self, detail_page_html_bs):
        return (
            self.data_directory
            + detail_page_html_bs.select(TITLE_SELECTOR_IN_BOOK_INFO)[
                0
            ].text.replace(" ", "_")
            + ".pdf"
        )

    def get_epub_name(self, detail_page_html_bs):
        return (
            self.data_directory
            + detail_page_html_bs.select(TITLE_SELECTOR_IN_BOOK_INFO)[
                0
            ].text.replace(" ", "_")
            + ".epub"
        )


scraper = Scraper(url=START_URL)
# scraper.collect_detail_page_urls()

# with open("./../log/detail_page_urls", "wb") as d_file_w:
# pickle.dump(scraper.detail_page_urls, d_file_w)

with open("./../log/detail_page_urls", "rb") as d_file_r:
    scraper.detail_page_urls = pickle.load(d_file_r)

scraper.collect_pdf_file_urls(init_n=0, range_n=60)

with open("./../log/pdf_page_urls", "wb") as pdf_file:
    pickle.dump(scraper.file_detail_d, pdf_file)

scraper.sleep_time = 40

scraper.downlod_pdfs()
