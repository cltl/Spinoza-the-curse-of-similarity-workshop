#!/usr/bin/env python3
"""
Creates a Google Form quiz for 24 whiteboard images.

Prerequisites:
  1. Go to https://console.cloud.google.com/
  2. Create a project, enable "Google Forms API" and "Google Drive API"
  3. Create OAuth 2.0 credentials (Desktop app type)
  4. Download the credentials JSON and save it as 'credentials.json' next to this script
  5. Run: pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client
  6. Run: python3 create_quiz_form.py

On first run a browser window will open asking you to log in with your Google account.
The form URL is printed at the end.
"""

import os
import json
import pickle
import mimetypes
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive",
]

SCRIPT_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Quiz content: 24 whiteboards
# ---------------------------------------------------------------------------
QUIZ_DATA = [
    {
        "number": 1,
        "file": "1.bram-who-is-in-control1.HEIC",
        "q1_answer": "who-is-in-control",
        "q2_answer": "April, 2026",
        "q3": "What HI use-case is discussed?",
        "q3_answer": "Diabetes lifestyle coaching",
    },
    {
        "number": 2,
        "file": "2.combot-project.HEIC",
        "q1_answer": "combot-course",
        "q2_answer": "February, 2023",
        "q3": "What is the goal of the student-project?",
        "q3_answer": "To reconstruct the Knowledge Graph of the other agent",
    },
    {
        "number": 3,
        "file": "3.dasym2.JPG",
        "q1_answer": "dasym-start-up",
        "q2_answer": "July, 2022",
        "q3": "Why is there a separation between CLTL and the start-up?",
        "q3_answer": "Because CLTL software is open source and cannot be commercialised.",
    },
    {
        "number": 4,
        "file": "4.data2text.JPG",
        "q1_answer": "data2text",
        "q2_answer": "March, 2017",
        "q3": "What project proposal is being prepared?",
        "q3_answer": "Dutch FrameNet",
    },
    {
        "number": 5,
        "file": "5.get2knowmore.HEIC",
        "q1_answer": "Monitoring Activities of Daily Life",
        "q2_answer": "May, 2024",
        "q3": "What drive is being modeled here?",
        "q3_answer": "filling knowledge gaps",
    },
    {
        "number": 6,
        "file": "6.HLT-intro-design2.JPG",
        "q1_answer": "HLT introduction",
        "q2_answer": "July, 2017",
        "q3": "What corpus analysis is explained in unix-for-poets?",
        "q3_answer": "concordance",
    },
    {
        "number": 7,
        "file": "7.jaap-phd1.HEIC",
        "q1_answer": "Jaap",
        "q2_answer": "April, 2024",
        "q3": "What does a score of 1.2 mean?",
        "q3_answer": "We do not know",
    },
    {
        "number": 8,
        "file": "8.lea-phd1.HEIC",
        "q1_answer": "Lea",
        "q2_answer": "March, 2024",
        "q3": "What do 0 and the text boxes represent?",
        "q3_answer": "the conversational context",
    },
    {
        "number": 9,
        "file": "9.lea-phd2.HEIC",
        "q1_answer": "Lea",
        "q2_answer": "August, 2023",
        "q3": "Where is Lea?",
        "q3_answer": "Oxford.",
    },
    {
        "number": 10,
        "file": "10.levi-phd2.HEIC",
        "q1_answer": "Levi",
        "q2_answer": "July, 2023",
        "q3": "What does DPA stand for?",
        "q3_answer": "Direct Anchor Participant",
    },
    {
        "number": 11,
        "file": "11.marten-basic-level.HEIC",
        "q1_answer": "Dutch FrameNet",
        "q2_answer": "July, 2022",
        "q3": "What level was being detected?",
        "q3_answer": "event basic level",
    },
    {
        "number": 12,
        "file": "12.semeval.marten-filip-longtail.JPG",
        "q1_answer": "SemEval 2018 long tail",
        "q2_answer": "November, 2017",
        "q3": "What does the straight line represent in the power-law-graph?",
        "q3_answer": "the frequency in the world",
    },
    {
        "number": 13,
        "file": "13.marten-wsd1.JPG",
        "q1_answer": "Marten",
        "q2_answer": "November, 2017",
        "q3": "How many word senses are represented here?",
        "q3_answer": "4",
    },
    {
        "number": 14,
        "file": "14.newsreader-demo.JPG",
        "q1_answer": "Newsreader",
        "q2_answer": "July, 2016",
        "q3": "What demo is designed here?",
        "q3_answer": "Storyteller",
    },
    {
        "number": 15,
        "file": "15.newsreader.JPG",
        "q1_answer": "newsreader",
        "q2_answer": "July, 2016",
        "q3": "What do WTL and NTL stand for?",
        "q3_answer": "World Time Line and News Time Line",
    },
    {
        "number": 16,
        "file": "16.selea.HEIC",
        "q1_answer": "Selea",
        "q2_answer": "August, 2025",
        "q3": "Who is leaving?",
        "q3_answer": "Selene",
    },
    {
        "number": 17,
        "file": "17.selene-thesis1.HEIC",
        "q1_answer": "Selene",
        "q2_answer": "October, 2024",
        "q3": "Is what Karla speaks a subject or complement gap?",
        "q3_answer": "Complement gap",
    },
    {
        "number": 18,
        "file": "18.stella-phd1.HEIC",
        "q1_answer": "Stella",
        "q2_answer": "February, 2026",
        "q3": "Which word is misspelled here?",
        "q3_answer": "identities",
    },
    {
        "number": 19,
        "file": "19.stella-phd2.HEIC",
        "q1_answer": "Stella",
        "q2_answer": "May, 2026",
        "q3": "What is the holy grail?",
        "q3_answer": "full reconstruction of a historical world",
    },
    {
        "number": 20,
        "file": "20.unknown-project.JPG",
        "q1_answer": "Unknown",
        "q2_answer": "March, 2017",
        "q3": "Who is the guy to the left of the picture?",
        "q3_answer": "Yassine",
    },
    {
        "number": 21,
        "file": "21.tommaso2.jpg",
        "q1_answer": "Tommaso",
        "q2_answer": "December, 2015",
        "q3": "What is being placed in time?",
        "q3_answer": "Events",
    },
    {
        "number": 22,
        "file": "22.unk2.JPG",
        "q1_answer": "unknown",
        "q2_answer": "March, 2017",
        "q3": "What is the English translation?",
        "q3_answer": "A welcome on behalf of your colleagues in the Computational Lexicology and Textmining Lab",
    },
    {
        "number": 23,
        "file": "23.wende-phd1.HEIC",
        "q1_answer": "Wende",
        "q2_answer": "July, 2023",
        "q3": "What does the graph indicate for Event3 for English, Dutch and Arabic?",
        "q3_answer": "Different toxicity",
    },
    {
        "number": 24,
        "file": "24.wende-phd2.HEIC",
        "q1_answer": "Wende",
        "q2_answer": "March, 2023",
        "q3": "What is the green jigsaw puzzle suggesting?",
        "q3_answer": "Language Transfer",
    },
]

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def get_credentials():
    creds = None
    token_path = SCRIPT_DIR / "token.pickle"
    creds_path = SCRIPT_DIR / "credentials.json"

    if not creds_path.exists():
        raise FileNotFoundError(
            "credentials.json not found. Download it from Google Cloud Console "
            "(APIs & Services > Credentials > OAuth 2.0 Client IDs > Download)."
        )

    if token_path.exists():
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    return creds

