from setuptools import setup, find_packages

package_name = 'my_robot_movement'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/basic_test_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rohith-rajeev',
    maintainer_email='rajeevrohith10@gmail.com',
    description='Movement package for Mecanum robot',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'test_node = my_robot_movement.test_node:main',
        ],
    },
)
