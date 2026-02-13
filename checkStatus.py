import requests

API_KEY = "628b8f3609900928861087f555d7f9a4b44f20a0"  # Replace with your actual API key
TASK_ID = 158842746  # Replace with the task ID you received
BASE_URL = "https://cordis.europa.eu/api/dataextractions"


def get_extraction_status(task_id):
    url = f"{BASE_URL}/getExtractionStatus"
    params = {
        "taskId": task_id,
        "key": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed with status code {response.status_code}", "details": response.text}


# Check the status of your extraction
status = get_extraction_status(TASK_ID)
print(status)