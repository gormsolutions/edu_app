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
from frappe.core.doctype.file.file import File
from frappe import _
from werkzeug.utils import secure_filename # type: ignore

@frappe.whitelist(allow_guest=True)
def create_document():
    try:
        import json
        from werkzeug.utils import secure_filename # type: ignore

        # Get form data
        data = frappe.form_dict.get("data")
        if not data:
            frappe.throw("No data provided", frappe.MandatoryError)

        if isinstance(data, str):
            data = json.loads(data)

        email_address = data.get("email_address")
        if not email_address:
            frappe.throw("Email address not provided", frappe.MandatoryError)

        # Prepare file field mapping
        file_fields = [
            "senior_four",
            "academic_transcript",
            "senior_six",
            "ahpc_registration_cert"
        ]

        # Initialize one row to hold all file fields
        attach_row = {
            "doctype": "UPGRADERS ATTACH"
        }

        uploaded_files = []

        for fieldname in file_fields:
            file = frappe.request.files.get(fieldname)
            if file:
                if not file.filename.lower().endswith('.pdf'):
                    frappe.throw(f"Only PDF files are allowed for {fieldname}.")

                filename = secure_filename(file.filename)

                file_doc = frappe.get_doc({
                    "doctype": "File",
                    "file_name": filename,
                    "is_private": 0,
                    "folder": "Home",
                    "content": file.read()
                })
                file_doc.save()
                frappe.db.commit()

                # Add URL to correct field in attach_row
                attach_row[fieldname] = file_doc.file_url
                uploaded_files.append(file_doc.file_url)

        # Only add to child table if at least one file was uploaded
        if any(attach_row.get(field) for field in file_fields):
            data["for_upgraders_attach"] = [attach_row]

        # Create main doc
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Send confirmation email
        subject = f"Application Submitted Successfully: {doc.name}"
        message = f"""
        Dear {data.get('surname')},<br><br>
        Your application (<strong>{doc.name}</strong>) has been received successfully.<br><br>
        Please keep this document name for reference.<br><br>
        Thank you.
        """

        frappe.sendmail(
            recipients=[email_address],
            subject=subject,
            message=message,
            reference_doctype=doc.doctype,
            reference_name=doc.name
        )

        return {
            "message": "Document and PDF file(s) uploaded successfully.",
            "success": True,
            "docname": doc.name,
            "file_urls": uploaded_files
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Application Form Submission Failed")
        frappe.throw(f"Invalid Request: {str(e)}")

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

@frappe.whitelist(allow_guest=True)
def get_institutions():
    try:
        # Fetch all Institution
        institution = frappe.get_all("Institution", fields=["institution"])
             
     
        return {
            "institutions": institution,
        }
    except Exception as e:
        frappe.log_error(f"Error fetching institution: {str(e)}")
        return {"institution": []}


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


from frappe.model.document import Document
from frappe import _

@frappe.whitelist(allow_guest=True)
def submit_application_form(name):
    """
    Submit an Application Form by name if it's in Draft (docstatus=0)
    """
    doc = frappe.get_doc("APPLICATION FORM", name)

    if doc.docstatus == 1:
        return _("Application Form is already submitted.")

    if doc.docstatus == 2:
        return _("Cannot submit a cancelled Application Form.")

    # Submit the document
    doc.submit()

    return _("Application Form {0} has been successfully submitted.").format(name)


import frappe
from frappe.utils.file_manager import save_file

@frappe.whitelist(allow_guest=True)
def upload_document():
    files = frappe.request.files.getlist('file')  # Get all uploaded files
    
    if not files:
        return {'message': 'No files uploaded'}

    uploaded_files = []  # To store the names of successfully uploaded files

    for filedata in files:
        # Save each file to ERPNext using save_file method
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filedata.filename,
            "file_url": None,
            "folder": "Home",
            "is_private": 0,  # 0 for public, 1 for private
            "content": filedata.read()
        })

        file_doc.save()
        uploaded_files.append(filedata.filename)

    return {'message': 'Success', 'uploaded_files': uploaded_files}


import frappe

def force_session_refresh_without_logout(user):
    """Regenerate CSRF token without logging the user out."""
    # Ensure the user is authenticated
    if frappe.session.user == user and user != "Guest":
        # Generate and return a new CSRF token without logout
        return frappe.sessions.get_csrf_token()
    else:
        raise frappe.PermissionError("User is not logged in or session is invalid.")

@frappe.whitelist(allow_guest=True)
def regenerate_session():
    """Custom endpoint to regenerate the session and provide a new CSRF token."""
    user = frappe.session.user
    if user == "Guest":
        return {"error": "Not logged in"}
    
    # Regenerate the CSRF token
    try:
        csrf_token = force_session_refresh_without_logout(user)
        return {"csrf_token": csrf_token}
    except frappe.PermissionError as e:
        return {"error": str(e)}