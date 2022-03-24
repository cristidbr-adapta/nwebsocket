"""Setuptools entry point."""
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

dirname = os.path.dirname(__file__)
readme_filename = os.path.join(dirname, 'README.rst')

description = 'WebSocket client without async'

with open(readme_filename, 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(name='nwebsocket',
      version='0.9.1',
      description=description,
      long_description=long_description,
      long_description_content_type='text/x-rst',
      url='https://github.com/cristidbr-adapta/nwebsocket',
      author='Cristian Dobre',
      author_email='cristian.dobre@adaptarobotics.com',
      license='MIT',
      packages=['nwebsocket'],
      install_requires=[
          'curio',
          'wsproto'
      ],
      tests_require=['pytest'],
      zip_safe=False,
      python_requires=">=3.7"
)
