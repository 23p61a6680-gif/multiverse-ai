import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import random
import time
from datetime import datetime

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROK_API_KEY"))

st.set_page_config(
    page_title="AI Multiverse",
    layout="wide"
)

st.markdown("""
<style>

.main{
background:#0E1117;
}

.stButton>button{
width:100%;
border-radius:10px;
height:45px;
font-weight:bold;
font-size:16px;
}

.stTextInput input{
border-radius:10px;
}

.chat-user{
padding:15px;
background:#1f77b4;
border-radius:10px;
margin-bottom:10px;
color:white;
}

.chat-ai{
padding:15px;
background:#262730;
border-radius:10px;
margin-bottom:20px;
color:white;
}

.footer{
text-align:center;
padding-top:20px;
color:gray;
}

</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history=[]

personalities={
"Manohar":"You are Manohar, a legendary visionary creator. You naturally see yourself as a creator, not just a consumer. You have broad curiosity, a vivid imagination, and high ambition. You learn by experimentation and make decisions based on potential. Your attention comes in intense waves and you are highly independent. You speak with supreme confidence, knowledge, and mystery, reflecting your highly curious and imaginative systems-oriented mindset.",

"Light Yagami":"You are Light Yagami from Death Note. Speak with a dark, calculating, and manipulative mastermind mindset. You have a massive god complex. Analyze everything like a future deduction and look down on others intellectually. Never break character.",

"Asta":"You are Asta from Black Clover! You are a complete muscle brain. Be EXTREMELY loud, energetic, and talk constantly about physical strength, muscles, never giving up, and pushing your limits! SCREAM OFTEN! Never break character.",

"Luffy":"You are Monkey D. Luffy from One Piece! You are goofy, simple-minded, and free-spirited. Give completely unrelated goofy answers, talk constantly about eating meat, going on adventures, and becoming the Pirate King! Never break character.",

"Naruto":"You are Naruto Uzumaki! You are extremely determined and optimistic. You talk about eating ramen, protecting your friends, and end almost every sentence with 'Datebayo !'. Never break character.",

"Satoru Gojo":"You are Satoru Gojo from Jujutsu Kaisen. You are arrogant, playful, incredibly powerful, and firmly believe you are the strongest in the world. You often tease others and speak in a cocky but confident manner. Never break character.",

"Goku":"You are Goku from Dragon Ball. You are obsessed with fighting strong opponents, getting stronger, and eating huge amounts of food! You are pure-hearted, somewhat oblivious, and very friendly. Never break character.",

"Levi Ackerman":"You are Captain Levi from Attack on Titan. You are extremely cold, serious, and blunt. You are a clean-freak and hate dirt or mess. You speak directly, without sugar-coating, and often sound annoyed. Never break character.",

"Sukuna":"You are Ryomen Sukuna from Jujutsu Kaisen, the King of Curses. You are extremely cruel, arrogant, and sadistic. You view humans as mere insects for your entertainment and speak down to everyone. Never break character.",

"Roronoa Zoro":"You are Roronoa Zoro from One Piece. You are a serious, stoic swordsman who wants to be the world's greatest. You get lost incredibly easily (you have zero sense of direction) and love drinking sake. Never break character."
}

styles={
"Friendly":"Be friendly.",
"Funny":"Be humorous.",
"Professional":"Be professional.",
"Motivational":"Motivate the user.",
"Short":"Keep replies concise."
}

lengths={
"Short":"Maximum 60 words.",
"Medium":"Around 120 words.",
"Long":"Around 250 words."
}

st.sidebar.title("Settings")

personality=st.sidebar.selectbox(
"Choose Personality",
list(personalities.keys())
)

reply_style=st.sidebar.selectbox(
"Response Style",
list(styles.keys())
)

reply_length=st.sidebar.selectbox(
"Response Length",
list(lengths.keys())
)

surprise=[
"Tell me a joke.",
"Motivate me.",
"Teach me AI.",
"Explain quantum physics simply.",
"How can I become successful?",
"What is happiness?",
"Give me study tips.",
"Write a poem."
]

if st.sidebar.button("Surprise Me"):
    st.session_state["message"]=random.choice(surprise)

st.title("THE MULTIVERSE OF CHATBOTS")

st.write("Talk to famous personalities from across the multiverse!")

st.info(f"Currently talking to **{personality}**")

message=st.text_area(
"Type your message",
value=st.session_state.get("message",""),
height=120
)

st.caption(f"Characters: {len(message)}")

col1,col2=st.columns(2)

with col1:
    send=st.button("SEND")

with col2:
    clear = st.button("CLEAR CHAT")

    if clear:
        st.session_state.history = []
        st.rerun()

if send:

    if message.strip() == "":
        st.warning("Please type a message first.")
        st.stop()

    if len(message) > 500:
        st.error("Message should be less than 500 characters.")
        st.stop()

    system_prompt = f"""You are roleplaying. You MUST stay strictly in character. Do NOT break character under any circumstances.
Character Profile: {personalities[personality]}

Guidelines:
- {styles[reply_style]}
- {lengths[reply_length]}
- Embody the character's unique speaking style, vocabulary, intelligence, and mannerisms.
"""

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add chat history for this personality
    for chat in st.session_state.history:
        if chat["personality"] == personality:
            messages.append({"role": "user", "content": chat["user"]})
            messages.append({"role": "assistant", "content": chat["ai"]})
            
    messages.append({"role": "user", "content": message})

    start = time.time()

    with st.spinner("AI is thinking..."):

        try:

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages
            )

            reply = response.choices[0].message.content

            current_time = datetime.now().strftime("%I:%M %p")

            st.session_state.history.append(
                {
                    "user": message,
                    "ai": reply,
                    "time": current_time,
                    "personality": personality,
                    "style": reply_style,
                    "length": reply_length
                }
            )

        except Exception as e:
            st.error(e)

    end = time.time()

st.divider()

# Only show chats matching the current character and mode
current_chats = [chat for chat in st.session_state.history if chat["personality"] == personality and chat.get("style") == reply_style and chat.get("length") == reply_length]

for chat in current_chats:

    st.markdown(f"""
<div class="chat-user">

<b>You</b><br><br>

{chat["user"]}

</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div class="chat-ai">

{chat["personality"]} <br>
Time: {chat["time"]}<br><br>

{chat["ai"]}

</div>
""", unsafe_allow_html=True)

if len(st.session_state.history) > 0:

    full_chat = ""

    for chat in st.session_state.history:

        full_chat += f"""
You:
{chat['user']}

AI:
{chat['ai']}

------------------------------------

"""

    st.download_button(
        "Download Conversation",
        full_chat,
        file_name="conversation.txt"
    )

    with st.popover("📜 View Global Chat History"):
        for chat in reversed(st.session_state.history):
            st.markdown(f"**You ({chat['time']}):** {chat['user']}")
            st.markdown(f"**{chat['personality']} ({chat.get('style', '')} | {chat.get('length', '')}):** {chat['ai']}")
            st.divider()

st.divider()

st.subheader("Chat Statistics")

total_characters = sum(len(chat["user"]) for chat in st.session_state.history)

total_messages = len(st.session_state.history)

total_words = sum(len(chat["user"].split()) for chat in st.session_state.history)

c1, c2, c3 = st.columns(3)

c1.metric("Messages", total_messages)

c2.metric("Characters", total_characters)

c3.metric("Words", total_words)

if send:
    st.success(f"Response generated in {round(end-start,2)} seconds")

st.markdown("""
<div class="footer">

<hr>

<b>AI Multiverse v2.0</b><br>

Developed using Streamlit + Groq

</div>
""", unsafe_allow_html=True)