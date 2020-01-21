from setuptools import setup, find_packages

setup(
    name='aiohttp-oauth2-gitlab',
    version='0.1',
    description='',
    url='https://github.com/factorysh/aiohttp-oauth2-gitlab',
    install_requires=[
        'aioauth-client',
        'aiohttp_session[secure]',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'example']),
    extras_require={
        'test': ['pytest', 'pytest-cov', 'pytest-mock', 'pytest-asyncio'],
    },
    license="3 terms BSD",
    classifiers=[
      'Operating System :: MacOS',
      'Operating System :: POSIX',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
    ]
)
