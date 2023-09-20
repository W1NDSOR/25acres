# File to populate the database with dummy data for testing
# Can stop using this file once we have a front-end to create users, properties, etc.

import subprocess


# change these according to the tables to be populated
command1 = "python manage.py databases/populateUsers"
command2 = "python manage.py databases/populateLocation"
command3 = "python manage.py databases/populateProperties"
command4 = "python manage.py databases/populateImages"
command5 = "python manage.py databases/populateTransactions"
command6 = "python manage.py databases/populateContracts"

try:
    subprocess.check_call(command1, shell=True)
    subprocess.check_call(command2, shell=True)
    subprocess.check_call(command3, shell=True)
    subprocess.check_call(command4, shell=True)
    subprocess.check_call(command5, shell=True)
    subprocess.check_call(command6, shell=True)

    print("Database populated successfully")
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
