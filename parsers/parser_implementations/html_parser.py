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
from consts import YEAR, MONTH, DAY, HEADER_MAX_LENGTH, MAX_ROW_SUM
from validator import DocumentValidator, DateValidator, HeaderLengthValidator, TotalSumValidator, ValidationStatus


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
        self.data_collection = "html data"
        self.discrepancy_collection = "html discrepancies"

        year = kwargs.get("year", YEAR)
        month = kwargs.get("month", MONTH)
        day = kwargs.get("day", DAY)

        self.header_validator = HeaderLengthValidator(
            header_max_length=kwargs.get("header_max_length", HEADER_MAX_LENGTH),
            header_tag=head_tag)
        self.date_validator = DateValidator(max_date=datetime(year, month, day), footer_tag=footer_tag)
        self.total_sum_validator = TotalSumValidator(max_sum=kwargs.get("max_row_sum", MAX_ROW_SUM),
                                                     row_container=body_tag)

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

            Thread(target=self.insert_to_mongodb, args=(page_data, self.html_document)).start()

    def insert_to_mongodb(self, data: list | object, document: BeautifulSoup):
        mongo_manager = manager_factory.get_manager("mongo")
        insert_results = mongo_manager.insert(collection_name=self.data_collection, data=data)

        if insert_results:
            inserted_ids = insert_results.inserted_ids if isinstance(data, list) else str(insert_results.inserted_id)
            len_inserted_ids = len(inserted_ids) if isinstance(data, list) else 1
            print(f"Successfully inserted: {len_inserted_ids} documents into db under {self.data_collection}")
            self.find_discrepancies(document=document, db_id=inserted_ids, mongo_manager=mongo_manager)
        else:
            print(f"Failed to insert {data} into db")

    def find_discrepancies(self, document: BeautifulSoup, db_id: str, mongo_manager):
        def find_and_insert_discrepancy_to_db():
            update_result_dict = lambda results: results[1].update({"discrepancy_type": results[0].value,
                                                                    "document_id": db_id})
            validation_results = document_validator.validate(document)

            if not validation_results[0] == ValidationStatus.VALID:
                print(f"Found discrepancies for {db_id}")
                update_result_dict(validation_results)
                insert_results = mongo_manager.insert(collection_name=self.discrepancy_collection,
                                                      data=validation_results[1])
                if insert_results:
                    inserted_id = str(insert_results.inserted_id)
                    print(f"Successfully inserted: {inserted_id} documents into db under {self.discrepancy_collection}")
                else:
                    print(f"Failed to insert {validation_results[1]} into db")
            else:
                print(f"No discrepancies found for {db_id}")

        document_validator = DocumentValidator(self.header_validator)
        find_and_insert_discrepancy_to_db()

        document_validator.strategy = self.date_validator
        find_and_insert_discrepancy_to_db()

        document_validator.strategy = self.total_sum_validator
        find_and_insert_discrepancy_to_db()

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
