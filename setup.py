from setuptools import setup
 
setup(
    name = 'astpath',
    packages = ['astpath'],
    version = '0.1.0',
    description = 'A query language from Python abstract syntax trees',
    license='MIT',
    author='H. Chase Stevens',
    author_email='chase@chasestevens.com',
    url='https://github.com/hchasestevens/astpath',
    install_requires=[
        'lxml',
    ],
    keywords='xpath xml ast asts syntax query',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
    ]
)