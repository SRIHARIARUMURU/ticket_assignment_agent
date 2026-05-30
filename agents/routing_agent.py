class RoutingAgent:

    def route_ticket(

            self,
            ticket,
            shift,
            excel_service
    ):

        assignment_group = ticket.get("assignment_group").strip()

        engineer = excel_service.get_engineer(assignment_group, shift)

        return engineer
