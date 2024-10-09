import json
import re
import os
import glob
import sys
from dotenv import load_dotenv

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()
# Initialize the MomentDatabase object
url = os.getenv("MONGO_URI")
qdrantUrl = os.getenv("QDRANT_URL")
qdrantKey = os.getenv("QDRANT_KEY")


class Final_Json_Processor:
    def __init__(self):
        pass

    # Helper function to process the Year
    def process_year(self, year):
        try:
            if year is None:
                return None
            if str(year).isdigit():
                return str(year)
            # Check for formats like '785 BC', '785 BCE', '785 AD', '785 CE'
            match1 = re.match(r"^(\d+)\s+(BC|BCE|AD|CE|)$", year.strip())
            if match1:
                return match1.group(1)

            # Check for formats like '1400s' or '1400S'
            match = re.match(r"^(\d{3,4})[sS]$", year.strip())
            if match:
                return match.group(1)
            # Check for formats like '1995-1997' or '1995-97'

            match = re.match(r"^(\d{4})-\d{2,4}$", year.strip())
            if match:
                return match.group(1)
            else:
                return year
        except Exception:
            return year

    # Helper function to process the Month
    def process_month(self, month):
        try:
            month_mapping = {
                "1": "January",
                "01": "January",
                "2": "February",
                "02": "February",
                "3": "March",
                "03": "March",
                "4": "April",
                "04": "April",
                "5": "May",
                "05": "May",
                "6": "June",
                "06": "June",
                "7": "July",
                "07": "July",
                "8": "August",
                "08": "August",
                "9": "September",
                "09": "September",
                "10": "October",
                "11": "November",
                "12": "December",
                "jan": "January",
                "january": "January",
                "feb": "February",
                "february": "February",
                "mar": "March",
                "march": "March",
                "apr": "April",
                "april": "April",
                "may": "May",
                "jun": "June",
                "june": "June",
                "jul": "July",
                "july": "July",
                "aug": "August",
                "august": "August",
                "sep": "September",
                "september": "September",
                "oct": "October",
                "october": "October",
                "nov": "November",
                "november": "November",
                "dec": "December",
                "december": "December",
            }
            if month is None:
                return None
            if isinstance(month, int) or month.isdigit():
                month = str(int(month))  # Convert to int first to remove leading zeros
            return month_mapping.get(month.lower(), month)
        except Exception:
            return month

    # Helper function to process the Day
    def process_day(self, day):
        if day is None:
            return None
        try:
            day = str(day)
            if day.isdigit() and 1 <= int(day) <= 31:
                return f"{int(day):02d}"  # Ensure day is in the format "01", "02", etc.
            else:
                return None
        except Exception:
            return day  # Return None if day is not a valid number

    # Helper function to process the Era
    def process_era(self, era):
        try:
            if era == "BC":
                return "BCE"
            if era == "AD":
                return "CE"
            if era is None:
                return "CE"
            else:
                return era
        except Exception:
            return era

    def process_category(self, category):
        try:
            if category is None:
                return []
            else:
                return [cat for cat in category if cat.lower() != "history"]
        except Exception:
            return category

    # Main function to process incidents
    def process_incidents(
        self,
        data,
        filepath,
        source_name,
        life_id="00000000000000000",
    ):
        processed_incidents = []
        if data is None:
            return data
        else:
            for incident in data:
                # Check for required attributes
                required_attributes = [
                    "Year",
                    "Title",
                    "Description",
                ]
                if not all(attr in incident for attr in required_attributes):
                    continue  # Skip if any required attribute is missing

                # Add Month and Day if missing, default to None
                incident["Month"] = incident.get("Month", None)
                incident["Day"] = incident.get("Day", None)
                incident["Era"] = incident.get("Era", "CE")
                incident["category"] = incident.get("category", [])

                # Process Year
                year = self.process_year(incident.get("Year"))
                if year is None:
                    continue  # Skip if Year is null

                # Process Month and Day
                month = self.process_month(incident.get("Month"))
                day = self.process_day(incident.get("Day"))

                # Process Era
                era = self.process_era(incident.get("Era"))

                # Keep Title, Description, and category as is
                title = incident.get("Title")
                description = incident.get("Description")
                category = self.process_category(incident.get("category", []))

                # Create the processed incident
                processed_incident = {
                    "Year": year,
                    "Month": month,
                    "Day": day,
                    "Era": era,
                    "Title": title,
                    "Description": description,
                    "category": category,
                    "source_name": str(source_name),
                    "source_id": str(filepath),
                    "life_id": str(life_id),
                }

                # Add to the processed incidents list
                processed_incidents.append(processed_incident)

            return processed_incidents

    # Save the processed data to a JSON file
    def save_to_json(self, processed_data, file_path):
        # Extract the base name without extension
        # base_name = os.path.splitext(os.path.basename(file_path))[0]

        # Construct the path to the JSON_Processed folder
        json_file_path = os.path.join(
            "JSON_Data", f"{file_path}", f"{file_path}_processed.json"
        )

        # Ensure the directory exists

        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

        # Save the processed data to the JSON file
        with open(json_file_path, "w", encoding="utf-8") as file:
            json.dump({"incidents": processed_data}, file, indent=4)

    def load_json(self, file_path):
        # Extract the base name without extension
        # base_name = os.path.splitext(os.path.basename(file_path))[0]

        # Construct the path to the JSON files
        json_folder_path = os.path.join("JSON_Data", f"{file_path}", "enhanced")
        json_file_pattern = os.path.join(json_folder_path, "incidents_*_enhanced.json")

        # Load all JSON files matching the pattern
        all_data = []
        for json_file_path in glob.glob(json_file_pattern):
            with open(json_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                all_data.extend(data.get("incidents", []))

        return all_data


# # filename = "artifacts/Margret.pdf"
# processor = Final_Json_Processor()
# data1 = processor.load_json("00000000000")
# data2 = processor.process_incidents(data1, "00000000000", source_name="Sample Book")
# processor.save_to_json(data2, "00000000000")
