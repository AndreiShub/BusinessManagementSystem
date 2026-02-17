// ==============================
// utils
// ==============================
function getTeamIdFromUrl() {
  const parts = window.location.pathname.split("/");
  return parts[2]; // /teams/{team_id}/tasks
}

function getAuthHeaders() {
  return {
    "Authorization": `Bearer ${localStorage.getItem("token")}`,
    "Content-Type": "application/json"
  };
}

// ==============================
// state
// ==============================
const teamId = getTeamIdFromUrl();
let selectedAssigneeId = null;

// ==============================
// tasks
// ==============================
async function loadTasks() {
  if (!teamId) return;

  const res = await fetch(`/api/v1/teams/${teamId}/tasks`, {
    headers: getAuthHeaders()
  });

  if (!res.ok) return;

  const tasks = await res.json();
  const list = document.getElementById("task-list");
  list.innerHTML = "";

  tasks.forEach(task => {
    const li = document.createElement("li");
    li.style.padding = "8px";
    li.style.marginBottom = "6px";
    li.style.cursor = "pointer";

    li.onclick = () => {
      window.location.href = `/teams/${teamId}/tasks/${task.id}/page`;
    };

    li.innerHTML = `
      <strong>${task.title}</strong> — ${task.status} —
      Исполнители: ${task.assignee?.email || "нет"}
      <button data-edit="${task.id}">Редактировать</button>
      <button data-delete="${task.id}">Удалить</button>
    `;

    list.appendChild(li);
  });

  // делегирование событий
  list.querySelectorAll("[data-delete]").forEach(btn => {
    btn.onclick = e => {
      e.stopPropagation();
      deleteTask(btn.dataset.delete);
    };
  });

  list.querySelectorAll("[data-edit]").forEach(btn => {
    btn.onclick = e => {
      e.stopPropagation();
      editTask(btn.dataset.edit);
    };
  });
}

// ==============================
// create task
// ==============================
document
  .getElementById("create-task-form")
  .addEventListener("submit", async e => {
    e.preventDefault();

    const data = {
      title: document.getElementById("task-title").value,
      assignee_id: selectedAssigneeId,
      deadline: document.getElementById("task-deadline").value,
      status: document.getElementById("task-status").value
    };

    const res = await fetch(`/api/v1/teams/${teamId}/tasks`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });

    if (!res.ok) {
      const err = await res.json();
      return alert("Ошибка: " + (err.detail || JSON.stringify(err)));
    }

    resetAssignee();
    loadTasks();
  });

// ==============================
// delete / edit
// ==============================
async function deleteTask(taskId) {
  const res = await fetch(
    `/api/v1/teams/${teamId}/tasks/${taskId}`,
    { method: "DELETE", headers: getAuthHeaders() }
  );

  if (!res.ok) return alert("Ошибка удаления");

  loadTasks();
}

async function editTask(taskId) {
  const newStatus = prompt("open | in_progress | done");
  if (!newStatus) return;

  const res = await fetch(
    `/api/v1/teams/${teamId}/tasks/${taskId}`,
    {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: JSON.stringify({ status: newStatus })
    }
  );

  if (!res.ok) return alert("Ошибка обновления");

  loadTasks();
}

// ==============================
// assignees (single now, ready for multiple)
// ==============================
const assigneeSelect = document.getElementById("assignee-select");
const chipsContainer = document.getElementById("assignee-chips");

async function loadTeamMembers(teamId) {
  const token = localStorage.getItem("token");
  if (!token) return;

  const res = await fetch(`/api/v1/teams/${teamId}/members`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) {
    console.error("Ошибка загрузки участников");
    return;
  }

  const members = await res.json();

  assigneeSelect.innerHTML = `<option value="">Назначить исполнителя</option>`;

  members.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m.user.id;
    opt.textContent = m.user.nickname || m.user.email;
    assigneeSelect.appendChild(opt);
  });
}



const selectedAssignees = []; // массив выбранных исполнителей

assigneeSelect.addEventListener("change", () => {
  const id = assigneeSelect.value;
  const label = assigneeSelect.selectedOptions[0]?.textContent;
  if (!id || !label) return;

  // если уже выбран, не добавляем повторно
  if (selectedAssignees.find(a => a.id === id)) {
    assigneeSelect.value = "";
    return;
  }

  selectedAssignees.push({ id, label });
  assigneeSelect.value = ""; // сбрасываем селект
  renderChips();
});

function renderChips() {
  chipsContainer.innerHTML = "";
  selectedAssignees.forEach(a => {
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.innerHTML = `
      ${a.label} <button type="button">×</button>
    `;
    // удаление конкретного исполнителя
    chip.querySelector("button").onclick = () => {
      const index = selectedAssignees.findIndex(sa => sa.id === a.id);
      if (index !== -1) selectedAssignees.splice(index, 1);
      renderChips();
    };
    chipsContainer.appendChild(chip);
  });
}

// при отправке формы
document
  .getElementById("create-task-form")
  .addEventListener("submit", async e => {
    e.preventDefault();

    const data = {
      title: document.getElementById("task-title").value,
      assignee_id: selectedAssignees.map(a => a.id), // теперь массив
      deadline: document.getElementById("task-deadline").value,
      status: document.getElementById("task-status").value
    };

    const token = localStorage.getItem("token");
    const teamId = getTeamIdFromUrl();

    const res = await fetch(`/api/v1/teams/${teamId}/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(data)
    });

    if (!res.ok) {
      const err = await res.json();
      return alert("Ошибка: " + (err.detail || JSON.stringify(err)));
    }

    selectedAssignees.length = 0; // очищаем массив
    renderChips(); // очищаем чипы
    loadTasks(); // перезагружаем задачи
  });


// ==============================
// init
// ==============================
document.addEventListener("DOMContentLoaded", () => {
  const teamId = getTeamIdFromUrl();
  if (!teamId) return;

  const teamName = localStorage.getItem("currentTeamName");
  if (teamName) {
    document.getElementById("team-name").textContent = teamName;
  }

  loadTasks();
  loadTeamMembers(teamId);
});