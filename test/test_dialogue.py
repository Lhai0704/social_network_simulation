import requests
import json


def start_dialogue(node1_id, node2_id, num_turns=5):
    url = "http://localhost:8000/start-dialogue/"
    params = {
        "node1_id": node1_id,
        "node2_id": node2_id,
        "num_turns": num_turns
    }

    try:
        response = requests.post(url, params=params)

        # Print the raw response for debugging
        print("Raw response:", response.text)

        # Check if the response status code is successful
        response.raise_for_status()

        # Try to parse the JSON response
        data = response.json()
        print("Dialogue history:")
        for turn in data['history']:
            print(f"Turn {turn['turn']}: {turn['sender']} to {turn['receiver']}: {turn['content']}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
        print(f"Response content: {response.text}")
    except KeyError as e:
        print(f"Expected key not found in the response: {e}")
        print(f"Response content: {response.json()}")


# Example usage
start_dialogue(1, 2, 5)