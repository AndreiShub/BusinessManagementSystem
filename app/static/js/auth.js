function isAuthenticated() {
  return Boolean(localStorage.getItem("token"));
}

function updateNavbar() {
  const loginLink = document.getElementById("login-link");
  const registerLink = document.getElementById("register-link");
  const logoutLink = document.getElementById("logout-link");
  const teamsLink = document.getElementById("teams-link");

  if (isAuthenticated()) {
    loginLink.style.display = "none";
    registerLink.style.display = "none";
    logoutLink.style.display = "inline";
    teamsLink.style.display = "inline";
  } else {
    loginLink.style.display = "inline";
    registerLink.style.display = "inline";
    logoutLink.style.display = "none";
    teamsLink.style.display = "none";
  }
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "/";
}

async function login(event) {
  event.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const body = new URLSearchParams();
    body.append("username", email);
    body.append("password", password);
    body.append("grant_type", "password");
    body.append("scope", "");
    body.append("client_id", "");
    body.append("client_secret", "");

    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString()
    });

    if (!res.ok) {
      alert("Ошибка входа");
      return;
    }

    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    updateNavbar();
    window.location.href = "/teams";
  } catch (err) {
    console.error(err);
    alert("Ошибка сети");
  }
}

document.addEventListener("DOMContentLoaded", updateNavbar);
