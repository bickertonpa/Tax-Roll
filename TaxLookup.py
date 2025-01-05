import csv
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import random
import table_extract as tb
import json
import os
import re

Wards = {
    '1':'Orléans East-Cumberland',
    '2':'Orléans West-Innes',
    '3':'Barrhaven West',
    '4':'Kanata North',
    '5':'West Carleton-March',
    '6':'Stittsville',
    '7':'Bay',
    '8':'College',
    '9':'Knoxdale-Merivale',
    '10':'Gloucester-Southgate',
    '11':'Beacon Hill-Cyrville',
    '12':'Rideau-Vanier',
    '13':'Rideau-Rockcliffe',
    '14':'Somerset',
    '15':'Kitchissippi',
    '16':'River',
    '17':'Capital',
    '18':'Alta Vista',
    '19':'Orléans South-Navan',
    '19':'Orléans South-Navan',
    '20':'Osgoode',
    '21':'Rideau-Jock',
    '22':'Riverside South-Findlay Creek',
    '23':'Kanata South',
    '24':'Barrhaven East'
}

# Select the Ward
Ward = Wards['24']

# Setup file paths
input_parcel_path = f"Addresses/College_test_address with related parcel.csv"
input_address_path = f"Addresses/College_test_address with related parcel.csv"
output_csv_path = f"Output/College_test.json"
checkpoint_file = f"Output/College_test_to_be_checked.json"

# data frames
addresses_df = pd.read_csv(input_address_path)
#output_data = pd.DataFrame()

# Start for checkpoint
if os.path.exists(checkpoint_file):
    with open(checkpoint_file,"r") as f:
        to_be_checked = json.load(f)
else:
    with open(checkpoint_file, 'w') as f:
        json.dump(addresses_df.to_dict(orient = "records"), f, indent=4, ensure_ascii=False)
        to_be_checked = addresses_df.to_dict(orient = "records") #converts the dataframe to a list of dicts

# Initialize driver
def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")  # Optional, improve performance in headless mode
    chrome_options.add_argument("--log-level=1") #suppress Tensorflow related messages
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def save_to_json(data, path):
    """
    Saves the given data as a properly formatted JSON array in the file.

    Args:
        data (list): List of dictionaries to save as JSON.
        path (str): Path to the output JSON file.
    """
    # If the file already exists, read existing data and append new data
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            try:
                existing_data = json.load(file)  # Load existing JSON array
            except json.JSONDecodeError:
                existing_data = []  # If file is empty or invalid, start fresh
    else:
        existing_data = []

    # Append new data to the existing data
    existing_data.extend(data)

    # Write the combined data back to the file
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)
    print(f"Saved {len(data)} records to {path}.")

# Function to wait for a page element
def wait_for_element(driver, by, value, timeout=15):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return True
    except Exception as e:
        print(f"Timeout or error while waiting for element: {e}")
        return False

