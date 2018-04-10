from setuptools import setup, find_packages


REQUIRES = open("requirements.txt").readlines()


setup(
    name="mano",
    version="0.0.1",
    packages=find_packages(),
    install_requires=REQUIRES,
    entry_points={"console_scripts": ["mano = mano.entry_point:group"]}
)