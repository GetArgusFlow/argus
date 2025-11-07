# argus/services/extractor/app/modules/json_ld/parsers/product_parser.py

from typing import Dict, Any
from loguru import logger
from app.modules.json_ld.utils import extract_value
from app.utils.data_utils import is_valid_ean_checksum


def parse_product_details(node: Dict[str, Any], extracted_fields: Dict[str, Any]):
    """
    Extracts product-specific details from a Product or ProductGroup node.
    Modifies the 'extracted_fields' dictionary in-place.
    """
    node_type = node.get("@type", "").lower()
    logger.debug(f"Product Parser: Processing node type: {node_type}")

    if node_type not in ["product", "productgroup"]:
        return

    # Title
    title = node.get("name")
    if title:
        extracted_fields["title"] = title

    # Description
    description = node.get("description")
    if description:
        extracted_fields["description"] = description

    # Image
    image_data = node.get("image")
    if isinstance(image_data, str):
        extracted_fields["image"] = image_data
    elif isinstance(image_data, dict) and "url" in image_data:
        extracted_fields["image"] = image_data["url"]
    elif isinstance(image_data, list) and image_data:
        if isinstance(image_data[0], str):
            extracted_fields["image"] = image_data[0]
        elif isinstance(image_data[0], dict) and "url" in image_data[0]:
            extracted_fields["image"] = image_data[0]["url"]

    # Brand
    brand = extract_value(node, "brand.name")
    if not brand:
        brand = extract_value(node, "manufacturer.name")
    if not brand:
        direct_brand = node.get("brand")
        if isinstance(direct_brand, str):
            brand = direct_brand
    if brand:
        extracted_fields["brand"] = brand

    # SKU / Product ID
    sku = node.get("sku") or node.get("productID")
    if sku:
        extracted_fields["sku"] = str(sku)

    # EAN / GTIN
    ean_candidate = (
        node.get("gtin13")
        or node.get("gtin")
        or node.get("gtin8")
        or node.get("gtin14")
        or node.get("ean")
    )
    if ean_candidate:
        ean_str = str(ean_candidate)
        if len(ean_str) == 13 and ean_str.isdigit() and is_valid_ean_checksum(ean_str):
            extracted_fields["ean"] = ean_str
            logger.debug(f"Product Parser: Valid EAN (gtin13) found: {ean_str}")
        else:
            logger.debug(
                f"Product Parser: Found EAN/GTIN '{ean_str}' in JSON-LD is invalid. Skipping."
            )
