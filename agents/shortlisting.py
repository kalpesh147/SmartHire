# shortlisting.py

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.supabase_client import fetch_pending_matches, update_match_status

def shortlist_candidates(threshold=0.8):
    print("✅ Shortlisting Agent Started...")  # Always print when starting

    pending_matches = fetch_pending_matches()

    if not pending_matches:
        print("❌ No pending matches found!")
        return

    for match in pending_matches:
        candidate_id = match['candidate_id']
        job_id = match['job_id']
        match_score = match['match_score']

        print(f"Checking Candidate {candidate_id}, Job {job_id}, Score: {match_score}")

        if match_score is None:
            update_match_status(candidate_id, job_id, "Rejected")
            continue

        if match_score >= threshold:
            new_status = "Shortlisted"
        else:
            new_status = "Rejected"

        update_match_status(candidate_id, job_id, new_status)

    print("✅ Shortlisting process completed!")

# ✨ THIS MUST BE PRESENT BELOW ✨
if __name__ == "__main__":
    shortlist_candidates()
