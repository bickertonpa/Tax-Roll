import csv
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import random
import table_extract as tb
import json
import os


# Initialize driver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")  # Optional, improve performance in headless mode
chrome_options.add_argument("--log-level=1") #suppress Tensorflow related messages

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
Ward = Wards['8']

# Setup file paths
input_csv_path = f"Addresses/Addresses_{Ward}.csv"
output_csv_path = f"Output/{Ward}.json"
checkpoint_file = f"Output/{Ward}_to_be_checked.json"

# data frames
addresses_df = pd.read_csv(input_csv_path)
addresses_df['FULL_ROADN'] = addresses_df['FULL_ROADN'].str.rstrip('.') # Clean the road names by removing trailing periods
output_data = pd.DataFrame()

# Start for checkpoint
if os.path.exists(checkpoint_file):
    with open(checkpoint_file,"r") as f:
        to_be_checked = json.load(f)
else:
    with open(checkpoint_file, 'w') as f:
        json.dump(addresses_df.to_dict(orient = "records"), f, indent=4, ensure_ascii=False)
        to_be_checked = addresses_df.to_dict(orient = "records") #converts the dataframe to a list of dicts

# Function to extract key-value pairs from a table
def save_to_csv(data, file_name = 'output.csv'):
    with open(output_csv_path, mode = 'a', newline = '', encoding = 'utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data) # append rows
        print('Saving batch ...')

def wait_for_page(driver, timeout=15):
    """Wait for page to load."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.find_elements(By.XPATH,'//*[@id="main-content"]/ott-radio/div/fieldset/div/div[2]/label')  # Valid tax table
        )
        return True
    except Exception as e:
        print(f"Timeout or error while waiting for page: {e}")
        return False
    
def wait_for_results(driver, timeout=15):
    """Wait for either the valid tax table or an error message."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.find_elements(By.ID, "year1-tax-info") or  # Valid tax table
                      d.find_elements(By.ID, "assessment-search-result-message")  # Error message
        )
        return True
    except Exception as e:
        print(f"Timeout or error while waiting for results: {e}")
        return False

# Initialization
print(Ward,": ",len(to_be_checked), " remaining")


