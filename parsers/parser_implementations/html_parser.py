import os
import re
from glob import glob
from typing import Any
from threading import Thread
from datetime import datetime
from data_layer import manager_factory
from bs4.element import Tag
from bs4 import BeautifulSoup, element
from parsers import Parser, register_parser


@register_parser("html")
class HTMLParser(Parser):
    def __init__(self,
                 *args,
                 id_tag: str = "id",
                 title_tag: str = "title",
                 head_tag: str = "head",
                 body_tag: str = "body",
                 footer_tag: str = "footer",
                 extract_country_and_date_from_footer: bool = False,
                 country_date_regex: str | None = None,
                 date_format: str | None = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.id_tag = id_tag
        self.title_tag = title_tag
        self.head_tag = head_tag
        self.body_tag = body_tag
        self.footer_tag = footer_tag
        self.extract_country_and_date_from_footer = extract_country_and_date_from_footer
        self.country_date_regex = country_date_regex
        self.date_format = date_format
        self.html_document = None

        self.collection_name = kwargs.get("collection_name", "html data")
        self.db_name = kwargs.get("db_name", "0")

    def parse(self, dir_path: str):
        """Parses all the files given from within a given folder of html files and sends the parsed results to MongoDB.

        Args:
            dir_path: A path to a directory containing .html files.

        """

        files = glob(os.path.join(dir_path, "*.html"))

        for file_name in files:
            page_data = {}

            with open(file_name, 'r') as f:
                self.html_document = BeautifulSoup(f, "html.parser")

            page_data["document id"] = self.extract_field(self.id_tag, get_expression='id')
            page_data["title"] = self.extract_field(self.title_tag, extract_text=True)
            page_data["header"] = str(self.extract_field(self.head_tag))
            page_data["body"] = str(self.extract_field(self.body_tag))

            footer = self.extract_field(self.footer_tag)
            page_data["footer"] = str(footer)

            creation_date, country = self.extract_date_and_country(footer)
            page_data["creation date"] = creation_date
            page_data["country"] = country

            Thread(target=self.insert_to_mongodb, args=(page_data,)).start()

    def insert_to_mongodb(self, data: list | object):
        mongo_manager = manager_factory.get_manager("mongo", db_name=self.db_name)

        if mongo_manager.insert(collection_name=self.collection_name, data=data):
            print(f"Successfully inserted: {data} into db")
        else:
            print(f"Failed to insert {data} into db")

    def extract_field(self, tag: str,
                      get_expression: str = None,
                      extract_text: bool = False) -> Tag | str | Any:
        """A generic function that uses BeautifulSoup4 abilities to get different parts of a html element.

        Args:
            tag: What tag to search for, e.g. 'head'.
            get_expression: If you should try to extract information from within the tag itself, e.g. for: "<head id=1>"
                'id' should be passed if it is to be extracted.
            extract_text: If the text within the tag is to be extracted, e.g. "<p>extract me</p>" True is to be passed
                if the contents of p are desired.

        Returns:
            Either the tag itself if no other extra parameters were passed, str of the content of a tag if extract_text
            was passed, and whatever is the type of the extracted value gotten from .get if get_expression was passed.
        """

        try:
            result = self.html_document.find(tag)

            if get_expression:
                result = result.get(get_expression)

            if extract_text:
                result = result.text
        except Exception:
            result = None

        return result

    def extract_date_and_country(self, footer: element.Tag) -> tuple:
        """A function to extract the creation date and country of a html document. Assumes the data is located inside
        the footer element.
        Uses the self.country_date_regex expression in order to extract the date (according to the self.date_format)
        and country.

        Args:
            footer: The footer element tag, should contain within it's the text the date and country.

        Returns:
            A tuple consisting of the (country, creation_date)

        """

        try:
            match = re.search(self.country_date_regex, footer.text)
        except Exception:
            match = None

        if match:
            creation_date_str = match.group(1)
            country = match.group(2)

            try:
                creation_date = datetime.strptime(creation_date_str, self.date_format).strftime("%d-%m-%Y")
            except ValueError:
                creation_date = None
        else:
            country = None
            creation_date = None

        return country, creation_date
