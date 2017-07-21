from setuptools import setup, find_packages
import sys

version = sys.version_info
if not (version.major == 3 and version.minor >= 4):
    sys.exit("""
        =========================================================
        Please install Python 3.4+ before installing this package.
        =========================================================
    """)

setup(
    name='book_builder',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        akb=book_builder.scripts.book_builder:cli
        generate=book_builder.scripts.generate_output:generate
    ''',
)