def wait_for_results(driver, timeout=15):
    """
    Waits for the results page to load after a search.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        timeout (int): Maximum time to wait in seconds.

    Returns:
        bool: True if results or error message is found, False otherwise.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.find_elements(By.ID, "year1-tax-info") or
                      d.find_elements(By.ID, "assessment-search-result-message")
        )
        return True
    except Exception as e:
        print(f"Timeout or error while waiting for results: {e}")
        return False

def save_batch_if_needed(batch, batch_size, output_path):
    """
    Saves the current batch to the JSON file if it reaches the batch size.

    Args:
        batch (list): The current batch of data to save.
        batch_size (int): The number of items required to trigger a save.
        output_path (str): Path to the JSON file.
    """
    if len(batch) >= batch_size:
        save_to_json(batch, output_path)
        batch.clear()  # Clear the batch after saving

def convert_scientific_to_full_form_with_leading_zero(sci_str):
    """
    Convert a scientific notation string into full form with a leading zero as a string.
    
    Args:
        sci_str (str): The input string in scientific notation.
        
    Returns:
        str: The full form of the number as a string with a leading zero.

    Example usage"
        sci_string = "6.14120565035e+18"
        result = convert_scientific_to_full_form_with_leading_zero(sci_string)
        print(result)  # Output: '06141205650350000000'

    """
    try:
        # Convert the string to a float, then format it into full form
        full_form = f"{float(sci_str):f}"
        # Remove any trailing zeros and the decimal point if not needed
        full_form = full_form.rstrip('0').rstrip('.') if '.' in full_form else full_form
        # Add a leading zero if necessary
        return '0' + full_form
    except ValueError:
        return "Invalid input"

def process_group(driver, group, to_be_checked, batch_data, batch_size = 2):
    """
    Processes a group of addresses associated with a common `PARCEL_ASSESSMENT_ROLL_NUMBER`.
    If successful using the roll number, all related addresses are removed from `to_be_checked`.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        group (list): List of addresses sharing a common PARCEL_ASSESSMENT_ROLL_NUMBER.
        to_be_checked (list): List of addresses to check.

    Returns:
        group_data: a data frame of all extracted information from either the PARCEL_ASSESSMENT_ROLL or contained addresses.
    """
    # Use the first address in the group for roll number search
    group_data = pd.DataFrame()
    primary_address = group[0]
    parcel_roll_number = '0' + str(primary_address.get('PARCEL_ASSESSMENT_ROLL_NUMBER'))

    if parcel_roll_number and not pd.isna(parcel_roll_number):
        try:
           
            # Setup driver
            url = 'https://propertytaxes-taxesfoncieres.ottawa.ca/en?t=taxassessmentlookup'
            driver.get(url)
            # Wait for the page to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/ott-radio/div/fieldset/div/div[2]/label'))
            )
            # Interact with the page
            driver.find_element(By.XPATH,'//*[@id="main-content"]/ott-radio/div/fieldset/div/div[2]/label').click() # "Look up existing tax and assessment information"
            driver.find_element(By.XPATH,'//*[@id="property-tax-assessment-widget"]/div/form/ott-radio/div/fieldset/div/div[2]/label').click() # "Roll Number"

            # Fill out the form
            driver.find_element(By.XPATH,'//*[@id="propertyRollNumber"]').clear()
            driver.find_element(By.XPATH,'//*[@id="propertyRollNumber"]').send_keys(parcel_roll_number) 

            # Submit the form
            WebDriverWait(driver,timeout = 15).until(
                lambda d: d.find_element(By.XPATH,'//*[@id="assessmentTermOfService"]'))
            driver.find_element(By.XPATH,'//*[@id="assessmentTermOfService"]').click()
            driver.find_element(By.XPATH, '//*[@id="submit-button"]').click()

            # Wait for results
            if wait_for_results(driver):
                if extract_tax_data(driver):
                    data = extract_tax_data(driver)
                    data.update({"PARCEL_ASSESSMENT_ROLL_NUMBER": parcel_roll_number})
                    print(f"Valid parcel: {data['EXTRACTED_ADDRESS_SUMMARY']} ({primary_address.get('PARCEL_ASSESSMENT_ROLL_NUMBER')})")
                    batch_data.append(data)
                    save_batch_if_needed(batch_data, batch_size, output_csv_path)

                else:
                    pass
            else:
                pass               

        except Exception as e:
            # Failed attempt to search by parcel roll number. Attent to search by contained addresses
            print(f"Error processing {primary_address.get('PARCEL_ASSESSMENT_ROLL_NUMBER')}")
            print(f"Attempting search of {len(group)} address(es) contained within parcel...")
            for i, address in enumerate(group):
                try:
                    data = process_address(driver, address)
                    #group_data = pd.concat([group_data, pd.DataFrame([data])], ignore_index=True)
                    batch_data.append(data)
                    save_batch_if_needed(batch_data, batch_size, output_csv_path)
                except:
                    print(f"Error processing address")
            if batch_data:
                save_batch_if_needed(batch_data, batch_size, output_csv_path)

    if batch_data:
        save_batch_if_needed(batch_data, batch_size, output_csv_path)

    #return group_data      

def extract_tax_data(driver):
    """
    Extracts tax data from the results page.

    Args:
        driver (WebDriver): Selenium WebDriver instance.

    Returns:
        dict: Dictionary containing extracted tax data.
    """
    tax_data = {
            }
    #Find tables               
    year1_assessment_table = driver.find_element(By.ID, "year1-assessment")  # Replace with actual table ID
    year1_tax_table = driver.find_element(By.ID, "year1-tax-info")  # Replace with actual table ID
    year1_year = tb.extract_table_year(year1_tax_table)
    full_address, roll_number = tb.extract_address_informatin(driver)
    current_assessment_data = tb.extract_table_data( year1_assessment_table)
    current_tax_data = tb.extract_table_data(year1_tax_table)

    # append address_data
    tax_data["EXTRACTED_ASSESSMENT_ROLL_NUMBER"] = roll_number
    tax_data["EXTRACTED_ADDRESS_SUMMARY"] = full_address
    tax_data.update({f"{year1_year} - {k}": v for k, v in current_assessment_data.items()})
    tax_data.update({f"{year1_year} - {k}": v for k, v in current_tax_data.items()})
    try:
        #look for previous year tax data
        year2_assessment_table = driver.find_element(By.ID, "year2-assessment")  # Replace with actual table ID
        year2_tax_table = driver.find_element(By.ID, "year2-tax-info")  # Replace with actual table ID
        year2_year = tb.extract_table_year(year2_tax_table)
        previous_assessment_data = tb.extract_table_data(year2_assessment_table)
        previous_tax_data = tb.extract_table_data(year2_tax_table)
        tax_data.update({f"{year2_year} - {k}": v for k, v in previous_assessment_data.items()})
        tax_data.update({f"{year2_year} - {k}": v for k, v in previous_tax_data.items()})
        
    except:
        pass

    if driver.find_elements(By.ID, "assessment-search-result-message"):
        # Invalid address: Extract error message
        error_message = driver.find_element(By.ID, "assessment-search-result-message").text
        tax_data["Error Message"] = error_message

    return tax_data

def process_address(driver, address):
    """
    Process an address by first attempting to search with ASSESSMENT_ROLL_NUMBER
    and falling back to searching by address if the roll number search fails.
    
    Args:
        driver (WebDriver): Selenium WebDriver instance.
        address (dict): Dictionary containing address information.

    Returns:
        dict: A result dictionary containing the status and data or an error message.
    """
    address_data = {}

    try:
        url = 'https://propertytaxes-taxesfoncieres.ottawa.ca/en?t=taxassessmentlookup'
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/ott-radio/div/fieldset/div/div[2]/label'))
        )

        # Click the "Address" radio button
        driver.find_element(By.XPATH,'//*[@id="main-content"]/ott-radio/div/fieldset/div/div[2]/label').click() # "Look up existing tax and assessment information"
        driver.find_element(By.XPATH,'//*[@id="property-tax-assessment-widget"]/div/form/ott-radio/div/fieldset/div/div[1]/label').click()

        # Address
        street_number = str(address['ADDRNUM'])
        street_name = address['FULL_ROADN'] #includes DIRECTION
        unit = str(address['UNIT']) if pd.notna(address['UNIT']) else ""
        qualifier = str(address['QUALIFIER']) if pd.notna(address['QUALIFIER']) else ""

        # Enter address details
            #input values into the form
        driver.find_element(By.XPATH,'//*[@id="propertyStreetNumber"]').clear()
        driver.find_element(By.XPATH,'//*[@id="propertyStreetNumber"]').send_keys(street_number)
        
        driver.find_element(By.XPATH,'//*[@id="propertyStreetName"]').clear()
        driver.find_element(By.XPATH,'//*[@id="propertyStreetName"]').send_keys(street_name)

        driver.find_element(By.XPATH,'//*[@id="propertyUnit"]').clear()
        driver.find_element(By.XPATH,'//*[@id="propertyUnit"]').send_keys(unit)

        driver.find_element(By.XPATH,'//*[@id="propertyQualifier"]').clear()
        driver.find_element(By.XPATH,'//*[@id="propertyQualifier"]').send_keys(qualifier)

        # Accept Terms of Service and submit
        driver.find_element(By.XPATH, '//*[@id="assessmentTermOfService"]').click()
        driver.find_element(By.XPATH, '//*[@id="submit-button"]').click()

        # Wait for results
        if wait_for_results(driver):
            try:
                address_data.update({"street_number": street_number, "street_name": street_name, "unit": unit, "qualifier": qualifier, "PARCEL_ASSESSMENT_ROLL_NUMBER":'0'+ str(address.get('PARCEL_ASSESSMENT_ROLL_NUMBER'))})
                address_data.update(extract_tax_data(driver))
                print(f"Valid address: {address['FULL_ADDRE']}")
            except:
                pass
        elif driver.find_element(By.ID, "assessment-search-result-message"):
            error_message = driver.find_element(By.ID, "assessment-search-result-message").text
            print(f"No return found for address: {address['FULL_ADDRE']}")
        else:
            print("error wait_for_results()")

    except Exception as e:
        print(f"Error processing address {address['FULL_ADDRE']}")
    return address_data
def group_addresses_by_parcel(df):
    grouped = df.groupby('PARCEL_ASSESSMENT_ROLL_NUMBER', dropna=False).apply(
        lambda x: x.to_dict(orient='records'),
        #include_groups=False  # Ensures the grouping column is excluded
    )
    print("Number of parcels: ", len(grouped))
    return grouped.to_dict()

def main_workflow(driver, addresses_df):
    """
    Main workflow to process all addresses.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        addresses_df (DataFrame): DataFrame containing addresses to check.
    """
        # Preprocess and group by `parcel_assessment_roll_number`
    grouped_addresses = group_addresses_by_parcel(addresses_df)
    to_be_checked = addresses_df.to_dict(orient='records')  # Convert to list of dicts
    batch_data = []

    # Process each group
    for roll_number, group in grouped_addresses.items():
        if group and len(group) > 0:
            #sprint(f"Processing group with PARCEL_ASSESSMENT_ROLL_NUMBER: {roll_number}")
            process_group(driver, group, to_be_checked=[], batch_data=batch_data)
            #output_data = pd.concat([output_data, group_result], ignore_index=True)
            #output_data.to_json(output_csv_path, orient="records", force_ascii=False, indent=4)
        # Save remaining data in the batch
    if batch_data:
        save_to_json(batch_data, output_csv_path)
        batch_data.clear()

    print("All addresses processed.")

# Run the scraper
if __name__ == "__main__":
    # Initialization
    print("Number of addresses remaining: ", len(to_be_checked))
    driver = initialize_driver()
    main_workflow(driver,addresses_df)
    print("Completed all addresses.")