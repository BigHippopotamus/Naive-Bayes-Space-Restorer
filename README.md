# Naive Bayes Tamil Space Restorer

A Python library for training Naive Bayes-based statistical machine learning models for restoring spaces to unsegmented sequences of Tamil characters.

## Getting started

### Install the library using `pip`

```
!pip install git+https://github.com/BigHippopotamus/Naive-Bayes-Tamil-Space-Restorer.git
```

### Import the `NBTamilSpaceRestorer` class and the `map` and `unmap` functions

```python
from nb_tamil_space_restorer import NBTamilSpaceRestorer
```

### Import the `map` and `unmap` functions

```python
from nb_tamil_space_restorer.mapper import map, unmap
```

## Model training, optimization, and inference using the `NBSpaceRestorer` class

### Map/unmap text

Converts multibyte Tamil characters to single-byte ASCII characters and vice versa

#### Example usage:

```python
map('நன்றி')
```

> `鵵鱗鲚`

```python
unmap('鵵鱗鲚')
```

> `நன்றி`

### Initialize and train a model

#### `NBSpaceRestorer.__init__`

```python
    # ====================
    def __init__(self,
                 train_texts: list,
                 uyir_letters: list[str] = None,
                 mei_letters: list[str] = None,
                 ignore_case: bool = True,
                 save_path: Optional[str] = None,
                 max_n_gram: int = 2,
                 unknown_function: str = 'exponential'):
        """Initialize and train an instance of the class.

        Args:
          train_texts (list):
            The list of 'gold standard' documents (running text with spaces)
            on which to train the model.
          uyir_letters (list):
            A mapped list of letters that can only appear at the beginning of
            words. Can be left blank if using the included mapper and unmapper.
          mei_letters (list):
            A mapped list of letters that can never appear at the beginning of
            words. Can be left blank if using the included mapper and unmapper.
          ignore_case (bool, optional):
            Whether or not to ignore case during training (so that e.g.
            'banana', 'Banana', and 'BANANA' are all counted as instances
            of 'banana'). Only relevant if handling English. Defaults to True.
          save_path (Optional[str], optional):
            The path to a pickle file to save the model to. Defaults to None.
          max_n_gram (int, optional):
            The maximum value of N to calculate all N-grams for. Defaults to 2.
          unknown_function (str, optional):
            The function to use to predict the probability of an unseen word.
            Can be 'exponential' or 'gaussian', defaults to 'exponential'
        """
```

#### Example usage:

```python
restorer = NBSpaceRestorer(
    train_texts=map(train['reference'].to_list()),
    ignore_case=True,
    save_path='AncientTamil.pickle'
    max_n_gram=3
)
```

### Run a grid search to find optimal hyperparameters for inference

#### `NBSpaceRestorer.add_grid_search`

```python
    # ====================
    def add_grid_search(self,
                        grid_search_name: str,
                        L: List[int],
                        lambda_: List[float],
                        ref: List[str],
                        input: List[str]):
        """Add and start running a grid search to find optimal hyperparameters
        for the model.

        Args:
          grid_search_name (str):
            A name for the grid search (e.g. 'grid_search_1')
          L (List[int]):
            A list of values for the hyperparameter L.
            (E.g. [18, 20, 22])
          lambda_ (List[float]):
            A list of values for the hyperparameter lambda.
            (E.g. [8.0, 10.0, 12.0])
          ref (List[str]):
            A list of reference documents to use in the grid search
          input (List[str]):
            A list of input documents to use in the grid search. Should be the
            same as the reference documents, but with spaces removed.
        """
```

#### Example usage:

```python
restorer.add_grid_search(
    grid_search_name='grid_search_1',
    L=[18, 20, 22],
    lambda_=[1e-6, 1e-9, 1e-12],
    ref=map(test_ref),
    input=map(test_input)
)
```

### Show optimal hyperparameters from the current grid search

#### `NBSpaceRestorer.show_optimal_params`

