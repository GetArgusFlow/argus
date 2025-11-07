# argus/services/extractor/app/core/models.py

from pydantic import BaseModel, Field, create_model
from typing import Dict, Any, Optional, List, Type

# Import the new building blocks from types.py
from app.core.types import FieldExtractionStatus, ExtractionResult


class _BaseProductData(BaseModel):
    """
    The base class for our dynamic product data model.
    It contains the core scoreboard and metadata functionality.
    """

    all_results: Dict[str, List[ExtractionResult]] = Field(
        default_factory=dict, exclude=True
    )
    field_status: Dict[str, FieldExtractionStatus] = Field(
        default_factory=dict, exclude=True
    )
    selectors_used: Dict[str, str] = Field(default_factory=dict, exclude=True)

    def add_result(self, field_name: str, result: ExtractionResult):
        """Adds a new found result to the scoreboard."""
        if field_name not in self.all_results:
            self.all_results[field_name] = []
        self.all_results[field_name].append(result)

    def get_final_results(self) -> Dict[str, Any]:
        """Returns the final model data, excluding metadata."""
        # This helper function makes cleanup in the analyzer easier
        return self.model_dump(
            exclude={"all_results", "field_status", "selectors_used"}
        )


# The Dynamic Model Factory
def get_product_data_model(
    discovered_modules: Dict[str, Any],
) -> Type[_BaseProductData]:
    """
    Dynamically creates the ProductData model by adding fields discovered
    from the module files.
    """
    dynamic_fields: Dict[str, Any] = {}

    for name, module in discovered_modules.items():
        if hasattr(module, "FIELD_TYPE"):
            # Field definition: (Type Hint, Default Value)
            # Example: title: (Optional[str], None)
            dynamic_fields[name] = (getattr(module, "FIELD_TYPE"), None)
        else:
            # Fallback for modules without FIELD_TYPE
            dynamic_fields[name] = (Optional[Any], None)

    # Use Pydantic's create_model to build a new class
    # that inherits from _BaseProductData and contains the dynamic fields.
    ProductDataModel = create_model(
        "ProductDataModel", __base__=_BaseProductData, **dynamic_fields
    )

    return ProductDataModel
