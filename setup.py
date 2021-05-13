import flypool
import os,sys
import setuptools

setuptools.setup(
  name = 'flypool_cli',
  packages = ['flypool'],
  version = '1.0.0',
  url='https://github.com/KohakuBlueleaf/ethermine_cli',
  description = 'A command-line tool for monitoring the status on flypools(ether and raven).',
  author = 'BlueLeaf',
  author_email = 'apolloyeh0123@gmail.com',
  zip_safe = False,
  entry_points={
    'console_scripts': [
      'ethermine = flypool.__main__: ethermine',
      'raven = flypool.__main__: ravencoin',
    ]
  },
  install_requires=[
    'requests'
  ]
)
