# /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# File name: test.py
# First Edit: 2020-04-11
# Last Change: 13-Apr-2020.
"""
This scrip is for test

"""
#
import csv
import pickle
import urllib.request
from collections import OrderedDict
from time import sleep

import bs4
import mechanicalsoup
import pandas as pd
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


def write_history(filename, data_l):
    # with open("outfile", "w") as outfile:
    # outfile.write("\n".join(data_l))
    with open("filename", "a", newline="") as csvfile:
        fieldnames = ["name", "link"]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for name_v, link_v in data.items():
            writer.writerow({fieldnames[0]: name_v, fieldnames[1]: link_v})


def read_history(filename):
    with open(filename, "w") as outfile:
        return pd.read_csv(outfile)


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

    def collect_file_urls(self, init_n=0, max_n=0):
        names = []
        urls = []

        for detail_page_link in tqdm(self.detail_page_urls[init_n:max_n]):
            detail_page_bs = self.get_page_information(detail_page_link)

            if detail_page_bs.select(EPUB_LINK_SELECTOR_IN_BOOK_INFO):
                names.append(self.get_epub_name(detail_page_bs))
                urls.append(self.get_epub_url_link(detail_page_bs))
                # self.file_detail_d.update({names: urls})
            else:
                names.append(self.get_pdf_name(detail_page_bs))
                urls.append(self.get_pdf_url_link(detail_page_bs))
                # self.file_detail_d.update({names: urls})

        return dict(zip(names, urls))

    def download_pdfs(self, data):
        for output_path, url in tqdm(data.items(), desc="file-loop"):
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

        try:
            with DownloadProgressBar(
                unit="B", unit_scale=True, miniters=1, desc=url.split("/")[-1]
            ) as t:
                urllib.request.urlretrieve(
                    url, filename=output_path, reporthook=t.update_to
                )
        except:
            raise output_path

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
            + detail_page_html_bs.select(TITLE_SELECTOR_IN_BOOK_INFO)[0]
            .text.replace(" ", "_")
            .replace("/", "|")
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

Main_Progress = tqdm(range(320, len(scraper.detail_page_urls), 10))

for i in Main_Progress:
    print(i)

    if i + 10 > len(scraper.detail_page_urls):
        data = scraper.collect_file_urls(
            init_n=i, max_n=len(scraper.detail_page_urls)
        )
    else:
        data = scraper.collect_file_urls(init_n=i, max_n=i + 10)
    write_history("./../log/pdf_data_working.csv", data)

    scraper.download_pdfs(data)
