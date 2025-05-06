# SPDX-FileCopyrightText: 2025 Joe Pardue
# SPDX-License-Identifier: MIT

import setuptools

setuptools.setup(
    name="circuitpython-as7343",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="CircuitPython driver for the AMS AS7343 14-channel spectral sensor",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/your_username/circuitpython-as7343",
    py_modules=["as7343"],
    python_requires=">=3.7",
    install_requires=["adafruit-circuitpython-busdevice"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Hardware",
    ],
)
