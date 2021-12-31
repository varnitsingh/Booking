XPATHS = {
    # parsing through hotel page
    "hotel_name": "//h2[@id='hp_hotel_name']",
    "address": "//span[@data-source='top_link']",
    "room_types": "//a[@class='jqrt togglelink']",
    "features": "//div[@class='bui-text bui-text--variant-emphasized_1']",
    "facilities": "//li[@class='bui-list__item bui-spacer--medium hotel-facilities-group__list-item']/div/div",
    "description": "//div[@class='hp_desc_main_content ']",
    "description2": "//div[@class='hp_desc_main_content']",
    "rating": "//span[@class='_3ae5d40db _617879812 _6ab38b430']",
    "review_score": "//div[@class='_9c5f726ff bd528f9ea6']",
    "policies": "//div[@id='hotelPoliciesInc']",
    "nearby_places": "//div[@class='hp_location_block__section_container']",
    "transport_nearby": "//div[@class='hp_location_block__section_container transport_airport']/ul/li",

    # parsing through search results.
    "main_table": "//div[@class='_814193827']",
    "hotel_link": "//a[@data-testid='title-link']",
    "room_price": "//div[@data-testid='price-and-discounted-price']/span",
    "next_page": "//button[@aria-label='Next page']",
    "last_page": "//button[@disabled='' and @aria-label='Next page']",
    "checkboxes": "//div[@id='searchboxInc']//input",

    # homepage
    "search_input": "//input[@data-component='search/destination/input-placeholder']",
    "search_button": "//button[@class='sb-searchbox__button ']",
    "cancel_button": "//button[@class='sb-destination__clear -visible']",
}