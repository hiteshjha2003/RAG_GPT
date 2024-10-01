import streamlit as st
import pandas as pd
import io
import tempfile
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage

def calculate_gpa(scores, max_score):
    if len(scores) == 0:
        return 0.0
    return round((sum(scores) / (len(scores) * max_score)) * 10, 2)

def calculate_completion_rate(row, assignment_columns, project_columns):
    total_assignments = len(assignment_columns)
    total_projects = len(project_columns)
    total = (total_assignments + 2 * total_projects)
    completed_assignments = sum(1 for col in assignment_columns if not pd.isna(row[col]))
    completed_projects = sum(1 for col in project_columns if not pd.isna(row[col]))
    return round(((completed_assignments + 2 * completed_projects) / total) * 100, 2)

def calculate_final_score(row):
    completion_rate = row['Overall Completion Rate']
    assignment_gpa = row['Assignment GPA']
    project_gpa = row['Project GPA']
    final_score = (completion_rate * (assignment_gpa + project_gpa) / 2)
    return round(final_score/10, 2)

def create_pdf_report_card(row, logo_path):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Add logo
    logo_img = Image(logo_path, width=1.5*inch, height=1.5*inch)
    logo_img.hAlign = 'RIGHT'
    elements.append(logo_img)

    # Add student name
    student_name_style = ParagraphStyle(
        'StudentName',
        parent=styles['Heading2'],
        textColor=colors.blue
    )
    elements.append(Paragraph(f"Student Name: {row['Student Name']}", student_name_style))
    elements.append(Spacer(1, 12))

    # Add disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['BodyText'],
        fontSize=8,
        textColor=colors.grey
    )
    disclaimer_text = "Disclaimer: This report card is for informational purposes only. The maximum achievable marks for assignments is 10, and for projects is 20. The completion rate is calculated based on the number of assignments submitted. The final score depends on both the number of assignments submitted and the score in assignments."
    elements.append(Paragraph(disclaimer_text, disclaimer_style))
    elements.append(Spacer(1, 12))

    # Create table data
    data = [['Assignment', 'Score']]
    for col in row.index:
        if col not in ['Student Name', 'Overall Completion Rate', 'Final Score', 'Assignment GPA', 'Project GPA']:
            score = row[col]
            if pd.isna(score):
                score = "Not submitted"
            data.append([col, score])

    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Add overall completion rate and final score
    elements.append(Paragraph(f"Overall Completion Rate: {row['Overall Completion Rate']}%", styles['BodyText']))
    elements.append(Paragraph(f"Final Score: {row['Final Score']}%", styles['BodyText']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def load_data(file):
    file_extension = file.name.split('.')[-1].lower()
    if file_extension == 'csv':
        return pd.read_csv(file)
    elif file_extension in ['xls', 'xlsx']:
        return pd.read_excel(file)
    else:
        st.error("Unsupported file format. Please upload a CSV or Excel file.")
        return None

def find_student(df, student_name):
    return df[df['Student Name'].str.lower() == student_name.lower()]

def process_student_data(row, assignment_columns, project_columns):
    try:
        assignment_scores = [row[col] for col in assignment_columns if not pd.isna(row[col])]
        project_scores = [row[col] for col in project_columns if not pd.isna(row[col])]

        assignment_gpa = calculate_gpa(assignment_scores, max_score=10)
        project_gpa = calculate_gpa(project_scores, max_score=20)
        overall_completion_rate = calculate_completion_rate(row, assignment_columns, project_columns)

        # Create a new Series with the calculated values
        new_data = pd.Series({
            'Assignment GPA': assignment_gpa,
            'Project GPA': project_gpa,
            'Overall Completion Rate': overall_completion_rate,
            'Final Score': calculate_final_score({
                'Overall Completion Rate': overall_completion_rate,
                'Assignment GPA': assignment_gpa,
                'Project GPA': project_gpa
            })
        })

        # Combine the original row with the new data
        return pd.concat([row, new_data])
    except Exception as e:
        st.error(f"Error processing student data: {str(e)}")
        return None
    
    
def display_student_info(student_data, assignment_columns, project_columns):
    st.subheader("Student Information")
    st.write(f"Name: {student_data['Student Name'].values[0]}")
    
    st.write("Assignments:")
    for col in assignment_columns:
        score = student_data[col].values[0]
        st.write(f"- {col}: {score if not pd.isna(score) else 'Not submitted'}")
    
    st.write("Projects:")
    for col in project_columns:
        score = student_data[col].values[0]
        st.write(f"- {col}: {score if not pd.isna(score) else 'Not submitted'}")
    
    st.write(f"Assignment GPA: {student_data['Assignment GPA'].values[0]:.2f}")
    st.write(f"Project GPA: {student_data['Project GPA'].values[0]:.2f}")
    st.write(f"Overall Completion Rate: {student_data['Overall Completion Rate'].values[0]:.2f}%")
    st.write(f"Final Score: {student_data['Final Score'].values[0]:.2f}%")

def main():
    st.title("Student Report Card Generator")

    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"])
    uploaded_logo = st.file_uploader("Choose a logo image", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None and uploaded_logo is not None:
        df = load_data(uploaded_file)
        
        if df is not None:
            # Save the uploaded logo to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(uploaded_logo.getvalue())
                logo_path = tmp_file.name

            assignment_columns = [col for col in df.columns if 'Assignment' in col]
            project_columns = [col for col in df.columns if 'Projects' in col]

            # Add text area for student name input
            student_name = st.text_input("Enter student name:")

            if student_name:
                student_data = find_student(df, student_name)

                if not student_data.empty:
                    # Process student data
                    processed_data = process_student_data(student_data.iloc[0], assignment_columns, project_columns)
                    
                    if processed_data is not None:
                        # Display student information
                        display_student_info(pd.DataFrame([processed_data]), assignment_columns, project_columns)

                        # Generate and offer download of the report card
                        if st.button("Generate Report Card"):
                            pdf_buffer = create_pdf_report_card(processed_data, logo_path)
                            
                            st.download_button(
                                label=f"Download {processed_data['Student Name']}'s Report Card",
                                data=pdf_buffer,
                                file_name=f"{processed_data['Student Name']}_report.pdf",
                                mime="application/pdf"
                            )
                    else:
                        st.error("Error processing student data. Please check the input file format.")
                else:
                    st.error("Student not found. Please check the name and try again.")

            # Clean up the temporary file
            os.unlink(logo_path)

if __name__ == "__main__":
    main()
    
    