from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version = fh.read().strip()

setup(
    name="cltl.dialogue_evaluation",
    description="The Leolani Language module for evaluating interactions",
    version=version,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leolani/cltl-dialogueevaluation",
    license='MIT License',
    authors={
        "Piek Vossen":{"Piek Vossen", "piekvossen@gmailcom"},
        "Baez Santamaria": ("Selene Baez Santamaria", "s.baezsantamaria@vu.nl"),
        "Baier": ("Thomas Baier", "t.baier@vu.nl")
    },
    package_dir={'': 'src'},
    packages=find_namespace_packages(include=['cltl.*'], where='src'),
    package_data={'cltl.dialogue_evaluation': ['data/*']},
    python_requires='>=3.10',
#     install_requires=[
#     'numpy==1.26.4',
#     'pandas==2.2.3',
#     'scipy==1.15.2',
#     'seaborn==0.13.2',
#     'transformers==4.51.3',
#     'emissor==0.0.dev4',  # Note this is a slightly different version from your setup.py
#     'torch==2.2.2',
#     'valuate==0.4.3',
#     'accelerate==1.6.0',
#     'bert-score==0.3.13',
#     'bleach==6.2.0',
#     'chardet==5.2.0',
#     'click==8.1.8',
#     'datasets==3.5.1',
#     'fqdn==1.5.1',
#     'nltk==3.9.1',
#     'rouge-score==0.1.2',
#     'spacy==3.8.5',
#     'tqdm==4.67.1',
#     'openpyxl==3.1.5',
#     'cltl.combot==1.1.dev1'
# ]
    ,
    setup_requires=['flake8']
)