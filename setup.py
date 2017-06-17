from setuptools import setup, find_packages
import sys

version = sys.version_info
if not (version.major == 3 and version.minor == 6):
    sys.exit("""
        =========================================================
        Please install Python 3.6 before installing this package.
        =========================================================
    """)

setup(
    name='atomickotlinbuilder',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        akb=src.scripts.atomic_kotlin_builder:cli
    ''',
)
