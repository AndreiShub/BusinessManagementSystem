document.addEventListener("DOMContentLoaded", () => {
    const editBtn = document.getElementById("edit-profile-btn");
    const profileDisplay = document.getElementById("profile-display");
    const editForm = document.getElementById("profile-edit-form");
    const cancelBtn = document.getElementById("cancel-edit");
    const deactivateBtn = document.getElementById("deactivate-account");
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Вы не вошли в систему");
        window.location.href = "/login";
        return;
    }

    // --- Кнопка "Редактировать" ---
    editBtn.addEventListener("click", () => {
        profileDisplay.style.display = "none";
        editForm.style.display = "block";
        deactivateBtn.style.display = "inline-block";
    });

    // --- Кнопка "Отмена" ---
    cancelBtn.addEventListener("click", () => {
        editForm.style.display = "none";
        profileDisplay.style.display = "block";
        deactivateBtn.style.display = "none";
    });

    // --- Загрузка профиля ---
    async function loadProfile() {
        const response = await fetch("/api/v1/users/me", {
            headers: { "Authorization": "Bearer " + token }
        });

        if (!response.ok) {
            alert("Ваша сессия недействительна. Пожалуйста, войдите снова.");
            logout();
            return;
        }

        const user = await response.json();
        document.getElementById("email-display").textContent = user.email;
        document.getElementById("nickname-display").textContent = user.nickname;
        document.getElementById("superuser-display").textContent = user.is_superuser;
        document.getElementById("manager-display").textContent = user.is_manager;

        document.getElementById("email").value = user.email;
        document.getElementById("nickname").value = user.nickname;
    }

    loadProfile();

    // --- Функция logout ---
    function logout() {
        localStorage.removeItem("token");
        window.location.href = "/login";
    }

    // --- Деактивация аккаунта (soft delete) ---
    deactivateBtn.addEventListener("click", async () => {
        if (!confirm("Вы точно хотите деактивировать аккаунт? Это приведет к выходу из системы.")) {
            return;
        }

        const response = await fetch("/api/v1/users/me", {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ is_active: false })
        });

        if (!response.ok) {
            const data = await response.json();
            alert(data.detail ?? "Ошибка при деактивации аккаунта");
            return;
        }

        alert("Аккаунт деактивирован. Вы будете разлогинены.");
        logout();
    });

    // --- Обработка submit формы редактирования профиля + смена пароля ---
    document.getElementById("profile-edit-form").addEventListener("submit", async (e) => {
        e.preventDefault();

        // --- Валидация никнейма ---
        const nicknameInput = document.getElementById("nickname");
        const nicknameError = document.getElementById("nickname-error");
        const nickname = nicknameInput.value.trim();
        if (!nickname || nickname.length < 3) {
            nicknameError.textContent = "Никнейм минимум 3 символа";
            return;
        }
        nicknameError.textContent = "";

        // --- Обновление email/никнейма ---
        const email = document.getElementById("email").value.trim();
        const patchResponse = await fetch("/api/v1/users/me", {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ email, nickname })
        });

        if (!patchResponse.ok) {
            const data = await patchResponse.json();
            alert(JSON.stringify(data, null, 2) ?? "Ошибка обновления профиля");
            return;
        }

        // --- Смена пароля ---
        const currentPassword = document.getElementById("current-password").value.trim();
        const newPassword = document.getElementById("new-password").value.trim();
        const newPassword2 = document.getElementById("new-password-2").value.trim();
        const passwordError = document.getElementById("password-error");

        if (currentPassword || newPassword || newPassword2) {
            if (newPassword.length < 8) { passwordError.textContent = "Пароль минимум 8 символов"; return; }
            if (newPassword !== newPassword2) { passwordError.textContent = "Пароли не совпадают"; return; }

            passwordError.textContent = "";

            const passResp = await fetch("/api/v1/auth/jwt/change-password", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
            });

            if (!passResp.ok) {
                const data = await passResp.json();
                passwordError.textContent = data.detail ?? "Ошибка смены пароля";
                return;
            } else {
                alert("Пароль успешно изменён");
            }
        }

        alert("Профиль обновлён");
        editForm.style.display = "none";
        profileDisplay.style.display = "block";
        loadProfile();
    });
});