"""Helpers for using OpenSearch aggregations."""

from typing import List, Union

from opensearch_dsl.response import AggResponse
from opensearch_dsl.response.aggs import FieldBucket


def get_aggregation_buckets(agg_or_sub_agg: Union[AggResponse, FieldBucket], key: str) -> List[FieldBucket]:
    """Safely parse the aggregations from an OpenSearch response.

    NOTE: the "aggregations" attribute in the response dictionary is not set
    if the query uses an index pattern and no shards match the pattern.
    """
    agg = getattr(agg_or_sub_agg, key, None)
    if agg is None:
        return []
    buckets = getattr(agg, "buckets", [])
    return buckets
