import streamlit as st
import requests
import json
import os
import pandas as pd
from collections import defaultdict

# Constants
MAX_HOTEL_CODES = 200  # Set the limit for hotel codes

# ISO4217 currency codes
ISO4217_CURRENCIES = ["USD","AED","AFN","ALL","AMD","ANG","AOA","ARS","AUD","AWG","AZN","BAM","BBD","BDT","BGN","BHD","BIF","BMD","BND","BOB","BOV","BRL","BSD","BTN","BWP","BYN","BZD","CAD","CDF","CHE","CHF","CHW","CLF","CLP","CNY","COP","COU","CRC","CUP","CVE","CZK","DJF","DKK","DOP","DZD","EGP","ERN","ETB","EUR","FJD","FKP","GBP","GEL","GHS","GIP","GMD","GNF","GTQ","GYD","HKD","HNL","HTG","HUF","IDR","ILS","INR","IQD","IRR","ISK","JMD","JOD","JPY","KES","KGS","KHR","KMF","KPW","KRW","KWD","KYD","KZT","LAK","LBP","LKR","LRD","LSL","LYD","MAD","MDL","MGA","MKD","MMK","MNT","MOP","MRU","MUR","MVR","MWK","MXN","MXV","MYR","MZN","NAD","NGN","NIO","NOK","NPR","NZD","OMR","PAB","PEN","PGK","PHP","PKR","PLN","PYG","QAR","RON","RSD","RUB","RWF","SAR","SBD","SCR","SDG","SEK","SGD","SHP","SLE","SOS","SRD","SSP","STN","SVC","SYP","SZL","THB","TJS","TMT","TND","TOP","TRY","TTD","TWD","TZS","UAH","UGX","USN","UYI","UYU","UYW","UZS","VED","VES","VND","VUV","WST","XAF","XAG","XAU","XBA","XBB","XBC","XBD","XCD","XDR","XOF","XPD","XPF","XPT","XSU","XTS","XUA","XXX","YER","ZAR","ZMW","ZWG","ZWL"]  # Add more as needed

# ISO2 country codes
ISO2_COUNTRIES = ["US","AD","AE","AF","AG","AI","AL","AM","AO","AQ","AR","AS","AT","AU","AW","AX","AZ","BA","BB","BD","BE","BF","BG","BH","BI","BJ","BL","BM","BN","BO","BQ","BR","BS","BT","BV","BW","BY","BZ","CA","CC","CD","CF","CG","CH","CI","CK","CL","CM","CN","CO","CR","CU","CV","CW","CX","CY","CZ","DE","DJ","DK","DM","DO","DZ","EC","EE","EG","EH","ER","ES","ET","FI","FJ","FK","FM","FO","FR","GA","GB","GD","GE","GF","GG","GH","GI","GL","GM","GN","GP","GQ","GR","GS","GT","GU","GW","GY","HK","HM","HN","HR","HT","HU","ID","IE","IL","IM","IN","IO","IQ","IR","IS","IT","JE","JM","JO","JP","KE","KG","KH","KI","KM","KN","KP","KR","KW","KY","KZ","LA","LB","LC","LI","LK","LR","LS","LT","LU","LV","LY","MA","MC","MD","ME","MF","MG","MH","MK","ML","MM","MN","MO","MP","MQ","MR","MS","MT","MU","MV","MW","MX","MY","MZ","NA","NC","NE","NF","NG","NI","NL","NO","NP","NR","NU","NZ","OM","PA","PE","PF","PG","PH","PK","PL","PM","PN","PR","PS","PT","PW","PY","QA","RE","RO","RS","RU","RW","SA","SB","SC","SD","SE","SG","SH","SI","SJ","SK","SL","SM","SN","SO","SR","SS","ST","SV","SX","SY","SZ","TC","TD","TF","TG","TH","TJ","TK","TL","TM","TN","TO","TR","TT","TV","TW","TZ","UA","UG","UM","UY","UZ","VA","VC","VE","VG","VI","VN","VU","WF","WS","YE","YT","ZA","ZM","ZW"]

