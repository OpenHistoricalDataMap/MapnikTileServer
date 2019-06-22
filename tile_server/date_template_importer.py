import argparse
from collections import deque
from pathlib import Path, PosixPath

import sqlparse
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.scalarstring import LiteralScalarString
from sqlparse.sql import TokenList, Where, Statement


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

        self.table_names = ('physics', 'chemistry', 1997, 2000)

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
                            if isinstance(token, Where):
                                token.tokens.extend(self.parsed.tokens)
                        formatted: str = self.prettify_sql(stmt)
                        layer['Datasource']['table'] = formatted

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
        print('Changes have been written into {0}'.format(self.output_file.name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Inserts a date template into the Mapnik style configuration file.')

    parser.add_argument(
        '-i', '--input',
        default='project.mml',
        type=Path,
        help='Input file (default : project.mml)',
        metavar='input-file',
        dest='input_file')

    parser.add_argument(
        '-o', '--output',
        default='project.mml',
        type=Path,
        help='Output file (default : project.mml)',
        metavar='output-file',
        dest='output_file')

    args: argparse.Namespace = parser.parse_args()

    date_template_importer: DateTemplateImporter = DateTemplateImporter(
        input_file=args.input_file,
        output_file=args.output_file
    )
    date_template_importer.insert_date_template()
    date_template_importer.write_yaml_to_file()
