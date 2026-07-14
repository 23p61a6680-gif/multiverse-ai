import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import random
import time
from datetime import datetime
from PIL import Image

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROK_API_KEY"))

st.set_page_config(
    page_title="AI Multiverse",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main{
background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}

.stButton>button{
width:100%;
border-radius:12px;
height:45px;
font-weight:bold;
font-size:16px;
background: rgba(255, 255, 255, 0.1);
border: 1px solid rgba(255, 255, 255, 0.2);
transition: all 0.3s ease;
}

.stButton>button:hover{
background: rgba(255, 255, 255, 0.2);
transform: scale(1.02);
}

.footer{
text-align:center;
padding-top:20px;
color:rgba(255, 255, 255, 0.5);
font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history=[]

if "messages" not in st.session_state:
    st.session_state.messages = []

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

col1, col2 = st.columns([8, 2])
with col2:
    clear = st.button("CLEAR CHAT", use_container_width=True)
    if clear:
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()

st.divider()

# Helper function to load local character avatars
def get_character_avatar(name):
    # Mapping exact names to the generated asset filenames
    filename_map = {
        "Manohar": "manohar.png",
        "Light Yagami": "light.png",
        "Asta": "asta.png",
        "Luffy": "luffy.png",
        "Naruto": "naruto.png",
        "Satoru Gojo": "gojo.png",
        "Goku": "goku.png",
        "Levi Ackerman": "levi.png",
        "Sukuna": "sukuna.png",
        "Roronoa Zoro": "zoro.png",
        "Astronaut-User": "manohar.png" # You can use the generic manohar avatar for the user or fallback
    }
    
    # If it's the user, use a generic astronaut or the user's custom manohar face
    if name == "Astronaut-User":
        return "🧑‍🚀" # Fallback to emoji for user if we don't have a user image yet
        
    filename = filename_map.get(name)
    if filename:
        filepath = os.path.join("assets", filename)
        if os.path.exists(filepath):
            return Image.open(filepath)
    return "🤖"

user_avatar = "🧑‍🚀" # Let's stick with the cool astronaut for the user!

for msg in st.session_state.messages:
    if msg.get("personality") == personality:
        avatar = user_avatar if msg["role"] == "user" else get_character_avatar(personality)
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

if user_message := st.chat_input("Say something..."):
    if len(user_message) > 500:
        st.error("Message should be less than 500 characters.")
        st.stop()
        
    st.session_state.messages.append({"role": "user", "content": user_message, "personality": personality, "time": datetime.now().strftime("%I:%M %p")})
    
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(user_message)
        
    system_prompt = f"""You are roleplaying. You MUST stay strictly in character. Do NOT break character under any circumstances.
Character Profile: {personalities[personality]}

Guidelines:
- {styles[reply_style]}
- {lengths[reply_length]}
- Embody the character's unique speaking style, vocabulary, intelligence, and mannerisms.
"""
    api_messages = [{"role": "system", "content": system_prompt}]
    
    for msg in st.session_state.messages:
        if msg.get("personality") == personality:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
            
    start = time.time()
    
    with st.spinner("AI is thinking..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=api_messages
            )
            reply = response.choices[0].message.content
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": reply, 
                "personality": personality,
                "time": datetime.now().strftime("%I:%M %p")
            })
            
            # Keep legacy history format for the global view popover
            st.session_state.history.append({
                "user": user_message,
                "ai": reply,
                "time": datetime.now().strftime("%I:%M %p"),
                "personality": personality,
                "style": reply_style,
                "length": reply_length
            })
            
            with st.chat_message("assistant", avatar=get_character_avatar(personality)):
                st.markdown(reply)
                
            end = time.time()
            st.success(f"Response generated in {round(end-start,2)} seconds")
            
        except Exception as e:
            st.error(e)

if len(st.session_state.messages) > 0:

    full_chat = ""

    for chat in st.session_state.messages:

        full_chat += f"""
{chat['role'].upper()}:
{chat['content']}

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

user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
total_characters = sum(len(m["content"]) for m in user_msgs)
total_messages = len(st.session_state.messages)
total_words = sum(len(m["content"].split()) for m in user_msgs)

c1, c2, c3 = st.columns(3)

c1.metric("Messages", total_messages)

c2.metric("Characters", total_characters)

c3.metric("Words", total_words)

st.markdown("""
<div class="footer">

<hr>

<b>AI Multiverse v2.0</b><br>

Developed using Streamlit + Groq

</div>
""", unsafe_allow_html=True)