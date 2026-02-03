document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const passwordConfirm = document.getElementById("password_confirm").value;

  if (password !== passwordConfirm) {
    alert("Пароли не совпадают");
    return;
  }

  try {
    // регистрация
    const registerRes = await fetch("/api/v1/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    if (!registerRes.ok) {
      const err = await registerRes.json();
      alert("Ошибка регистрации: " + (err.detail || JSON.stringify(err)));
      return;
    }

    // автологин
    const body = new URLSearchParams();
    body.append("username", email);
    body.append("password", password);
    body.append("grant_type", "password");
    body.append("scope", "");
    body.append("client_id", "");
    body.append("client_secret", "");

    const loginRes = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString()
    });

    if (!loginRes.ok) {
      const err = await loginRes.json();
      alert("Ошибка входа после регистрации: " + (err.detail || JSON.stringify(err)));
      return;
    }

    const data = await loginRes.json();
    localStorage.setItem("token", data.access_token);
    updateNavbar();
    window.location.href = "/teams";
  } catch (err) {
    console.error(err);
    alert("Ошибка сети");
  }
});
