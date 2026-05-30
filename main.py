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

import sqlite3
import os
from datetime import datetime


# =========================================================
# LOGGER
# =========================================================

logger = setup_logger()


# =========================================================
# DATABASE SETUP
# =========================================================

os.makedirs("database", exist_ok=True)

DB_PATH = os.path.join(
    "database",
    "tickets.db"
)

connection = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS processed_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_number TEXT UNIQUE,
    short_description TEXT,
    assignment_group TEXT,
    assigned_engineer TEXT,
    priority TEXT,
    status TEXT,
    processed_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

connection.commit()


# =========================================================
# INITIALIZE SERVICES
# =========================================================

excel_service = ExcelService(
    "data/shifts.xlsx"
)

shift_service = ShiftService()

servicenow_service = ServiceNowService(
    "data/mock_tickets.json"
)

database_service = DatabaseService(
    DB_PATH
)

notification_service = NotificationService()


# =========================================================
# INITIALIZE AGENTS
# =========================================================

routing_agent = RoutingAgent()

assignment_agent = AssignmentAgent()

monitor_agent = MonitorAgent()

notification_agent = NotificationAgent()

ai_routing_agent = AIRoutingAgent()


# =========================================================
# SAVE TO SQLITE
# =========================================================

def save_ticket_to_database(
        ticket,
        assignment_group,
        engineer,
        status="Processed"
):

    try:

        cursor.execute("""
        INSERT OR IGNORE INTO processed_tickets (
            ticket_number,
            short_description,
            assignment_group,
            assigned_engineer,
            priority,
            status,
            processed_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (

            ticket["ticket_number"],

            ticket["short_description"],

            assignment_group,

            engineer,

            ticket["priority"],

            status,

            datetime.now()

        ))

        connection.commit()

        logger.info(
            f"Saved ticket "
            f"{ticket['ticket_number']} "
            f"to database"
        )

    except Exception as e:

        logger.error(
            f"Database save error: {str(e)}"
        )


# =========================================================
# PROCESS TICKETS
# =========================================================

def process_tickets():

    logger.info(
        "Checking for new tickets..."
    )

    print(
        "\nChecking for new tickets..."
    )

    # =====================================================
    # CURRENT SHIFT
    # =====================================================

    current_shift = (
        shift_service.get_current_shift()
    )

    print(
        f"\nCurrent Shift: "
        f"{current_shift}"
    )

    logger.info(
        f"Current Shift: {current_shift}"
    )

    # =====================================================
    # FETCH TICKETS
    # =====================================================

    tickets = (
        servicenow_service.get_new_tickets()
    )

    print(
        f"\nFetched {len(tickets)} tickets"
    )

    # =====================================================
    # PROCESS EACH TICKET
    # =====================================================

    for ticket in tickets:

        try:

            # =============================================
            # DUPLICATE CHECK
            # =============================================

            if database_service.is_ticket_processed(
                    ticket["ticket_number"]
            ):

                print(
                    f"\nTicket "
                    f"{ticket['ticket_number']} "
                    f"already processed"
                )

                logger.info(
                    f"Duplicate ticket skipped: "
                    f"{ticket['ticket_number']}"
                )

                continue

            print("\n--------------------------------")

            print(
                f"Processing Ticket: "
                f"{ticket['ticket_number']}"
            )

            logger.info(
                f"Processing "
                f"{ticket['ticket_number']}"
            )

            # =============================================
            # AI ROUTING
            # =============================================

            ai_result = (
                ai_routing_agent
                .predict_assignment_group(
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

            logger.info(
                f"Predicted Group: "
                f"{predicted_group}"
            )

            # =============================================
            # LOW CONFIDENCE HANDLING
            # =============================================

            if confidence < 70:

                print(
                    "Low Confidence Detected"
                )

                logger.warning(
                    f"Low confidence routing for "
                    f"{ticket['ticket_number']}"
                )

                save_ticket_to_database(
                    ticket,
                    predicted_group,
                    "Manual Review",
                    "Escalated"
                )

                continue

            # =============================================
            # UPDATE TICKET
            # =============================================

            ticket["assignment_group"] = (
                predicted_group
            )

            # =============================================
            # ROUTE TICKET
            # =============================================

            engineer_data = (
                routing_agent.route_ticket(
                    ticket,
                    current_shift,
                    excel_service
                )
            )

            # =============================================
            # ASSIGN ENGINEER
            # =============================================

            if engineer_data:

                engineer_name = (
                    engineer_data["engineer"]
                )

                assignment_agent.assign_ticket(
                    ticket,
                    engineer_data
                )

                logger.info(
                    f"Ticket "
                    f"{ticket['ticket_number']} "
                    f"assigned to "
                    f"{engineer_name}"
                )

                print(
                    f"Assigned Engineer: "
                    f"{engineer_name}"
                )

                # =========================================
                # SEND NOTIFICATION
                # =========================================

                notification_agent.notify(

                    notification_service,

                    f"Ticket "
                    f"{ticket['ticket_number']} "
                    f"assigned to "
                    f"{engineer_name}"

                )

                # =========================================
                # SAVE TO DATABASE
                # =========================================

                save_ticket_to_database(

                    ticket,

                    predicted_group,

                    engineer_name,

                    "Processed"

                )

                # =========================================
                # MARK AS PROCESSED
                # =========================================

                database_service.save_processed_ticket(

                    ticket["ticket_number"],

                    engineer_name

                )

            else:

                print(
                    "No Engineer Found"
                )

                logger.warning(
                    f"No engineer found for "
                    f"{ticket['ticket_number']}"
                )

                save_ticket_to_database(

                    ticket,

                    predicted_group,

                    "Unassigned",

                    "Pending"

                )

        except Exception as e:

            logger.error(
                f"Error processing ticket "
                f"{ticket['ticket_number']}: "
                f"{str(e)}"
            )

            print(
                f"Error processing "
                f"{ticket['ticket_number']}"
            )


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "\n================================"
    )

    print(
        "AI Ticket Assignment Platform"
    )

    print(
        "================================"
    )

    logger.info(
        "Application Started"
    )

    monitor_agent.start_monitoring(
        process_tickets
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()
