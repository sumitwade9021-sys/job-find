import os
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
import smtplib

def fetch_jobs_from_rss(url, max_items=10):
    try:
        resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.content, "xml")
        items = soup.find_all("item")[:max_items]
        jobs = []
        for it in items:
            jobs.append({
                "title": it.title.text if it.title else "",
                "link": it.link.text if it.link else "",
                "desc": (it.description.text if it.description else "")[:300]
            })
        return jobs
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []

def format_email(jobs):
    if not jobs:
        return "No matching jobs today."
    return "\n\n".join(
        f"{i+1}. {j['title']}\n{j['link']}\n{j['desc']}"
        for i, j in enumerate(jobs)
    )

def send_email(subject, body):
    msg = EmailMessage()
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["EMAIL_TO"]
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"])) as smtp:
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        smtp.send_message(msg)

def main():
    RSS_FEEDS = [
        "https://remoteok.com/rss?search=devops",
        "https://wellfound.com/jobs/feed?keywords=devops&remote=true"
    ]
    all_jobs = []
    for url in RSS_FEEDS:
        all_jobs.extend(fetch_jobs_from_rss(url))

    # Remove duplicate links
    unique = {job["link"]: job for job in all_jobs}
    all_jobs = list(unique.values())

    print(f"Collected {len(all_jobs)} jobs")
    email_body = format_email(all_jobs)
    send_email("Daily Entry-Level DevOps Job Alerts", email_body)

if __name__ == "__main__":
    main()
