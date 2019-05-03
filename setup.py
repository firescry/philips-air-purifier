from setuptools import setup

setup(
    name='philips_air_purifier',
    version='0.1.0',
    packages=['philips_air_purifier'],

    install_requires=['pyaes>=1.6.1', 'requests>=2.22.0'],

    author='firescry',
    description='Python module to connect with Philips air purifiers',
    license='MIT',
    url='https://github.com/firescry/philips-air-purifier'
)
