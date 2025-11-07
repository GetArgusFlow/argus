# argus/services/generalizer/app/prompts/en/examples.py

# FEW-SHOT EXAMPLE DATA
# These examples are crucial for the content extraction logic.
# They are designed to mirror the Dutch examples in complexity, testing
# conversions (m, kg, L) and field logic.
json_examples = [
    # 1. Basic - Price vs. Weight (kg), Standard Item Unit
    #    Learning: Numeric parsing for price, weight in kg, specific item_unit.
    {
        "title": "Bag of potatoes 2.5 kg, price $3.99",
        "json": {
            "brand": None,
            "brand_type": "unknown",
            "product_type": "Potatoes",
            "price": 3.99,
            "material": None,
            "color": None,
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": 2.5,  # 2.5 kg remains 2.5
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": None,
            "item_count": 1,
            "item_unit": "bag",  # More specific than 'piece'
            "category": "Voeding & Dranken",  # Assumes English category in config
            "ean": None,
        },
    },
    # 2. Dimensions (LxWxH in cm -> meters) & Material
    #    Learning: Conversion cm->m, LBH numeric, dimensions None.
    {
        "title": "Oak wooden plank 200x20x2cm",
        "json": {
            "brand": None,
            "brand_type": "unknown",
            "product_type": "Wooden plank",
            "price": None,
            "material": "oak",
            "color": None,
            "height": 0.02,
            "width": 0.20,
            "length": 2.00,
            "dimensions": None,  # <-- L,W,H are separate, so dimensions is None
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": None,
            "item_count": 1,
            "item_unit": "piece",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
    # 3. Handling 'item_count' and specific 'item_unit' (rolls) + premium brand
    #    Learning: correct count, specific unit, recognize A-brand.
    {
        "title": "Charmin Toilet Paper Original - 24 rolls",
        "json": {
            "brand": "Charmin",
            "brand_type": "premium",
            "product_type": "Toilet Paper",
            "price": None,
            "material": None,
            "color": "white",
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": "Original",
            "item_count": 24,
            "item_unit": "rolls",
            "category": "Huishoudelijke Apparaten",
            "ean": None,
        },
    },
    # 4. Specific dimension notation (diameter) and length
    #    Learning: Retain original dimension string for non-LWH formats, length in meters.
    {
        "title": "Steel pipe Ø50mm x 2 meters",
        "json": {
            "brand": None,
            "brand_type": "unknown",
            "product_type": "Steel pipe",
            "price": None,
            "material": "steel",
            "color": None,
            "height": None,
            "width": None,
            "length": 2.0,
            "dimensions": "Ø50mm",  # <-- Specific non-LWH dimension
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": None,
            "item_count": 1,
            "item_unit": "piece",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
    # 5. Extraction of capacity (Storage GB), Complex Specifications, Color
    #    Learning: Capacity (GB), multiple specifications in string, color extraction.
    {
        "title": "Samsung Galaxy S21 Ultra 5G 128GB Phantom Black",
        "json": {
            "brand": "Samsung",
            "brand_type": "premium",
            "product_type": "Smartphone",
            "price": None,
            "material": None,
            "color": "Phantom Black",
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": "128GB",
            "area": None,
            "specifications": "Galaxy S21 Ultra 5G",
            "item_count": 1,
            "item_unit": "piece",
            "category": "Elektronica & Gadgets",
            "ean": None,
        },
    },
    # 6. Extraction of capacity (Power/Wattage) & Multiple Specifications
    #    Learning: Capacity (Watt), combining multiple specifications.
    {
        "title": "Philips Hue White E27 LED bulb - 60W equivalent, dimmable",
        "json": {
            "brand": "Philips Hue",
            "brand_type": "premium",
            "product_type": "LED bulb",
            "price": None,
            "material": None,
            "color": "white",
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": "60W equivalent",
            "area": None,
            "specifications": "dimmable; E27; White",
            "item_count": 1,
            "item_unit": "piece",
            "category": "Verlichting",
            "ean": None,
        },
    },
    # 7. Volume (liter -> liter) & Private Label, Price
    #    Learning: Volume in liters (direct), recognizing private label.
    {
        "title": "Tesco Organic Semi-Skimmed Milk 1 liter | $1.99",
        "json": {
            "brand": "Tesco",
            "brand_type": "private",
            "product_type": "Milk",
            "price": 1.99,
            "material": None,
            "color": None,
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": 1.0,  # 1 liter remains 1.0 liter
            "net_volume_unit": "liter",
            "capacity": None,
            "area": None,
            "specifications": "Organic; Semi-Skimmed",
            "item_count": 1,
            "item_unit": "carton",
            "category": "Voeding & Dranken",
            "ean": None,
        },
    },
    # 8. Volume (ml -> liter) & Specific Paint characteristics
    #    Learning: Conversion ml->liter, combining complex specifications.
    {
        "title": "Dulux Weathershield Exterior Paint Satin Finish Racing Green 750 ml",
        "json": {
            "brand": "Dulux",
            "brand_type": "premium",
            "product_type": "Exterior Paint",
            "price": None,
            "material": None,
            "color": "Racing Green",
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": 0.75,  # 750 ml = 0.75 liter
            "net_volume_unit": "ml",  # Original unit
            "capacity": None,
            "area": None,
            "specifications": "Weathershield; Satin Finish",
            "item_count": 1,
            "item_unit": "can",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
    # 9. More complex Dimensions (e.g., 3x2.5mm² cable), No LWH
    #    Learning: Retain non-standard dimensions as a string.
    {
        "title": "Electrical Cable 3x2.5mm² Brown 10 meters",
        "json": {
            "brand": None,
            "brand_type": "unknown",
            "product_type": "Electrical Cable",
            "price": None,
            "material": None,
            "color": "brown",
            "height": None,
            "width": None,
            "length": 10.0,
            "dimensions": "3x2.5mm²",  # <-- Specific non-LWH dimension
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": None,
            "item_count": 1,
            "item_unit": "roll",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
    # 10. Product with multiple packaging units (box with bags) and weight in grams
    #     Learning: 'box' as item_unit, weight in kg, item_count of the main package.
    {
        "title": "Twinings English Breakfast Tea - 20 bags x 2g - Box 40g",
        "json": {
            "brand": "Twinings",
            "brand_type": "premium",
            "product_type": "Tea",
            "price": None,
            "material": None,
            "color": None,
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": 0.040,  # 40 gram = 0.040 kg
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": "20 bags",  # This refers to the internal "capacity" of the box
            "area": None,
            "specifications": "English Breakfast",
            "item_count": 1,
            "item_unit": "box",
            "category": "Voeding & Dranken",
            "ean": None,
        },
    },
    # 11. Dimensions in millimeters, no LWH, and a product with 'set'
    #     Learning: 'set' as item_unit, non-LWH dimensions.
    {
        "title": "Bosch 5-piece Screwdriver Set - Torx T20 - 150mm length",
        "json": {
            "brand": "Bosch",
            "brand_type": "premium",
            "product_type": "Screwdriver Set",
            "price": None,
            "material": None,
            "color": None,
            "height": None,
            "width": None,
            "length": None,
            "dimensions": "150mm (length)",  # Specific non-LWH dimension
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": "5-piece; Torx T20",
            "item_count": 1,
            "item_unit": "set",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
    # 12. Example with unbranded product, focus on materials, colors, and specifications
    {
        "title": "Blue Cotton T-shirt Size M with V-neck",
        "json": {
            "brand": None,
            "brand_type": "unknown",
            "product_type": "T-shirt",
            "price": None,
            "material": "cotton",
            "color": "blue",
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": "Size M; V-neck",
            "item_count": 1,
            "item_unit": "piece",
            "category": "Mode & Accessoires",
            "ean": None,
        },
    },
    # 13. Example with complex product name, model number, and EAN
    {
        "title": "HP Pavilion Gaming Laptop 15-dk1000 SERIES - Intel Core i5 10th Gen - EAN: 1234567890123",
        "json": {
            "brand": "HP",
            "brand_type": "premium",
            "product_type": "Gaming Laptop",
            "price": None,
            "material": None,
            "color": None,
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": "Pavilion; 15-dk1000 SERIES; Intel Core i5 10th Gen",
            "item_count": 1,
            "item_unit": "piece",
            "category": "Elektronica & Gadgets",
            "ean": "1234567890123",
        },
    },
    # 14. Example with price, unit "set", and multiple specifications
    {
        "title": "Duralex Picardie Glass Set of 6 - 250ml - $14.99",
        "json": {
            "brand": "Duralex",
            "brand_type": "premium",
            "product_type": "Glasses",
            "price": 14.99,
            "material": "glass",
            "color": None,
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": 0.25,  # 250ml per glass = 0.25 liter
            "net_volume_unit": "ml",  # Original unit
            "capacity": "250ml per glass",  # Describes content of items in the set
            "area": None,
            "specifications": "Picardie",
            "item_count": 1,
            "item_unit": "set",
            "category": "Huis & Tuin",
            "ean": None,
        },
    },
    # 15. NEW EXAMPLE FOR AREA:
    {
        "title": "Grey Floor Tiles 60x60cm - 1.44 m² per pack",
        "json": {
            "brand": None,
            "brand_type": "unknown",
            "product_type": "Floor Tiles",
            "price": None,
            "material": None,
            "color": "grey",
            "height": None,
            "width": 0.60,
            "length": 0.60,  # Per tile
            "dimensions": None,
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": 1.44,  # <-- Area per pack
            "specifications": "60x60cm",  # Tile dimension
            "item_count": 1,
            "item_unit": "pack",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
    # 16. Wall/Ceiling Panel - Thickness (mm), Area (m2), Brand, Material
    #     Learning: Brand 'B&Q' as private brand, 'mm' thickness to height, 'm2' to area.
    {
        "title": "B&Q quality line wall and ceiling panel mdf aqua pine 8 mm 2.34 m2",
        "json": {
            "brand": "B&Q",
            "brand_type": "private",
            "product_type": "Wall and Ceiling Panel",
            "price": None,
            "material": "MDF",
            "color": "aqua",
            "height": 0.008,  # 8mm
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": 2.34,
            "specifications": "Quality Line; pine",
            "item_count": 1,
            "item_unit": "pack",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
]
