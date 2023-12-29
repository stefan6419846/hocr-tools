#!/usr/bin/env python

from setuptools import find_packages, setup


__version__ = '1.0.0'


setup(
    name='hocr-tools-lib',
    version=__version__,
    description='Advanced tools for hOCR integration',
    author='Thomas Breuel, stefan6419846 (library version)',
    # maintainer='Konstantin Baierer',
    # maintainer_email='konstantin.baierer@gmail.com',
    url='https://github.com/stefan6419846/hocr-tools/',
    download_url='https://github.com/stefan6419846/hocr-tools/tarball/v' + __version__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Utilities',
    ],
    install_requires=[
        'Pillow>=9.3.0',
        'lxml>=3.5.0',
        'reportlab>=3.3.0',
        'python-bidi',
    ],
    extras_require={
        'dev': [
            'beautifulsoup4',
            'requests',
            'importlib-resources; python_version<"3.10"',
        ],
    },
    packages=find_packages(
        include=['hocr_tools_lib', 'hocr_tools_lib.*']
    ),
    entry_points={
        'console_scripts': [
            'hocr-check=hocr_tools_lib.tools.hocr_check:main',
            'hocr-combine=hocr_tools_lib.tools.hocr_combine:main',
            'hocr-cut=hocr_tools_lib.tools.hocr_cut:main',
            'hocr-eval=hocr_tools_lib.tools.hocr_eval:main',
            'hocr-eval-geom=hocr_tools_lib.tools.hocr_eval_geom:main',
            'hocr-eval-lines=hocr_tools_lib.tools.hocr_eval_lines:main',
            'hocr-extract-g1000=hocr_tools_lib.tools.hocr_extract_g1000:main',
            'hocr-extract-images=hocr_tools_lib.tools.hocr_extract_images:main',
            'hocr-lines=hocr_tools_lib.tools.hocr_lines:main',
            'hocr-merge-dc=hocr_tools_lib.tools.hocr_merge_dc:main',
            'hocr-pdf=hocr_tools_lib.tools.hocr_pdf:main',
            'hocr-split=hocr_tools_lib.tools.hocr_split:main',
            'hocr-wordfreq=hocr_tools_lib.tools.hocr_wordfreq:main',
        ]
    }
)
