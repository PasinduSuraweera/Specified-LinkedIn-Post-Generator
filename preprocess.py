import json
import re
import unicodedata
import logging
from llm_helper import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

# Set up logging
logging.basicConfig(filename='preprocess_errors.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def clean_text(text: str) -> str:
    """
    Clean text by removing or replacing invalid Unicode characters and surrogates.
    Preserve valid Sinhala characters (U+0D80–U+0DFF).
    """
    try:
        # Encode to UTF-8, ignoring errors
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
    except UnicodeEncodeError:
        # Normalize and remove surrogate characters (U+D800 to U+DFFF)
        text = unicodedata.normalize('NFKC', text)
        text = ''.join(c for c in text if not (0xD800 <= ord(c) <= 0xDFFF))
    # Preserve printable ASCII, common Unicode, and Sinhala (U+0D80–U+0DFF)
    text = re.sub(r'[^\x20-\x7E\u00A0-\uFFFF\u0D80-\u0DFF]', ' ', text)
    return text.strip()


def clean_metadata(metadata: dict) -> dict:
    """
    Clean all string values in metadata dictionary.
    """
    cleaned = {}
    for key, value in metadata.items():
        if isinstance(value, str):
            cleaned[key] = clean_text(value)
        elif isinstance(value, list):
            cleaned[key] = [clean_text(item) if isinstance(item, str) else item for item in value]
        else:
            cleaned[key] = value
    return cleaned


def extract_json_from_response(response_text: str) -> str:
    """
    Extract JSON object from LLM response, removing preamble or trailing text.
    """
    # Match a JSON object (starting with { and ending with })
    json_pattern = r'\{.*?\}'
    match = re.search(json_pattern, response_text, re.DOTALL)
    if match:
        return match.group(0)
    raise ValueError("No valid JSON object found in response")


def process_posts(raw_file_path, processed_file_path=None):
    try:
        with open(raw_file_path, encoding='utf-8') as file:
            posts = json.load(file)
            enriched_posts = []
            for i, post in enumerate(posts):
                try:
                    logging.info(f"Processing post {i}: {post['text'][:100]}...")
                    if 'text' not in post:
                        logging.warning(f"Post {i} missing 'text' field. Skipping.")
                        print(f"Warning: Post {i} missing 'text' field. Skipping.")
                        continue
                    # Clean the original post text
                    cleaned_post_text = clean_text(post['text'])
                    metadata = extract_metadata(cleaned_post_text)
                    # Clean the metadata returned by LLM
                    cleaned_metadata = clean_metadata(metadata)
                    # Create post with cleaned text and metadata
                    post_with_metadata = post.copy()  # Copy original post
                    post_with_metadata['text'] = cleaned_post_text  # Use cleaned text
                    post_with_metadata.update(cleaned_metadata)  # Merge cleaned metadata
                    enriched_posts.append(post_with_metadata)
                except Exception as e:
                    error_msg = f"Error processing post {i}: {post['text'][:100]}... | Error: {str(e)}"
                    logging.error(error_msg)
                    print(error_msg)
                    continue  # Skip problematic posts

        if not enriched_posts:
            error_msg = "No posts were successfully processed."
            logging.error(error_msg)
            raise ValueError(error_msg)

        unified_tags = get_unified_tags(enriched_posts)
        # Clean unified tags
        cleaned_unified_tags = clean_metadata(unified_tags)
        for post in enriched_posts:
            current_tags = post.get('tags', [])
            new_tags = {cleaned_unified_tags.get(tag, tag) for tag in current_tags}
            post['tags'] = list(new_tags)

        if processed_file_path:
            with open(processed_file_path, 'w', encoding='utf-8') as outfile:
                json.dump(enriched_posts, outfile, ensure_ascii=False, indent=4)
                logging.info(f"Successfully wrote {len(enriched_posts)} posts to {processed_file_path}")
        return enriched_posts

    except FileNotFoundError as e:
        logging.error(f"Input file {raw_file_path} not found: {str(e)}")
        raise FileNotFoundError(f"Input file {raw_file_path} not found.")
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {raw_file_path}: {str(e)}")
        raise ValueError(f"Invalid JSON in {raw_file_path}.")
    except Exception as e:
        logging.error(f"Error processing posts: {str(e)}")
        raise Exception(f"Error processing posts: {str(e)}")


def extract_metadata(post):
    template = '''
    You are given a LinkedIn post. You need to extract number of lines, language of the post, and tags.
    1. Return ONLY a valid JSON object. Do NOT include any preamble, explanation, or additional text.
    2. JSON object must have exactly three keys: line_count (integer), language (string), tags (array of strings).
    3. tags is an array of up to two text tags, in title case, without emojis or special characters.
    4. Language must be "English" or "Sinhala" (Sinhala is the language used in Sri Lanka, often mixed with English).
    5. Avoid using emojis or special characters in the output.
    6. Ensure line_count is accurate based on newline characters (\n).

    Example output: {{"line_count": 2, "language": "English", "tags": ["Job Search", "Motivation"]}}

    Here is the actual post:  
    {post}
    '''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    try:
        # Post is already cleaned before calling this function
        response = chain.invoke(input={"post": post})
        # Extract JSON from response
        json_str = extract_json_from_response(response.content)
        json_parser = JsonOutputParser()
        res = json_parser.parse(json_str)
        # Validate the response structure
        if not isinstance(res, dict) or not all(k in res for k in ['line_count', 'language', 'tags']):
            raise ValueError("Invalid metadata format returned by LLM.")
        if res['language'] not in ["English", "Sinhala"]:
            raise ValueError(f"Invalid language '{res['language']}' returned by LLM.")
        return res
    except OutputParserException as e:
        logging.error(f"Failed to parse LLM response: {str(e)}")
        raise OutputParserException(f"Failed to parse LLM response: {str(e)}")
    except Exception as e:
        logging.error(f"Error extracting metadata: {str(e)}")
        raise Exception(f"Error extracting metadata: {str(e)}")


def get_unified_tags(posts_with_metadata):
    unique_tags = set()
    for post in posts_with_metadata:
        tags = post.get('tags', [])
        unique_tags.update(clean_text(tag) for tag in tags)  # Clean tags

    unique_tags_list = ','.join(unique_tags)

    template = '''
    You are given a comma-separated list of tags. You need to unify the tags with the following requirements:
    1. Tags are unified and merged to create a shorter list.
       Example 1: "Jobseekers", "Job Hunting" merge into "Job Search".
       Example 2: "Motivation", "Inspiration", "Drive" map to "Motivation".
       Example 3: "Personal Growth", "Personal Development", "Self Improvement" map to "Self Improvement".
       Example 4: "Scam Alert", "Job Scam" map to "Scams".
    2. Each tag must follow title case convention (e.g., "Motivation", "Job Search").
    3. Return ONLY a valid JSON object, with no preamble, explanation, or additional text.
    4. Output must be a JSON object mapping original tags to unified tags.
       Example: {{"Jobseekers": "Job Search", "Job Hunting": "Job Search", "Motivation": "Motivation"}}
    5. Avoid using emojis or special characters in the output.

    Here is the list of tags: 
    {tags}
    '''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    try:
        response = chain.invoke(input={"tags": clean_text(unique_tags_list)})
        # Extract JSON from response
        json_str = extract_json_from_response(response.content)
        json_parser = JsonOutputParser()
        res = json_parser.parse(json_str)
        if not isinstance(res, dict):
            raise ValueError("Invalid tag unification format returned by LLM.")
        return res
    except OutputParserException as e:
        logging.error(f"Failed to parse tag unification response: {str(e)}")
        raise OutputParserException(f"Failed to parse tag unification response: {str(e)}")
    except Exception as e:
        logging.error(f"Error unifying tags: {str(e)}")
        raise Exception(f"Error unifying tags: {str(e)}")


if __name__ == "__main__":
    process_posts("data/raw_posts.json", "data/processed_posts.json")