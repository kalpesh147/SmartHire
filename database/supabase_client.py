from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to insert candidate data into "Candidates" table
def insert_candidate_data(data: dict):
    try:
        response = supabase.table("Candidates").insert(data).execute()
        print(f"✅ Successfully inserted candidate {data['name']} into Candidates table.")
        return response
    except Exception as e:
        print(f"❌ Error inserting candidate data: {e}")
        return None

# Function to insert job data into Supabase
def insert_job_data(data: dict):
    try:
        print(f"Inserting job data: {data}")  # Debug print
        response = supabase.table("Job_descriptions").insert(data).execute()  # Correct table name
        print(f"Job data inserted: {data['job_title']}")
    except Exception as e:
        print(f"Error inserting job data: {e}")

# Fetch candidates from Supabase
def fetch_candidates():
    try:
        response = supabase.table("Candidates").select("*").execute()
        return response.data
    except Exception as e:
        print(f"❌ Error fetching candidates: {e}")
        return []

# Fetch jobs from Supabase
def fetch_jobs():
    try:
        response = supabase.table("Job_descriptions").select("*").execute()
        return response.data
    except Exception as e:
        print(f"❌ Error fetching jobs: {e}")
        return []

def insert_match_data(candidate_id, job_id, match_score):
    try:
        # Convert match_score to a regular Python float (float64)
        match_score = float(match_score)

        data = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "match_score": match_score,
            "status": "Pending"
        }
        response = supabase.table("Matches").insert(data).execute()
        print(f"✅ Match inserted: Candidate {candidate_id} with Job {job_id} (Score: {match_score:.2f})")
    except Exception as e:
        print(f"❌ Error inserting match data: {e}")

# Fetch pending matches
def fetch_pending_matches():
    try:
        response = supabase.table("Matches").select("*").eq("status", "Pending").execute()
        return response.data
    except Exception as e:
        print(f"❌ Error fetching pending matches: {e}")
        return []

# Update match status (Shortlisted or Rejected)
def update_match_status(candidate_id, job_id, new_status):
    try:
        response = supabase.table("Matches").update(    
            {"status": new_status}
        ).match({
            "candidate_id": candidate_id,
            "job_id": job_id
        }).execute()
        print(f"✅ Updated status for Candidate {candidate_id}, Job {job_id} to {new_status}")
    except Exception as e:
        print(f"❌ Error updating match status: {e}")

# Fetch shortlisted matches for interview scheduling
def fetch_shortlisted_matches():
    try:
        response = supabase.table("Matches").select(
            "candidate_id, job_id, match_score, status, Candidates(name, email), Job_descriptions(job_title)"
        ).eq("status", "Shortlisted").execute()
        return [
            {
                "candidate_id": m['candidate_id'],
                "job_id": m['job_id'],
                "match_score": m.get('match_score', 0.0),
                "candidate_name": m.get('Candidates', {}).get('name', 'Candidate'),
                "candidate_email": m.get('Candidates', {}).get('email', None),
                "job_title": m.get('Job_descriptions', {}).get('job_title', 'Unknown Job'),
            }
            for m in response.data
        ]
    except Exception as e:
        print(f"❌ Error fetching shortlisted matches: {e}")
        return []

# Insert interview schedule
def insert_interview_schedule(candidate_id, job_id, interview_time):
    try:
        data = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "interview_time": interview_time.isoformat(),
            "status": "Scheduled"
        }
        response = supabase.table("Interviews").insert(data).execute()
        print(f"✅ Interview scheduled for {candidate_id}-{job_id} on {interview_time}")
        return response
    except Exception as e:
        print(f"❌ Error inserting interview schedule: {e}")
        raise