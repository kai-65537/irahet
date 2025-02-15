import os
import re
import glob
import datetime
import openai

# If you have your OpenAI key in an environment variable, you can do:
# openai.api_key = os.getenv("OPENAI_API_KEY")

# Otherwise, set it directly (not recommended for production):
client = openai.OpenAI(
    # base_url = , (uncomment if you use a proxy to OpenAI)
    api_key = YOUR_API_KEY,
)

# Today’s date in YYYY-MM-DD format
today = datetime.date.today().strftime("%Y-%m-%d")

# Adjust if your naming scheme is different.
FEEDBACK_FILE_PATTERN = "Feedback *.md"
MASTER_FEEDBACK_FILE = "Feedback.md"
chinese_name_pattern = re.compile(r"^Feedback (.+)\.md$")
date_heading_pattern = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$")

def parse_markdown_headings(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    headings_content = []
    current_date = None
    current_content = []

    for line in lines:
        match = date_heading_pattern.match(line.strip())
        if match:
            if current_date is not None:
                headings_content.append((current_date, "".join(current_content).strip()))
            current_date = match.group(1)
            current_content = []
        else:
            current_content.append(line)
    if current_date is not None:
        headings_content.append((current_date, "".join(current_content).strip()))

    return headings_content

def get_recent_notes(headings_content, today):
    index_for_today = None
    for i, (date_str, _) in enumerate(headings_content):
        if date_str == today:
            index_for_today = i
            break

    if index_for_today is None:
        return ("", "", "")

    # For a lack of better names:
    # noteA = content for today
    noteA = headings_content[index_for_today][1]

    # noteB = content for the heading above today's
    noteB = ""
    if index_for_today - 1 >= 0:
        noteB = headings_content[index_for_today - 1][1]

    # noteC = content for the heading above that
    noteC = ""
    if index_for_today - 2 >= 0:
        noteC = headings_content[index_for_today - 2][1]

    return (noteA, noteB, noteC)

# ---------------------------------------------------------------------------
# ChatGPT prompt
# ---------------------------------------------------------------------------
def build_prompt(student_name, noteA, noteB, noteC):
    template = f"""
You are an experienced and supportive ESL teacher who provides personalized feedback in Chinese. You will receive:
1. The student’s name (in Chinese).
2. Teacher’s notes from the last 3 days or less, where each note is a single line using the following notation:

Error Notation Format: [category-suffix] [word_or_phrase_WITH_CAPS_ON_ERROR]

Error Code Explanations:
- omi: Phoneme omission (omitted sound is marked by capitalization)
- rep: Phoneme replacement (replaced sound is marked by capitalization. always provide a simple word containing the correct phoneme)
- ins: Phoneme insertion (inserted sound is marked by capitalization, or a "0" at the point of insertion)
- str: Stress error (correct stress is marked by capitalization. say "重音" in Chinese)
- gro: Semantic grouping (correct grouping is marked by parenthesis. say "意群" in Chinese)
- res: Resyllabification (phrase to be resyllabified is provided after the code. say "连读" in Chinese)

Suffixes:
- "m" indicates a minor issue.
- "s" indicates a significant issue.

Your task is to generate a final feedback summary in Chinese that:
1. Greets the student by name.
2. Summarizes the key pronunciation errors based on the notes.
3. Provides detailed explanations and correction tips for each error using simple English phoneme analogies or teacher repetition suggestions.
4. Includes additional examples or minimal pair practice if needed.
5. Ends with a motivational closing remark.

The final feedback should be written in Chinese, 150-200 words total, and in a casual, conversational tone. DO NOT be overly affectionate.
Your response SHOULD NOT explicitly reference any error codes.
Your response should focus on TODAY's reponse, only referencing to previous notes when addressing trends, improvements, or repeated errors.
Your response should be in ONE single paragraph without formatting.
Try to focus on showcasing the correct pronounciation.

[User Provided Variables Start Here]

Student's Name (in Chinese): {student_name}

Notes (each line contains only the error notation):
The day before yesterday:
{noteC}

Yesterday:
{noteB}

Today:
{noteA}

[User Provided Variables End Here]

Please generate the final feedback summary in Chinese following the instructions above.
"""
    return template.strip()

def main():
    files = glob.glob(FEEDBACK_FILE_PATTERN)

    feedback_results = []  # will hold (student_name, gpt_output)

    for file_path in files:
        if file_path == MASTER_FEEDBACK_FILE:
            continue
        m = chinese_name_pattern.match(file_path)
        if not m:
            continue
        
        student_name = m.group(1)
        headings_content = parse_markdown_headings(file_path)
        noteA, noteB, noteC = get_recent_notes(headings_content, today)

        if not noteA:
            continue

        prompt = build_prompt(student_name, noteA, noteB, noteC)

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an experienced and supportive ESL teacher who provides personalized feedback in Chinese."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )
            gpt_output = response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API call failed for {student_name}: {e}")
            gpt_output = f"Error calling OpenAI API: {e}"

        feedback_results.append((student_name, gpt_output))

    # This overwrite the master feedback file. You might want to change this
    if feedback_results:
        with open(MASTER_FEEDBACK_FILE, "w", encoding="utf-8") as f:
            for student_name, gpt_output in feedback_results:
                f.write(f"## {student_name}\n\n")
                f.write(gpt_output.strip() + "\n\n")
        print(f"Finished. Consolidated feedback written to {MASTER_FEEDBACK_FILE}.")
    else:
        print("No feedback generated (no files contained a heading for today's date).")

if __name__ == "__main__":
    main()
