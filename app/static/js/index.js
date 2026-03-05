// Текущая отображаемая дата (год и месяц)
let currentDate = new Date();
let currentYear = currentDate.getFullYear();
let currentMonth = currentDate.getMonth(); // 0-11
let selectedDate = null;
let eventsCache = [];

// Элементы DOM
const calendarEl = document.getElementById('calendar');
const currentMonthYearEl = document.getElementById('currentMonthYear');
const prevBtn = document.getElementById('prevMonthBtn');
const nextBtn = document.getElementById('nextMonthBtn');
const selectedDateTitleEl = document.getElementById('selectedDateTitle');
const eventListEl = document.getElementById('eventList');

// --- Вспомогательные функции ---
function formatDateUTC(year, month, day) {
    // Создаем дату в локальной временной зоне
    const date = new Date(year, month, day);
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, "0");
    const d = String(date.getDate()).padStart(2, "0");
    return `${y}-${m}-${d}`;
}

function formatDate(date) {

    if (!(date instanceof Date)) {
        date = new Date(date);
    }

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
}

function getEventColor(event) {
    if (event.event_type === 'meeting') return '#6f42c1';
    if (event.status === 'completed') return '#28a745';
    if (event.status === 'cancelled') return '#dc3545';
    if (event.status === 'in_progress') return '#ffc107';
    return '#007bff';
}

// Загрузка событий с API
async function fetchEvents(year, month) {
    const token = localStorage.getItem("token");
    console.log("🔍 Загрузка событий за:", year, "месяц:", month + 1);
    
    const response = await fetch(
        `/api/v1/events?year=${year}&month=${month + 1}`,
        {
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        }
    );

    if (!response.ok) {
        console.error("❌ Ошибка загрузки событий:", response.status);
        return;
    }

    const data = await response.json();
    console.log("📦 Получены события:", data);
    
    // Подробный вывод каждого события
    data.forEach((event, index) => {
        console.log(`  Событие ${index + 1}:`, {
            id: event.id,
            title: event.title,
            date: event.date,
            time: event.time,
            type: event.event_type,
            status: event.status
        });
    });
    
    // Проверка на мартовские события
    const marchEvents = data.filter(e => e.date.startsWith('2026-03'));
    console.log(`📅 Событий в марте: ${marchEvents.length}`);
    if (marchEvents.length > 0) {
        console.log("✅ Мартовские события найдены!");
    } else {
        console.log("❌ Мартовских событий нет в ответе");
    }

    eventsCache = data;
}

// Получить события для конкретного дня
function getEventsForDay(year, month, day) {
    const dayStr = formatDateUTC(year, month, day);
    return eventsCache.filter(event => event.date === dayStr);
}

// Статус на русском
function getStatusInRussian(status) {
    const statusMap = {
        'open': 'Открыта',
        'in_progress': 'В работе',
        'completed': 'Завершена',
        'cancelled': 'Отменена'
    };
    return statusMap[status] || status;
}

