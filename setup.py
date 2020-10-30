import setuptools

REQUIREMENTS = [
    "imgkit",
    "pageshot",
    "pillow",
    "pyyaml",
    "jinja2",
    "google-api-python-client",
    "google-auth-httplib2",
    "google-auth-oauthlib",
]

setuptools.setup(
    name="playtest_cards",
    version="0.0.1",
    author="Boris",
    description="A python package for making cards quickly",
    url="https://github.com/dat-boris/card_maker",
    packages=["playtest_cards"],
    install_requires=REQUIREMENTS,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
