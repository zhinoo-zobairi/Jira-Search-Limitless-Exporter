import requests
from requests.auth import HTTPBasicAuth
import json
import csv

url = "https://axelspringer-test.atlassian.net/rest/api/3/search"

auth = HTTPBasicAuth("xxx@axelspringer.com", "Your_Token")

headers = {
  # This header tells the server (Jira API) that the client (your code) expects to receive data in JSON format: "I accept responses in the JSON format."
    "Accept": "application/json",
  # This header indicates the type of data that is being sent in the request body. In this case, it's specifying that the content being sent is in JSON format: "I am sending data to you, and it is in JSON format."
    "Content-Type": "application/json"
}

# Initialize variables: "Hey, we're going to a place with lots of information. We can't take everything at once, so let's take it step by step. We'll start at the beginning (startAt) and get information in small batches (maxResults)."
max_results = 4000
start_at = 0
total_results = max_results  # Set an initial value greater than max_results to enter the loop

# List to store rows for CSV, creating an empty list to later append rows of data to it. As the program progresses, the list (rows) will be populated with dictionaries representing Jira issues (a big empty bag where you plan to collect all the information you're going to get).
rows = []

# Pagination loop(As long as I haven't gotten all the information and I haven't reached my limit, keep going.)
while start_at < total_results and start_at < 4000:
# The request body is like a package that your code sends to the server, containing specific information or data that the server needs to understand and process. The payload dictionary represents the data you want to send in the request body. They are not generic Python concepts but rather parameters specific to the Jira API endpoint being called.
 payload = {
        "jql": 'priority = "High (migrated)" OR priority = "Low (migrated)" OR priority = "Medium (migrated)"',
   # ensures that the value of maxResults is the minimum of two values. MaxResults will be the smaller of these two values, ensuring that you don't exceed the maximum allowed and that you only request what's left to retrieve.
        "maxResults": min(100, max_results - start_at),
        "startAt": start_at
    }
# A luggage for all that you want to send: "I want details about things with certain priorities." 
  response = requests.post(
        url,
        json=payload,
        headers=headers,
        auth=auth
    )

    if response.status_code == 200:
      # You create a variable called "data" which keeps the result of json.loads(response.text). "response.text" retrieves the content of the response received from the server.If the server responds with JSON data, .text would contain a string representation of that JSON data, and you use json.loads(response.text) to parse and convert it into a Python object such as a dictionary or a list, depending on the structure of the JSON data.
        data = json.loads(response.text)
      # This line is using the get method of a dictionary to retrieve the value associated with the key 'issues' from the dictionary data. The get method allows you to specify a default value to return if the key is not found. In this case, [] (an empty list) is the default value.
        issues = data.get('issues', [])
      # This line is extracting the value associated with the key 'total' from the data dictionary. If the key doesn't exist, it sets total_results to 0.
        total_results = data.get('total', 0)

        # Going through each piece of information (issue) in the box and doing something with it.
        for issue in issues:
            key = issue.get('key', '')
            priority = issue.get('fields', {}).get('priority', {}).get('name', '')
            project_key = issue.get('fields', {}).get('project', {}).get('key', '')

            # Append to the rows list:for each iteration in the loop (each Jira issue), a dictionary is created with keys 'Issue key', 'Priority', and 'Project key', and their corresponding values are set to the variables key, priority, and project_key respectively.
            rows.append({'Issue key': key, 'Priority': priority, 'Project key': project_key})

        # Increment startAt for the next page(moving to the next set of information. You're updating where you should start next time: I didn't get everything yet. Let me go back and get more until I have it all. It keeps going back until it has all the information or until it reaches a limit you set (4000).
        start_at += len(issues)
    else:
        print(f"Error: {response.status_code}, {response.text}")
        break

# Write to CSV file(deciding where to put all the information you collected. It's the file where you'll save your bag of information.)
csv_file_path = 'jira_search_result.csv'
with open(csv_file_path, 'w', newline='') as csv_file:
    fieldnames = ['Issue key', 'Priority', 'Project key']
  # a helper who knows how to take the information from your bag and neatly organize it in a file.
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

  
  # Telling the helper to write the titles (headers) and the information (rows) in the file.
    csv_writer.writeheader()
    csv_writer.writerows(rows)

print(f"CSV export successful. CSV file created at: {csv_file_path}")
