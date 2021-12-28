import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='exctrap',
    version='0.0.1',
    python_requires='~=3.7',
    author='Isaac To',
    author_email='isaac.to@gmail.com',
    description='Exception trap',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/isaacto/exctrap',
    packages=setuptools.find_packages(),
    package_data={'exctrap': ['py.typed']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
