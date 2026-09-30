import uuid
import streamlit as st
import streamlit.components.v1 as components

from chatbot.graph import graph


st.set_page_config(
    page_title="StudyMate AI",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------
# Design tokens
# Night-desk palette: low-glare navy, periwinkle focus color,
# lamp-amber for warmth, mint for "correct / done".
# One typeface (Lexend) - designed to make reading easier.
# ---------------------------------------------------------------

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600&display=swap');

:root {
  --ink: #14172b;
  --panel: #1d2140;
  --panel-2: #262b52;
  --line: #343a6b;
  --text: #e8eaff;
  --muted: #9aa0cf;
  --focus: #8ba3ff;
  --lamp: #ffc978;
  --mint: #6ee7b7;
}

html, body, [class*="css"], .stApp, .stMarkdown, button, textarea, input {
  font-family: 'Lexend', system-ui, sans-serif !important;
}

.stApp {
  background:
    radial-gradient(900px 500px at 15% -10%, #262b5c 0%, transparent 60%),
    radial-gradient(700px 400px at 100% 10%, #2b2350 0%, transparent 55%),
    var(--ink);
  color: var(--text);
}

header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.2rem; max-width: 780px; }

/* ---------- Title ---------- */
.title-wrap { text-align: center; margin-top: -0.6rem; }
.title-wrap h1 {
  font-weight: 600; font-size: 2.1rem; letter-spacing: -0.02em;
  color: var(--text); margin: 0;
}
.title-wrap p { color: var(--muted); font-weight: 300; margin: 0.3rem 0 0; }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
  background: var(--panel);
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] * { color: var(--text); }
.side-label { color: var(--muted); font-size: 0.8rem; margin: 1rem 0 0.3rem; }

/* ---------- Buttons: 3D tilt on hover, press-down on click ---------- */
.stButton > button {
  background: var(--panel-2);
  color: var(--text);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 0.7rem 1rem;
  text-align: left;
  transition: transform .25s cubic-bezier(.2,.8,.2,1), box-shadow .25s, border-color .25s;
  transform: perspective(700px) rotateX(0) translateY(0);
  box-shadow: 0 4px 0 #1a1e3d;
}
.stButton > button:hover {
  transform: perspective(700px) rotateX(-6deg) translateY(-4px);
  border-color: var(--focus);
  box-shadow: 0 10px 22px rgba(0,0,0,.35), 0 4px 0 #1a1e3d;
  color: var(--text);
}
.stButton > button:active {
  transform: perspective(700px) rotateX(0) translateY(3px);
  box-shadow: 0 1px 0 #1a1e3d;
}
.stButton > button:focus-visible { outline: 3px solid var(--lamp); outline-offset: 2px; }

/* ---------- Chat bubbles ---------- */
[data-testid="stChatMessage"] {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 1rem 1.1rem;
  margin-bottom: 0.8rem;
  animation: settle .35s cubic-bezier(.2,.8,.2,1);
  transform-origin: bottom center;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: var(--panel-2);
  border-color: var(--focus);
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li { line-height: 1.75; font-size: 1rem; }
[data-testid="stChatMessage"] code { color: var(--lamp); }

@keyframes settle {
  from { opacity: 0; transform: perspective(800px) rotateX(10deg) translateY(10px); }
  to   { opacity: 1; transform: perspective(800px) rotateX(0) translateY(0); }
}

/* ---------- Chat input ---------- */
[data-testid="stChatInput"] {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--focus);
  box-shadow: 0 0 0 3px rgba(139,163,255,.25);
}
[data-testid="stChatInput"] textarea { color: var(--text); }
[data-testid="stBottom"] > div { background: transparent; }

/* ---------- Thinking dots ---------- */
.thinking { display: flex; gap: 6px; align-items: center; color: var(--muted); }
.thinking i {
  width: 9px; height: 9px; border-radius: 50%; background: var(--focus);
  animation: hop 1s infinite ease-in-out;
}
.thinking i:nth-child(2) { animation-delay: .15s; background: var(--lamp); }
.thinking i:nth-child(3) { animation-delay: .3s;  background: var(--mint); }
@keyframes hop { 0%,80%,100% { transform: translateY(0); } 40% { transform: translateY(-8px); } }

/* ---------- Empty state ---------- */
.empty { text-align: center; color: var(--muted); margin: 0.4rem 0 1rem; }
.empty b { color: var(--text); font-weight: 500; }

@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------
# 3D hero: a floating book with orbiting shapes (Three.js).
# Follows the cursor gently. Honors reduced-motion.
# ---------------------------------------------------------------

HERO_3D = """
<div id="wrap" style="width:100%;height:100%;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
  const wrap = document.getElementById('wrap');
  const W = () => wrap.clientWidth, H = () => wrap.clientHeight;
  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, W() / H(), 0.1, 100);
  camera.position.set(0, 0.2, 7);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(W(), H());
  wrap.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.65));
  const key = new THREE.DirectionalLight(0xffe3b0, 0.9);
  key.position.set(4, 5, 5);
  scene.add(key);
  const rim = new THREE.PointLight(0x8ba3ff, 1.2, 20);
  rim.position.set(-4, 1, 3);
  scene.add(rim);

  // Book
  const book = new THREE.Group();
  const cover = new THREE.Mesh(
    new THREE.BoxGeometry(1.7, 2.2, 0.4),
    new THREE.MeshStandardMaterial({ color: 0x6f86f0, roughness: 0.45, metalness: 0.1 })
  );
  const pages = new THREE.Mesh(
    new THREE.BoxGeometry(1.55, 2.05, 0.32),
    new THREE.MeshStandardMaterial({ color: 0xf4f1ff, roughness: 0.9 })
  );
  pages.position.set(0.06, 0, 0.02);
  const band = new THREE.Mesh(
    new THREE.BoxGeometry(0.16, 2.24, 0.44),
    new THREE.MeshStandardMaterial({ color: 0xffc978, roughness: 0.4 })
  );
  band.position.set(0.55, 0, 0);
  book.add(cover, pages, band);
  book.rotation.set(0.25, -0.5, 0.08);
  scene.add(book);

  // Orbiting shapes
  const orbit = [];
  const specs = [
    [new THREE.IcosahedronGeometry(0.22, 0), 0xffc978, 2.1, 0.0],
    [new THREE.OctahedronGeometry(0.2, 0),   0x6ee7b7, 2.5, 2.1],
    [new THREE.TetrahedronGeometry(0.22, 0), 0xff9ec4, 1.9, 4.2],
  ];
  specs.forEach(([geo, color, r, phase]) => {
    const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color, roughness: 0.35, flatShading: true }));
    scene.add(m);
    orbit.push({ m, r, phase });
  });

  // Dust
  const N = 90, pos = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) {
    pos[i*3] = (Math.random() - 0.5) * 12;
    pos[i*3+1] = (Math.random() - 0.5) * 5;
    pos[i*3+2] = (Math.random() - 0.5) * 6;
  }
  const dustGeo = new THREE.BufferGeometry();
  dustGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const dust = new THREE.Points(dustGeo, new THREE.PointsMaterial({ color: 0xaab6ff, size: 0.035, transparent: true, opacity: 0.7 }));
  scene.add(dust);

  // Cursor parallax
  let mx = 0, my = 0;
  window.addEventListener('pointermove', (e) => {
    mx = (e.clientX / window.innerWidth - 0.5) * 2;
    my = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  const clock = new THREE.Clock();
  function frame() {
    const t = clock.getElapsedTime();
    if (!still) {
      book.position.y = Math.sin(t * 1.1) * 0.12;
      book.rotation.y += ((-0.5 + mx * 0.6) - book.rotation.y) * 0.05;
      book.rotation.x += ((0.25 + my * 0.3) - book.rotation.x) * 0.05;
      orbit.forEach((o, i) => {
        const a = t * (0.6 + i * 0.12) + o.phase;
        o.m.position.set(Math.cos(a) * o.r, Math.sin(a * 1.3) * 0.7, Math.sin(a) * o.r * 0.6);
        o.m.rotation.x += 0.012; o.m.rotation.y += 0.016;
      });
      dust.rotation.y = t * 0.02;
    }
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  frame();

  window.addEventListener('resize', () => {
    camera.aspect = W() / H();
    camera.updateProjectionMatrix();
    renderer.setSize(W(), H());
  });
})();
</script>
<style>html,body{margin:0;background:transparent;overflow:hidden}</style>
"""


# ---------------------------------------------------------------
# State
# ---------------------------------------------------------------

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

MODES = {
    "Explain simply": "Explain this in simple words, like I'm new to the topic. Use one everyday example.",
    "Step by step": "Walk me through this step by step. Number the steps and keep each one short.",
    "Quiz me": "Ask me 3 short quiz questions about this topic, one at a time. Wait for my answer before giving feedback.",
    "Summarize": "Give me a short summary with key points I should remember for an exam.",
}

QUICK_STARTS = [
    ("💡", "Explain photosynthesis simply"),
    ("🧮", "Help me solve a quadratic equation"),
    ("📝", "Make a revision plan for 3 days"),
    ("🧠", "Quiz me on the French Revolution"),
]


# ---------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🎓 StudyMate")
    st.markdown('<div class="side-label">How should I teach you?</div>', unsafe_allow_html=True)
    mode = st.radio(
        "Teaching style",
        list(MODES.keys()),
        label_visibility="collapsed",
    )

    st.markdown('<div class="side-label">This session</div>', unsafe_allow_html=True)
    asked = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.metric("Questions asked", asked)

    if st.button("🗑️ Start a new chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()


# ---------------------------------------------------------------
# Header + 3D hero
# ---------------------------------------------------------------

components.html(HERO_3D, height=240)

st.markdown(
    """
    <div class="title-wrap">
      <h1>StudyMate AI</h1>
      <p>Ask anything. We'll go at your pace.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# Empty state with quick starts
# ---------------------------------------------------------------

if not st.session_state.messages:
    st.markdown(
        '<div class="empty"><b>Not sure where to start?</b> Pick one, or type your own question below.</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, (icon, text) in enumerate(QUICK_STARTS):
        if cols[i % 2].button(f"{icon}  {text}", key=f"qs{i}", use_container_width=True):
            st.session_state.queued = text
            st.rerun()

# ---------------------------------------------------------------
# History
# ---------------------------------------------------------------

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🎓"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ---------------------------------------------------------------
# Input
# ---------------------------------------------------------------

typed = st.chat_input("Ask something about your study material...")
question = typed or st.session_state.pop("queued", None)

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(question)

    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    # The mode instruction is sent to the model, but only your
    # original question is shown in the chat.
    prompt = f"{question}\n\n({MODES[mode]})"

    with st.chat_message("assistant", avatar="🎓"):
        slot = st.empty()
        slot.markdown(
            '<div class="thinking"><i></i><i></i><i></i>&nbsp;Thinking it through</div>',
            unsafe_allow_html=True,
        )
        try:
            result = graph.invoke(
                {"messages": [{"role": "user", "content": prompt}]},
                config=config,
            )
            answer = result["messages"][-1].content
        except Exception as e:
            answer = (
                "I couldn't get an answer just now. This is usually a network "
                "issue or a rate limit. Wait a few seconds and send your question again.\n\n"
                f"`{type(e).__name__}`"
            )
        slot.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()