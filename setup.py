from setuptools import setup, find_packages

setup(
    name='passcheck',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    extras_require={
        'full': [
            'hunspell',
        ],
    },
    entry_points={
        'console_scripts': [
            'passcheck = passcheck.commandline:main',
        ],
    },
)
