# argus/services/generalizer/app/prompts/nl/examples.py

# FEW-SHOT EXAMPLE DATA
# These examples are crucial for the content extraction logic.
# They have been updated to correct previously identified errors and to convert
# dimensions to meters, weights to kilograms (kg), and volumes to liters (L).
# Use None for null in Python.
json_examples = [
    # 1. Basic - Price vs. Weight (kg), Standard Item Unit
    #    Learning: Numeric parsing for price, weight in kg, default item_unit.
    {
        "title": "Zak aardappelen 2.5 kg, prijs Eur 3.99",
        "json": {
            "brand": None,
            "brand_type": "unknown",
            "product_type": "Aardappelen",
            "price": 3.99,
            "material": None,
            "color": None,
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": 2.5,  # 2.5 kg remains 2.5 in kg
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": None,
            "item_count": 1,
            "item_unit": "zak",  # More specific than 'stuk'
            "category": "Voeding & Dranken",
            "ean": None,
        },
    },
    # 2. Dimensions (LxWxH in cm -> meters) & Material
    #    Learning: Conversion cm->m, LBH numeric, dimensions None.
    {
        "title": "Houten plank 200x20x2cm eiken",
        "json": {
            "brand": None,
            "brand_type": "unknown",
            "product_type": "Houten plank",
            "price": None,
            "material": "eiken",
            "color": None,
            "height": 0.02,
            "width": 0.20,
            "length": 2.00,
            "dimensions": None,  # <-- L,W,H are already separate, so dimensions is None
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": None,
            "item_count": 1,
            "item_unit": "stuk",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
    # 3. Handling 'item_count' and specific 'item_unit' (rolls) + premium brand
    #    Learning: correct count, specific unit, recognize A-brand.
    {
        "title": "Page Toiletpapier Original - 24 rollen",
        "json": {
            "brand": "Page",
            "brand_type": "premium",
            "product_type": "Toiletpapier",
            "price": None,
            "material": None,
            "color": "wit",
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
            "item_unit": "rollen",
            "category": "Huishoudelijke Apparaten",
            "ean": None,
        },
    },
    # 4. Specific dimension notation (diameter) and length
    #    Learning: Retain original dimension string for non-LWH formats, length in meters.
    {
        "title": "Stalen buis Ø50mm x 2 meter",
        "json": {
            "brand": None,
            "brand_type": "unknown",
            "product_type": "Stalen buis",
            "price": None,
            "material": "Staal",
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
            "item_unit": "stuk",
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
            "item_unit": "stuk",
            "category": "Elektronica & Gadgets",
            "ean": None,
        },
    },
    # 6. Extraction of capacity (Power/Wattage) & Multiple Specifications
    #    Learning: Capacity (Watt), combining multiple specifications.
    {
        "title": "Philips Hue White E27 LED lamp - 60W equivalent, dimbaar",
        "json": {
            "brand": "Philips Hue",
            "brand_type": "premium",
            "product_type": "LED lamp",
            "price": None,
            "material": None,
            "color": "wit",
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": "60W equivalent",
            "area": None,
            "specifications": "dimbaar; E27; White",
            "item_count": 1,
            "item_unit": "stuk",
            "category": "Verlichting",
            "ean": None,
        },
    },
    # 7. Volume (liter -> liter) & Private Label, Price
    #    Learning: Volume in liters (direct), recognizing private label.
    {
        "title": "Albert Heijn Biologische Halfvolle Melk 1 liter | 2.99",
        "json": {
            "brand": "Albert Heijn",
            "brand_type": "private",
            "product_type": "Melk",
            "price": 2.99,
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
            "specifications": "Biologisch; Halfvolle",
            "item_count": 1,
            "item_unit": "pak",
            "category": "Voeding & Dranken",
            "ean": None,
        },
    },
    # 8. Volume (ml -> liter) & Specific Paint/Stain characteristics (Gloss, Coverage, Application)
    #    Learning: Conversion ml->liter, correctly combining complex specifications, correct brand/product_type.
    {
        "title": "Rambo Pantserbeits Deur & Kozijn Zijdeglans Dekkend Rijtuiggroen 750 ml",
        "json": {
            "brand": "Rambo",
            "brand_type": "premium",
            "product_type": "Pantserbeits",
            "price": None,
            "material": None,
            "color": "rijtuiggroen",
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,  # <-- L,W,H and diameters/cross-sections are not applicable here
            "weight": None,
            "net_volume": 0.75,  # 750 ml = 0.75 liter
            "net_volume_unit": "ml",  # Original unit
            "capacity": None,
            "area": None,
            "specifications": "zijdeglans; dekkend; deur & kozijn",
            "item_count": 1,
            "item_unit": "blik",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
    # 9. More complex Dimensions (e.g., 3x2.5mm² cable), No LWH
    #    Learning: Retain non-standard dimensions as a string, do not put in height/width/length.
    {
        "title": "VD Draad 3x2.5mm² Bruin 10 meter installatiekabel",
        "json": {
            "brand": None,
            "brand_type": "unknown",
            "product_type": "VD Draad",
            "price": None,
            "material": None,
            "color": "bruin",
            "height": None,
            "width": None,
            "length": 10.0,
            "dimensions": "3x2.5mm²",  # <-- Specific non-LWH dimension
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": "installatiekabel",
            "item_count": 1,
            "item_unit": "rol",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
    # 10. Product with multiple packaging units (box with bags) and weight in grams
    #     Learning: 'Doos' (box) as item_unit, weight in kg, item_count of the main package.
    {
        "title": "Pickwick English Tea - 20 zakjes x 2 gram - Doos 40 gram",
        "json": {
            "brand": "Pickwick",
            "brand_type": "premium",
            "product_type": "Engelse Thee",
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
            "capacity": "20 zakjes",  # This refers to the internal "capacity" of the box
            "area": None,
            "specifications": "English Tea",
            "item_count": 1,
            "item_unit": "doos",
            "category": "Voeding & Dranken",
            "ean": None,
        },
    },
    # 11. Dimensions in millimeters, no LWH, and a product with 'set'
    #     Learning: Conversion mm->meter, set as item_unit, no LWH-dimensions.
    {
        "title": "Bosch Schroevendraaierset 5-delig - Torx T20 - 150mm lengte",
        "json": {
            "brand": "Bosch",
            "brand_type": "premium",
            "product_type": "Schroevendraaierset",
            "price": None,
            "material": None,
            "color": None,
            "height": None,
            "width": None,
            "length": None,
            "dimensions": "150mm (lengte)",  # Specific non-LWH dimension
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": "5-delig; Torx T20",
            "item_count": 1,
            "item_unit": "set",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
    # 12. Example with unbranded product, focus on materials, colors, and specifications
    {
        "title": "Blauwe Katoenen T-shirt Maat M met V-hals",
        "json": {
            "brand": None,
            "brand_type": "unknown",
            "product_type": "T-shirt",
            "price": None,
            "material": "katoen",
            "color": "blauw",
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": None,
            "specifications": "Maat M; V-hals",
            "item_count": 1,
            "item_unit": "stuk",
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
            "item_unit": "stuk",
            "category": "Elektronica & Gadgets",
            "ean": "1234567890123",
        },
    },
    # 14. Example with price, unit "set", and multiple specifications
    {
        "title": "Duralex Picardie Glazen Set van 6 - 250ml - €14.99",
        "json": {
            "brand": "Duralex",
            "brand_type": "premium",
            "product_type": "Glazen",
            "price": 14.99,
            "material": "glas",
            "color": None,
            "height": None,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": 0.25,  # 250ml per glass = 0.25 liter per glass (important: volume per piece in the set)
            "net_volume_unit": "ml",  # Original unit
            "capacity": "250ml per glas",  # Optionally more detailed here, describes content of items in the set
            "area": None,
            "specifications": "Picardie",
            "item_count": 1,
            "item_unit": "set",
            "category": "Huis & Tuin",
            "ean": None,
        },
    },
    # NEW EXAMPLE FOR AREA:
    {
        "title": "Grijze Vloertegels 60x60cm - 1.44 m² per pak",
        "json": {
            "brand": None,
            "brand_type": "unknown",
            "product_type": "Vloertegels",
            "price": None,
            "material": None,
            "color": "grijs",
            "height": None,
            "width": 0.60,
            "length": 0.60,  # Per tile, if relevant
            "dimensions": None,  # No diameter/cross-section here
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": 1.44,  # <-- HERE comes the area per pack, as a float
            "specifications": "60x60cm",  # The tile dimension as a specification
            "item_count": 1,
            "item_unit": "pak",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
    # 17. Wall/Ceiling Panel - Thickness (mm), Area (m2), Brand, Material, Color/Finish
    #     Learning: Brand 'Gamma' as private brand, 'mm' as thickness to height, 'm2' to area,
    #     'dimensions' null, finish to specifications.
    {
        "title": "gamma quality line wand- en plafondpaneel mdf aqua larspur pine 8 mm 2,34 m2",
        "json": {
            "brand": "GAMMA",
            "brand_type": "private",
            "product_type": "Wand- en Plafondpaneel",
            "price": None,
            "material": "MDF",
            "color": "aqua",
            "height": 0.008,
            "width": None,
            "length": None,
            "dimensions": None,
            "weight": None,
            "net_volume": None,
            "net_volume_unit": None,
            "capacity": None,
            "area": 2.34,
            "specifications": "Quality Line; larspur pine",
            "item_count": 1,
            "item_unit": "pak",
            "category": "Bouw & Klussen",
            "ean": None,
        },
    },
]
