# coding=utf8

from l20n.format.parser import FTLParser
from l20n.format.serializer import FTLSerializer
from l20n.util import ftl


ftl_parser = FTLParser()
ftl_serializer = FTLSerializer()


def parse(Parser, string):
    if Parser is FTLParser:
        ast, errors = ftl_parser.parse(string, with_source=False)
        return ast

    # Parsing a legacy resource.

    # Parse the string into the internal Context.
    parser = Parser()
    parser.readContents(string)
    # Transform the parsed result which is an iterator into a dict.
    return {ent.key: ent for ent in parser}


def ftl_resource_to_ast(code):
    ast, errors = ftl_parser.parse(ftl(code), with_source=False)
    return ast


def ftl_resource_to_json(code):
    ast, errors = ftl_parser.parseResource(ftl(code), with_source=False)
    return ast


def ftl_message_to_json(code):
    ast, errors = ftl_parser.parse(ftl(code), with_source=False)
    return ast.body[0].toJSON()


def to_json(merged_iter):
    return {
        path: resource.toJSON()
        for path, resource in merged_iter
    }


def get_entity(entities, ident):
    """Get entity called `ident` from the `entities` iterable."""
    for entity in entities:
        if entity.id.name == ident:
            return entity
