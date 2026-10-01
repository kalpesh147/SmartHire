import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.supabase_client import supabase

# Candidate data to insert
candidate_data = {
    "name": "Alyssa Chavez",
    "email": "alyssachavez88@gmail.com",
    "skills": [
        "Cybersecurity", 
        "Penetration testing", 
        "Risk assessment", 
        "Securing enterprise networks", 
        "AWS Certified Solutions Architect", 
        "Java", 
        "Spring Boot", 
        "MySQL", 
        "Kafka", 
        "Azure DevOps"
    ],
    "experience_years": 4,  # 2019-2023 (4 years of experience)
    "parsed_resume": """Candidate Resume (ID: C1061)
    Name: Alyssa Chavez
    Email: alyssachavez88@gmail.com
    Phone: +1-465-3587
    Education: Diploma in Software Engineering (2013-2015)
    Hands-on experience in full-stack web development and mobile app creation.
    Work Experience: Data Scientist at ABC Inc. (2019-2023)
    Built predictive models that enhanced decision-making processes, reducing operational costs by 25%.
    Skills: Cybersecurity - Skilled in penetration testing, risk assessment, and securing enterprise networks against cyber threats.
    Certifications: AWS Certified Solutions Architect
    Achievements: Published a research paper on AI ethics - Contributed to an AI ethics framework adopted by industry leaders, shaping responsible AI development.
    Tech Stack: Java, Spring Boot, MySQL, Kafka, Azure DevOps
    """
}

print("Candidate data:", candidate_data)

# Insert data into Candidates table
response = supabase.table("Candidates").insert(candidate_data).execute()

# Check the response object for success or error
if response.data:
    print("Candidate data inserted successfully!")
else:
    print(f"Error inserting candidate: {response.error}")
