# Author:
# Date:
# Email:
# Description:
from setuptools import setup

setup(
    name='yourapplication',
    packages=['yourapplication'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    dependency_links=['requirements.txt']
)
