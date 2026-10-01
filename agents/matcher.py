
import os
import sys
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.supabase_client import fetch_candidates, fetch_jobs, insert_match_data

# Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def match_candidates_to_jobs():
    candidates = fetch_candidates()
    jobs = fetch_jobs()

    if not candidates or not jobs:
        print("❌ No candidates or jobs found!")
        return

    print("✅ Starting matching process...")

    candidate_embeddings = {
        c['id']: model.encode(" ".join(c.get('skills', [])))
        for c in candidates
    }
    job_embeddings = {
        j['id']: model.encode(" ".join(j.get('requirements', [])))
        for j in jobs
    }

    match_results = []

    for candidate in tqdm(candidates, desc="Matching candidates"):
        for job in jobs:
            match_score = calculate_match_score(candidate, job, candidate_embeddings, job_embeddings)
            if match_score >= 0.5:
                match_results.append((candidate['id'], job['id'], match_score))

    if match_results:
        insert_bulk_matches(match_results)
    else:
        print("❌ No significant matches found.")

    print("✅ Matching process completed!")

def calculate_match_score(candidate, job, candidate_embeddings, job_embeddings):
    experience_score = calculate_experience_score(candidate, job)
    skill_match = calculate_skill_match(candidate['id'], job['id'], candidate_embeddings, job_embeddings)
    education_match = calculate_education_match(candidate, job)
    job_title_match = calculate_job_title_match(candidate, job)

    # Updated weights: experience title match > skills > education > experience_years
    final_score = (
        0.45 * experience_score +
        0.30 * skill_match +
        0.15 * education_match +
        0.10 * job_title_match
    )
    return final_score

def calculate_skill_match(candidate_id, job_id, candidate_embeddings, job_embeddings):
    if candidate_id not in candidate_embeddings or job_id not in job_embeddings:
        return 0.0

    candidate_embedding = candidate_embeddings[candidate_id]
    job_embedding = job_embeddings[job_id]

    return cosine_similarity(
        candidate_embedding.reshape(1, -1),
        job_embedding.reshape(1, -1)
    )[0][0]

def calculate_education_match(candidate, job):
    candidate_education = candidate.get('parsed_resume', '').lower()
    job_education = job.get('education', '').lower()

    if candidate_education and job_education:
        return 1 if job_education in candidate_education else 0
    return 0

def calculate_job_title_match(candidate, job):
    parsed_resume = candidate.get('parsed_resume', '').lower()
    job_title = job.get('job_title', '').lower()
    if job_title in parsed_resume:
        return 1
    return 0

def calculate_experience_score(candidate, job):
    parsed_resume = candidate.get('parsed_resume', '').lower()
    job_title = job.get('job_title', '').lower()

    # High score if the candidate has held a similar job title before
    if job_title in parsed_resume:
        return 1.0

    # Otherwise, fallback to numeric experience match
    candidate_experience = candidate.get('experience_years', 0)
    job_experience = job.get('required_experience', 0)

    if job_experience > 0:
        experience_diff = abs(candidate_experience - job_experience)
        return max(0, 1 - (experience_diff / 10))
    return 0.0

def insert_bulk_matches(matches):
    from database.supabase_client import supabase
    try:
        data = [{'candidate_id': cid, 'job_id': jid, 'match_score': float(score), 'status': 'Pending'}
                for cid, jid, score in matches]
        supabase.table("Matches").insert(data).execute()
        print(f"✅ Inserted {len(matches)} optimized matches into the database.")
    except Exception as e:
        print(f"❌ Error inserting bulk matches: {e}")

if __name__ == "__main__":
    match_candidates_to_jobs()
