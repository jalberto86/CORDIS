# Connect to the CORDIS API

import base64
import requests
import datetime
import xml.etree.ElementTree as ET
import json

API_KEY = "628b8f3609900928861087f555d7f9a4b44f20a0"
BASE_URL = "https://cordis.europa.eu/api/dataextractions"


def get_extraction(query, output_format="json"):
    url = f"{BASE_URL}/getExtraction"
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


# Example usage
#query = "contenttype='project' AND (programme/code='H2020') AND 'biofuel'"
query = "contenttype='project' AND (programme/code='HORIZON','H2020','FP7','FP6','FP5') AND ('biofuel' OR 'bioenergy')"
result = get_extraction(query)
print(result)