// Отображение событий выбранного дня
function showEventsForSelectedDay() {
    if (!selectedDate) {
        eventListEl.innerHTML = '<li>Выберите дату в календаре</li>';
        return;
    }

    const dayEvents = eventsCache.filter(
        event => event.date === selectedDate
    );

    if (dayEvents.length === 0) {
        eventListEl.innerHTML = '<li>Нет задач на этот день</li>';
    } else {
        eventListEl.innerHTML = '';
        dayEvents.forEach(event => {
            const li = document.createElement('li');

            // здесь вставляем новый код по цвету и тексту
            let statusColor = '#007bff';
            let statusText = '';

            if (event.event_type === 'meeting') {
                statusColor = '#6f42c1'; // фиолетовый для встреч
                statusText = 'Встреча';
            } else {
                if (event.status === 'completed') {
                    statusColor = '#28a745';
                } else if (event.status === 'cancelled') {
                    statusColor = '#dc3545';
                } else if (event.status === 'in_progress') {
                    statusColor = '#ffc107';
                }
                statusText = event.status ? getStatusInRussian(event.status) : '';
            }

            li.style.borderLeftColor = statusColor;

            li.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <strong>${event.time || 'Весь день'}</strong> - ${event.title}
                        <br>
                        <small>${event.description || 'Нет описания'}</small>
                    </div>
                    <span style="font-size: 0.8em; color: #000000; background: #f0f0f0; padding: 2px 5px; border-radius: 3px;">
                        ${statusText}
                    </span>
                </div>
            `;

            li.addEventListener('click', () => {
                showEventDetails(event.id);
            });
            li.style.cursor = 'pointer';

            eventListEl.appendChild(li);
        });
    }
}

// Детали события
async function showEventDetails(eventId) {
    try {
        const response = await fetch(`/api/v1/events/${eventId}`);
        if (response.ok) {
            const details = await response.json();
            alert(`
        Задача: ${details.title}
        Описание: ${details.description || 'Нет описания'}
        Статус: ${getStatusInRussian(details.status)}
        Дедлайн: ${details.deadline ? new Date(details.deadline).toLocaleString() : 'Не указан'}
                    `);
                }
    } catch (error) {
        console.error('Ошибка при загрузке деталей:', error);
    }
    console.log("Запрос событий:", `/api/v1/events?year=${year}&month=${month+1}`);
}

// Отрисовка календаря
async function renderCalendar() {
    currentMonthYearEl.textContent = `${['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'][currentMonth]} ${currentYear}`;

    await fetchEvents(currentYear, currentMonth);
    console.log("EVENT CACHE:", eventsCache);

    calendarEl.innerHTML = '';
    ['Пн','Вт','Ср','Чт','Пт','Сб','Вс'].forEach(day => {
        const dayEl = document.createElement('div');
        dayEl.classList.add('weekday');
        dayEl.textContent = day;
        calendarEl.appendChild(dayEl);
    });

    const firstDay = new Date(Date.UTC(currentYear, currentMonth, 1));
    let startOffset = firstDay.getUTCDay() - 1;
    if (startOffset === -1) startOffset = 6;

    const lastDate = new Date(Date.UTC(currentYear, currentMonth + 1, 0)).getUTCDate();

    for (let i = 0; i < startOffset; i++) {
        const empty = document.createElement('div');
        empty.classList.add('calendar-day','empty');
        calendarEl.appendChild(empty);
    }

    for (let day = 1; day <= lastDate; day++) {
        const cell = document.createElement('div');
        cell.classList.add('calendar-day');
        const dateStr = formatDateUTC(currentYear, currentMonth, day);
        cell.setAttribute('data-date', dateStr);
        cell.setAttribute('data-day', day);

        const dayNumberSpan = document.createElement('div');
        dayNumberSpan.classList.add('day-number');
        dayNumberSpan.textContent = day;
        cell.appendChild(dayNumberSpan);
        
        console.log("CHECK DAY:", formatDateUTC(currentYear, currentMonth, day), eventsCache);
        const dayEvents = getEventsForDay(currentYear, currentMonth, day);

        // Добавляем индикаторы
        dayEvents.slice(0, 3).forEach(event => {
            const evSpan = document.createElement('div');
            evSpan.classList.add('event-indicator');
            evSpan.textContent = event.title.length > 15 ? event.title.slice(0,15)+'...' : event.title;
            evSpan.style.backgroundColor = getEventColor(event);
            evSpan.style.color = "#fff";
            evSpan.style.padding = "2px 5px";
            evSpan.style.borderRadius = "4px";
            evSpan.style.marginTop = "2px";
            evSpan.style.display = "block";
            cell.appendChild(evSpan);
        });

        if (dayEvents.length > 3) {
            const moreSpan = document.createElement('div');
            moreSpan.classList.add('event-indicator');
            moreSpan.textContent = `+${dayEvents.length - 3} еще`;
            cell.appendChild(moreSpan);
        }

        cell.addEventListener('click', () => {
            document.querySelectorAll('.calendar-day').forEach(el => el.classList.remove('selected'));
            cell.classList.add('selected');
            selectedDate = dateStr;

            const displayDate = new Date(Date.UTC(currentYear, currentMonth, day));
            selectedDateTitleEl.textContent = displayDate.toLocaleDateString('ru-RU',{year:'numeric',month:'long',day:'numeric'});

            showEventsForSelectedDay();
        });

        calendarEl.appendChild(cell);
    }

    const totalCells = Math.ceil((startOffset + lastDate) / 7) * 7;
    for (let i = startOffset + lastDate; i < totalCells; i++) {
        const empty = document.createElement('div');
        empty.classList.add('calendar-day','empty');
        calendarEl.appendChild(empty);
    }

    selectedDate = null;
    selectedDateTitleEl.textContent = 'сегодня';
    eventListEl.innerHTML = '<li>Выберите дату в календаре</li>';
}

// Кнопки переключения
prevBtn.addEventListener('click', () => {
    currentMonth--;
    if (currentMonth < 0) { currentMonth = 11; currentYear--; }
    renderCalendar();
});

nextBtn.addEventListener('click', () => {
    currentMonth++;
    if (currentMonth > 11) { currentMonth = 0; currentYear++; }
    renderCalendar();
});

// Инициализация
renderCalendar();
console.log("EVENT CACHE:", eventsCache);