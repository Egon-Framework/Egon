"""Egon is a lightweight framework for the development of parallelized data
analysis pipelines. See the online documentation at
https://mwvgroup.github.io/Egon/
"""

__version__ = '0.6.0'
__author__ = 'MWV Research Group'
__license__ = 'GPL 3.0'

import warnings

try:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        import ray

except ImportError:
    warnings.warn('Ray must be installed to use the egon package.')

else:
    ray.init(
        ignore_reinit_error=True,
        include_dashboard=False,
        log_to_driver=False,
        logging_level=50)
