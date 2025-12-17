from setuptools import find_packages
from setuptools import setup

setup(
    name='ros_control_interfaces',
    version='0.0.0',
    packages=find_packages(
        include=('ros_control_interfaces', 'ros_control_interfaces.*')),
)
