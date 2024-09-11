from serpapi import GoogleSearch

# Function to fetch contact information using SERP API
def fetch_contact_info_with_serp(pe_fund_name, serp_api_key):
    params = {
        "engine": "google",
        "q": f"{pe_fund_name} contact information",
        "api_key": serp_api_key
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    contact_info = {
        'emails': [],
        'phones': [],
        'addresses': [],
        'websites': []
    }
    
    for result in results.get('organic_results', []):
        website_url = result.get('link')
        contact_info['websites'].append(website_url)
        
        # Extract snippets for potential contact info
        snippet = result.get('snippet', '')
        if 'email' in snippet.lower():
            contact_info['emails'].append(snippet)
        if 'phone' in snippet.lower():
            contact_info['phones'].append(snippet)
        if 'address' in snippet.lower():
            contact_info['addresses'].append(snippet)
    
    return contact_info

# Main function to gather contact information
def gather_pe_contact_info(pe_fund_names, serp_api_key):
    for fund_name in pe_fund_names:
        print(f"Gathering contact information for: {fund_name}")
        try:
            contact_info = fetch_contact_info_with_serp(fund_name, serp_api_key)
            print(f"Contact Information for {fund_name}:")
            print("Emails:")
            for email in contact_info['emails']:
                print(f"  - {email}")
            print("Phones:")
            for phone in contact_info['phones']:
                print(f"  - {phone}")
            print("Addresses:")
            for address in contact_info['addresses']:
                print(f"  - {address}")
            print("Websites:")
            for website in contact_info['websites']:
                print(f"  - {website}")
        except Exception as e:
            print(f"Error gathering contact information for {fund_name}: {e}")
        print("-" * 50)

# Example usage
if __name__ == "__main__":
    PE_FUND_NAMES = ['Blackstone', 'KKR', 'Carlyle Group']  # Replace with actual PE fund names
    SERP_API_KEY = 'API-KEY'
    
    gather_pe_contact_info(PE_FUND_NAMES, SERP_API_KEY)