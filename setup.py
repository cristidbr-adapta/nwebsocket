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
      version='0.9.2',
      description=description,
      long_description=long_description,
      long_description_content_type='text/x-rst',
      url='https://github.com/cristidbr-adapta/nwebsocket',
      author='Cristian Dobre',
      author_email='cristian.dobre@adaptarobotics.com',
      license='MIT',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Framework :: Jupyter',
        'Framework :: Jupyter :: JupyterLab',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
      ],
      packages=['nwebsocket'],
      install_requires=[
          'curio',
          'wsproto'
      ],
      tests_require=['pytest'],
      zip_safe=False,
      python_requires=">=3.7",
)
