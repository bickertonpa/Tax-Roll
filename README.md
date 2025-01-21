# Tax-Roll

# Test file
The test file contains parcel and address combinations that verify the following cases:

1. Invalid PARCEL_ASSESSMENT_ROLL_NUMBER with multiple addresses
    input: 6140421010360003708
    return: 
        10 valid addresses: 
            9 x 446 Gilmore; and
            1 x 442 Gilmore
        1 invalid aaddress:
            1 x 446 Gilmore
4. Invalid PARCEL_ASSESSMENT_ROLL_NUMBER with address error: "Your search has returned multiple properties..."
    input: 06140420011450114523
    return
        3 x invalid addresses:
            1 x "Your search has returned multiple properties..."(342 MacLaren); and
            2 x "No matching property found" (338, 340 MacLaren)
            
6. NULL PARCEL_ASSESSMENT_ROLL_NUMBER with at least one valid address
    input: 1609 A Lunenberg Cres with a  NULL PARCEL_ASSESSMENT_ROLL_NUMBER which is converted to "0614000000000000000"
    return: valid address

7. Valid PARCEL_ASSESSMENT_ROLL_NUMBER with single related address
    input: 06146001852060000000
    return: valid parcel 41 Tauvette St
8. Valid PARCEL_ASSESSMERNT_ROLL_NUMBER with multiple related addresses
    input:6141208303330000000
    return: 1 x valid parcel (82-2 HAMMILL CRT) negating the need to query 121 addresses within that parcel (XXX Hammil)
9. (REMOVED FROM TEST SCRIPT - FAILURE IS ADDRESSED UPSTREAM IN DATA FLOW PARCEL VALIDATION). Valid PARCEL_ASSESSMENT_ROLL_NUMBER for polygon overlapping address points AND individual address parcel polygonsS
    input; 06143008163399400000
    return: 65 addresses within (eg 95 Kinmount). need to manually remove from parcel layer of ward geopackage. Use the select by location "CONTAIN" to identify parcels of concern.
10. Valid PARCEL_ASSESSMENT_ROLL_NUMBER for parcel with more than one closed polygons:
    input: 6140417012160100000. This ASSESSMENT_ROLL_NUMBER is associated with 3 x independent polygons. QGIS model "Points to Polygons" was updated to dissolve polygon on the "ASSESSMENT_ROLL_NUMBER" attribute value.
    return: valid parcel, negating need to query 2 x addresses within parcel:
        199 Slater St. Returns "Your search has returned multiple properties..."; and
        185 Slater St. Returns valid address

11. Scientific PARCEL_ASSESSMENT_ROLL_NUMBER
    input: 6.14271830098e+18
    return: valid parcel "DAVID MANCHEST RD"