for address in to_be_checked[:]:
    print("Batch size: ",len(output_data))
    driver = webdriver.Chrome(options=chrome_options)
    # open the url
    url = 'https://propertytaxes-taxesfoncieres.ottawa.ca/en?t=taxassessmentlookup'
    driver.get(url)

    if wait_for_page(driver):
        # Set Search by Address
        WebDriverWait(driver,timeout = 15).until(
            lambda d: d.find_element(By.XPATH,'//*[@id="main-content"]/ott-radio/div/fieldset/div/div[2]/label')) # "Look up existing tax and assessment information"
        time.sleep(random.uniform(2, 5))
        driver.find_element(By.XPATH,'//*[@id="main-content"]/ott-radio/div/fieldset/div/div[2]/label').click()
        WebDriverWait(driver,timeout = 15).until(
            lambda d: d.find_element(By.XPATH,'//*[@id="property-tax-assessment-widget"]/div/form/ott-radio/div/fieldset/div/div[1]/label')) # "Address"
        driver.find_element(By.XPATH,'//*[@id="property-tax-assessment-widget"]/div/form/ott-radio/div/fieldset/div/div[1]/label').click()
        
        # Define Term of Service and Submit buttons
        WebDriverWait(driver,timeout = 15).until(
            lambda d: d.find_element(By.XPATH,'//*[@id="assessmentTermOfService"]'))
        tos_button = driver.find_element(By.XPATH,'//*[@id="assessmentTermOfService"]')
        tos_button.click()
        submit_button = driver.find_element(By.XPATH,'//*[@id="submit-button"]')

        # Extract fields
        street_number = address['ADDRNUM']
        street_name = address['FULL_ROADN'] #includes DIRECTION
        unit = address['UNIT'] if pd.notna(address['UNIT']) else ""
        qualifier = address['QUALIFIER'] if pd.notna(address['QUALIFIER']) else ""
        
        try:

            #input values into the form
            driver.find_element(By.XPATH,'//*[@id="propertyStreetNumber"]').clear()
            driver.find_element(By.XPATH,'//*[@id="propertyStreetNumber"]').send_keys(street_number)
            
            driver.find_element(By.XPATH,'//*[@id="propertyStreetName"]').clear()
            driver.find_element(By.XPATH,'//*[@id="propertyStreetName"]').send_keys(street_name)

            driver.find_element(By.XPATH,'//*[@id="propertyUnit"]').clear()
            driver.find_element(By.XPATH,'//*[@id="propertyUnit"]').send_keys(unit)

            driver.find_element(By.XPATH,'//*[@id="propertyQualifier"]').clear()
            driver.find_element(By.XPATH,'//*[@id="propertyQualifier"]').send_keys(qualifier)

            submit_button.click()


            # Wait for results
            if wait_for_results(driver):
                # Initialize address data
                address_data = {
                    "Street Number": street_number,
                    "Street Name": street_name,
                    "Apartment": unit,
                    "Qualifier": qualifier,
                }

                # Check if the valid tax table is present
                if driver.find_elements(By.ID, "year1-tax-info"):
                    print(f"Valid: {street_number} {street_name} {unit} {qualifier}...")
                    
                    #Find tables               
                    year1_assessment_table = driver.find_element(By.ID, "year1-assessment")  # Replace with actual table ID
                    year1_tax_table = driver.find_element(By.ID, "year1-tax-info")  # Replace with actual table ID
                    year1_year = tb.extract_table_year(year1_tax_table)
                    full_address, roll_number = tb.extract_address_informatin(driver)
                    current_assessment_data = tb.extract_table_data( year1_assessment_table)
                    current_tax_data = tb.extract_table_data(year1_tax_table)

                    # append address_data
                    address_data["Roll Number"] = roll_number
                    address_data.update({f"{year1_year} - {k}": v for k, v in current_assessment_data.items()})
                    address_data.update({f"{year1_year} - {k}": v for k, v in current_tax_data.items()})
                    try:
                        #look for previous year tax data
                        year2_assessment_table = driver.find_element(By.ID, "year2-assessment")  # Replace with actual table ID
                        year2_tax_table = driver.find_element(By.ID, "year2-tax-info")  # Replace with actual table ID
                        year2_year = tb.extract_table_year(year2_tax_table)
                        previous_assessment_data = tb.extract_table_data(year2_assessment_table)
                        previous_tax_data = tb.extract_table_data(year2_tax_table)
                        address_data.update({f"{year2_year} - {k}": v for k, v in previous_assessment_data.items()})
                        address_data.update({f"{year2_year} - {k}": v for k, v in previous_tax_data.items()})
                        
                    except:
                        pass

                elif driver.find_elements(By.ID, "assessment-search-result-message"):
                    # Invalid address: Extract error message
                    error_message = driver.find_element(By.ID, "assessment-search-result-message").text
                    print(f"Invalid: {street_number} {street_name} {unit} {qualifier}: Error: {error_message}")
                    address_data["Error Message"] = error_message

                # Append address data to output
                output_data = pd.concat([output_data, pd.DataFrame([address_data])], ignore_index=True)
        
                # Remove successfully processed address
                to_be_checked.remove(address)

        except Exception as e:
            #print(f"Error inputing address {address}: {e}")
            pass
        driver.quit()
        #time.sleep(random.uniform(2, 5))
        # Periodically save progress
        if len(output_data) >= 5 or len(output_data) >= len(to_be_checked): # batch size
            with open(checkpoint_file, "w") as f:
                json.dump(to_be_checked, f, indent=4, ensure_ascii=False)
            print(f"Progress saved. {len(to_be_checked)} addresses remaining.")
            output_data.to_json(output_csv_path, orient="records", lines=True, mode="a")
            print('Saving batch...')
            output_data = pd.DataFrame() # clear memory

# Save the output data to CSV
output_data.to_json(output_csv_path, mode = 'a', lines = True, orient = "records", index=False)
print('Completed all addresses')