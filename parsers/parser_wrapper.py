from parsers import Parser


class ParserWrapper:
    def __init__(self):
        self._parsers = {}

    def register_parser(self, parser_type: str, parser_class: Parser):
        self._parsers[parser_type] = parser_class

    def get_parser(self, parser_type: str, *args, **kwargs) -> Parser:
        if parser_type in self._parsers:
            return self._parsers[parser_type](*args, **kwargs)

        raise ValueError(f"Unknown db type: {parser_type}")