# ---------------------------------------------------------------------------
# Upload image to Drive and return a publicly readable URI for Forms
# ---------------------------------------------------------------------------

def upload_image(drive_service, image_path: Path, folder_id: str) -> str:
    """Upload image to Drive folder and return a URI suitable for Forms imageItem."""
    mime, _ = mimetypes.guess_type(str(image_path))
    # HEIC is not widely recognised; Google Drive handles it fine
    if mime is None:
        mime = "image/heic"

    file_metadata = {"name": image_path.name, "parents": [folder_id]}
    media = MediaFileUpload(str(image_path), mimetype=mime, resumable=True)
    uploaded = (
        drive_service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    file_id = uploaded["id"]

    # Make file publicly readable so Forms can embed it
    drive_service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    # Return the URI that the Forms API accepts
    return f"https://drive.google.com/uc?id={file_id}"


def create_drive_folder(drive_service, name: str) -> str:
    folder_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
    return folder["id"]


# ---------------------------------------------------------------------------
# Build the Forms API batch-update request body
# ---------------------------------------------------------------------------

def build_requests(image_uris: dict) -> list:
    """Return a list of batchUpdate request items for all 24 whiteboards."""
    requests = []
    index = 0  # insertion index within the form

    for wb in QUIZ_DATA:
        n = wb["number"]
        uri = image_uris.get(n)

        # --- Page-break / section header ---
        if n > 1:
            requests.append({
                "createItem": {
                    "item": {
                        "title": f"Whiteboard {n}",
                        "pageBreakItem": {},
                    },
                    "location": {"index": index},
                }
            })
            index += 1

        # --- Image ---
        if uri:
            requests.append({
                "createItem": {
                    "item": {
                        "title": f"Whiteboard {n}",
                        "imageItem": {
                            "image": {
                                "sourceUri": uri,
                                "altText": f"Whiteboard image {n}",
                            },
                            "alignment": "CENTER",
                        },
                    },
                    "location": {"index": index},
                }
            })
            index += 1

        # --- Q1: Name (1 point) ---
        requests.append({
            "createItem": {
                "item": {
                    "title": "What is the name of the project, PhD, course, or demo?",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "grading": {
                                "pointValue": 1,
                                "correctAnswers": {
                                    "answers": [{"value": wb["q1_answer"]}]
                                },
                            },
                            "textQuestion": {"paragraph": False},
                        }
                    },
                },
                "location": {"index": index},
            }
        })
        index += 1

        # --- Q2: Date (2 points) ---
        requests.append({
            "createItem": {
                "item": {
                    "title": "What is the month and year of this whiteboard? (e.g. April, 2026)",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "grading": {
                                "pointValue": 2,
                                "correctAnswers": {
                                    "answers": [{"value": wb["q2_answer"]}]
                                },
                            },
                            "textQuestion": {"paragraph": False},
                        }
                    },
                },
                "location": {"index": index},
            }
        })
        index += 1

        # --- Q3: Special question (3 points) ---
        requests.append({
            "createItem": {
                "item": {
                    "title": wb["q3"],
                    "questionItem": {
                        "question": {
                            "required": True,
                            "grading": {
                                "pointValue": 3,
                                "correctAnswers": {
                                    "answers": [{"value": wb["q3_answer"]}]
                                },
                            },
                            "textQuestion": {"paragraph": True},
                        }
                    },
                },
                "location": {"index": index},
            }
        })
        index += 1

    return requests


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Authenticating with Google…")
    creds = get_credentials()

    drive_service = build("drive", "v3", credentials=creds)
    forms_service = build("forms", "v1", credentials=creds)

    # --- Upload images ---
    print("Creating Drive folder for images…")
    folder_id = create_drive_folder(drive_service, "Whiteboard Quiz Images")
    print(f"Drive folder id: {folder_id}")

    image_uris = {}
    for wb in QUIZ_DATA:
        img_path = SCRIPT_DIR / wb["file"]
        if img_path.exists():
            print(f"  Uploading {wb['file']}…")
            uri = upload_image(drive_service, img_path, folder_id)
            image_uris[wb["number"]] = uri
        else:
            print(f"  WARNING: {wb['file']} not found, skipping image.")

    # --- Create the form ---
    print("Creating Google Form…")
    form_body = {
        "info": {
            "title": "Whiteboard Quiz",
            "documentTitle": "Whiteboard Quiz",
        }
    }
    form = forms_service.forms().create(body=form_body).execute()
    form_id = form["formId"]
    print(f"Form id: {form_id}")

    # Enable quiz mode
    forms_service.forms().batchUpdate(
        formId=form_id,
        body={
            "requests": [
                {
                    "updateSettings": {
                        "settings": {
                            "quizSettings": {"isQuiz": True}
                        },
                        "updateMask": "quizSettings.isQuiz",
                    }
                }
            ]
        },
    ).execute()

    # Update description
    forms_service.forms().batchUpdate(
        formId=form_id,
        body={
            "requests": [
                {
                    "updateFormInfo": {
                        "info": {
                            "description": (
                                "For each whiteboard your team can earn 6 points:\n"
                                "• What project / PhD / course / demo is discussed — 1 point\n"
                                "• The month and year of the whiteboard — 2 points\n"
                                "• Special question — 3 points\n\n"
                                "Total: 144 points"
                            )
                        },
                        "updateMask": "description",
                    }
                }
            ]
        },
    ).execute()

    # --- Add all questions ---
    print("Adding questions…")
    requests = build_requests(image_uris)

    # Forms API batchUpdate accepts max 200 requests at a time; chunk if needed
    chunk_size = 50
    for i in range(0, len(requests), chunk_size):
        chunk = requests[i : i + chunk_size]
        forms_service.forms().batchUpdate(
            formId=form_id, body={"requests": chunk}
        ).execute()
        print(f"  Sent requests {i+1}–{i+len(chunk)}/{len(requests)}")

    edit_url = f"https://docs.google.com/forms/d/{form_id}/edit"
    fill_url = f"https://docs.google.com/forms/d/{form_id}/viewform"

    print("\n✓ Done!")
    print(f"  Edit URL  : {edit_url}")
    print(f"  Fill URL  : {fill_url}")

    # Save URLs to a file for easy reference
    with open(SCRIPT_DIR / "form_urls.txt", "w") as f:
        f.write(f"Edit URL : {edit_url}\n")
        f.write(f"Fill URL : {fill_url}\n")
        f.write(f"Form ID  : {form_id}\n")
        f.write(f"Drive folder ID: {folder_id}\n")
    print("  URLs saved to form_urls.txt")


if __name__ == "__main__":
    main()
