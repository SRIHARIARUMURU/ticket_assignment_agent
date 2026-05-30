import schedule
import time


class MonitorAgent:

    def start_monitoring(

            self,
            process_function

    ):

        print(
            "\nMonitor Agent Started..."
        )

        print(
            "Monitoring tickets every 1 minute..."
        )

        # Run immediately once
        process_function()

        # Schedule every minute
        schedule.every(1).minutes.do(
            process_function
        )

        try:

            while True:

                schedule.run_pending()

                time.sleep(1)

        except KeyboardInterrupt:

            print(
                "\nMonitoring Stopped Gracefully"
            )