import os
import sys
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, filename='scheduler.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Add parent directory to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.supabase_client import fetch_shortlisted_matches, insert_interview_schedule

# Load environment variables
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email(to_email, candidate_name, job_title, interview_time):
    """Send an interview scheduling email to the candidate."""
    try:
        msg = EmailMessage()
        msg['Subject'] = f"Interview Scheduled for {job_title}"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email

        msg.set_content(f"""
        Hi {candidate_name},

        Congratulations! 🎉 You have been shortlisted for the position of {job_title}.

        Your interview is scheduled on {interview_time.strftime('%Y-%m-%d %H:%M:%S')}.

        Best of luck!

        Regards,
        SmartHire Team
        """)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        logging.info(f"Email sent to {candidate_name} ({to_email}) for job {job_title}")
        print(f"✅ Email sent to {candidate_name} ({to_email}) for job {job_title}")
        return True

    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}")
        print(f"❌ Error sending email to {to_email}: {str(e)}")
        return False

def schedule_interviews():
    """Schedule interviews for shortlisted candidates and send emails."""
    print("✅ Interview Scheduler Started...")
    logging.info("Interview Scheduler Started")

    # Fetch shortlisted matches
    try:
        shortlisted_matches = fetch_shortlisted_matches()
    except Exception as e:
        logging.error(f"Failed to fetch shortlisted matches: {str(e)}")
        print(f"❌ Error fetching shortlisted matches: {str(e)}")
        return

    if not shortlisted_matches:
        logging.info("No shortlisted matches found")
        print("❌ No shortlisted matches found!")
        return

    # Remove duplicates based on candidate_id to avoid sending multiple emails
    shortlisted_matches = {match['candidate_id']: match for match in shortlisted_matches}.values()

    # Track the last scheduled interview time for each candidate
    candidate_interview_times = {}

    # Start scheduling from the next business day at 9 AM
    current_time = datetime.now()
    next_day = current_time + timedelta(days=1)
    if next_day.weekday() >= 5:  # Skip weekends (Saturday=5, Sunday=6)
        next_day += timedelta(days=7 - next_day.weekday())
    interview_time = datetime(next_day.year, next_day.month, next_day.day, 9, 0)

    for match in shortlisted_matches:
        candidate_id = match.get('candidate_id')
        job_id = match.get('job_id')
        candidate_name = match.get('candidate_name', 'Unknown')
        to_email = match.get('candidate_email')
        job_title = match.get('job_title', 'Unknown')

        if not to_email:
            logging.warning(f"Missing email for candidate {candidate_name} (ID: {candidate_id})")
            print(f"⚠️ Skipping candidate {candidate_name} due to missing email.")
            continue

        # Check if candidate has already been scheduled for an interview
        if candidate_id in candidate_interview_times:
            interview_time = candidate_interview_times[candidate_id] + timedelta(minutes=30)
        else:
            # First interview for this candidate, use the current time slot
            interview_time = datetime(next_day.year, next_day.month, next_day.day, 9, 0)

        # Send email
        email_sent = send_email(to_email, candidate_name, job_title, interview_time)

        if email_sent:
            # Insert interview schedule into database
            try:
                insert_interview_schedule(candidate_id, job_id, interview_time)
                logging.info(f"Scheduled interview for {candidate_name} (Job: {job_title}) at {interview_time}")
                print(f"✅ Scheduled interview for {candidate_name} (Job: {job_title}) at {interview_time}")
            except Exception as e:
                logging.error(f"Failed to insert interview schedule for {candidate_name}: {str(e)}")
                print(f"❌ Error inserting interview schedule for {candidate_name}: {str(e)}")

            # Update the candidate's last scheduled interview time
            candidate_interview_times[candidate_id] = interview_time

        # Increment interview time by 30 minutes for the next candidate
        interview_time += timedelta(minutes=30)

    logging.info("Interview scheduling completed")
    print("✅ Interview scheduling completed!")

if __name__ == "__main__":
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        logging.error("Missing EMAIL_ADDRESS or EMAIL_PASSWORD in environment variables")
        print("❌ Missing EMAIL_ADDRESS or EMAIL_PASSWORD. Please set them in the .env file.")
        sys.exit(1)
    schedule_interviews()