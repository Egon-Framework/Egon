"""Egon is a lightweight framework for the development of parallelized data
analysis pipelines. See the online documentation at
https://mwvgroup.github.io/Egon/
"""

__version__ = '0.5.0'
__author__ = 'MWV Research Group'
__license__ = 'GPL 3.0'

import ray

ray.init(ignore_reinit_error=True, include_dashboard=False)
