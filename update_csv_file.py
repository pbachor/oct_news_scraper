import csv
import os

class CsvUpdater:

    def __init__(self, file=None):
        if file:
            self.csv_file = file
        else:
            self.csv_file = '.\\csv_file\\oct_news.csv'
            if os.path.isfile(self.csv_file) is False:
                with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['date', 'title', 'text', 'link'], delimiter=";")
                    writer.writeheader()
                    print(f"New file is created @ {self.csv_file}")


        # Ensure the file exists and read existing links. using set(), because here we do not have dublicates
        self.existing_links = set()

        if os.path.isfile(self.csv_file):
            with open(self.csv_file, newline='', encoding='utf-8') as f:
                self.reader = csv.DictReader(f, delimiter=";")
                for row in self.reader:
                    try:
                        self.existing_links.add(row['link'])
                    except KeyError as err:
                        print(f"There is an error with the keys in the .csv file. Not usable:\n{err}")
        else:
            print(f"The file {self.csv_file} does not exist. If the file exist, please include the file path.")

    def get_new_data(self,new_data):
        unique_new_data = [item for item in new_data if item['link'] not in self.existing_links]
        return unique_new_data

    def add_data(self, new_data):
        """This function is checking for new entries by using self.get_new_data(). Than adding the new ones
        into the .csv file. Returning all new entries as dictonary."""
        # Filter only new entries
        unique_new_data = self.get_new_data(new_data)

        # Write the new entries
        if unique_new_data:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['date', 'title', 'text', 'link'], delimiter=';')
                if os.path.getsize(self.csv_file) == 0:
                    writer.writeheader()  # Write header only once
                    print("Writing the first time in the file.")
                writer.writerows(unique_new_data)

            print(f"Added {len(unique_new_data)} new entries to {self.csv_file}.")
        else:
            print("No new entries to add.")
        return unique_new_data