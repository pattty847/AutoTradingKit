from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

setup(
    name='PySide6_VerticalQTabWidget',
    version='0.0.3',
    author='Maurilio Genovese',
    author_email='mauriliogenovese@gmail.com',
    license='MIT',
    packages=find_packages(),
    description='Vertical QTabWidget for PySide6',
    url='https://github.com/mauriliogenovese/PySide6_VerticalQTabWidget',
    long_description_content_type='text/markdown',
    long_description=long_description,
    install_requires=[
        'PySide6>=6.4'
    ]
)
