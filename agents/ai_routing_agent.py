from openai import OpenAI

from config import OPENAI_API_KEY


class AIRoutingAgent:

    def __init__(self):

        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )

    def fallback_prediction(

            self,
            description

    ):

        description = description.lower()

        # Linux
        linux_keywords = [

            "linux",
            "ubuntu",
            "unix",
            "disk",
            "filesystem",
            "server reboot"

        ]

        # Windows
        windows_keywords = [

            "windows",
            "iis",
            "active directory",
            "service stopped"

        ]

        # Database
        database_keywords = [

            "database",
            "oracle",
            "mysql",
            "sql"

        ]

        # Network
        network_keywords = [

            "network",
            "vpn",
            "router",
            "switch"

        ]

        for keyword in linux_keywords:

            if keyword in description:

                return {
                    "assignment_group":
                    "Linux Support",

                    "confidence": 90
                }

        for keyword in windows_keywords:

            if keyword in description:

                return {
                    "assignment_group":
                    "Windows Support",

                    "confidence": 88
                }

        for keyword in database_keywords:

            if keyword in description:

                return {
                    "assignment_group":
                    "Database Support",

                    "confidence": 92
                }

        for keyword in network_keywords:

            if keyword in description:

                return {
                    "assignment_group":
                    "Network Support",

                    "confidence": 85
                }

        return {

            "assignment_group":
            "Manual Review",

            "confidence": 40

        }

    def predict_assignment_group(

            self,
            short_description

    ):

        try:

            prompt = f"""

            You are an IT ticket routing AI.

            Identify:

            1. Assignment Group
            2. Confidence Score (0-100)

            Available Groups:

            - Linux Support
            - Windows Support
            - Database Support
            - Network Support

            Ticket:

            {short_description}

            Return format:

            Assignment Group | Confidence
            """

            response = (
                self.client.chat.completions.create(

                    model="gpt-4o-mini",

                    messages=[

                        {
                            "role": "system",
                            "content":
                            "You are an expert IT routing assistant."
                        },

                        {
                            "role": "user",
                            "content": prompt
                        }

                    ],

                    temperature=0

                )
            )

            prediction = (

                response.choices[0]
                .message.content
                .strip()

            )

            parts = prediction.split("|")

            assignment_group = (
                parts[0].strip()
            )

            confidence = int(
                parts[1].strip()
            )

            print(
                "\nGPT Prediction Successful"
            )

            return {

                "assignment_group":
                assignment_group,

                "confidence":
                confidence

            }

        except Exception as e:

            print(
                f"\nGPT Failed: {e}"
            )

            print(
                "Using Fallback AI..."
            )

            return self.fallback_prediction(
                short_description
            )