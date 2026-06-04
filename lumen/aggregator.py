
"""
Provides core aggregation interfaces and base implementations for Lumen.

This module defines the abstract class `Aggregator` interface, the class `AggregationResult` 
container, and the built-in class `BottomUpAggregator` strategy.

Aggregation strategies are responsible for combining multiple forecast or
historical time series into a single aggregated output.  They are used by the
`Orchestrator` to support multi-series forecasting workflows.

The module currently includes class `AggregationResult`, a standardized output container, 
class `Aggregator`, an abstract base class for all strategies, and class `BottomUpAggregator`,
which sums component series to produce totals.

Additional strategies (e.g. top-down constant, top_dowm_periodic) can be
registered via  class `AggregatorFactory`.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

import pandas as pd
import numpy as np

class AggregationResult:

    """
    Provides a container for aggregated outputs.

    This class standardizes the return value of all aggregation strategies.
    It holds the aggregated total series or DataFrame, the individual component 
    series used in the aggregation, and metadata describing the aggregation process.

    Parameters
    ----------
    **aggregated : pd.DataFrame | pd.Series | None**
    
    The final aggregated output produced by the strategy.  For bottom-up
    aggregation, this is typically the sum of all component forecasts.

    **components : dict[str, pd.DataFrame | pd.Series], optional**
    
    Mapping of component names to their aligned Series/DataFrames, defaults 
    to an empty dictionary.

    **metadata : dict[str, Any], optional**

    Additional information produced by the aggregator, such as strategy name, 
    aligned histories, aggregated history, and combined history + forecast frame, 
    defaults to an empty dictionary.

    Attributes
    ----------
    **aggregated : pd.DataFrame | pd.Series | None**

    The aggregated output.

    **components : dict[str, pd.DataFrame | pd.Series]**

    The aligned component series.

    **metadata : dict[str, Any]**

    Arbitrary metadata describing the aggregation process.

    Notes
    -----
    This container is intentionally lightweight and does not enforce any
    particular schema on metadata.  Strategies may include whatever additional
    information is useful for downstream export or diagnostics.
    """

    def __init__(
        self, 
        aggregated: pd.DataFrame | pd.Series | None,
        components: Dict[str, pd.DataFrame | pd.Series] | None = None,
        metadata: Dict[str, Any] | None = None,
    ):
        
        """
        Container for the outputs of an aggregation step.

        Parameters
        ----------
        **aggregated : pd.DataFrame | pd.Series | None**
        
        The aggregated series or DataFrame produced by the aggregation strategy. For 
        single-series workflows this is typically `None`.
        
        **components : dict[str, pd.DataFrame | pd.Series], optional**

        The individual component series that were combined to form the
        aggregated output. Keys are component names. Defaults to an empty
        dictionary.
        
        **metadata : dict[str, Any], optional**

        Additional information about the aggregation process, such as the
        strategy used or aligned histories. Defaults to an empty dictionary.
        """
        
        self.aggregated = aggregated

        self.components = components or {}

        self.metadata = metadata or {}

class Aggregator(ABC):

    """
    Abstract base class for all aggregation strategies.

    Aggregators define a single required method, `aggregate`, which
    accepts strategy-specific keyword arguments and returns a class `AggregationResult`.

    Subclasses implement different aggregation philosophies, such as bottom-up summation, 
    top-down constant proportion allocation, and top-down period-varying allocation
    
    Notes
    -----
    Aggregators do not perform forecasting themselves.  They operate on
    pre-computed forecasts and histories supplied by the orchestrator.
    """

    @abstractmethod
    def aggregate(self, **kwargs) -> AggregationResult:

        """
        Perform aggregation according to the strategy.

        Parameters
        ----------
        ****kwargs : dict[str, Any]**

        Strategy-specific inputs.  For example:

        * `forecasts` : dict[str, Series/DataFrame]
        * `histories` : dict[str, Series/DataFrame]
        * `proportions` : dict[str, float] (top-down)
        * `periodic_proportions` : DataFrame (top-down per period)

        Returns
        -------
        **AggregationResult**

        Container holding aggregated output, components, and metadata.

        Notes
        -----
        Subclasses must implement this method.
        """

class BottomUpAggregator(Aggregator):

    """
    Aggregation strategy that sums component series to produce a total.

    The bottom-up approach aligns all component histories and forecasts to a
    common index, fills missing values with zeros, and then computes the
    aggregate by simple addition. This strategy assumes that each component
    contributes additively to the total without weighting or reconciliation.
    """

    def aggregate(self, forecasts: dict, histories: dict, **kwargs):

        """
        Bottom-up aggregation strategy.

        This strategy sums all component series to produce a total forecast and
        total history.  It is the simplest and most common aggregation method.

        Workflow
        --------

        1. Align all histories to a common index.
        2. Sum aligned histories to an aggregated history.
        3. Align all forecasts to a common index.
        4. Sum aligned forecasts to an aggregated forecast.
        5. Convert Series to DataFrames with a standard ``value`` column.
        6. Build a combined history + forecast frame with an ``is_forecast`` flag.
        7. Return an :class:`AggregationResult`.

        Parameters
        ----------
        **forecasts : dict[str, Series | DataFrame]**

        Component forecast series keyed by work type.

        **histories : dict[str, Series | DataFrame]**

        Component historical series keyed by work type.

        Returns
        -------
        **AggregationResult**

        Contains:

        * `aggregated`, the aggregated forecast.
        * `components`, aligned component forecasts.
        * `metadata`, history, aggregated history, combined frame.

        Notes
        -----
        Missing values are filled with zero during alignment to ensure clean
        summation.  This behavior is intentional and consistent with most
        bottom-up forecasting pipelines.
        """

        # Align histories.

        aligned_hist = self._align(histories)

        total_hist = None

        for h in aligned_hist.values():

            total_hist = h if total_hist is None else total_hist + h

        # Align forecasts.

        aligned_fc = self._align(forecasts)

        total_fc = None

        for f in aligned_fc.values():

            total_fc = f if total_fc is None else total_fc + f

        # Ensure both are DateFrames.

        if isinstance(total_hist, pd.Series):

            total_hist = total_hist.to_frame(name="value")

        else:

            # rename first column to "value" if needed

            if total_hist.shape[1] == 1:

                total_hist.columns = ["value"]

        if isinstance(total_fc, pd.Series):

            total_fc = total_fc.to_frame(name="value")

        else:

            if total_fc.shape[1] == 1:

                total_fc.columns = ["value"]

        # Build aggregated combined frame.

        combined = pd.concat([

            total_hist.assign(is_forecast=False),

            total_fc.assign(is_forecast=True)

        ])

        # Return aggregation result.

        return AggregationResult(

            aggregated=total_fc,

            components=aligned_fc,

            metadata={

                "strategy": "bottom_up",

                "history": aligned_hist,

                "aggregated_history": total_hist,

                "aggregated_combined": combined

            }
            
        )

    def _align(self, series_dict):

        """
        Align all Series/DataFrames to a common index.

        This method computes the union of all indexes across the input
        series, reindexes each series to that union, and fills missing
        values with zero.  This ensures that summation across components 
        is well-defined.

        Parameters
        ----------
        **series_dict : dict[str, Series | DataFrame]**

        Mapping of component names to their time series.

        Returns
        -------
        **dict[str, Series | DataFrame]**

        A new dictionary where each series is aligned to the union index.

        Notes
        -----
        This method is internal but documented because it is a key part of
        the bottom-up strategy and may be reused by other aggregators.
        """

        # Build a union index across all series.

        all_indexes = None

        for s in series_dict.values():

            idx = s.index if hasattr(s, "index") else s.index

            all_indexes = idx if all_indexes is None else all_indexes.union(idx)

        # Reindex each series to the union index.

        aligned = {

            name: s.reindex(all_indexes).fillna(0)

            for name, s in series_dict.items()

        }

        return aligned
