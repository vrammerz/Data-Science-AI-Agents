import pandas as pd  # version 2.2.1
from serpapi import GoogleSearch  # version 2.4.2
import boto3  # version 1.34.98
import re
import time

# Initialize SerpAPI key and AWS clients
SERP_API_KEY = 'API-KEY'
comprehend = boto3.client('comprehend')  # detects entities


def extract_entity(text, entity_type):
    '''
    Extracts the first entity of a given type from the provided text using Amazon Comprehend.

    Args:
        text (str): The text from which to extract the entity.
        entity_type (str): The type of entity to extract (e.g., 'PERSON', 'LOCATION').

    Returns:
        str: The first entity of the specified type found in the text, or '-' if none is found.

    Example:
        >>> extract_entity("John Doe works at OpenAI in San Francisco.", "LOCATION")
        'San Francisco'
    '''
    response = comprehend.detect_entities(Text=text, LanguageCode='en')
    entities = [
        entity['Text'] for entity in response['Entities']
        if entity['Type'] == entity_type
    ]
    return entities[0] if entities else '-'


def extract_full_name(text):
    '''
    Extracts the longest full name from the text using Amazon Comprehend.

    Args:
        text (str): The text from which to extract the full name.

    Returns:
        str: The longest name found in the text, or '-' if none is found.

    Example:
        >>> extract_full_name("John Doe and Jane Smith are attending the conference.")
        'John Doe'
    '''
    response = comprehend.detect_entities(Text=text, LanguageCode='en')
    person_entities = [
        entity['Text'] for entity in response['Entities']
        if entity['Type'] == 'PERSON'
    ]
    return max(person_entities, key=len) if person_entities else '-'


def extract_phone_number(text):
    '''
    Extracts the first phone number from the provided text using a regular expression.

    Args:
        text (str): The text from which to extract the phone number.

    Returns:
        str: The first phone number found in the text, or '-' if none is found.

    Example:
        >>> extract_phone_number("Contact us at +1 (555) 123-4567 for more information.")
        '+1 (555) 123-4567'
    '''
    phone_pattern = r'\+?[\d\s()-]{10,20}'
    matches = re.findall(phone_pattern, text)
    return re.sub(r'\s+', ' ', matches[0]).strip() if matches else '-'


