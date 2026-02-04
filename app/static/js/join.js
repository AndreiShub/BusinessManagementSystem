document.addEventListener("DOMContentLoaded", () => {
    updateNavbar();  // обновляем навбар

    const form = document.getElementById("join-form");
    const message = document.getElementById("message");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const code = document.getElementById("code").value;
        const token = localStorage.getItem("token");

        if (!token) {
            message.textContent = "Сначала войдите в аккаунт";
            message.style.color = "red";
            return;
        }

        try {
            const res = await fetch("/api/v1/teams/join", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ code })
            });

            if (res.ok) {
                message.textContent = "Вы успешно присоединились к команде!";
                message.style.color = "green";
                form.reset();
            } else {
                const data = await res.json();
                message.textContent = data.detail || "Ошибка при присоединении к команде";
                message.style.color = "red";
            }
        } catch (err) {
            console.error(err);
            message.textContent = "Ошибка сети";
            message.style.color = "red";
        }
    });
});
