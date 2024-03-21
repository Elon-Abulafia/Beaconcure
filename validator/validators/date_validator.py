import re
from datetime import datetime
from bs4.element import Tag
from bs4 import BeautifulSoup
from typing import Tuple, Dict
from validator import ValidationStatus
from validator import ValidatorStrategy


class DateValidator(ValidatorStrategy):
    def __init__(self, max_date: datetime,
                 date_regex: str = r'\d{1,2}[A-Za-z]{3}\d{4}',
                 date_format: str = "%d%b%Y",
                 footer_tag: str = "footer"):
        self.max_date: datetime = max_date
        self.date_regex: str = date_regex
        self.date_format: str = date_format
        self.footer_tag: str = footer_tag

    def validate(self, document: BeautifulSoup) -> Tuple[ValidationStatus, Dict[str, str]]:
        footer: Tag = document.find(self.footer_tag)

        if footer is None:
            return (ValidationStatus.NOT_FOUND, {"Footer Tag Not Found": self.footer_tag,
                                                 "Location": self.footer_tag})

        footer_text: str = footer.text

        if not footer_text:
            response: tuple = (ValidationStatus.NOT_PROCESSED, {"Footer Tag Empty": footer_text,
                                                                "Location": self.footer_tag})
        else:
            match = re.search(self.date_regex, footer.text)

            if match:
                date = match.group()

                try:
                    date = datetime.strptime(date, self.date_format)

                    if date > self.max_date:
                        response: tuple = (ValidationStatus.INVALID,
                                           {"Date Greater Than Maximum": date.strftime("%d-%m-%Y"),
                                            "Location": self.footer_tag,
                                            "Gotten Date": date})
                    else:
                        response: tuple = (ValidationStatus.VALID,
                                           {"Date Is Valid": footer_text,
                                            "Location": self.footer_tag})

                except ValueError:
                    response: tuple = (
                        ValidationStatus.ERROR, {"Date Not In correct format": {"Expected Format": self.date_format,
                                                                                "Actual Format": footer_text},
                                                 "Location": self.footer_tag})
            else:
                response: tuple = (ValidationStatus.INVALID, {"Footer Date Missing": footer_text,
                                                              "Location": self.footer_tag})

        return response
