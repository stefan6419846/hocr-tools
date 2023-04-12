#!/usr/bin/env python

__version__ = '1.3.0'

from setuptools import find_packages, setup


setup(
    name="hocr-tools",
    version=__version__,
    description='Advanced tools for hOCR integration',
    author='Thomas Breuel',
    maintainer='Konstantin Baierer',
    maintainer_email='konstantin.baierer@gmail.com',
    url='https://github.com/tmbdev/hocr-tools',
    download_url='https://github.com/tmbdev/hocr-tools/tarball/v'
                 + __version__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Utilities',
    ],
    install_requires=[
        'Pillow',
        'lxml',
        'reportlab',
    ],
    extras_require={
        'dev': [
            'beautifulsoup4',
            'requests',
            'importlib-resources; python_version<"3.9"',
        ],
    },
    packages=find_packages(where='.', include='hocr_tools.*'),
    entry_points={
        'console_scripts': [
            'hocr-check=hocr_tools.tools.hocr_check:main',
            'hocr-combine=hocr_tools.tools.hocr_combine:main',
            'hocr-cut=hocr_tools.tools.hocr_cut:main',
            'hocr-eval=hocr_tools.tools.hocr_eval:main',
            'hocr-eval-geom=hocr_tools.tools.hocr_eval_geom:main',
            'hocr-eval-lines=hocr_tools.tools.hocr_eval_lines:main',
            'hocr-extract-g1000=hocr_tools.tools.hocr_extract_g1000:main',
            'hocr-extract-images=hocr_tools.tools.hocr_extract_images:main',
            'hocr-lines=hocr_tools.tools.hocr_lines:main',
            'hocr-merge-dc=hocr_tools.tools.hocr_merge_dc:main',
            'hocr-pdf=hocr_tools.tools.hocr_pdf:main',
            'hocr-split=hocr_tools.tools.hocr_split:main',
            'hocr-wordfreq=hocr_tools.tools.hocr_wordfreq:main',
        ]
    }
)
