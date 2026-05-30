class AssignmentAgent:

    def assign_ticket(

            self,
            ticket,
            engineer_data

    ):

        try:

            print("\nAssigning Ticket...")

            print(
                f"Ticket: "
                f"{ticket['ticket_number']}"
            )

            print(
                f"Assigned To: "
                f"{engineer_data['engineer']}"
            )

            print(
                f"Backup Engineer: "
                f"{engineer_data['backup']}"
            )

            print(
                "Assignment Successful"
            )

        except Exception as e:

            print(
                f"Assignment Error: {e}"
            )