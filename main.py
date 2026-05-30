from services.excel_service import ExcelService
from services.shift_service import ShiftService
from services.servicenow_service import ServiceNowService
from services.database_service import DatabaseService
from services.notification_service import NotificationService

from agents.routing_agent import RoutingAgent
from agents.assignment_agent import AssignmentAgent
from agents.monitor_agent import MonitorAgent
from agents.notification_agent import NotificationAgent
from agents.ai_routing_agent import AIRoutingAgent

from utils.logger import setup_logger


# Initialize Logger
logger = setup_logger()


# Initialize Services
excel_service = ExcelService(
    "data/shifts.xlsx"
)

shift_service = ShiftService()

servicenow_service = ServiceNowService(
    "data/mock_tickets.json"
)

database_service = DatabaseService(
    "database/tickets.db"
)

database_service.create_table()

notification_service = NotificationService()


# Initialize Agents
routing_agent = RoutingAgent()

assignment_agent = AssignmentAgent()

monitor_agent = MonitorAgent()

notification_agent = NotificationAgent()

ai_routing_agent = AIRoutingAgent()


def process_tickets():

    logger.info(
        "Checking for new tickets..."
    )

    print(
        "\nChecking for new tickets..."
    )

    # Detect Current Shift
    current_shift = (
        shift_service.get_current_shift()
    )

    print(
        f"\nCurrent Shift: "
        f"{current_shift}"
    )

    # Fetch Tickets
    tickets = (
        servicenow_service.get_new_tickets()
    )

    # Process Each Ticket
    for ticket in tickets:

        # Duplicate Protection
        if database_service.is_ticket_processed(
                ticket["ticket_number"]
        ):

            print(
                f"\nTicket "
                f"{ticket['ticket_number']} "
                f"already processed"
            )

            logger.info(

                f"Ticket "
                f"{ticket['ticket_number']} "
                f"already processed"

            )

            continue

        print("\n--------------------------------")

        print(
            f"Processing Ticket: "
            f"{ticket['ticket_number']}"
        )

        # AI Prediction
        ai_result = (

            ai_routing_agent.predict_assignment_group(

                ticket["short_description"]

            )

        )

        predicted_group = (
            ai_result["assignment_group"]
        )

        confidence = (
            ai_result["confidence"]
        )

        print(
            f"Predicted Assignment Group: "
            f"{predicted_group}"
        )

        print(
            f"Confidence Score: "
            f"{confidence}%"
        )

        # Low confidence handling
        if confidence < 70:

            print(
                "Low Confidence Detected"
            )

            print(
                "Sending Ticket For Manual Review"
            )

            logger.warning(

                f"Low confidence routing for "
                f"{ticket['ticket_number']}"

            )

            continue

        # Update ticket with predicted group
        ticket["assignment_group"] = predicted_group

        # Route Ticket
        engineer_data = (
            routing_agent.route_ticket(
                ticket,
                current_shift,
                excel_service
            )
        )

        # Assign Ticket
        if engineer_data:

            assignment_agent.assign_ticket(
                ticket,
                engineer_data
            )

            logger.info(

                f"Ticket "
                f"{ticket['ticket_number']} "
                f"assigned to "
                f"{engineer_data['engineer']}"

            )

            # Send Notification
            notification_agent.notify(

                notification_service,

                f"Ticket "
                f"{ticket['ticket_number']} "
                f"assigned to "
                f"{engineer_data['engineer']}"

            )

            # Save Processed Ticket
            database_service.save_processed_ticket(

                ticket["ticket_number"],

                engineer_data["engineer"]

            )

        else:

            print(
                "No Engineer Found"
            )

            logger.warning(

                f"No engineer found for "
                f"{ticket['ticket_number']}"

            )


def main():

    print(
        "\nStarting Ticket Assignment Agent..."
    )

    logger.info(
        "Application Started"
    )

    monitor_agent.start_monitoring(
        process_tickets
    )


if __name__ == "__main__":

    main()