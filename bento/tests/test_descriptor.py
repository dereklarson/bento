from bento import bento, demo_descriptor


minimal = {
    "data": {"covid": {"module": "bento.examples.covid"}},
    "pages": {"123": {"dataid": "covid", "banks": {"axis": {"type": "axis_controls"}}}},
}

fail_descriptors = [
    {},
    {"pages": {"bad__pagename": {}}},
    {"pages": {"good_page": {"banks": {"_bad_bankname": {}}}}},
]

pass_descriptors = [minimal, demo_descriptor.descriptor]


def test_fail_validation():
    for test_desc in fail_descriptors:
        invalid_instance = bento.Bento(test_desc)
        assert not invalid_instance.valid


def test_pass_validation():
    for test_desc in pass_descriptors:
        valid_instance = bento.Bento(test_desc)
        assert valid_instance.valid
