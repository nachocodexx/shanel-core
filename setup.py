from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='shanelcore',
    url='https://github.com/nachocode/shanel_core',
    author='Shanel Reyes',
    author_email='shanel.reyes@cinvestav.mx',
    # Needed to actually package something
    packages=['logger',"utils","security","security.cryptosystem","interfaces"],
    # Needed for dependencies
    install_requires=['numpy'],
    # *strongly* suggested for sharing
    version='0.4.1',
    # The license can be anything you like
    license='MIT',
    description='An example of a python package from pre-existing code',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)
