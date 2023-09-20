# run to populate the whole database

import subprocess

# Define the command to run
command1 = "python manage.py populate_users"
command2 = "python manage.py populate_location"
command3 = "python manage.py populate_properties"
command4 = "python manage.py populate_images"
command5 = "python manage.py populate_transactions"
command6 = "python manage.py populate_contracts"

try:
    # Run the command in the terminal
    subprocess.check_call(command1, shell=True)
    subprocess.check_call(command2, shell=True)
    subprocess.check_call(command3, shell=True)
    subprocess.check_call(command4, shell=True)
    subprocess.check_call(command5, shell=True)
    subprocess.check_call(command6, shell=True)
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
