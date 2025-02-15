# irahet
***IRAHET Requires A Human ESL Teacher***

IRAHET is a Python script designed to assist ESL teachers by generating personalized feedback summaries for students based on pronunciation error logs. It scans markdown files for daily feedback records, extracts relevant notes, and uses OpenAI's ChatGPT API to generate structured feedback in Chinese.

## 📂 File Structure

To run IRAHET effectively, maintain the following file structure in your working directory:

```
/your-folder/
│── Feedback 王小明.md
│── Feedback 李美丽.md
│── Feedback 张伟.md
│── ...
│── irahet.py
│── Feedback.md   # (Generated output)
```

Each student has a markdown file in the format:  
`Feedback <Chinese Name>.md`

Each file contains feedback records under second-level markdown headings (`## YYYY-MM-DD`), where `YYYY-MM-DD` is the date of the feedback entry.

## ⚙️ How It Works

1. **Scans Markdown Files**  
   - Searches for files matching `36.11 Feedback *.md` (excluding `36.11 Feedback.md`).
   - Extracts the Chinese name from each filename.

2. **Parses Markdown Headings**  
   - Identifies `## YYYY-MM-DD` headings in each file.
   - Extracts notes recorded for **today** and up to **two previous days**.

3. **Constructs a GPT Prompt**  
   - Formats extracted notes into a structured prompt.
   - Uses a predefined system message to guide ChatGPT in generating feedback.

4. **Calls OpenAI’s API**  
   - Uses `gpt-3.5-turbo` (customizable) to generate student feedback in Chinese.

5. **Writes to a Consolidated Feedback File**  
   - Appends feedback under `## <Chinese Name>` in `36.11 Feedback.md`.  
   - If the file exists, it overwrites previous runs.

## 📝 Error Coding System

IRAHET processes pronunciation errors based on a structured notation system. Each recorded error follows this format:

```
[category-suffix] [WORD_OR_PHRASE_WITH_CAPS_ON_ERROR]
```

### 🔍 **Error Categories**
| Code  | Meaning | Example |
|--------|--------------------------------------------------|----------------|
| **omi** | Phoneme omission (missing sound) | `omi-s wondER` → "wonder" pronounced as "wond" |
| **rep** | Phoneme replacement (incorrect substitution) | `rep-m bIt` → "bit" pronounced as "bet" |
| **ins** | Phoneme insertion (extra sound) | `ins-m g0lass` → "glass" pronounced as "galass" |
| **str** | Stress error (incorrect syllable emphasis) | `str-s aBOUT` → "about" pronounced with stress on "A" |
| **gro** | Semantic grouping (wrong word grouping) | `gro-s however, (she said)` → unnatural break between words |
| **res** | Resyllabification (mis-segmentation of syllables) | `res-m i-wanted-to` → missing resyllabification for "I wanted to" |

### 🔢 **Suffixes**
| Suffix | Meaning |
|--------|-----------------------------|
| **m**  | Minor issue (not severely affecting comprehension) |
| **s**  | Significant issue (may lead to miscommunication) |

### 🏗 **Example Notes in a Markdown File**
```
## 2025-02-13
omi-s wondER
rep-m bIt
str-s aBOUT

## 2025-02-14
ins-m g0lass
res-m i-wanted-to
```

## 🔧 Customization

- **API Key**:  
  - Set your OpenAI API key in `irahet.py` using `openai.api_key = "your_api_key"`, or use an environment variable.
  
- **Date Parsing & Heading Detection**:  
  - Adjust the regex pattern in `date_heading_pattern` if your file format differs.
  
- **Prompt Adjustments**:  
  - Modify the `build_prompt()` function to tweak GPT instructions or change the feedback format.
  
- **ChatGPT Model & Temperature**:  
  - Update `openai.ChatCompletion.create()` to change the model (e.g., `gpt-4`) or adjust `temperature` for more creative or precise responses.

## 🏃‍♂️ Running the Script

Ensure Python 3 is installed and run:

```sh
python irahet.py
```

### 🛠️ Dependencies

- Python 3+
- `openai` (Install via `pip install openai`)

---

🚀 **IRAHET keeps ESL teachers in control by automating feedback while maintaining the human touch.**
