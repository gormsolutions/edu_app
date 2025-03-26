from frappe.model.document import Document
import frappe

class APPLICATIONFORM(Document):
    def on_update(self):
        # Check if a Student Applicant already exists linked to this Application Form
        student_applicant_name = frappe.db.get_value("Student Applicant", {"custom_application_form_id": self.name}, "name")
        
        if not student_applicant_name:
            # Create a new Student Applicant record
            student_applicant = frappe.get_doc({
                "doctype": "Student Applicant",
                "academic_year": self.academic_year_of_admission,
                "first_name": self.surname,
                "last_name": self.other_names,
                "program": self.course_applied_for,
                "student_email_id": self.email_address,
                "custom_application_form_id": self.name  # Linking to Application Form
            })
            student_applicant.insert(ignore_permissions=True)
        else:
            # Fetch the existing Student Applicant
            student_applicant = frappe.get_doc("Student Applicant", student_applicant_name)
            # If the Student Applicant is still a draft, update its fields with the latest from the Application Form
            if student_applicant.docstatus == 0:
                student_applicant.academic_year = self.academic_year_of_admission
                student_applicant.first_name = self.surname
                student_applicant.last_name = self.other_names
                student_applicant.program = self.course_applied_for
                student_applicant.student_email_id = self.email_address
                student_applicant.db_update()

        # Update Application Form's application_status if the Student Applicant is still a draft
        # if student_applicant.docstatus == 0:
        application_status = student_applicant.application_status
        if application_status:
                self.db_set("application_status", application_status)

