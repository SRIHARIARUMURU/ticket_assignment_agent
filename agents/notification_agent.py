class NotificationAgent:

    def notify(

            self,
            notification_service,
            message

    ):

        notification_service.send_notification(
            message
        )