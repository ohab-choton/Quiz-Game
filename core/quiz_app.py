import streamlit as st
import requests

API_BASE_URL = 'http://127.0.0.1:8000/api/quizzes/'

# 🔷 function to add new question to the quiz
def add_question(quiz_id, question_text, answers):
    url = f"{API_BASE_URL}{quiz_id}/add_question/"
    data = {
        'text': question_text,
        'answers': answers,
    }
    response = requests.post(url, json=data)
    if response.status_code != 201:
        st.error(f"Failed to add question: {response.status_code} - {response.text}")
    return response.status_code == 201


# 🔷 function to add a quiz
def add_quiz(title):
    url = API_BASE_URL
    data = {'title': title}
    response = requests.post(url, json=data)
    if response.status_code == 201:
        return response.json()
    else:
        st.error(f"Failed to create quiz: {response.status_code} - {response.text}")
        return None


# 🔷 fetch all quizzes
def fetch_quizzes():
    response = requests.get(API_BASE_URL)
    if response.status_code == 200:
        quizzes = response.json() 
        return quizzes
    else:
        st.error("Failed to fetch quizzes")
        return []


# 🔷 fetch questions of a quiz
def fetch_questions(quiz_id):
    response = requests.get(f"{API_BASE_URL}{quiz_id}/")
    if response.status_code == 200:
        return response.json().get('questions', [])
    else:
        st.error(f"Failed to fetch questions: {response.status_code} - {response.text}")
        return []


# Streamlit UI
st.title("🎯 Welcome to Our Quizzes Platform")

mode = st.sidebar.selectbox("📋 Choose mode", ['Create Quiz', 'Add Questions', 'Play Quiz'])

if mode == 'Create Quiz':
    st.header('📝 Create a New Quiz')
    new_quiz_title = st.text_input("Enter the quiz title")

    if st.button('Create Quiz'):
        if new_quiz_title.strip():
            new_quiz = add_quiz(new_quiz_title)
            if new_quiz:
                st.success(f"✅ Quiz '{new_quiz_title}' created successfully")
        else:
            st.error("Quiz title cannot be empty")

elif mode == "Add Questions":
    st.header("➕ Add Questions to Quiz")

    quizzes = fetch_quizzes()
    if quizzes:
        quiz_titles = [quiz['title'] for quiz in quizzes]
        selected_quiz_title = st.selectbox("Select a quiz", quiz_titles)

        if selected_quiz_title:
            selected_quiz = next(quiz for quiz in quizzes if quiz['title'] == selected_quiz_title)

            question_text = st.text_input("Enter the question text:")
            answers = []

            for i in range(4):
                col1, col2 = st.columns([3, 1])
                with col1:
                    answer_text = st.text_input(f"Answer {i+1} Text", key=f"answer_text_{i}")
                with col2:
                    is_correct = st.checkbox(f"Correct?", key=f"is_correct_{i}")
                if answer_text.strip():
                    answers.append({'text': answer_text, 'is_correct': is_correct})

            if st.button('Add Question'):
                if question_text.strip() and answers:
                    if add_question(selected_quiz['id'], question_text, answers):
                        st.success("✅ Question added successfully")
                else:
                    st.error("Please provide a question and at least one answer.")
    else:
        st.info("ℹ️ No quizzes available. Please create a quiz first.")

elif mode == "Play Quiz":
    st.header("🎮 Play Quiz")

    quizzes = fetch_quizzes()
    if quizzes:
        quiz_titles = [quiz['title'] for quiz in quizzes]
        selected_quiz_title = st.selectbox("Select a quiz", quiz_titles)

        if selected_quiz_title:
            selected_quiz = next(quiz for quiz in quizzes if quiz['title'] == selected_quiz_title)
            questions = fetch_questions(selected_quiz['id'])

            if not questions:
                st.warning("⚠️ No questions available in this quiz yet.")
            else:
                st.write("📋 Answer all questions below and click **Submit Quiz** when done.")

                user_answers = {}
                for question in questions:
                    st.subheader(question['text'])
                    #st.write("Answers for question", question['id'], ":", question['answers'])  # debug

                    answer_options = {ans['id']: ans['text'] for ans in question['answers']}
                    #st.write("Answer options dict:", answer_options)  # debug

                    if answer_options:
                        selected_answer_id = st.radio(
                            f"Choose an answer for Question: {question['id']}:",
                            list(answer_options.keys()),
                            format_func=lambda x: answer_options[x],
                            key=f"question_{question['id']}"
                        )
                        user_answers[question['id']] = selected_answer_id
                    else:
                        st.warning(f"No answers found for question ID: {question['id']}")

                if st.button("✅ Submit Quiz"):
                    correct = 0
                    wrong = 0
                    for qid, ansid in user_answers.items():
                        #st.write(f"Submitting answer for Question ID: {qid} Answer ID: {ansid}")
                        response = requests.post(
                            f"{API_BASE_URL}{selected_quiz['id']}/submit_answer/",
                            json={'question_id': qid, 'answer_id': ansid}
                        )
                        #st.write(f"Response status: {response.status_code}, Response data: {response.text}")
                        if response.status_code == 200:
                            result = response.json()
                            if "Correct answer" in result.get("message", ""):
                                correct += 1
                            else:
                                wrong += 1
                        else:
                            wrong += 1
                    st.success(f"🎯 Correct answers: {correct}")
                    st.error(f"❌ Wrong answers: {wrong}")
    else:
        st.info("ℹ️ No quizzes available.")

