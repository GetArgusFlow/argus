json_examples = [
    {
        "html": "<div><h2>Processor</h2><p>Intel Core i7</p><h2>Geheugen</h2><p>16 GB</p></div>",
        "json": {
            "category": "Specificaties",
            "details": {"Processor": "Intel Core i7", "Geheugen": "16 GB"},
        },
    },
    {
        "html": """
<div>
    <h2>Specificaties</h2>
    <table>
        <tr>
            <th>Processor</th>
            <td>Octa-Core</td>
        </tr>
        <tr>
            <th>Geheugen</th>
            <td>8 GB RAM</td>
        </tr>
    </table>
</div>
""",
        "json": {
            "category": "Specificaties",
            "details": {"Processor": "Octa-Core", "Geheugen": "8 GB RAM"},
        },
    },
    {
        "html": """
<div class="product-specifications">
        <h2>Productkenmerken</h2>
        <table class="spec-table">
            <tbody>
                <tr>
                    <th class="spec-term">EAN</th>
                    <td class="spec-value">8711000044801</td>
                </tr>
                <tr>
                    <th class="spec-term">Inhoud</th>
                    <td class="spec-value">500 g</td>
                </tr>
                <tr>
                    <th class="spec-term">Soort koffie</th>
                    <td class="spec-value">Snelfilter</td>
                </tr>
            </tbody>
        </table>
    </div>
""",
        "json": {
            "category": "Productkenmerken",
            "details": {
                "EAN": "8711000044801",
                "Inhoud": "500 g",
                "Soort koffie": "Snelfilter",
            },
        },
    },
    {
        "html": """
    <div class="pdp-property-info">
            <h2 id="hp_hotel_name" class="pdp-title">Grand Plaza Hotel Amsterdam</h2>
            <div data-testid="price-and-discounted-price">
                <span class="price-show">Vanaf € 180 per nacht</span>
            </div>
        </div>

        <div id="property_description_content">
            <p>Het Grand Plaza Hotel ligt in het hart van Amsterdam en biedt luxe kamers met uitzicht op de stad. Geniet van ons restaurant van wereldklasse en de nabijheid van alle belangrijke bezienswaardigheden.</p>
        </div>

        <div id="hotel_facilities_block">
            <h2>Meest populaire faciliteiten</h2>
            <div class="facilities-block">
                <div class="facilities-category">
                    <ul>
                        <li><i class="icon-wifi"></i> Gratis WiFi</li>
                        <li><i class="icon-family"></i> Familiekamers</li>
                        <li><i class="icon-nosmoking"></i> Rookvrije kamers</li>
                    </ul>
                </div>
                <div class="facilities-category">
                    <h3>Badkamer</h3>
                    <ul>
                        <li>Eigen badkamer</li>
                        <li>Föhn</li>
                        <li>Gratis toiletartikelen</li>
                    </ul>
                </div>
                <div class="facilities-category">
                    <h3>Eten & Drinken</h3>
                    <ul>
                        <li>Restaurant</li>
                        <li>Bar</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
""",
        "json": [
            {
                "category": "Meest populaire faciliteiten",
                "details": ["Gratis WiFi", "Familiekamers", "Rookvrije kamers"],
            },
            {
                "category": "Badkamer",
                "details": ["Eigen badkamer", "Föhn", "Gratis toiletartikelen"],
            },
            {"category": "Eten & Drinken", "details": ["Restaurant", "Bar"]},
        ],
    },
]
