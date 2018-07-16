from setuptools import setup, find_packages
import tbtools

setup(
    name='tbtools',
    packages=find_packages(),
    version=tbtools.__version__,
    description='Tools for reading/writing files associated with the TxBLEND model',
    author='Taylor Sansom',
    author_email='taylor.sansom@twdb.texas.gov',
    url='https://github.com/twdb/tbtools',
    download_url='https://github.com/twdb/tbtools/archive/0.2.tar.gz',
    keywords=['TxBLEND'],
    classifiers=[],
    )
