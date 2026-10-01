import os
import re
import csv
import fitz  # PyMuPDF
import pandas as pd
import sys
import logging

# Set up path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.supabase_client import insert_candidate_data

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename='candidate_parser.log', filemode='w',
                    format='%(asctime)s - %(message)s')

# ------------------ Extract resume data ------------------
def extract_resume_data(resume_path):
    text = extract_text(resume_path)

    name = extract_name_from_text(text)
    email = extract_email_from_text(text)
    phone = extract_phone_from_text(text)
    skills = extract_skills(text)
    experience_years = extract_experience(text)

    logging.debug(f"Extracted experience for {name}: {experience_years} years")

    return {
        'name': name,
        'email': email,
        'phone': phone,
        'skills': skills,
        'experience_years': experience_years,
        'raw_text': text
    }

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_name_from_text(text):
    name_match = re.search(r'Name:\s*([A-Za-z\s]+)(?=\s*Email)', text)
    if name_match:
        return name_match.group(1).strip()
    first_line = text.split("\n")[0]
    name_match = re.search(r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)', first_line)
    return name_match.group(0) if name_match else "Unknown Candidate"

def extract_email_from_text(text):
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return email_match.group(0) if email_match else None

def extract_phone_from_text(text):
    phone_match = re.search(r'Phone:\s*(\+?\d{1,3}[-.\s]?\d{3}[-.\s]?\d{4})', text)
    return phone_match.group(1).strip() if phone_match else None

def extract_skills(text):
    skill_keywords = {
        'Python': r'\bpython\b',
        'Java': r'\bjava\b',
        'C++': r'\bc\+\+\b',
        'SQL': r'\b(sql|mysql|postgresql)\b',
        'AWS': r'\baws\b',
        'Azure': r'\bazure\b',
        'GCP': r'\bgcp\b',
        'Cloud Computing': r'\bcloud computing\b',
        'Machine Learning': r'\bmachine learning\b',
        'Deep Learning': r'\bdeep learning\b',
        'NLP': r'\bnlp\b',
        'TensorFlow': r'\btensorflow\b',
        'Keras': r'\bkeras\b',
        'PyTorch': r'\bpytorch\b',
        'Docker': r'\bdocker\b',
        'Kubernetes': r'\bkubernetes\b',
        'Cybersecurity': r'\bcybersecurity\b',
        'OpenCV': r'\bopencv\b',
        'CUDA': r'\bcuda\b'
    }

    sections = re.split(r'(Skills|Technical Skills|Tech Stack|Technologies)', text, flags=re.IGNORECASE)
    target_text = ""
    for i in range(len(sections)):
        if sections[i].lower() in ['skills', 'technical skills', 'tech stack', 'technologies'] and i + 1 < len(sections):
            section_content = sections[i + 1]
            section_content = re.split(r'(Education|Work Experience|Certifications|Achievements)', section_content, flags=re.IGNORECASE)[0]
            target_text += section_content + " "
    target_text = target_text.strip()

    if not target_text:
        target_text = text  # fallback

    extracted_skills = []
    target_text_lower = target_text.lower()

    for skill, pattern in skill_keywords.items():
        if re.search(pattern, target_text_lower, re.IGNORECASE):
            if skill == 'Cloud Computing':
                # Expand Cloud Computing into AWS, Azure, GCP
                extracted_skills.extend(['AWS', 'Azure', 'GCP'])
            else:
                extracted_skills.append(skill)

    return list(set(extracted_skills))  # remove duplicates



