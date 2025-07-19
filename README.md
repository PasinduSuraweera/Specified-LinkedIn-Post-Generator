# Specified LinkedIn Posts

A modern, lightweight **Streamlit**-based application for generating professional LinkedIn posts using **DeepSeek-R1** and **Llama** models, with customizable topics, lengths, and languages.

## Overview

**Specified LinkedIn Posts** is a web-based tool designed to help users create engaging, professional LinkedIn posts effortlessly. Whether you're sharing career advice, motivational insights, or job search tips, this app provides a user-friendly interface to generate tailored content based on your preferences, powered by advanced AI models.

## Key Features

- ✍️ **Customizable Posts**: Generate posts based on specific topics, lengths (Short, Medium, Long), and languages (English or Sinhala-English mix).
- 🎯 **Topic Selection**: Choose from a variety of topics like Job Search, Mental Health, Career Advice, and more.
- 📏 **Length Options**: Select Short (1-5 lines), Medium (6-10 lines), or Long (11-15 lines) posts.
- 🌐 **Language Support**: Create posts in English, with cleaned and processed text for consistency.
- 🔍 **Few-Shot Learning**: Uses pre-processed LinkedIn posts to ensure generated content aligns with real-world examples.
- 💻 **Modern UI**: Streamlined, centered layout with intuitive dropdowns and a professional design.
- ⏳ **Real-Time Generation**: Instantly generate posts with a single click, with a loading spinner for a smooth experience.

## How to Use

### Step 1: Set Up Environment
- Ensure you have a **GROQ_API_KEY** set in a `.env` file for accessing the LLM (DeepSeek-R1 and Llama).
- Install dependencies from `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

### Step 2: Run the App
- Launch the Streamlit app:
  ```bash
  streamlit run main.py
  ```

### Step 3: Generate a Post
- Select a **Topic** (e.g., Job Search, Mental Health) from the dropdown.
- Choose a **Length** (Short, Medium, or Long).
- Pick a **Language** (English or Sinhala).
- Click **Generate Post** to create your customized LinkedIn post.
- View the generated post in the output section and copy it for use on LinkedIn.

## Example Workflow

1. Open the app and select **Mental Health** as the topic.
2. Choose **Medium** length for a 6-10 line post.
3. Select **English** as the language.
4. Click **Generate Post** to receive a professional, engaging post like:
   > To everyone navigating the job search journey: I see you. Rejections sting, but they don’t define you. Your mental health matters more than any offer letter. Take a moment to breathe—you’ve got this. 🌟
5. Copy the post to share on LinkedIn or save for later.

## API Integration

The app uses the **ChatGroq** API (via `langchain_groq`) to interact with the **DeepSeek-R1-distill-llama-70b** model for generating posts. Key components:
- **Prompt Engineering**: Combines user inputs (topic, length, language) with few-shot examples for context-aware generation.
- **Few-Shot Learning**: Leverages pre-processed posts from `processed_posts.json` to guide the LLM.
- **Text Cleaning**: Ensures clean, Unicode-safe text using `preprocess.py`.

For more details, refer to the [Grok API documentation](https://x.ai/api).

## Project Structure

- `main.py`: Core Streamlit app with UI and post generation logic.
- `post_generator.py`: Handles prompt creation and LLM invocation for post generation.
- `preprocess.py`: Cleans and processes raw LinkedIn posts, extracting metadata like line count, language, and tags.
- `few_shot.py`: Manages few-shot learning by filtering posts based on user inputs.
- `llm_helper.py`: Configures the LLM connection using the Groq API.
- `raw_posts.json`: Sample raw LinkedIn posts for processing.
- `processed_posts.json`: Cleaned and enriched posts with metadata.

## Troubleshooting

| Problem | Solution |
|--------|----------|
| **API Key Not Working** | Ensure `GROQ_API_KEY` is set in `.env`. Check [x.ai/api](https://x.ai/api) for details. |
| **No Posts Generated** | Verify topic, length, and language selections. Ensure `processed_posts.json` exists. |
| **Unicode Errors** | Check `preprocess.py` logs (`preprocess_errors.log`) for text cleaning issues. |
| **Slow Generation** | Ensure a stable internet connection for API calls. |
| **Invalid JSON in Posts** | Validate `raw_posts.json` and `processed_posts.json` for correct JSON format. |

## Conclusion

**Specified LinkedIn Posts** simplifies the process of creating professional, engaging LinkedIn content. Whether you're a job seeker, career coach, or professional sharing insights, this tool combines AI-powered generation with a clean, intuitive interface to help you craft posts that resonate.

**Try the Live App → [specified-linkedin-post-generator.streamlit.app](https://specified-linkedin-post-generator.streamlit.app)**
