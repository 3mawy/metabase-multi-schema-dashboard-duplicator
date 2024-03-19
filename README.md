# Multi Schema Metabase Dashboard Helper

This Python package provides a convenient interface for interacting with the Metabase API to automate tasks such as copying and updating dashboards based on different schemas.

## Requirements

- Python 3.x
- requests library

## Installation

To use this package, you can install it via pip:

```bash
pip install metabase-api-client
```

## Usage

Here's how you can use the Metabase API Client to copy and update dashboards:

### **--> IMPORTANT NOTE <--**

**You need to convert all the questions (cards) in the dashboard to sql before being able to use this to change the schema dynamically**

```python
from metabase_api.metabase_api.api_client import MetabaseAPIClient

# Set up API credentials and parameters
api_url = "https://metabase.example.com"
username = "your_username"
password = "your_password"
database_id = 2
from_dashboard_id = 8  # Replace with the actual dashboard ID
collection_id = 130   # Replace with the actual collection ID where you want to place the copied dashboard
collection_position = 1
is_deep_copy = True
old_schema = "template_schema_name"

# Initialize the Metabase API client
api_client = MetabaseAPIClient(api_url, username, password, database_id)

# Update dashboards for different schemas
api_client.update_dashboards_for_schemas(from_dashboard_id, collection_id, collection_position, is_deep_copy, old_schema)
```

## Documentation

For detailed information about the methods and parameters provided by the `MetabaseAPIClient`, please refer to the source code comments and docstrings within the `metabase_api` package.

## Note

- Ensure that you replace placeholder values such as `api_url`, `username`, `password`, `database_id`, `from_dashboard_id`, `collection_id`, `collection_position`, and `old_schema` with your actual Metabase API credentials and parameters.
- This package assumes familiarity with the Metabase API and its endpoints. Refer to the official Metabase API documentation for more information on available endpoints and their usage.

## Disclaimer

This package is provided as-is without any warranty.
# metabase-multi-schema-dashboard-duplicator
