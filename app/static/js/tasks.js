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
  console.log("Загруженные задачи:", tasks);
  
  const list = document.getElementById("task-list");
  if (!list) return;
  
  list.innerHTML = "";

  for (const task of tasks) {
    const li = document.createElement("li");
    li.style.padding = "12px";
    li.style.marginBottom = "8px";
    li.style.cursor = "pointer";
    li.style.borderLeft = "4px solid #4caf50";
    li.style.borderRadius = "4px";
    li.style.backgroundColor = "#2f1b5c";
    li.style.listStyle = "none";

    li.onclick = () => {
      window.location.href = `/teams/${teamId}/tasks/${task.id}/page`;
    };

    // Получаем информацию об исполнителях
    const assigneeCount = task.assignee_ids?.length || 0;
    let assigneesText = "нет";
    
    if (assigneeCount > 0) {
      assigneesText = `${assigneeCount} исполнитель(ей)`;
      // Можно добавить ID для отладки
      // assigneesText += ` (${task.assignee_ids.join(", ")})`;
    }

    li.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="flex-grow: 1;">
          <strong style="font-size: 16px;">${task.title}</strong>
          <span style="
            margin-left: 10px;
            padding: 2px 8px;
            background: ${task.status === 'open' ? '#4caf50' : task.status === 'in_progress' ? '#ff9800' : '#9e9e9e'};
            color: white;
            border-radius: 12px;
            font-size: 12px;
          ">${task.status}</span>
          <br>
          <small style="color: #666; display: block; margin-top: 5px;">
            📅 ${task.deadline ? new Date(task.deadline).toLocaleString() : 'Нет дедлайна'}
          </small>
          <small style="color: #666; display: block;">
            👥 Исполнители: ${assigneesText}
          </small>
        </div>
        <div style="display: flex; gap: 5px;">
          <button onclick="event.stopPropagation(); editTask('${task.id}')" 
                  style="padding: 5px 10px; background: #ffc107; border: none; border-radius: 3px; cursor: pointer;">
            ✏️ Ред.
          </button>
          <button onclick="event.stopPropagation(); deleteTask('${task.id}')" 
                  style="padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 3px; cursor: pointer;">
            🗑️ Удал.
          </button>
        </div>
      </div>
    `;

    list.appendChild(li);
  }
}

// ==============================
// create task
// ==============================
document
  .getElementById("create-task-form")
  .addEventListener("submit", async e => {
    e.preventDefault();

    // получаем данные формы
    const title = document.getElementById("task-title").value;
    const description = document.getElementById("task-description")?.value || "";
    const status = document.getElementById("task-status").value;
    const deadlineInput = document.getElementById("task-deadline").value;

    // преобразуем deadline в ISO 8601 с таймзоной
    const deadlineISO = deadlineInput ? new Date(deadlineInput).toISOString() : null;

    // ВАЖНО: всегда отправляем массив, даже с одним исполнителем
    let assignee_ids = [];
    if (selectedAssignees.length > 0) {
      assignee_ids = selectedAssignees.map(a => a.id);
    }

    // Правильная структура данных для бэкенда
    const data = {
      title,
      description,
      deadline: deadlineISO,
      assignee_ids: assignee_ids
    };

    console.log("Отправляемые данные:", data);

    try {
      const res = await fetch(`/api/v1/teams/${teamId}/tasks`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(data)
      });

      if (!res.ok) {
        const err = await res.json();
        console.error("Ошибка ответа:", err);
        return alert("Ошибка: " + (err.detail || JSON.stringify(err)));
      }

      const result = await res.json();
      console.log("Задача создана:", result);
      
      // Проверяем, добавились ли исполнители
      if (result.assignee_ids && result.assignee_ids.length > 0) {
        console.log("✅ Исполнители добавлены:", result.assignee_ids);
      } else {
        console.warn("⚠️ Исполнители не добавились!");
      }

      // очищаем выбранных исполнителей и чипы
      selectedAssignees.length = 0;
      renderChips();

      // очищаем форму
      document.getElementById("task-title").value = "";
      document.getElementById("task-deadline").value = "";
      document.getElementById("task-status").value = "open";

      // перезагружаем задачи
      loadTasks();

    } catch (error) {
      console.error(error);
      alert("Ошибка при создании задачи");
    }
  });

// ==============================
// delete / edit
// ==============================
async function deleteTask(taskId) {
  if (!confirm("Удалить задачу?")) return;
  
  const res = await fetch(
    `/api/v1/teams/${teamId}/tasks/${taskId}`,
    { method: "DELETE", headers: getAuthHeaders() }
  );

  if (!res.ok) return alert("Ошибка удаления");

  loadTasks();
}

async function editTask(taskId) {
  const newStatus = prompt("Введите новый статус (open | in_progress | done):");
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
// assignees
// ==============================
const assigneeSelect = document.getElementById("assignee-select");
const chipsContainer = document.getElementById("assignee-chips");
const selectedAssignees = []; // массив выбранных исполнителей

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

// ==============================
// init
// ==============================
document.addEventListener("DOMContentLoaded", () => {
  const teamId = getTeamIdFromUrl();
  if (!teamId) return;

  const teamName = localStorage.getItem("currentTeamName");
  if (teamName) {
    const teamNameEl = document.getElementById("team-name");
    if (teamNameEl) teamNameEl.textContent = teamName;
  }

  loadTasks();
  loadTeamMembers(teamId);
});