def extract_email(text):
    '''
    Extracts the first email address from the provided text using a regular expression.

    Args:
        text (str): The text from which to extract the email address.

    Returns:
        str: The first email address found in the text, or '-' if none is found.

    Example:
        >>> extract_email("You can reach us at support@example.com for assistance.")
        'support@example.com'
    '''
    email_pattern = (
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
    match = re.search(email_pattern, text)
    return match.group(0) if match else '-'


def search_linkedin(name, company, title):
    '''
    Searches for a LinkedIn profile URL based on the provided name, company, and title.

    Args:
        name (str): The name of the individual to search for.
        company (str): The company where the individual works.
        title (str): The title or position of the individual.

    Returns:
        str: The LinkedIn profile URL, or '-' if none is found.

    Example:
        >>> search_linkedin("John Doe", "OpenAI", "Software Engineer")
        'https://www.linkedin.com/in/johndoe'
    '''
    params = {
        "engine": "google",
        "q": f"{name} {title} {company} site:linkedin.com",
        "api_key": SERP_API_KEY,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    if 'organic_results' in results and results['organic_results']:
        return results['organic_results'][0].get('link', '-')
    return '-'


def search_executive_info(company, title):
    '''
    Searches for executive information, including name, email, LinkedIn profile, and location.

    Args:
        company (str): The name of the company where the executive works.
        title (str): The title or position of the executive (e.g., 'CFO', 'CTO').

    Returns:
        tuple: A tuple containing the name, email, LinkedIn profile URL, and location of the executive.
               If any of these cannot be found, '-' is returned for that value.

    Example:
        >>> search_executive_info("OpenAI", "CFO")
        ('Jane Doe', 'jane.doe@example.com', 'https://www.linkedin.com/in/janedoe', 'San Francisco')
    '''
    params = {
        "engine": "google",
        "q": f"{title} {company}",
        "api_key": SERP_API_KEY,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    name = email = linkedin = location = '-'

    if 'organic_results' in results and results['organic_results']:
        for result in results['organic_results']:
            snippet = result.get('snippet', '')
            title_lower = title.lower()
            if title_lower in snippet.lower() or title_lower in result.get('title', '').lower():
                name = extract_full_name(snippet + ' ' + result.get('title', ''))
                if name != '-':
                    location = extract_entity(snippet, 'LOCATION')
                    email = extract_email(snippet)
                    linkedin = search_linkedin(name, company, title)
                    break

    return name, email, linkedin, location


def get_company_info(company):
    '''
    Fetches information about a company, including executive details and phone number.

    The function iterates over a list of executive titles (CFO, COO, CTO, Partner),
    searches for each title at the given company, and collects information such as
    the executive's name, email, LinkedIn profile, and location.

    Args:
        company (str): The name of the company for which to fetch information.

    Returns:
        dict: A dictionary containing the company's executive information and phone number.
              The keys in the dictionary are formatted as '{Title} Name', '{Title} Email',
              '{Title} LinkedIn', '{Title} Location', and 'Company Phone'.

    Example:
        >>> get_company_info("OpenAI")
        {
            'CFO Name': 'Jane Doe',
            'CFO Email': 'jane.doe@example.com',
            'CFO LinkedIn': 'https://www.linkedin.com/in/janedoe',
            'CFO Location': 'San Francisco',
            'Company Phone': '+1 (555) 123-4567'
        }
    '''
    executives = ['CFO', 'COO', 'CTO', 'Partner']
    company_info = {}

    for exec_title in executives:
        name, email, linkedin, location = search_executive_info(company, exec_title)
        company_info[f"{exec_title} Name"] = name
        company_info[f"{exec_title} Email"] = email
        company_info[f"{exec_title} LinkedIn"] = linkedin
        company_info[f"{exec_title} Location"] = location

    # Fetching company phone number
    phone_params = {
        "engine": "google",
        "q": f"{company} contact phone number",
        "api_key": SERP_API_KEY
    }
    phone_search = GoogleSearch(phone_params)
    phone_results = phone_search.get_dict()
    company_info["Company Phone"] = '-'
    if 'organic_results' in phone_results and phone_results['organic_results']:
        for result in phone_results['organic_results']:
            snippet = result.get('snippet', '')
            phone_number = extract_phone_number(snippet)
            if phone_number != '-':
                company_info["Company Phone"] = phone_number
                break

    return company_info


def autofill_csv(input_file, output_file):
    '''
    Autofills a CSV file with company information, including executive details and phone numbers.

    This function reads a CSV file containing a list of companies, fetches information
    for each company using the get_company_info function, and fills in any missing data
    in the CSV. The updated CSV is then saved to a specified output file.

    Args:
        input_file (str): The path to the input CSV file containing a list of companies.
        output_file (str): The path to the output CSV file where the filled-in data will be saved.

    Returns:
        None

    Example:
        >>> autofill_csv('input.csv', 'output.csv')
        Autofilled CSV saved to output.csv
    '''
    df = pd.read_csv(input_file)

    for index, row in df.iterrows():
        company_name = row['FIRM NAME']
        print(f"Processing {company_name}...")
        info = get_company_info(company_name)
        for key, value in info.items():
            if pd.isna(df.at[index, key]) or df.at[index, key] == '' or df.at[index, key] == '-':
                df.at[index, key] = value
        time.sleep(3)  # Increased delay to avoid hitting rate limits

    df.to_csv(output_file, index=False)
    print(f"Autofilled CSV saved to {output_file}")


# Usage
input_file = '/Users/vedramesh/Desktop/.../file_to_autofill.csv' # File to autofill
output_file = '/Users/vedramesh/Desktop/.../file_results.csv' # File that will have the autofilled results
autofill_csv(input_file, output_file)
