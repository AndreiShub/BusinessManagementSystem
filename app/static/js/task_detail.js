const token = localStorage.getItem("token");
const taskId = window.TASK_ID;
const teamId = window.CURRENT_TEAM_ID;

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
  };
}

// --------------------------
// Навигация назад
// --------------------------
function goBack() {
  window.location.href = "/teams";  // список всех команд
}

// --------------------------
// Рейтинг
// --------------------------
function renderStars(selected) {
  const container = document.getElementById("stars");
  container.innerHTML = "";
  for (let i = 1; i <= 5; i++) {
    const star = document.createElement("span");
    star.textContent = i <= selected ? "★" : "☆";
    star.style.cursor = "pointer";
    star.style.fontSize = "24px";
    star.onclick = () => submitRating(i);
    container.appendChild(star);
  }
}

async function loadMyRating() {
  const res = await fetch(`/api/v1/teams/${teamId}/tasks/${taskId}/rating`, { headers: authHeaders() });
  const data = await res.json();
  renderStars(data.score);
}

async function submitRating(score) {
  await fetch(`/api/v1/teams/${teamId}/tasks/${taskId}/rating`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ score }),
  });
  renderStars(score);
  loadRatingSummary();
}

async function loadRatingSummary() {
  const res = await fetch(`/api/v1/teams/${teamId}/tasks/${taskId}/rating/summary`, { headers: authHeaders() });
  const data = await res.json();
  const el = document.getElementById("rating-info");
  el.textContent = data.average ? `Средняя: ${data.average} (${data.count})` : "Нет оценок";
}

// --------------------------
// Комментарии
// --------------------------
async function loadComments() {
  const res = await fetch(`/api/v1/teams/${teamId}/tasks/${taskId}/comments`, { headers: authHeaders() });
  const comments = await res.json();
  const list = document.getElementById("comments-list");
  list.innerHTML = "";

  for (const c of comments) {
    const div = document.createElement("div");
    div.style.marginBottom = "6px";
    div.innerHTML = `
      <strong>User ${c.user_id}</strong>: ${c.text}<br>
      <small>${new Date(c.created_at).toLocaleString()}</small>
    `;
    list.appendChild(div);
  }
}

async function sendComment() {
  const input = document.getElementById("comment-input");
  const text = input.value.trim();
  if (!text) return;

  await fetch(`/api/v1/teams/${teamId}/tasks/${taskId}/comments`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ text }),
  });

  input.value = "";
  loadComments();
}

// --------------------------
// Инициализация
// --------------------------
async function init() {
  // загружаем данные задачи
  const res = await fetch(`/api/v1/teams/${teamId}/tasks/${taskId}`, { headers: authHeaders() });
  const task = await res.json();

  document.getElementById("task-title").textContent = task.title;
  document.getElementById("task-status").textContent = task.status;

  loadMyRating();
  loadRatingSummary();
  loadComments();

  document.getElementById("send-comment").onclick = sendComment;
}

init();
