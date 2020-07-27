#!/bin/bash
rm dist/bento?dash-0.*
pip uninstall -y bento-dash
python3 setup.py sdist bdist_wheel >> /dev/null
pip install -q dist/bento-dash-$1.tar.gz
