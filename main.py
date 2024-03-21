from parsers import parser_wrapper

if __name__ == '__main__':
    html_parser = parser_wrapper.get_parser(parser_type="html",
                                            id_tag="table",
                                            title_tag="caption",
                                            head_tag="thead",
                                            body_tag="tbody",
                                            footer_tag="tfoot",
                                            extract_country_and_date_from_footer=True,
                                            country_date_regex=r"Creation: (\d{1,2}[A-Za-z]{3}\d{4}) ([A-Za-z]+)",
                                            date_format="%d%b%Y"
                                            )

    html_parser.parse(".Beaconcure/documents")
