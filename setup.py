from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
setup(
    name='floorplankit',
    version='0.1.0',
    description='Floorplan analysis kit',
    long_description=long_description,
    url='https://github.com/nmarincic/floorplankit',
    author='Nikola Marincic',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5.1',
    ],
    keywords='floorplan extraction features tools',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['numpy','pandas','matplotlib', 'pyprind', 'scikit-image'],
    entry_points={
        'console_scripts': [
            'floorplans=floorplankit.__main__:main',
        ],
    },
)