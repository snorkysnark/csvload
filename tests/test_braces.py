from csvload.parser import find_text_in_braces


def test_simple():
    assert find_text_in_braces("aaaa{f20}bb") == "f20"


def test_nested():
    assert find_text_in_braces("aaa{find{'table'}.name}c") == "find{'table'}.name"


def test_nested_first_only():
    assert find_text_in_braces("aaa{find{'table'}.name}c{me}") == "find{'table'}.name"


def test_missing():
    assert find_text_in_braces("auwfbawf") is None


def test_no_closing():
    assert find_text_in_braces("aiwf{wf") is None


def test_no_opening():
    assert find_text_in_braces("aiwf}wf") is None


def test_out_of_order():
    assert find_text_in_braces("ai}wf{wf") is None
