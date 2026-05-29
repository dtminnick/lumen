
# lumen/aggregator_factory.py

"""
Factory utilities for constructing Lumen aggregation strategies.

This module defines the :class:`AggregatorFactory`, a registry-based factory
responsible for instantiating aggregation strategy classes such as
``BottomUpAggregator`` or any custom user-registered strategy.

The factory enables:
    * Lookup of aggregation strategies by string name.
    * Dynamic registration of new strategies at runtime.
    * Consistent instantiation interface across the Lumen orchestration layer.

Typical Usage
-------------
>>> from lumen.aggregator_factory import AggregatorFactory
>>> agg = AggregatorFactory.create("bottom_up")
>>> result = agg.aggregate(forecast = ..., histories = ...)

Notes
-----
The factory is intentionally lightweight.  It does not validate the semantics
of the aggregator class beyond ensuring it subclasses :class:`Aggregator`.
"""

from __future__ import annotations
from typing import Dict, Type

from lumen.aggregator import (
    Aggregator,
    BottomUpAggregator
)

class AggregatorFactory:

    """
    Factory for creating Lumen aggregation strategies by name.

    This class maintains a registry mapping string keys to concrete
    :class:`Aggregator` subclasses.  It provides two primary capabilities:

    * ``create(name, **kwargs)`` - Instantiate a registered aggregator.
    * ``register(name, cls)`` - Add a new aggregator strategy at runtime.

    The factory is used by :class:`Orchestrator` to construct aggregation
    strategies during multi-series forecasting workflows.

    Examples
    --------
    Create a built-in aggregator:

    >>> agg = AggregatorFactory.create("bottom_up")

    Register and instantiate a custom aggregator:

    >>> class MyAgg(Aggregator):
    ...     def aggregate(self, forecasts, histories, **kwargs):
    ...         return ...
    ...
    >>> AggregatorFactory.register("my_agg", MyAgg)
    >>> agg = AggregatorFactory.create("my_agg")
    """

    _registry: Dict[str, Type[Aggregator]] = {
        "bottom_up": BottomUpAggregator,
    }

    @classmethod
    def create(cls, name: str, **kwargs) -> Aggregator:

        """
        Instantiate an aggregator strategy by name.

        Parameters
        ----------
        name : str
            The name of the aggregation strategy.  This is matched
            case-insensitively against the internal registry.  Examples:
            ``"bottom_up"``, ``"top_down_constant"``, ``"top_down_periodic"``.

        **kwargs :
            Additional keyword arguments passed directly to the aggregator's
            constructor.  These allow strategies to accept configuration
            parameters such as proportion tables, weights, or reconciliation
            options.

        Returns
        -------
        Aggregator
            A fully constructed aggregator instance.

        Raises
        ------
        ValueError
            If ``name`` does not correspond to a registered strategy.

        Notes
        -----
        This method does not validate the correctness of ``kwargs`` for the
        target aggregator.  Validation is delegated to the aggregator class
        itself.
        """

        key = name.lower().strip()

        if key not in cls._registry:
            raise ValueError(
                f"Unknown aggregation strategy '{name}'. "
                f"Available: {list(cls._registry.keys())}"
            )

        return cls._registry[key](**kwargs)

    @classmethod
    def register(cls, name: str, aggregator_cls: Type[Aggregator]) -> None:

        """
        Register a new aggregation strategy dynamically.

        Parameters
        ----------
        name : str
            The string key used to reference the strategy.  This value is
            normalized to lowercase and stripped of whitespace.

        aggregator_cls : Type[Aggregator]
            A subclass of :class:`Aggregator` implementing the required
            ``aggregate()`` interface.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If ``aggregator_cls`` is not a subclass of :class:`Aggregator`.

        Notes
        -----
        Registration is idempotent - re-registering a name overwrites the
        previous entry.  This allows users to override built-in strategies
        when experimenting.
        """

        if not issubclass(aggregator_cls, Aggregator):
            raise TypeError(
                f"Registered class must subclass Aggregator, "
                f"got {aggregator_cls.__name__}"
            )

        cls._registry[name.lower().strip()] = aggregator_cls