# ISO639-1 language codes
ISO639_LANGUAGES = ["en","aa","ab","ae","af","ak","am","an","ar","as","av","ay","az","ba","be","bg","bi","bm","bn","bo","br","bs","ca","ce","ch","co","cr","cs","cu","cv","cy","da","de","dv","dz","ee","el","eo","es","et","eu","fa","ff","fi","fj","fo","fr","fy","ga","gd","gl","gn","gu","gv","ha","he","hi","ho","hr","ht","hu","hy","hz","ia","id","ie","ig","ii","ik","io","is","it","iu","ja","jv","ka","kg","ki","kj","kk","kl","km","kn","ko","kr","ks","ku","kv","kw","ky","la","lb","lg","li","ln","lo","lt","lu","lv","mg","mh","mi","mk","ml","mn","mr","ms","mt","my","na","nb","nd","ne","ng","nl","nn","no","nr","nv","ny","oc","oj","om","or","os","pa","pi","pl","ps","pt","qu","rm","rn","ro","ru","rw","sa","sc","sd","se","sg","si","sk","sl","sm","sn","so","sq","sr","ss","st","su","sv","sw","ta","te","tg","th","ti","tk","tl","tn","to","tr","ts","tt","tw","ty","ug","uk","ur","uz","ve","vi","vo","wa","wo","xh","yi","yo","za","zh","zu"]  # Add more as needed

# Define the GraphQL query
graphql_query = """
query (
    $criteriaSearch: HotelCriteriaSearchInput
    $settings: HotelSettingsInput
    $filterSearch: HotelXFilterSearchInput
) {
    hotelX {
        search(
            criteria: $criteriaSearch
            settings: $settings
            filterSearch: $filterSearch
        ) {
            options {
                accessCode
                supplierCode
                price {
                    net
                    currency
                }
                rooms {
                    description
                }
                boardCode
                hotelCode
                hotelName
            }
        }
    }
}
"""

