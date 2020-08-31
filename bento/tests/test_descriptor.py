from bento import bento
from bento.dashboards import demo, simple


minimal = {
    "data": {"covid": {"module": "bento.sample_data.covid"}},
    "pages": {
        "first": {"dataid": "covid", "banks": {"style": {"type": "style_controls"}}}
    },
}

fail_descriptors = [
    {},
    {"pages": {"bad__pagename": {}}},
    {"pages": {"good_page": {"banks": {"_bad_bankname": {}}}}},
]

pass_descriptors = [minimal, simple.descriptor, demo.descriptor]


def test_fail_validation():
    for test_desc in fail_descriptors:
        invalid_instance = bento.Bento(test_desc)
        assert not invalid_instance.valid


def test_pass_validation():
    for test_desc in pass_descriptors:
        valid_instance = bento.Bento(test_desc)
        assert valid_instance.valid
