from .parser import Parser
from .parser_wrapper import ParserWrapper

parser_wrapper = ParserWrapper()


def register_parser(parser_type: str):
    def decorator(parser_class: Parser):
        parser_wrapper.register_parser(parser_type, parser_class)

        return parser_class

    return decorator


from .parser_implementations import HTMLParser