# Function to fetch hotel rates from the API
def fetch_hotel_rates(criteria_search, settings, filter_search):
    os.environ['HOTELX_API_KEY'] = st.secrets['HOTELX_API_KEY']
    url = "https://api.travelgatex.com"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Apikey {os.environ['HOTELX_API_KEY']}"  # Use the environment variable here
    }
    payload = {
        "query": graphql_query,
        "variables": {
            "criteriaSearch": criteria_search,
            "settings": settings,
            "filterSearch": filter_search
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    
    
    return response.json()

# Function to process and rank suppliers
def rank_suppliers(data):
    # Check if 'data', 'hotelX', 'search', and 'options' exist
    if not data or 'data' not in data or 'hotelX' not in data['data'] or 'search' not in data['data']['hotelX'] or 'options' not in data['data']['hotelX']['search']:
        st.error("Invalid response structure from API")
        return {}
    
    options = data['data']['hotelX']['search']['options']
    hotel_dict = defaultdict(lambda: {'name': '', 'board_codes': defaultdict(list)})
    for option in options:
        hotel_code = option['hotelCode']
        hotel_name = option['hotelName']
        board_code = option['boardCode']
        
        # Concatenate room descriptions
        room_descriptions = " ".join([room['description'] for room in option['rooms']])
        
        hotel_dict[hotel_code]['name'] = hotel_name
        hotel_dict[hotel_code]['board_codes'][board_code].append({
            'supplierCode': option['supplierCode'],
            'accessCode': option['accessCode'],
            'netPrice': round(option['price']['net'],2),
            'roomDescription': room_descriptions,
            'netCurrency': option['price']['currency']
        })
    
    for hotel_code in hotel_dict:
        for board_code in hotel_dict[hotel_code]['board_codes']:
            hotel_dict[hotel_code]['board_codes'][board_code] = sorted(hotel_dict[hotel_code]['board_codes'][board_code], key=lambda x: x['netPrice'])
    
    return hotel_dict

# Streamlit app layout
st.title("Hotel Supplier Rates Ranking")

# settings input for client and context
col1, col2 = st.columns(2)
client = col1.text_input("Client", value="")
context = col2.text_input("Context", value="")

# Arrange check-in and check-out inputs on the same row using columns
today = pd.to_datetime("today").date()
col3, col4 = st.columns(2)
check_in_var = col3.date_input("Check-in Date", value=today + pd.DateOffset(days=1), min_value=today)
check_in = check_in_var.strftime("%Y-%m-%d")
check_out = col4.date_input("Check-out Date", value=check_in_var + pd.DateOffset(days=1), min_value=check_in_var + pd.DateOffset(days=1)).strftime("%Y-%m-%d")


# User-friendly input for occupancies
paxes_ages_input = st.text_input("Paxes Ages (comma-separated)", value="30,30")
paxes_ages = [int(age.strip()) for age in paxes_ages_input.split(",")]
occupancies = [{"paxes": [{"age": age} for age in paxes_ages]}]

hotels = st.text_area("Hotels (comma-separated IDs)", value="").split(",")

# Arrange currency, markets, language, and nationality inputs on the same row using columns
col5, col6, col7, col8 = st.columns(4)
currency = col5.selectbox("Currency", options=ISO4217_CURRENCIES)
markets = col6.selectbox("Markets (ISO2)", options=ISO2_COUNTRIES)
language = col7.selectbox("Language (ISO639-1)", options=ISO639_LANGUAGES)
nationality = col8.selectbox("Nationality (ISO2)", options=ISO2_COUNTRIES)

access_includes = st.text_area("Access Includes (comma-separated IDs)", value="").split(",")

criteria_search = {
    "checkIn": check_in,
    "checkOut": check_out,
    "occupancies": occupancies,
    "hotels": hotels,
    "currency": currency,
    "markets": markets,
    "language": language,
    "nationality": nationality
}

settings = {
    "client": client,
    "context": context,
    "testMode": False,
    "timeout": 25000,
    "plugins": [
        {
            "step": "RESPONSE",
            "pluginsType": {
                "type": "PRE_STEP",
                "name": "cheapest_price",
                "parameters": [{"key": "primaryKey", "value": "hotel,supplier,board"}]
            }
        }
    ]
}

filter_search = {
    "access": {
        "includes": access_includes
    }
}

# Button to trigger the search
all_fields_filled = all([
    client,       # Client must be filled
    context,      # Context must be filled
    len(hotels) > 0 and hotels[0] != "",  # At least one hotel must be entered
    len(access_includes) > 0 and access_includes[0] != ""  # At least one access code must be entered
])

# Button to trigger the search, disabled if fields are not filled
search_button = st.button("Search", disabled=not all_fields_filled)

if search_button:
    # Check the number of hotel codes
    if len(hotels) > MAX_HOTEL_CODES:
        st.error(f"Error: You have entered {len(hotels)} hotel codes, but the maximum allowed is {MAX_HOTEL_CODES}.")
    else:
        data = fetch_hotel_rates(criteria_search, settings, filter_search)
        ranked_suppliers = rank_suppliers(data)
        
        if ranked_suppliers:
            for hotel_code in ranked_suppliers:
                hotel_name = ranked_suppliers[hotel_code]['name']
                st.subheader(f"Hotel: {hotel_name} (Code: {hotel_code})")
                
                board_codes = ranked_suppliers[hotel_code]['board_codes']
                unique_board_codes = sorted(board_codes.keys())
                df_dict = {board_code: [] for board_code in unique_board_codes}
                max_length = max(len(board_codes[board_code]) for board_code in unique_board_codes)
                
                for i in range(max_length):
                    for board_code in unique_board_codes:
                        if i < len(board_codes[board_code]):
                            supplier_info = board_codes[board_code][i]
                            cell_content = f"{supplier_info['supplierCode']} (Access: {supplier_info['accessCode']})<br>{supplier_info['roomDescription']}<br>Net: {supplier_info['netPrice']} {supplier_info['netCurrency']}"
                            df_dict[board_code].append(cell_content)
                        else:
                            df_dict[board_code].append('')
                
                df = pd.DataFrame(df_dict)
                
                # Convert the DataFrame to HTML for display
                html_table = df.to_html(escape=False, index=False)
                st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.error("No valid supplier data found.")
