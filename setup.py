# ./setup.py

# Standard library

# Local imports

# Third-party packages
from setuptools import setup, find_packages


setup(
    name='pyvorg',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyvorg=source.main:main',  # This defines the CLI command
        ],
    },
    install_requires=[
        'colorlog',
        'guessit',
        'requests',
        'setuptools',
        'tqdm',
    ],
    author='Brett DeWitt',
    author_email='bdewitt1984@gmail.com',
    description='A lightweight CLI based media organizer',
    url='https://github.com/bdewitt84/pyvorg',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
