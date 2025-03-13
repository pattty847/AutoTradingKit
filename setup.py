from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        name="atklip.controls.pandas_ta.utils._numba",
        sources=["e:/AutoTradingKit/atklip/controls/pandas_ta/utils/_numba.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3"],
    )
]

setup(
    name="AutoTradingKit",
    ext_modules=cythonize(extensions),
    zip_safe=False,
)