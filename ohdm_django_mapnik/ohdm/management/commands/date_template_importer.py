from django.core.management.base import BaseCommand

from collections import deque
from pathlib import PosixPath

import sqlparse
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.scalarstring import LiteralScalarString
from sqlparse.sql import TokenList, Where, Statement, Parenthesis, IdentifierList, Identifier, Token

from config.settings.base import env
import subprocess


# todo does not work! Will it work in the future?

class Command(BaseCommand):
    help = "generate carto mml & xml file"

    def handle(self, *args, **options):
        date_template_importer: DateTemplateImporter = DateTemplateImporter(
            input_file=PosixPath("{}/project.mml".format(env("CARTO_STYLE_PATH"))),
            output_file=PosixPath("{}/style.xml".format(env("CARTO_STYLE_PATH")))
        )
        date_template_importer.insert_date_template()
        date_template_importer.write_yaml_to_file()
        self.generate_default_style_xml()

    @staticmethod
    def generate_default_style_xml():
        """
        Generate with carto and project.mml the default style.xml with jinja2 vars
        :return: jinja2 Template for custom date style.xml
        """
        # generate mapnik xml and return it to a string
        response = subprocess.run("carto {} > {}".format(
            "{}/project.mml".format(env("CARTO_STYLE_PATH")),
            "{}/style.xml".format(env("CARTO_STYLE_PATH"))
        ),
            cwd=env("CARTO_STYLE_PATH"),
            shell=True, stderr=subprocess.PIPE)
        print('Style XML was generated {0}'.format("{}/style.xml".format(env("CARTO_STYLE_PATH"))))
        return response.stderr.decode("utf-8")


class DateTemplateImporter(object):

    def __init__(self, input_file: PosixPath, output_file: PosixPath):
        self.input_file: PosixPath = input_file
        self.output_file: PosixPath = output_file

        self.yaml: YAML = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.width = 256

        # Parses the given input file to a dict
        self.sql_data: CommentedMap = self.yaml.load(input_file)

        template: str = "'{{ date.strftime('%Y-%m-%d') }}'"
        date_sql: str = ' AND valid_since <= {0}\nAND valid_until >= {0}\n'.format(template)

        self.parsed: Statement = sqlparse.parse(date_sql)[0]

    def insert_date_template(self) -> None:
        """
        Traverses the parsed YAML dict for the SQL statements and inserts the date template
        """
        if 'Layer' in self.sql_data:
            for layer in self.sql_data['Layer']:
                if 'Datasource' in layer:
                    if 'table' in layer['Datasource']:
                        sql: LiteralScalarString = layer['Datasource']['table']
                        stmt: Statement = sqlparse.parse(sql)[0]

                        for token in self.get_tokens(stmt):
                            if isinstance(token, IdentifierList):
                                token = self.update_select_token(token)
                            if isinstance(token, Where):
                                token = self.update_where_token(token)
                                # token.parent = self.update_token(token.parent)
                                # token.tokens.extend(self.get_valid_statements(token.parent.value).tokens)

                        formatted: str = self.prettify_sql(stmt)
                        layer['Datasource']['table'] = formatted

    @staticmethod
    def update_where_token(token: Where):
        template: str = "'{{ date.strftime('%Y-%m-%d') }}'"
        date_sql: str = ""

        if "planet_osm_line l" in token.parent.value:
            date_sql += ') AND l.valid_since <= {0}\nAND l.valid_until >= {0}\n'.format(template)
        if "planet_osm_point p" in token.parent.value:
            date_sql += ') AND p.valid_since <= {0}\nAND p.valid_until >= {0}\n'.format(template)
        if "planet_osm_polygon p" in token.parent.value:
            date_sql += ') AND p.valid_since <= {0}\nAND p.valid_until >= {0}\n'.format(template)
        if date_sql == "":
            date_sql = ') AND valid_since <= {0}\nAND valid_until >= {0}\n'.format(template)

        where_statement: Statement = sqlparse.parse(' (')[0]
        for where_bracket_begin_token in reversed(where_statement.tokens):
            token.tokens.insert(1, where_bracket_begin_token)

        date_sql_statement: Statement = sqlparse.parse(date_sql)[0]
        for date_sql_token in date_sql_statement.tokens:
            token.tokens.append(date_sql_token)

        return token

    @staticmethod
    def update_select_token(token: IdentifierList) -> IdentifierList:

        if "SELECT" in token.value:
            parsed: Statement = sqlparse.parse("valid_since, valid_until, ")[0]
            for valid_token in reversed(parsed.tokens):
                token.tokens.insert(0, valid_token)

        return token

    @staticmethod
    def get_valid_statements(parent_sql: str) -> Statement:
        template: str = "'{{ date.strftime('%Y-%m-%d') }}'"
        date_sql: str = ""

        if "planet_osm_line l" in parent_sql:
            date_sql += ' AND l.valid_since <= {0}\nAND l.valid_until >= {0}\n'.format(template)
        if "planet_osm_point p" in parent_sql:
            date_sql += ' AND p.valid_since <= {0}\nAND p.valid_until >= {0}\n'.format(template)
        if "planet_osm_polygon p" in parent_sql:
            date_sql += ' AND p.valid_since <= {0}\nAND p.valid_until >= {0}\n'.format(template)
        if date_sql == "":
            date_sql = ' AND valid_since <= {0}\nAND valid_until >= {0}\n'.format(template)

        # todo need smart handling!
        if "UNION ALL" in parent_sql:
            date_sql = " "
        if "natural" in parent_sql:
            date_sql = " "

        if "SELECT" in parent_sql:
            date_sql = " "

        return sqlparse.parse(date_sql)[0]

    @staticmethod
    def get_tokens(token: Statement) -> Statement:
        """
        Returns all the tokens in a given SQL statement
        :param token:
        """
        queue: deque = deque([token])
        while queue:
            token: Statement = queue.popleft()
            if isinstance(token, TokenList):
                queue.extend(token)
            yield token

    @staticmethod
    def prettify_sql(sql: Statement) -> str:
        """
        Prettifies a given SQL statement and returns the formatted string representation
        :param sql:
        :return:
        """
        if sql is None:
            return ""
        return sqlparse.format(
            str(sql),
            keyword_case='upper',
            reindent=False)

    def write_yaml_to_file(self) -> None:
        """
        Dumps the YAML dict and writes it back to the given output file
        """
        self.yaml.dump(self.sql_data, self.output_file)
        print('Changes have been written into {0}'.format(self.output_file))
