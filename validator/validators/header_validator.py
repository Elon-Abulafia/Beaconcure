from bs4.element import Tag
from bs4 import BeautifulSoup
from typing import Tuple, Dict
from validator import ValidationStatus
from validator import ValidatorStrategy


class HeaderLengthValidator(ValidatorStrategy):
    def __init__(self, header_max_length: int, header_tag: str = "head"):
        self.header_max_length: int = header_max_length
        self.header_tag: str = header_tag

    def validate(self, document: BeautifulSoup) -> Tuple[ValidationStatus, Dict[str, str]]:
        header: Tag = document.find(self.header_tag)

        if header is None:
            return (ValidationStatus.NOT_FOUND, {"Header Tag Not Found": self.header_tag,
                                                 "Location": self.header_tag})

        try:
            header_content: str = ""
            if self.header_tag == "thead":
                for th in header.find_all('th'):
                    header_content += th.text
            else:
                header_content: str = header.text
        except Exception as e:
            response: tuple = (ValidationStatus.ERROR, {"Error Details": e,
                                                        "Location": self.header_tag})
        else:
            if len(header_content) == 0:
                response: tuple = (ValidationStatus.NOT_PROCESSED, {"Header Tag Empty": header_content,
                                                                    "Location": self.header_tag})
            elif len(header_content) > self.header_max_length:
                response: tuple = (ValidationStatus.INVALID, {"header": header_content,
                                                              "Location": self.header_tag,
                                                              "Details": f"Header content too long",
                                                              "Max Length": self.header_max_length,
                                                              "Current Length": len(header_content)})
            else:
                response: tuple = (ValidationStatus.VALID, {"header": header_content,
                                                            "Location": self.header_tag})

        return response
