import sys
import os
import pandas as pd
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.supabase_client import insert_job_data  # Importing insert function from supabase_client.py

# Expanded list of skill keywords to detect in job descriptions
skill_keywords = [
    'Python', 'Java', 'C++', 'SQL', 'AWS', 'Machine Learning', 'Deep Learning',
    'NLP', 'TensorFlow', 'Keras', 'PyTorch', 'Docker', 'Kubernetes', 'Flask', 'Django',
    'React', 'Node.js', 'Angular', 'JavaScript', 'project management tools', 'leadership', 'communication skills',
    'R', 'Data Science', 'AI', 'Tableau', 'Power BI', 'HTML', 'CSS', 'Git', 'Microservices', 'PostgreSQL', 'MySQL', 
    'Apache', 'Figma', 'Adobe XD', 'Sketch', 'Cisco', 'Juniper', 'UI/UX Design', 'HCI', 'Design Thinking', 'Usability Testing', 
    'Network Protocols', 'TCP/IP', 'DNS', 'DHCP', 'Firewalls', 'VPN', 'Security', 'Networking', 'System Design',
    # Added Embedded System Keywords
    'C/C++', 'Assembly language', 'Embedded Linux', 'RTOS', 'Microcontrollers', 'Firmware', 'Real-time systems', 'Low-level programming', 'Embedded systems'
]

# Function to parse and insert job descriptions into the database
def parse_csv_and_insert(csv_file_path):
    try:
        # Use encoding='latin1' to handle special characters
        jobs_df = pd.read_csv(csv_file_path, encoding='latin1')  # Or 'ISO-8859-1'
        print("CSV loaded successfully")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print("Available Columns:", jobs_df.columns)  # Debugging column names

    for _, job in jobs_df.iterrows():
        job_title = job['Job Title']
        full_description = job['Job Description']
        
        # Extract education requirement from the job description
        education_requirement = extract_education_requirement(full_description)

        if pd.isna(job_title) or pd.isna(full_description):
            print("⚠️ Skipped due to missing Job Title or Job Description.")
            continue
        
        # Extract skills (requirements) from description
        requirements_list = extract_requirements(full_description)
        print(f"Extracted Requirements for {job_title}: {requirements_list}")  # Debug print for extracted skills
        
        # Summarize the Job Description
        summarized_description = summarize_description(full_description)

        # Prepare job data dictionary
        job_data = {
            'job_title': job_title.strip(),
            'requirements': requirements_list if requirements_list else [],  # Ensure non-empty list
            'summarized_jd': summarized_description,
            'education': education_requirement if education_requirement else 'Not specified'  # Default if missing
        }

        print(f"Prepared job data: {job_data}")  # Debug print before insertion
        
        # Insert into Supabase (Calling insert_job_data from supabase_client.py)
        insert_job_data(job_data)
        print(f"✅ Inserted job: {job_title} into the database.")

# Function to extract skills from job description
def extract_requirements(description):
    found_skills = []
    for skill in skill_keywords:
        if re.search(rf'\b{re.escape(skill)}\b', description, re.IGNORECASE):
            found_skills.append(skill)
    return found_skills

# Function to summarize the job description
def summarize_description(description):
    # Summarize by picking the first few important lines (simple summarization for now)
    lines = description.split('\n')
    summary_lines = []
    
    for line in lines:
        if line.strip():  # Avoid empty lines
            summary_lines.append(line.strip())
        if len(summary_lines) >= 5:  # Only take top 5 lines
            break

    return " ".join(summary_lines)

# Function to extract education requirement from job description
def extract_education_requirement(description):
    # Adjusted regex to capture complete education qualifications
    education_keywords = [
        r'\b(Bachelor\'s|Master\'s|Ph\.?D|Doctorate|degree)\s*(in|of)\s*([a-zA-Z\s]+)\b'
    ]
    
    # Combine the patterns and search in the job description
    for keyword in education_keywords:
        match = re.search(keyword, description, re.IGNORECASE)
        if match:
            return match.group().strip()  # Return the matched phrase (e.g., Bachelor's degree in Computer Science)
    
    return None  # If no match found, return None

# Main function
if __name__ == "__main__":
    # Use raw string for path to avoid escape sequence errors
    csv_file_path = r'Z:\SmartHire\job_description.csv'  # Update this path as needed

    print("🚀 Starting job parsing and insertion...")
    parse_csv_and_insert(csv_file_path)
    print("🏁 All jobs have been processed and inserted.")
