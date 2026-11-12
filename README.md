# Telegram Contract Analysis Bot

A Python project designed to analyse PDF contracts through Telegram and explain clauses and potential risks in simple language. It is intended for different contract types, including rental and employment agreements.

## Features and intended output

- Extract text from uploaded PDF contracts
- Summarise the agreement
- Identify clauses about payments, penalties, liability and termination
- Highlight potential risks and missing protections
- Return the analysis through Telegram

The example screenshots also show a risk score and suggestions. These are AI-generated outputs, not validated legal assessments.

## Technology

- Python
- FastAPI and Uvicorn
- Telegram Bot API through python-telegram-bot
- PyPDF2 for PDF text extraction
- Groq API with Llama 3.3 70B Versatile

The repository also contains an earlier WhatsApp prototype using pywa, requests and keyword matching.

## Intended workflow

1. A user uploads a PDF contract in Telegram.
2. The bot downloads the document and extracts its text.
3. The first 12,000 characters are sent to Groq for LLM analysis.
4. The analysis is returned to the user in the Telegram chat.

## Repository status

The current bot.py combines the WhatsApp and Telegram prototypes. As committed, a stray pasted line causes a Python syntax error, and the Telegram update polling loop is not started. The uploaded code therefore needs cleanup before it can run end to end.

There are no verified installation and launch instructions yet. API credentials must be kept out of version control; loading them through environment variables is a planned improvement.

## Screenshots

These screenshots illustrate a Telegram conversation and the analysis output format. They do not verify that the current committed code runs successfully or that the analysis is accurate. One example shows a rental filename but an employment-agreement summary, so the input and response need checking.

<img width="720" height="1385" alt="Contract upload and analysis example" src="https://github.com/user-attachments/assets/0ff636a6-91ce-4fef-959d-9d3a5934be26" />

<img width="720" height="1210" alt="Contract analysis example continued" src="https://github.com/user-attachments/assets/bd250066-f495-4e13-8581-8fd1fd74fecf" />

<img width="720" height="1192" alt="Risk analysis example" src="https://github.com/user-attachments/assets/7d7fb918-a813-4205-b4e7-e643561acd6c" />

<img width="720" height="1215" alt="Analysis suggestions example" src="https://github.com/user-attachments/assets/b8909eaf-d3a2-4c9b-849e-59fee1008512" />

## Limitations and privacy

- AI-generated analysis can contain mistakes. It is not legal advice or a substitute for a qualified lawyer.
- Contract text is sent to Groq, an external AI service. Do not upload confidential or sensitive documents without appropriate permission.
- The current extraction approach handles PDF text and limits analysis to the first 12,000 characters. Scanned PDFs may require OCR, which is not implemented here.
- Supporting different contract types does not guarantee correct identification or analysis of every document.

## Next steps

- Separate the Telegram and WhatsApp prototypes
- Fix the syntax error and complete Telegram message polling
- Load credentials securely from environment variables
- Test with clearly labelled sample contracts
- Add reproducible setup instructions and document test results
