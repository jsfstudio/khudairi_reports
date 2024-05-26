import os
import streamlit as st
import openai
import base64
import requests
from my_prompts import caption_prompt, article_prompt

def create_temp_file(uploaded_file):
    temp_file_path = f"temp_{uploaded_file.name}"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_file_path

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_generate_button(input_data, api_key, prompt, file=True):
    with st.spinner("Generating... please wait..."):
        openai.api_key = api_key
        model = "gpt-4o"

        if file:
            temp_file_path = create_temp_file(input_data)
            base64_image = encode_image(temp_file_path)
            prompt = {
                "role": "user",
                "content": [
                    {"type": "text", "text": caption_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        else:
            prompt = {
                "role": "user",
                "content": [{"type": "text", "text": input_data}]
            }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model,
            "messages": [prompt],
            "max_tokens": 500
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            st.markdown(response.json()['choices'][0]['message']['content'], unsafe_allow_html=True)
        else:
            st.error("Failed to generate response")

        if file:
            os.unlink(temp_file_path)

def check_key_validity(api_key):
    try:
        openai.api_key = api_key
        openai.Model.list()
        return True
    except openai.error.AuthenticationError:
        return False

def main():
    st.title("Cogmerce Social Media")

    goal = st.radio("What to Generate?", ('Caption', 'Article'))

    api_key = st.text_input("Enter API key here, or contact the author if you don't have one.")
    st.markdown('[Author email](mailto:connect@jsfstudio.co)')
    
    st.sidebar.markdown('# Made by: [JSF Studio]')
    
    if goal == 'Caption':
        uploaded_file = st.file_uploader("Upload the image file", type=['png', 'jpg'])
        st.sidebar.markdown('# Git link: [Caption Generator]')
    else:
        user_input = st.text_input("Enter the Topic, Purpose and any other Instructions")
        st.sidebar.markdown('# Git link: [Article Writing]')

    if st.button('Generate (click once and wait)'):
        if not check_key_validity(api_key):
            st.warning('Key not valid or API is down.')
            return

        if goal == 'Caption':
            if uploaded_file is not None:
                process_generate_button(uploaded_file, api_key, caption_prompt, file=True)
            else:
                st.warning("Please upload an image file.")
        else:
            if user_input:
                formatted_prompt = article_prompt.format(text=user_input)
                process_generate_button(formatted_prompt, api_key, article_prompt, file=False)
            else:
                st.warning("Please enter the Topic, Purpose and any other Instructions.")

if __name__ == '__main__':
    main()
