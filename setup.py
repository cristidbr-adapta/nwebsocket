"""Setuptools entry point."""
import codecs
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

dirname = os.path.dirname(__file__)
readme_filename = os.path.join(dirname, 'README.rst')

description = 'WebSocket client without async'
long_description = description

if os.path.exists(readme_filename):
    readme_content = codecs.open(readme_filename, encoding='utf-8').read()
    long_description = readme_content

setup(name='nwebsocket',
      version='0.9.0',
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
      zip_safe=False)
