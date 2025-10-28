// ==========================================================
// 💗 Luvisa Frontend Script (Render Edition)
// ==========================================================

// 🛰️ Backend API URL (change this to your deployed link)
const BACKEND_URL = "https://luvisa-render.onrender.com";

// ==========================================================
// 🌸 Utility: Local Storage
// ==========================================================
function saveToken(token, email) {
  localStorage.setItem("luvisa_token", token);
  localStorage.setItem("luvisa_email", email);
}

function getUserEmail() {
  return localStorage.getItem("luvisa_email");
}

function logout() {
  localStorage.removeItem("luvisa_token");
  localStorage.removeItem("luvisa_email");
  window.location.href = "login.html";
}

// ==========================================================
// 👥 Signup & Login
// ==========================================================
async function signupUser() {
  const email = document.getElementById("signupEmail").value;
  const password = document.getElementById("signupPassword").value;

  try {
    const response = await fetch(`${BACKEND_URL}/api/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();
    if (data.success) {
      saveToken(data.token, email);
      alert("Signup successful! Redirecting to chat...");
      window.location.href = "index.html";
    } else {
      alert(data.message || "Signup failed");
    }
  } catch (error) {
    console.error("Signup Error:", error);
    alert("Server error during signup");
  }
}

async function loginUser() {
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  try {
    const response = await fetch(`${BACKEND_URL}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();
    if (data.success) {
      saveToken(data.token, email);
      alert("Login successful! Redirecting to chat...");
      window.location.href = "index.html";
    } else {
      alert(data.message || "Login failed");
    }
  } catch (error) {
    console.error("Login Error:", error);
    alert("Server error during login");
  }
}

// ==========================================================
// 💬 Chat with Luvisa
// ==========================================================
async function sendMessage() {
  const input = document.getElementById("userInput");
  const message = input.value.trim();
  const chatBox = document.getElementById("chatBox");

  if (!message) return;

  const email = getUserEmail();
  if (!email) {
    alert("Please login first!");
    return (window.location.href = "login.html");
  }

  // Display user message
  appendMessage("You", message, "user");
  input.value = "";

  try {
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, text: message }),
    });

    const data = await response.json();
    if (data.success) {
      appendMessage("Luvisa 💗", data.reply, "luvisa");
    } else {
      appendMessage("Luvisa 💗", "Sorry, something went wrong 💭", "luvisa");
    }
  } catch (error) {
    console.error("Chat Error:", error);
    appendMessage("Luvisa 💗", "Server is unreachable 😢", "luvisa");
  }
}

// ==========================================================
// 🕊️ Display Chat Messages
// ==========================================================
function appendMessage(sender, text, type) {
  const chatBox = document.getElementById("chatBox");
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", type);
  msgDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// ==========================================================
// 🕰️ Chat History Loader
// ==========================================================
async function loadChatHistory() {
  const email = getUserEmail();
  if (!email) return;

  try {
    const response = await fetch(`${BACKEND_URL}/api/chat_history?email=${email}`);
    const data = await response.json();

    if (data.success && data.history) {
      const chatBox = document.getElementById("chatBox");
      chatBox.innerHTML = "";
      data.history.forEach((msg) => {
        const sender = msg.sender === "user" ? "You" : "Luvisa 💗";
        appendMessage(sender, msg.message, msg.sender);
      });
    }
  } catch (error) {
    console.error("Load history error:", error);
  }
}

// ==========================================================
// 🧠 Forget Memory
// ==========================================================
async function forgetMemory() {
  const email = getUserEmail();
  if (!email) return;

  if (!confirm("Are you sure you want to erase all chat history? 💔")) return;

  try {
    const response = await fetch(`${BACKEND_URL}/api/forget_memory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();
    alert(data.message || "Memory erased!");
    document.getElementById("chatBox").innerHTML = "";
  } catch (error) {
    console.error("Forget Memory Error:", error);
    alert("Failed to erase memory.");
  }
}

// ==========================================================
// 👤 Load Profile
// ==========================================================
async function loadProfile() {
  const email = getUserEmail();
  if (!email) return;

  try {
    const response = await fetch(`${BACKEND_URL}/api/profile?email=${email}`);
    const data = await response.json();
    if (data.success) {
      document.getElementById("displayName").textContent = data.profile.display_name;
      if (data.profile.avatar) {
        document.getElementById("avatar").src = data.profile.avatar;
      }
    }
  } catch (error) {
    console.error("Profile Load Error:", error);
  }
}

// ==========================================================
// 🎯 Auto Load on Page Ready
// ==========================================================
document.addEventListener("DOMContentLoaded", () => {
  const currentPage = window.location.pathname.split("/").pop();
  if (currentPage === "index.html" || currentPage === "") {
    loadChatHistory();
    loadProfile();
  }
});
