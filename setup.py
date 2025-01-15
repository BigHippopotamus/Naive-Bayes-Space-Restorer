from setuptools import setup

REQUIREMENTS = [
    'nltk',
    'pandas',
    'tqdm',
    'psutil',
    'sklearn',
    'fre @ git+https://github.com/ljdyer/feature-restoration-evaluator.git'
]

setup(
    name='nb_tamil_space_restorer',
    version='0.1',
    description="""Train Naive Bayes-based statistical machine learning \
models for restoring spaces to unsegmented sequences of Tamil characters""",
    author='Bharadwaj Sudarsan',
    author_email='bharadwajsudarsan@gmail.com',
    url='https://github.com/BigHippopotamus/Naive-Bayes-Space-Restorer',
    packages=['nb_tamil_space_restorer'],
    install_requires=REQUIREMENTS
)
