function getTeamIdFromUrl() {
  const parts = window.location.pathname.split("/");
  return parts[2]; // /teams/{team_id}/tasks → parts[2] = team_id
}

async function loadTasks() {
  const token = localStorage.getItem("token");
  const teamId = getTeamIdFromUrl();
  if (!token || !teamId) return;

  const res = await fetch(`/api/v1/teams/${teamId}/tasks`, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!res.ok) return;

  const tasks = await res.json();
  const list = document.getElementById("task-list");
  list.innerHTML = "";

  tasks.forEach(task => {
  const li = document.createElement("li");
  li.style.padding = "8px";
  li.style.marginBottom = "6px";
  li.style.cursor = "pointer"; // курсор как ссылка

  // при клике на задачу — переходим на страницу задачи
  li.onclick = () => {
  const teamId = localStorage.getItem("currentTeamId");
  window.location.href = `/teams/${teamId}/tasks/${task.id}/page`;
};

  li.innerHTML = `
    <strong>${task.title}</strong> — ${task.status} —
    Исполнитель: ${task.assignee_id || 'нет'}
    <button onclick="event.stopPropagation(); editTask('${task.id}')">Редактировать</button>
    <button onclick="event.stopPropagation(); deleteTask('${task.id}')">Удалить</button>
  `;

  list.appendChild(li);
});
}

document.addEventListener("DOMContentLoaded", loadTasks);

// Создание задачи
document.getElementById("create-task-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const token = localStorage.getItem("token");
  if (!token || !currentTeamId) return alert("Выберите команду");

  const data = {
    title: document.getElementById("task-title").value,
    assignee_id: document.getElementById("task-assignee").value || null,
    deadline: document.getElementById("task-deadline").value,
    status: document.getElementById("task-status").value
  };

  const res = await fetch(`/api/v1/teams/${currentTeamId}/tasks`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });

  if (!res.ok) {
    const err = await res.json();
    alert("Ошибка: " + (err.detail || JSON.stringify(err)));
    return;
  }

  alert("Задача создана!");
  loadTasks();
});

// Удаление задачи
async function deleteTask(taskId) {
  const token = localStorage.getItem("token");
  if (!token || !currentTeamId) return;

  const res = await fetch(`/api/v1/teams/${currentTeamId}/tasks/${taskId}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!res.ok) {
    const err = await res.json();
    alert("Ошибка: " + (err.detail || JSON.stringify(err)));
    return;
  }

  alert("Задача удалена!");
  loadTasks();
}

// Редактирование задачи (например изменить статус)
async function editTask(taskId) {
  const newStatus = prompt("Введите новый статус: open, in_progress, done");
  if (!newStatus) return;

  const token = localStorage.getItem("token");

  const res = await fetch(`/api/v1/teams/${currentTeamId}/tasks/${taskId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ status: newStatus })
  });

  if (!res.ok) {
    const err = await res.json();
    alert("Ошибка: " + (err.detail || JSON.stringify(err)));
    return;
  }

  alert("Статус обновлён!");
  loadTasks();
}

// Пример: задать team_id при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
  currentTeamId = localStorage.getItem("currentTeamId"); // можно хранить выбранную команду
  const teamName = localStorage.getItem("currentTeamName");
  if (teamName) document.getElementById("team-name").textContent = teamName;

  loadTasks();
});
