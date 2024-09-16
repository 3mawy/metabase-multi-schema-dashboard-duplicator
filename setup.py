from setuptools import setup, find_packages

setup(
    name='multischema-metabase-dashboard-helper',
    version='0.1.4',
    packages=find_packages(),
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'multischema-metabase-dashboard-helper=metabase_api.main:main',
        ],
    },
    description='A Python client for duplicating Metabase dashboard for multi schemas',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
