import pandas as pd


class ExcelService:

    def __init__(self, file_path):

        self.file_path = file_path

        try:

            self.df = pd.read_excel(file_path)

            # Remove unwanted spaces from column names
            self.df.columns = self.df.columns.str.strip()

            print("Excel loaded successfully")

        except Exception as e:

            print(f"Error loading Excel: {e}")

            self.df = None

    def get_engineer(self, assignment_group, shift):

        try:

            if self.df is None:

                print("Excel data not loaded")

                return None

            # Normalize input
            assignment_group = assignment_group.strip()
            shift = shift.strip()

            print("\nSearching Engineer...")
            print(f"Assignment Group: {assignment_group}")
            print(f"Shift: {shift}")

            # Normalize dataframe values
            filtered = self.df[

                (self.df["Assignment Group"].astype(str).str.strip() == assignment_group)

                &

                (self.df["Shift"].astype(str).str.strip() == shift)

                &

                (self.df["Status"].astype(str).str.strip() == "Active")

            ]

            print("\nFiltered Records:")
            print(filtered)

            # No matching records
            if filtered.empty:

                print("No matching engineer found")

                return None

            # Fetch first matching engineer
            engineer_data = {

                "engineer": filtered.iloc[0]["Engineer"],

                "backup": filtered.iloc[0]["Backup"]

            }

            print("\nEngineer Found Successfully")

            return engineer_data

        except Exception as e:

            print(f"Routing Error: {e}")

            return None