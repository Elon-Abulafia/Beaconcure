from bs4.element import Tag
from bs4 import BeautifulSoup
from typing import Tuple, Dict
from validator import ValidationStatus
from validator import ValidatorStrategy


class TotalSumValidator(ValidatorStrategy):
    def __init__(self, max_sum: int, row_container: str = "tbody"):
        self.max_sum: int = max_sum
        self.row_container = row_container

    def validate(self, document: BeautifulSoup) -> Tuple[ValidationStatus, Dict[str, str]]:
        total_row_sum: int = 0
        body: Tag = document.find(self.row_container)

        if body:
            first_row_values: list = [td.text.strip() for td in body.find('tr').find_all('td')]
        else:
            return (ValidationStatus.NOT_FOUND, {"Row Container Not Found": self.row_container,
                                                 "Location": self.row_container})

        if not first_row_values:
            return (ValidationStatus.NOT_PROCESSED, {"First Row Empty": first_row_values,
                                                     "Location": self.row_container})

        for value in first_row_values:
            try:
                total_row_sum += int(value)
            except ValueError as e:
                pass
            except Exception as e:
                return (ValidationStatus.ERROR, {"Error Details": e,
                                                 "Location": self.row_container})

        if total_row_sum > self.max_sum:
            response: tuple = (ValidationStatus.INVALID, {"First Row Total Sum Greater Than Max": {
                "Max Total": self.max_sum,
                "Row Total": total_row_sum
            },
                "Location": self.row_container})
        else:
            response: tuple = (ValidationStatus.VALID, {"First Row": first_row_values,
                                                        "Location": self.row_container})

        return response
