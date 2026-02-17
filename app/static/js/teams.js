async function loadTeams() {
  const token = localStorage.getItem("token");
  if (!token) return;

  const res = await fetch("/api/v1/teams/", {
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!res.ok) return;

  const teams = await res.json();
  const list = document.getElementById("team-list");
  list.innerHTML = "";

  teams.forEach(team => {
    const li = document.createElement("li");
    li.style.marginBottom = "12px";

    // название команды
    const title = document.createElement("strong");
    title.textContent = team.name;

    // код для вступления
    const code = document.createElement("code");
    code.textContent = team.code;
    code.style.marginLeft = "6px";

    const copyBtn = document.createElement("button");
    copyBtn.textContent = "Скопировать код";
    copyBtn.style.marginLeft = "6px";
    copyBtn.title = "Скопировать код";

    copyBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(team.code);
      alert("Код приглашения скопирован");
    });

    // кнопка открыть задачи
    const btn = document.createElement("button");
    btn.textContent = "Открыть задачи";
    btn.style.marginLeft = "12px";

    btn.addEventListener("click", () => {
      const url = `/teams/${team.id}/tasks`;
      window.location.assign(url);
    });

    // сборка DOM
    li.appendChild(title);
    li.appendChild(document.createTextNode(" : "));
    li.appendChild(code);
    li.appendChild(copyBtn);
    li.appendChild(btn);

    list.appendChild(li);
  });
}

document.getElementById("create-team-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const token = localStorage.getItem("token");
  const name = document.getElementById("team-name").value;

  if (!token) return alert("Сначала войдите");

  const res = await fetch("/api/v1/teams/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ name })
  });

  if (!res.ok) {
    const err = await res.json();
    alert("Ошибка: " + (err.detail || JSON.stringify(err)));
    return;
  }

  const team = await res.json();
  alert(`Команда "${team.name}" создана`);
  loadTeams();
});

document.addEventListener("DOMContentLoaded", loadTeams);
