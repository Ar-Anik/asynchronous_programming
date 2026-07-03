import csv
import os
from contextlib import contextmanager


@contextmanager
def inplace(filename, mode='r', newline=''):
    # Define a backup filename
    backup_filename = filename + '.bak'

    # Rename the original file to the backup filename
    os.rename(filename, backup_filename)

    try:
        # Open the backup file for reading and the original filename for writing
        with open(backup_filename, mode, newline=newline) as infh, \
                open(filename, 'w', newline=newline) as outfh:
            # Yield the file handles to the with statement target
            yield infh, outfh

        # If the block finishes successfully, remove the backup file
        os.unlink(backup_filename)
    except Exception as error:
        # If an exception occurs, restore the original file from the backup
        if os.path.exists(filename):
            os.unlink(filename)
        os.rename(backup_filename, filename)
        # Raise the exception to ensure visibility
        raise error


# Helper function to create dummy CSV data for testing
def create_initial_csv(filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Role'])
        writer.writerow(['Alice', 'Developer'])
        writer.writerow(['Bob', 'Designer'])


# Execution block
if __name__ == '__main__':
    csvfilename = 'employees.csv'

    # Step 1: Create a dummy CSV file
    create_initial_csv(csvfilename)

    print("--- File content before update ---")
    with open(csvfilename, 'r') as f:
        print(f.read())

    # Step 2: Use the completed inplace context manager to update the file
    with inplace(csvfilename, 'r', newline='') as (infh, outfh):
        reader = csv.reader(infh)
        writer = csv.writer(outfh)

        for row in reader:
            row += ['new', 'columns']
            writer.writerow(row)

    print("--- File content after update ---")
    with open(csvfilename, 'r') as f:
        print(f.read())
