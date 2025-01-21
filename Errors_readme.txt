Examples of possible errors

FIXED accents "C\u00f4te-des-Neiges Rd" instead of "Côte-des-Neiges" # script appears to have handled it in College. probably on the later portion after encoding = 'utf-8' was incorporated
FIXED Period '.'  after street direction "164 Hinton Ave N." instead of "164 Hinton Ave N". addressed with rstrip('.')
Selenium dropping space " " between address number and street name. Consider setting a local variable before  send_keys()
Addresses don't pull roll number from parcel. 
somewhat random. example: Invalid: 99 Gilchrist Ave  : Error: No matching property found. but has return is valid when performed manually.

batch size isn't increasing as expected. len remains 0 for ~20 then len = 1 for ~5 then increases by 1 on every loop. Behaviour is unaffected by validity of address.

fixed. main scrape prioritizes parcel roll number first. Many municipal addresse to single parcel. E.g., 125 Viewmount Drive and 127 Viewmount Drive --> 125-127 Viewmount Drive. In Addresses_.csv the field "RELATED_AD" and "ADDRTYPE" may be a useful features. scape should also pull the assessment table title to confirm how the property is described from an assessment roll perspective.

Properties like 5 Forester Cres return error "Your search has returned multiple properties...". Adding a qualifier like "C" to "5C FORESTER CRES: 0614.120.830.34004.0000 " is a valid return. However, the roll number for this property differs from the parcel roll number (0614.120.830.33900.34113)

Parcel 06143008163399400000 contains holes and streets and surrounds >50 addresses and individual parcels. E.g., 1 Kinmount Private. The TaxLookup.py duplicates the return for addresses within 06143008163399400000.

some parcel assessment roll numbers have disconnected multiple polygons. For example "6140417012160100000" has three disjointed polygons but only one is assigned the aggregate tax value of the 2 x addresses within. Each independent parcel has a differnt ODF_ID so I suspect that is where the error is.

need to validate whether batch saving in the middle of process_address is working properly. It appears that all addresses associated with the processessed PARCEL_ASSESSEMENT_ROLL_NUMBER are removed from to_be_checked at the save_to_json() call, regardless if those addressesed have actually been processed.