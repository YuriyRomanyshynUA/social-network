import setuptools


setuptools.setup(
    name="social-network-pkg-yuriy-romanyshyn",
    version="0.0.1",
    author="Yuriy Romanyshyn",
    author_email="yuriy.romanyshyn.lv.ua@gmail.com",
    description="social-network",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires='>=3.6'
)