```python
    # ====================
    def show_optimal_params(self,
                            metric_to_optimize: Optional[str] = None,
                            min_or_max: Optional[str] = None):
        """Display the rows from the grid search results table with the best
        results based on the values of the metric_to_optimize and min_or_max
        attributes of the class instance, and the values of the hyperparameters
        that produce those results.
        If there is more than one hyperparameter combination that produces the
        best result for metric_to_optimize, the one that was tested first will
        be selected.

        Args:
          metric_to_optimize (Optional[str], optional):
            If provided, the metric_to_optimize attribute of the class
            instance will be set to this value before finding the optimal
            hyperparameter values.
            Defaults to None.
          min_or_max (Optional[str], optional):
            If provided, the min_or_max attribute of the class
            instance will be set to this value before finding the optimal
            hyperparameter values. Defaults to None.
        """
```

#### Example usage:

```python
restorer.show_optimal_params(metric_to_optimize='Recall')
```

### Apply the optimal hyperparameters from the current grid search

#### `NBSpaceRestorer.set_optimal_params`

```python
    # ====================
    def set_optimal_params(self,
                           metric_to_optimize: Optional[str] = None,
                           min_or_max: Optional[str] = None):
        """Set the L and lambda_ attributes of the class instance to the
        optimal hyperparameters for the model based on the values of the
        metric_to_optimize and min_or_max attributes of the class instance.
        If there is more than one hyperparameter combination that produces the
        best result for metric_to_optimize, the one that was tested first will
        be selected.

        Args:
          metric_to_optimize (Optional[str], optional):
            If provided, the metric_to_optimize attribute of the class
            instance will be set to this value before finding the optimal
            hyperparameter values.
            Defaults to None.
          min_or_max (Optional[str], optional):
            If provided, the min_or_max attribute of the class
            instance will be set to this value before finding the optimal
            hyperparameter values. Defaults to None.
        """
```

#### Example usage:

```python
restorer.set_optimal_params()
```

### Load a previously saved model from a pickle file

#### `NBSpaceRestorer.load`

```python
    # ====================
    @classmethod
    def load(cls,
             load_path: str,
             read_only: bool = False) -> 'NBSpaceRestorer':
        """Load a previously saved instance of the class.

        Args:
          load_path (str):
            The path to the pickle file that contains the model
            attributes
          read_only (bool, optional):
            If set to True, the model will be loaded but changes made after
            loading will not be written back to the pickle file.

        Returns:
          NBSpaceRestorer:
            The loaded class instance
        """
```

#### Example usage:

```python
restorer = NBSpaceRestorer.load(
    'AncientTamil.pickle',
    read_only=True
)
```

### Restore spaces to an unsegmented sequence of input characters

#### `NBSpaceRestorer.restore`

```python
    # ====================
    def restore(self,
                texts: Union[str, List[str]],
                L: Optional[int] = None,
                lambda_: Optional[int] = None) -> Union[str, List[str]]:
        """Restore spaces to either a single string, or a list of
        strings.

        Args:
          texts (Union[str, List[str]]):
            Either a single string of input characters not containing spaces
            (e.g. 'thisisasentence') or a list of such strings
          L (Optional[int], optional):
            The value of the hyperparameter L to set before restoring
          lambda_ (Optional[float], optional):
            The value of the hyperparameter lambda_ to set before restoring

        Returns:
          Union[str, List[str]]:
            The string or list of strings with spaces restored
        """
```

#### Example usage:

```python
unmap(restorer.restore(map(test_input)))
```

## References

G. Jenks, ”python-wordsegment,” July, 2018. [Online]. Available:
https://github.com/grantjenks/python-wordsegment. [Accessed May
2, 2022].

P. Norvig, “Natural language corpus data,” in Beautiful Data, T.
Segaran and J. Hammerbacher, Eds. Sebastopol: O’Reilly, 2009, pp.
219-242.

Sandeep S, Sanjith S, Bharadwaj Sudarsan et al. "Word Segmentation 
of Ancient Tamil Text extracted from inscriptions", 16 September
2024, PREPRINT (Version 1) available at Research Square 
[https://doi.org/10.21203/rs.3.rs-4901928/v1]
