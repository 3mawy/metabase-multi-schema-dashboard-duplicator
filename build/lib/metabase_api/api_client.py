from collections import defaultdict

import requests


class MetabaseAPIClient:
    def __init__(self, api_url, username, password, database_id):
        self.api_url = api_url
        self.username = username
        self.password = password
        self.database_id = database_id
        self.session_token = self.get_session_token()

        self.headers = {
            "Content-Type": "application/json",
            "X-Metabase-Session": self.session_token
        }

    def get_session_token(self):
        session_url = f"{self.api_url}/api/session"
        data = {"username": self.username, "password": self.password}
        response = requests.post(session_url, json=data)

        if response.status_code == 200:
            return response.json()["id"]
        else:
            print(f"Failed to obtain session token. Status code: {response.status_code}")
            print(response.text)
            return None

    def get_dashboard(self, dashboard_id):
        get_url = f"{self.api_url}/api/dashboard/{dashboard_id}"
        response = requests.get(get_url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get dashboard. Status code: {response.status_code}")
            print(response.text)
            return None

    def update_dashboard(self, dashboard_id, modified_data):
        update_url = f"{self.api_url}/api/dashboard/{dashboard_id}"
        response = requests.put(update_url, json=modified_data, headers=self.headers)

        if response.status_code == 200:
            print("Copied dashboard updated successfully!")
            return response.json()
        else:
            print(f"Failed to update copied dashboard. Status code: {response.status_code}")
            print(response.text)
            return None

    def copy_and_update_dashboard(self, from_dashboard_id, name, old_schema, new_schema, description=None,
                                  collection_id=None,
                                  collection_position=None, is_deep_copy=None):
        existing_dashboard = self.get_dashboard(from_dashboard_id)

        if existing_dashboard:
            copy_url = f"{self.api_url}/api/dashboard/{from_dashboard_id}/copy"
            data = {
                "from-dashboard-id": from_dashboard_id,
                "name": name,
                "description": description,
                "collection_id": collection_id,
                "collection_position": collection_position,
                "is_deep_copy": is_deep_copy,
                "param_values": existing_dashboard.get("param_values"),
            }

            response = requests.post(copy_url, json=data, headers=self.headers)

            if response.status_code == 200:
                print("Dashboard copied successfully!")
                copied_dashboard_id = response.json().get("id")
                modified_data = self.get_dashboard(copied_dashboard_id)

                for dashcard in modified_data.get("dashcards", []):
                    self.update_card(dashcard["card_id"], old_schema, new_schema)

                self.update_dashboard(copied_dashboard_id, modified_data)
            else:
                print(f"Failed to copy dashboard. Status code: {response.status_code}")
                print(response.text)

    def get_card(self, card_id):
        update_url = f"{self.api_url}/api/card/{card_id}"
        response = requests.get(update_url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get card with ID {card_id}. Status code: {response.status_code}")
            print(response.text)
            return None

    def update_card(self, card_id, old_schema, new_schema):
        update_url = f"{self.api_url}/api/card/{card_id}"
        targeted_card = self.get_card(card_id)

        if targeted_card.get('name'):
            targeted_card['name'] = targeted_card['name'].replace(old_schema, new_schema)

        if 'dataset_query' in targeted_card and 'native' in targeted_card['dataset_query'] and 'query' in \
                targeted_card['dataset_query']['native']:
            targeted_card['dataset_query']['native']['query'] = targeted_card['dataset_query']['native'][
                'query'].replace(f'"{old_schema}"', f'"{new_schema}"')
        else:
            pass
        print(targeted_card)

        response = requests.put(update_url, json=targeted_card, headers=self.headers)
        if response.status_code == 200:
            print(f"Card with ID {card_id} updated successfully!")
            return response.json()
        else:
            print(f"Failed to update card with ID {card_id}. Status code: {response.status_code}")
            print(response.text)
            return None

    def get_schemas(self):
        get_schemas_url = f"{self.api_url}/api/database/{self.database_id}/schemas"
        response = requests.get(get_schemas_url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch schemas. Status code: {response.status_code}")
            print(response.text)
            return None

    def update_dashboards_for_schemas(self, from_dashboard_id, collection_id, collection_position, is_deep_copy,
                                      old_schema):
        session_token = self.get_session_token()
        print(f"Session token: {from_dashboard_id}")
        print(f"Session token: {collection_id}")
        if session_token:
            schemas = self.get_schemas()

            if schemas:
                for schema_name in schemas:
                    name = f"{schema_name} Dashboard"
                    description = f"{schema_name} created via API"
                    old_schema = old_schema
                    new_schema = schema_name

                    # Copy and update dashboard
                    self.copy_and_update_dashboard(
                        from_dashboard_id, name, old_schema, new_schema, description, collection_id,
                        collection_position, is_deep_copy
                    )

    def get_cards_in_collection(self, collection_id):
        # This method retrieves all cards in the specified collection
        get_cards_url = f"{self.api_url}/api/card?collection={collection_id}"
        response = requests.get(get_cards_url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch cards in the collection. Status code: {response.status_code}")
            print(response.text)
            return None

    def extract_topic(self, card_name):
        # This method extracts the topic from the card name
        parts = card_name.split(' ', 1)
        if len(parts) == 2:
            return parts[1]
        else:
            return None

    def create_dashboards_for_topics(self, cards):
        # This method creates dashboards for each topic and adds the respective cards to each dashboard
        grouped_cards = defaultdict(list)
        for card in cards:
            topic = self.extract_topic(card['name'])
            if topic:
                grouped_cards[topic].append(card)

        for topic, topic_cards in grouped_cards.items():
            # Create a dashboard for the topic
            dashboard_name = f"{topic} Dashboard"
            dashboard = {
                "name": dashboard_name,
                "collection_id": 136,
            }
            create_dashboard_url = f"{self.api_url}/api/dashboard"
            response = requests.post(create_dashboard_url, json=dashboard, headers=self.headers)

            if response.status_code == 200:
                dashboard_id = response.json().get("id")
                print(f"Dashboard '{dashboard_name}' created successfully with ID: {dashboard_id}")

                # Add cards to the dashboard
                for card in topic_cards:
                    self.add_card_to_dashboard(card, dashboard_id, topic)

                print(f"All {len(topic_cards)} cards added to the dashboard '{dashboard_name}'")
            else:
                print(f"Failed to create dashboard '{dashboard_name}'. Status code: {response.status_code}")
                print(response.text)

    def add_card_to_dashboard(self, card, dashboard_id, topic):
        # This method adds a card to a dashboard
        dashboard_data = self.get_dashboard(dashboard_id)
        if not dashboard_data:
            print(f"Failed to retrieve dashboard data for dashboard ID {dashboard_id}")
            return

        # Get the existing dashcards from the dashboard data
        dashcards = dashboard_data.get("dashcards", [])
        size_x = 16
        size_y = 5
        if topic == "User Sign-in Rate":
            size_y = 7
        if topic == "Feedback Satisfaction Percentages":
            size_x = 8
        # Append the card to the dashcards list in the correct format
        dashcard = {
            "id": card["id"],  # Assuming card has an 'id' field
            "card_id": card["id"],  # Assuming card has an 'id' field
            "card": card,
            "size_x": size_x,
            "size_y": size_y,
            "row": 0,
            "col": 0
        }
        dashcards.append(dashcard)

        # Update the dashboard data with the new dashcards
        dashboard_data["dashcards"] = dashcards

        # Update the dashboard
        self.update_dashboard(dashboard_id, dashboard_data)
