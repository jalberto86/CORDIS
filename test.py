import requests

API_KEY = "628b8f3609900928861087f555d7f9a4b44f20a0"
BASE_URL = "https://cordis.europa.eu/api/dataextractions"

def get_extraction(content_type, programme_code, keywords, output_format="json"):
    url = f"{BASE_URL}/getExtraction"

    # Constructing the query dynamically based on user input
    query = f"contenttype='{content_type}' AND (programme/code='{programme_code}') AND '{keywords}'"

    params = {
        "query": query,
        "outputFormat": output_format,
        "key": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed with status code {response.status_code}", "details": response.text}

# Taking user input
content_type = input("Enter content type (e.g., project): ").strip()
programme_code = input("Enter programme code (e.g., H2020): ").strip()
keywords = input("Enter search keywords (e.g., biofuel): ").strip()

# Calling the API with user inputs
result = get_extraction(content_type, programme_code, keywords)
print(result)