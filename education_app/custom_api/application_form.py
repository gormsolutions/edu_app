import frappe

@frappe.whitelist(allow_guest=True)
def fetch_applications(name):
    """
    Fetches and returns a list of Application Forms with all their fields,
    including any child tables. Filters by name if provided.
    
    Args:
        name (str, optional): The name of the Application Form to filter by.
    
    Returns:
        list | str: A list of Application Form documents as dictionaries,
                    "Application Submitted" if submitted, or
                    "No existing application" if no record is found.
    """
    # Build the filters dictionary to only fetch draft applications
    filters = {"docstatus": 0}  # docstatus 0 = Draft, 1 = Submitted, 2 = Canceled
    if name:
        filters["name"] = name

    # Get a list of Application Form names based on the filters
    application_names = frappe.get_all("APPLICATION FORM", filters=filters, fields=["name"])

    if not application_names:
        # Check if the application exists but is submitted
        submitted_application = frappe.get_all("APPLICATION FORM", filters={"name": name, "docstatus": 1})
        if submitted_application:
            return "Application Submitted"
        return "No existing application"

    applications = []
    for app in application_names:
        # Fetch the full document for each Application Form
        doc = frappe.get_doc("APPLICATION FORM", app.name)
        # Convert the document to a dict, which includes child tables
        applications.append(doc.as_dict())
    
    return applications

@frappe.whitelist(allow_guest=True)
def fetch_applications_status(applicant_form_id):
    """
    Fetches and returns a list of Application Forms with all their fields,
    including any child tables. Filters by name if provided.
    
    Args:
        name (str, optional): The name of the Application Form to filter by.
    
    Returns:
        list: A list of Application Form documents as dictionaries.
    """
    # Build the filters dictionary
    filters = {}
    if applicant_form_id:
        filters["custom_application_form_id"] = applicant_form_id

    # Get a list of Application Form names based on the filters
    application_names = frappe.get_all("Student Applicant",
                                       filters=filters, fields=[
                                           "first_name",
                                            "middle_name","last_name","student_email_id",
                                            "application_status","name","program"])
    
   
    return application_names


import frappe
import json

@frappe.whitelist(allow_guest=True)
def create_document():
    try:
        # Fetch JSON data from request
        data = frappe.form_dict.get("data")

        # Debugging: Print received data
        frappe.logger().info(f"Received Data: {data}")

        if not data:
            frappe.throw("No data provided", frappe.MandatoryError)

        # Ensure data is a valid JSON object
        if isinstance(data, str):
            data = json.loads(data)

        # Create new document
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)

        return {"message": "Document created successfully", "name": doc.name}

    except Exception as e:
        frappe.logger().error(f"Error: {str(e)}")
        frappe.throw(f"Invalid JSON data: {str(e)}")



@frappe.whitelist(allow_guest=True)
def get_academic_years_and_programs():
    try:
        # Fetch all Academic Year names
        academic_years = frappe.get_all("Academic Year", fields=["name", "year_start_date", "year_end_date"], order_by="year_start_date DESC")

        # Fetch all Programs with child table 'courses'
        programs = []
        program_docs = frappe.get_all("Program", fields=["name", "program_name", "program_abbreviation", "department"])

        for program in program_docs:
            # Fetch child table courses for each program
            program_doc = frappe.get_doc("Program", program["name"])
            courses = [{"course": course.course, "course_name": course.course_name} for course in program_doc.courses]

            # Add courses to the program data
            program["courses"] = courses
            programs.append(program)

        return {
            "academic_years": academic_years,
            "programs": programs
        }

    except Exception as e:
        frappe.logger().error(f"Error fetching lists: {str(e)}")
        frappe.throw(f"Error fetching data: {str(e)}")

@frappe.whitelist(allow_guest=True)
def get_districts_and_countries():
    try:
        # Fetch all districts with their linked country IDs
        districts = frappe.get_all("District", fields=["district_name","country"])
             
        # Fetch all countries separately
        countries = frappe.get_all("Country", fields=["country_name"])


        return {
            "districts": districts,
            "countries": countries
        }
    except Exception as e:
        frappe.log_error(f"Error fetching districts and countries: {str(e)}")
        return {"districts": [], "countries": []}


import frappe
from frappe.exceptions import ValidationError
@frappe.whitelist(allow_guest=True)
def check_existing_application_by_email(email_address):
    """
    Checks if an Application Form already exists for the given email address.
    
    Args:
        email_address (str): The email address to check.
        
    Raises:
        ValidationError: If an application form already exists for the given email address.
    """
    if frappe.db.exists("APPLICATION FORM", {"email_address": email_address}):
        frappe.throw("An Application Form already exists for this email address.", ValidationError)
