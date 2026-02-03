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
    li.innerHTML = `
      <strong>${team.name}</strong>
      <button id="select-${team.id}">Открыть задачи</button>
    `;
    list.appendChild(li);

    // Добавляем обработчик кнопки "Открыть задачи"
    document.getElementById(`select-${team.id}`).addEventListener("click", () => {
      // сохраняем текущую команду в localStorage
      localStorage.setItem("currentTeamId", team.id);
      localStorage.setItem("currentTeamName", team.name);
      window.location.href = "/tasks"; // переходим на страницу задач
    });
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
  alert(`Команда ${team.name} создана`);
  loadTeams();
});

document.addEventListener("DOMContentLoaded", loadTeams);
