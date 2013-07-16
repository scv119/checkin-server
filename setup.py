from setuptools import setup, find_packages

setup(
    name = "checkin",
    version = "1.0",
    url = 'http://scv119.me',
    license = 'Private',
    description = "",
    author = '',
    packages = ["checkin"],
    install_requires = ['setuptools',
                        'tornado',
                        'redis',
                        ],
    entry_points="""
    [console_scripts]
    checkin-web = checkin.app:main
    """,
)
