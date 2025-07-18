import streamlit as st
from few_shot import FewShotPosts
from post_generator import generate_post

# Initialize session state for storing generated post
if 'generated_post' not in st.session_state:
    st.session_state.generated_post = None

# Options for length and language
length_options = ["Short", "Medium", "Long"]
language_options = ["English"]

# Modern styling
st.set_page_config(page_title="Specified LinkedIn Posts", layout="centered")
st.markdown("""
    <style>
    .main-container {
        max-width: 800px;
        margin: auto;
        padding: 2rem;
    }
    .header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #0077B5;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        border: none;
    }
    .stButton>button:hover {
        background-color: #005f8f;
    }
    .post-output {
        margin-top: 1rem;
        border: 0.1px solid #e9ecef;
    }
    </style>
""", unsafe_allow_html=True)


# Main app layout
def main():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="header">
            <h1>Specified LinkedIn Posts</h1>
            <p style="color: #666;">Create specified professional LinkedIn posts with ease. Use bellow categories to start generating. (This app uses open source DeepSeek-R1-Distill-Llama-70B)</p>
        </div>
    """, unsafe_allow_html=True)

    # Create form for inputs
    with st.form(key='post_generator_form'):
        # Create three columns for the dropdowns
        col1, col2, col3 = st.columns(3)

        fs = FewShotPosts()
        tags = fs.get_tags()

        with col1:
            selected_tag = st.selectbox(
                "Topic",
                options=tags,
                help="Choose a topic for your post"
            )

        with col2:
            selected_length = st.selectbox(
                "Length",
                options=length_options,
                help="Select the desired post length"
            )

        with col3:
            selected_language = st.selectbox(
                "Language",
                options=language_options,
                help="Select the post language"
            )

        # Generate Button
        submit_button = st.form_submit_button("Generate Post")

    # Handle form submission
    if submit_button:
        with st.spinner("Generating your post..."):
            st.session_state.generated_post = generate_post(
                selected_length,
                selected_language,
                selected_tag
            )

    # Display generated post
    if st.session_state.generated_post:
        st.markdown('<div class="post-output">', unsafe_allow_html=True)
        st.markdown("### Generated Post")
        st.write(st.session_state.generated_post)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# Run the app
if __name__ == "__main__":
    main()