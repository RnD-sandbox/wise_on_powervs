import csv


def validate_and_count_csv(csv_file_path):
    try:
        with open(csv_file_path, "r", newline="") as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)  # Read the header row

            if not header:
                raise ValueError("CSV file has no header")

            row_count = sum(1 for row in reader)

            print(f"The CSV file is valid and contains {row_count} rows.")
            return row_count

    except FileNotFoundError:
        print("The CSV file was not found.")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except csv.Error as e:
        print(f"CSV error: {e}")


# Example usage
csv_file_path = "initial_results.csv"  # Path to your CSV file
validate_and_count_csv(csv_file_path)
