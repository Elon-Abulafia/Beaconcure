from .parser import Parser
from .parser_factory import ParserFactory

parser_factory = ParserFactory()


def register_parser(parser_type: str):
    def decorator(parser_class: Parser):
        parser_factory.register_parser(parser_type, parser_class)

        return parser_class

    return decorator


from .parser_implementations import HTMLParser
