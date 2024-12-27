from selenium.webdriver.common.by import By
import re

def currency_to_number(value_str):
    """Convert a currency string like '$5,919.96' to a float."""
    return float(value_str.replace("$", "").replace(",", ""))

def extract_address_informatin(driver):
    """Extract the full address and roll number from the 'address-information' section."""
    try:
        # Locate the paragraph by its ID
        address_info = driver.find_element(By.ID, "address-information").text

        # Split the text to extract the roll number
        # Expected format: "184 MAIN ST \nRoll number: 0614.052.801.01200.0000"
        lines = address_info.split("\n")
        full_address = lines[0]
        for line in lines:
            if "Roll number:" in line:
                # Extract the number after "Roll number:"
                roll_number = line.split("Roll number:")[1].strip().replace(".","")+"0" #need to append a '0'
                return full_address, roll_number
    except Exception as e:
        print(f"Error extracting roll number: {e}")
        return None

def extract_table_year(driver):
    """Extract the year of the table based on the 'caption' tag"""
    
    try:
        caption = driver.find_element(By.TAG_NAME, "caption").text
        match = re.search(r'\b\d{4}\b',caption) # year is 4 digits followed by end of line
        if match:
            return match.group(0) #return matched year
        else:
            print("No year founds in the caption")
            return None
    except Exception as e:
        print(f"Error Extracting table year: {e}")
        return None


def extract_table_data(table_element):
    data = {}
    rows = table_element.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) == 2:  # Ensure it's a key-value pair row
            key = cells[0].text.strip()
            value = currency_to_number(cells[1].text.strip())
            data[key] = value
    return data