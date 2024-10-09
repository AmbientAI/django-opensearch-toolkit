"""Custom Field Type for a 'knn_vector'.

Refs:
  [1] knn_vector type in OpenSearch
       - https://opensearch.org/docs/latest/field-types/supported-field-types/knn-vector/
       - This is specific to OpenSearch. It's analogue in ElasticSearch is the
         'dense_vector' type. This latter type is included in the DSL (opensearch_dsl
         is forked from elasticsearch_dsl), but the former is not.
  [2] dense_vector type in ElasticSearch
       - https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html
       - Parameter analogues:
            - 'element_type' -> 'data_type'
            - 'dims' -> 'dimension'
            - 'similarity' -> 'method':'space_type'
            - 'index_type' -> 'method':{'name', 'engine'}
  [2] dense_vector type in opensearch_dsl
       - https://github.com/opensearch-project/opensearch-dsl-py/blob/
            60732211b543650e09051bc6ecf2ba78407edac2/opensearch_dsl/field.py#L355
"""

import dataclasses
import enum
from typing import Any, Dict, Optional

from opensearch_dsl import Float


class KnnVectorDataType(enum.Enum):
    """Supported data_type values for the knn_vector field."""

    FLOAT = "float"  # 4 bytes (default)
    BYTE = "byte"  # 1 byte. Only supported for the LUCENE engine.


class KnnVectorMethodName(enum.Enum):
    """Supported approximate-kNN methods.

    Refs:
      [1] https://opensearch.org/docs/latest/search-plugins/knn/knn-index/
    """

    HNSW = "hnsw"
    IVF = "ivf"


class kNNVectorSpace(enum.Enum):
    """Supported approximate-kNN metric spaces.

    Refs:
      [1] https://opensearch.org/docs/latest/search-plugins/knn/approximate-knn/#spaces
    """

    LONE = "l1"
    LTWO = "l2"
    LINF = "linf"
    COSINESIMIL = "cosinesimil"
    INNERPRODUCT = "innerproduct"  # Not supported for the LUCENE engine.


class kNNVectorEngine(enum.Enum):
    """Supported approximate-kNN engines.

    Refs:
      [1] https://opensearch.org/docs/latest/search-plugins/knn/knn-index/
    """

    NMSLIB = "nmslib"
    LUCENE = "lucene"
    FAISS = "faiss"


@dataclasses.dataclass
class KnnVectorMethod:
    """Definition of an approximate-kNN method.

    Refs:
      [1] https://opensearch.org/docs/latest/search-plugins/knn/knn-index/#method-definitions
    """

    name: KnnVectorMethodName
    space_type: Optional[kNNVectorSpace] = None
    engine: Optional[kNNVectorEngine] = None
    parameters: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Represent the method as a dictionary."""
        as_dict: Dict[str, Any] = {}
        as_dict["name"] = self.name.value
        if self.space_type:
            as_dict["space_type"] = self.space_type.value
        if self.engine:
            as_dict["engine"] = self.engine.value
        if self.parameters:
            as_dict["parameters"] = self.parameters
        return as_dict


class KnnVector(Float):
    """Custom Field Type for a 'knn_vector'."""

    name = "knn_vector"

    def __init__(
        self,
        dimension: int,
        data_type: KnnVectorDataType = KnnVectorDataType.FLOAT,
        method: Optional[KnnVectorMethod] = None,
        **kwargs: Any,
    ):
        """Initialize the field type."""
        kwargs["multi"] = True
        kwargs["dimension"] = dimension
        kwargs["data_type"] = data_type.value
        if method:
            kwargs["method"] = method.to_dict()
        super(KnnVector, self).__init__(**kwargs)
