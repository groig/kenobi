# coding: utf-8
from jedi import Script
from jedi.api.classes import Completion, Definition
from kenobi.util import uri_to_path
from kenobi.util import jedi_to_lsp_kind, path_to_uri
from typing import List
from pygls.types import (
    CompletionParams,
    CompletionList,
    Location,
    TextDocumentPositionParams,
    CompletionItem,
    Range,
    Position,
)
from pygls.features import (
    COMPLETION,
    DEFINITION,
)
from kenobi.server import feature


def complete(uri: str, content: str, line: int, char: int) -> List[Completion]:
    path = uri_to_path(uri)
    return Script(content, line, char, path).completions()


def find_definition(uri, content, line, char) -> List[Definition]:
    path = uri_to_path(uri)
    return Script(content, line, char, path).goto_definitions()


@feature(COMPLETION, trigger_character=["."])
def complete_code(ls, c: CompletionParams) -> CompletionList:  # noqa
    doc = ls.workspace.get_document(c.textDocument.uri)
    completions = complete(doc.uri, doc.source, c.position.line, c.position.character) # noqa
    items = [
        CompletionItem(x.name, jedi_to_lsp_kind(x.type), documentation=x.docstring()) # noqa
        for x in completions
    ]
    return CompletionList(False, items)


@feature(DEFINITION)
def jump_to_definition(ls, c: TextDocumentPositionParams) -> List[Location]:
    doc = ls.workspace.get_document(c.textDocument.uri)
    items = find_definition(
        doc.uri, doc.source, c.position.line + 1, c.position.character
    )
    return [
        Location(
            path_to_uri(item.module_path),
            Range(
                Position(item.line - 1, item.column),
                Position(item.line - 1, item.column + len(item.name)),
            ),
        )
        for item in items
    ]