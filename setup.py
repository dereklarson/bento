import pathlib
from setuptools import setup

# The directory containing this file, relative to cwd
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()


def requires(req_mode):
    with open("requires-{}.txt".format(req_mode)) as fh:
        requires = [line.strip() for line in fh]
        return [req for req in requires if req and not req.startswith("#")]


setup(
    name="bento-dash",
    version="0.1.1",
    description="Create Plotly Dash apps from a template",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/dereklarson/bento",
    author="Derek Larson",
    author_email="larson.derek.a@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    packages=[
        "bento",
        "bento.common",
        "bento.common.scrub",
        "bento.dashboards",
        "bento.examples",
        "bento.templates",
    ],
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=requires("install"),
    entry_points={"console_scripts": ["bento-test-gen=bento.test_gen:main"]},
)
