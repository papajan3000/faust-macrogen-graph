# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
setup(
      
      name='faust-macrogen-graph',
      version='1.0.0',
      description= 'Creation of a graph which represents an absolute order of the creation date of the manuscripts based on the macrogenesis of the digital Faust-Edition (http://www.faustedition.net/).',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      
      author='Jan Paulus',
      author_email='janpaulus95@web.de'
      )


