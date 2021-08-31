"""
DeepHyper is a distributed machine learning (`AutoML <https://en.wikipedia.org/wiki/Automated_machine_learning>`_) package for automating the developement of deep neural networks for scientific applications. It can run on a single laptop as well as on 1,000 of nodes.

It comprises different tools such as:

* :ref:`Tutorial 1 <tutorial-01>`: optimizing hyper-parameters for a given black-box function.
* :ref:`Tutorial 4 <tutorial-04>`: neural architecture search to discover high-performing deep neural network with variable operations and connections.
* :ref:`Tutorial 5 <tutorial-05>`: automated machine learning, to easily experiment many learning algorithms from Scikit-Learn.

DeepHyper provides an infrastructure that targets experimental research in NAS and HPS methods, scalability, and portability across diverse supercomputers.
It comprises three main modules:

* :mod:`deephyper.problem`: Tools for defining neural architecture and hyper-parameter search problems.
* :mod:`deephyper.evaluator` : A simple interface to dispatch model evaluation tasks. Implementations range from `subprocess` for laptop experiments to `ray` for large-scale runs on HPC systems.
* :mod:`deephyper.search`: Search methods for NAS and HPS.  By extending the generic `Search` class, one can easily add new NAS or HPS methods to DeepHyper.


DeepHyper installation requires **Python >= 3.7**.

"""
import os
import warnings
from deephyper.__version__ import __version__, __version_suffix__

name = "deephyper"
version = __version__

# ! Check if a balsam db is connected or not
if os.environ.get("BALSAM_DB_PATH") is None:
    os.environ["BALSAM_SPHINX_DOC_BUILD_ONLY"] = "TRUE"

# Suppress warnings from skopt using deprecated sklearn API
warnings.filterwarnings(
    "ignore", category=FutureWarning, message="sklearn.externals.joblib is deprecated"
)
warnings.filterwarnings(
    "ignore", category=FutureWarning, message="the sklearn.metrics.scorer module"
)