def extract_experience(text):
    logging.debug(f"Extracting experience from resume text: {text[:200]}...")

    # Isolate Work Experience section
    sections = re.split(r'Work Experience\s*', text, flags=re.IGNORECASE)
    work_text = text
    if len(sections) > 1:
        work_text = sections[1]
        work_text = re.split(r'(Education|Skills|Certifications|Achievements)', work_text, flags=re.IGNORECASE)[0]

    logging.debug(f"Work Experience section: {work_text[:200]}...")
    
    # Look for patterns like (2019-2023) in Work Experience section
    date_ranges = re.findall(r'\((\d{4})\s*-\s*(\d{4})\)', work_text)
    logging.debug(f"Extracted date ranges: {date_ranges}")

    if date_ranges:
        start_years = []
        end_years = []
        for start, end in date_ranges:
            try:
                start = int(start)
                end = int(end)
                if end > start:
                    start_years.append(start)
                    end_years.append(end)
            except ValueError:
                continue
        
        if start_years and end_years:
            total_span = max(end_years) - min(start_years)
            logging.debug(f"Total calculated experience span: {total_span} years")
            return total_span if total_span > 0 else 0

    # Fallback: Look for explicit mentions like "5 years of experience"
    matches = re.findall(r'(\d+)\s*(?:years?|yrs?|year)\s*(?:of\s*experience)?', work_text, re.IGNORECASE)
    if matches:
        years = [int(match) for match in matches]
        logging.debug(f"Experience matches found: {years}")
        return max(years)
    
    logging.debug("No experience found.")
    return 0

# ------------------ Save extracted data to CSV ------------------
def save_to_csv(data, filename='parsed_resumes.csv'):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = ['Name', 'Email', 'Phone', 'Skills', 'Experience_Years', 'Raw_Text']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        logging.debug(f"Writing to CSV: {data}")
        writer.writerow({
            'Name': data['name'],
            'Email': data['email'],
            'Phone': data['phone'],
            'Skills': ', '.join(data['skills']),
            'Experience_Years': data['experience_years'],
            'Raw_Text': data['raw_text']
        })

# ------------------ Cleaning Helpers ------------------
def clean_field(value):
    if pd.isna(value) or value is None:
        return None
    value = str(value).strip()
    if value.lower() in ['none', 'unknown', 'candidate resume']:
        return None
    return value

def clean_name(name):
    if not name:
        return None
    name = re.split(r'\n|Email', name)[0]
    name = name.strip()
    if name.lower() in ['candidate resume', 'unknown']:
        return None
    return name

# ------------------ Parse CSV and Insert to DB ------------------
def parse_csv_and_insert(csv_file_path):
    parsed_df = pd.read_csv(csv_file_path)

    print("Columns in CSV:", parsed_df.columns)
    logging.debug(f"CSV columns: {parsed_df.columns}")

    inserted_count = 0
    for _, candidate in parsed_df.iterrows():
        name = clean_name(candidate.get('Name'))
        email = clean_field(candidate.get('Email'))
        phone = clean_field(candidate.get('Phone'))
        print(f"Phone for {name}: {phone}")
        logging.debug(f"Phone for {name}: {phone}")
        skills_str = candidate.get('Skills')
        raw_text = clean_field(candidate.get('Raw_Text'))
        experience_years = candidate.get('Experience_Years')

        if experience_years == "Not Specified" or pd.isna(experience_years):
            experience_years = 0

        skills_list = [skill.strip() for skill in skills_str.split(',')] if isinstance(skills_str, str) else []

        if name and email:
            candidate_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'skills': skills_list,
                'experience_years': int(experience_years),
                'parsed_resume': raw_text
            }

            logging.debug(f"Inserting candidate data: {candidate_data}")
            response = insert_candidate_data(candidate_data)
            if response:
                inserted_count += 1
            print(f"✅ Inserted candidate: {name} (Experience: {experience_years} years) into the database.")
        else:
            print(f"⚠️ Skipped candidate due to missing name or email.")

    print(f"Total candidates inserted: {inserted_count}")

# ------------------ MAIN EXECUTION ------------------
if __name__ == "__main__":
    folder_path = "Z:/SmartHire/CVs1"
    
    # Clean old parsed file (optional, for fresh run)
    parsed_csv_path = "Z:/SmartHire/parsed_resumes.csv"
    if os.path.exists(parsed_csv_path):
        os.remove(parsed_csv_path)

    # Parse all resumes and save to CSV
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            print(f"Parsing {filename}...")
            extracted_data = extract_resume_data(file_path)
            print("Extracted Resume Data:")
            print(extracted_data)
            save_to_csv(extracted_data, filename=parsed_csv_path)
            print(f"Saved {filename} to CSV ✅\n")

    # Insert all parsed candidates into database
    print("🚀 Starting the parsing and insertion process...")
    parse_csv_and_insert(parsed_csv_path)
    print("🎯 All candidates have been processed and inserted.")