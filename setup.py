import pathlib
from typing import List

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent


def read_version() -> str:
    file_path = here / "version"
    with open(file_path, encoding="utf-8") as version_file:
        return version_file.read().strip()


def development_status(version: str) -> str:
    if "a" in version:
        dev_status = "Development Status :: 3 - Alpha"
    elif "dev" in version or "rc" in version:
        dev_status = "Development Status :: 4 - Beta"
    else:
        dev_status = "Development Status :: 5 - Production/Stable"
    return dev_status


def long_description(short_description: str) -> str:
    readme_path = here / "README.md"
    try:
        with open(readme_path, encoding="utf-8") as readme:
            long_desc = "\n" + readme.read()
            return long_desc
    except FileNotFoundError:
        return short_description


def read_requirements(path: str) -> List[str]:
    file_path = here / path
    with open(file_path, encoding="utf-8") as requirements_file:
        return requirements_file.read().split("\n")


NAME = "aiqst"
DESCRIPTION = "Delta Pipelines"
URL = "http://example.com"
AUTHOR = "Example"
EMAIL = "example@example.com"
VERSION = read_version()
DEVELOPMENT_STATUS = development_status(VERSION)
LONG_DESCRIPTION = long_description(DESCRIPTION)
REQUIREMENTS = read_requirements("requirements.txt")
DEV_REQUIREMENTS = read_requirements("requirements.dev.txt")

setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    extras_require={
        "dev": DEV_REQUIREMENTS,
    },
    url=URL,
    classifiers=[
        DEVELOPMENT_STATUS,
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    # entry_points={
    # 'console_scripts': [
    #     'aiq-db = aiqst.db.__main__:main'
    # ]},
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    zip_safe=False,
)
