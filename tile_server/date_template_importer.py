#!/usr/bin/env python

import argparse
from collections import deque
from pathlib import Path

import sqlparse
from ruamel.yaml import YAML
from sqlparse.sql import TokenList, Where

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

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 256

    # Parses the given input file to a dict
    data = yaml.load(input_file)

    template = "{{ date.strftime('%Y-%m-%d') }}"
    date_sql = 'AND valid_since <= {0}\nAND valid_until >= {0}\n'.format(template)
    parsed = sqlparse.parse(date_sql)[0]

    # Traverses the parsed YAML dict for the SQL statements and inserts the date template
    def insert_date_template(data):
        if 'Layer' in data:
            for layer in data['Layer']:
                if 'Datasource' in layer:
                    if 'table' in layer['Datasource']:
                        sql = layer['Datasource']['table']
                        stmt = sqlparse.parse(sql)[0]
                        for token in get_tokens(stmt):
                            if isinstance(token, Where):
                                token.tokens.extend(parsed.tokens)
                        formatted = prettify_sql(stmt)
                        layer['Datasource']['table'] = formatted

    # Returns all the tokens in a given SQL statement
    def get_tokens(token):
        queue = deque([token])
        while queue:
            token = queue.popleft()
            if isinstance(token, TokenList):
                queue.extend(token)
            yield token

    # Prettifies a given SQL statement and returns the formatted string representation
    def prettify_sql(sql):
        if sql is None:
            return None
        return sqlparse.format(
            str(sql),
            keyword_case='upper',
            reindent=True)

    insert_date_template(data)

    # Dumps the YAML dict and writes it back to the given output file
    yaml.dump(data, output_file)
    print('Changes have been written into {0}'.format(output_file.name))
