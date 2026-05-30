import json


class ServiceNowService:

    def __init__(self, file_path):

        self.file_path = file_path

    def get_new_tickets(self):

        try:

            with open(self.file_path, "r") as file:

                tickets = json.load(file)

            print(
                f"Fetched {len(tickets)} tickets"
            )

            return tickets

        except Exception as e:

            print(
                f"Error Reading Tickets: {e}"
            )

            return []