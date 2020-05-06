from setuptools import setup


setup(
    name="bbb-pymonitor",
    version="0.1",
    description="Tools to monitor Big Blue Button",
    url="http://github.com/Abstract-Tech/bbb-pymonitor",
    author="Silvio Tomatis",
    author_email="silviot@gmail.com",
    license="GPL",
    install_requires=["requests", "rich"],
    entry_points={"console_scripts": ["bbb_show_usage=bbb_pymonitor.show_usage:main"]},
    packages=["bbb_pymonitor"],
)
