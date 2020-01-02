# Created: 26.12.2019
# Copyright (c) 2019 Manfred Moitzi
# License: MIT License

import pytest
from steputils.stepfile import step_file, header_entity, LIST, string, BINARY, typed_parameter, KEYWORD
from pyparsing import ParseException

SHORT_STEP_FILE = r"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition [CoordinationView, SpaceBoundary2ndLevelAddOnView, QuantityTakeOffAddOnView]','Option [Filter: ]'),'2;1');
FILE_NAME('S:\\[IFC]\\[COMPLETE-BUILDINGS]\\xyz.ifc','2011-01-17T09:42:14',('Architect'),('Building Designer Office'),'PreProc - EDM 5.0','ArchiCAD 14.00 Release 1. Windows Build Number of the Ifc 2x3 interface: 3427','The authorising person');
FILE_SCHEMA(('IFC2X3'));
ENDSEC;

DATA;
#1= IFCORGANIZATION('GS','Graphisoft','Graphisoft',$,$);
#5= IFCAPPLICATION(#1,'14.0','ArchiCAD 14.0','ArchiCAD');
#6= IFCPERSON('','Nicht definiert','',$,$,$,$,$);
#8= IFCORGANIZATION('','Nicht definiert','',$,$);
ENDSEC;

END-ISO-10303-21;
"""


def parse_str(pattern, s) -> str:
    return pattern.parseString(s).asList()[0]


def test_short_step_file():
    result = list(step_file.parseString(SHORT_STEP_FILE))
    assert len(result) > 0


def test_header_entity():
    result = list(header_entity.parseString("FILE_SCHEMA(('IFC2X3'));"))
    assert result == ['FILE_SCHEMA', (('IFC2X3',),)]


def test_empty_list():
    result = list(LIST.parseString("()"))
    assert result == [tuple()]  # empty tuple


def test_list_1():
    result = list(LIST.parseString("('IFC2X3')"))
    assert result[0] == ('IFC2X3',)


def test_list_2():
    result = list(LIST.parseString("(1, 3.1415)"))
    assert result[0] == (1, 3.1415)


def test_string_apostrophe_1():
    assert parse_str(string, "''''") == "'"


def test_string_apostrophe_2():
    assert parse_str(string, "'x''x'") == "x'x"


def test_string_quote_1():
    assert parse_str(string, "'\"'") == "\""


def test_string_quote_2():
    assert parse_str(string, "'x\"x'") == "x\"x"


def test_string_backslash_1():
    assert parse_str(string, "'\\\\'") == "\\"


def test_string_backslash_2():
    assert parse_str(string, "'x\\\\x'") == "x\\x"


def test_extended_string_x2():
    assert parse_str(string, r"'\X2\00E4\X0\'") == '\u00E4'


def test_extended_string_multi_x2():
    assert parse_str(string, r"'\X2\00E400E4\X0\'") == '\u00E4\u00E4'


def test_extended_string_x4():
    assert parse_str(string, r"'\X4\000000E4\X0\'") == '\u00E4'


def test_binary():
    assert BINARY.parseString('"0FF"')[0] == 255


def test_typed_parameter_1():
    result = typed_parameter.parseString("TEST(100)").asList()[0]
    assert result.type_name == 'TEST'
    assert result.param == 100


def test_typed_parameter_2():
    result = typed_parameter.parseString("TEST((100, 200))").asList()[0]
    assert result.type_name == 'TEST'
    assert result.param[0] == 100
    assert result.param[1] == 200


def test_valid_keywords():
    assert parse_str(KEYWORD, 'KEYWORD') == 'KEYWORD'
    assert parse_str(KEYWORD, 'KEYWORD_0') == 'KEYWORD_0'
    assert parse_str(KEYWORD, '_KEYWORD_0') == '_KEYWORD_0'
    assert parse_str(KEYWORD, '!USER_KEYWORD') == '!USER_KEYWORD'
    assert parse_str(KEYWORD, '!_USER_KEYWORD') == '!_USER_KEYWORD'


def test_invalid_keywords():
    pytest.raises(ParseException, KEYWORD.parseString, '0KEYWORD', ('parseAll', True))
    pytest.raises(ParseException, KEYWORD.parseString, 'KEYWORD.', ('parseAll', True))
    pytest.raises(ParseException, KEYWORD.parseString, 'KEYWORD!', ('parseAll', True))
    pytest.raises(ParseException, KEYWORD.parseString, 'Keyword', ('parseAll', True))


if __name__ == '__main__':
    pytest.main([__file__])
