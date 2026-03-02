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
function formatDate(year, month, day) {
    return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

// Загрузка событий с API
async function fetchEvents(year, month) {
    try {
        const response = await fetch(`/api/v1/events?year=${year}&month=${month + 1}`);
        if (!response.ok) {
            throw new Error('Ошибка загрузки событий');
        }
        eventsCache = await response.json();
        console.log('Загруженные задачи:', eventsCache);
    } catch (error) {
        console.error('Не удалось загрузить задачи:', error);
        eventsCache = [];
    }
}

// Получить события для конкретного дня
function getEventsForDay(year, month, day) {
    const dateStr = formatDate(year, month, day);
    return eventsCache.filter(event => event.date === dateStr);
}

// Получить статус задачи на русском
function getStatusInRussian(status) {
    const statusMap = {
        'open': 'Открыта',
        'in_progress': 'В работе',
        'completed': 'Завершена',
        'cancelled': 'Отменена'
        // добавьте другие статусы в зависимости от вашего TaskStatus
    };
    return statusMap[status] || status;
}

// Отображение событий выбранного дня
function showEventsForSelectedDay() {
    if (!selectedDate) {
        eventListEl.innerHTML = '<li>Выберите дату в календаре</li>';
        return;
    }

    const dayEvents = eventsCache.filter(event => event.date === selectedDate);

    if (dayEvents.length === 0) {
        eventListEl.innerHTML = '<li>Нет задач на этот день</li>';
    } else {
        eventListEl.innerHTML = '';
        dayEvents.forEach(event => {
            const li = document.createElement('li');
            
            // Определяем цвет в зависимости от статуса
            let statusColor = '#007bff'; // синий по умолчанию
            if (event.status === 'completed') {
                statusColor = '#28a745'; // зеленый для завершенных
            } else if (event.status === 'cancelled') {
                statusColor = '#dc3545'; // красный для отмененных
            } else if (event.status === 'in_progress') {
                statusColor = '#ffc107'; // желтый для в работе
            }
            
            li.style.borderLeftColor = statusColor;
            
            // Формируем HTML для элемента списка
            let timeInfo = event.time ? event.time : 'Весь день';
            let statusText = event.status ? getStatusInRussian(event.status) : '';
            
            li.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <strong>${timeInfo}</strong> - ${event.title}
                        <br>
                        <small>${event.description || 'Нет описания'}</small>
                    </div>
                    <span style="font-size: 0.8em; color: #000000; background: #f0f0f0; padding: 2px 5px; border-radius: 3px;">
                        ${statusText}
                    </span>
                </div>
            `;
            
            // Добавляем обработчик клика для просмотра деталей
            li.addEventListener('click', () => {
                showEventDetails(event.id);
            });
            li.style.cursor = 'pointer';
            
            eventListEl.appendChild(li);
        });
    }
}

// Функция для показа деталей задачи (можно открывать модальное окно)
async function showEventDetails(eventId) {
    try {
        const response = await fetch(`/api/v1/events/${eventId}`);
        if (response.ok) {
            const details = await response.json();
            // Здесь можно показать модальное окно с деталями
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
}

// Отрисовка календаря
async function renderCalendar() {
    // Обновляем заголовок
    const monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
    currentMonthYearEl.textContent = `${monthNames[currentMonth]} ${currentYear}`;

    // Загружаем задачи для этого месяца
    await fetchEvents(currentYear, currentMonth);

    // Очищаем календарь
    calendarEl.innerHTML = '';

    // Добавляем названия дней недели
    const weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
    weekdays.forEach(day => {
        const dayEl = document.createElement('div');
        dayEl.classList.add('weekday');
        dayEl.textContent = day;
        calendarEl.appendChild(dayEl);
    });

    // Определяем первый день месяца
    const firstDayOfMonth = new Date(currentYear, currentMonth, 1);
    let startOffset = firstDayOfMonth.getDay() - 1;
    if (startOffset === -1) startOffset = 6;

    // Определяем последнее число месяца
    const lastDateOfMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

    // Заполняем пустые ячейки перед началом месяца
    for (let i = 0; i < startOffset; i++) {
        const emptyCell = document.createElement('div');
        emptyCell.classList.add('calendar-day', 'empty');
        calendarEl.appendChild(emptyCell);
    }

    // Заполняем ячейки с днями месяца
    for (let day = 1; day <= lastDateOfMonth; day++) {
        const cell = document.createElement('div');
        cell.classList.add('calendar-day');
        cell.setAttribute('data-date', formatDate(currentYear, currentMonth, day));
        cell.setAttribute('data-day', day);

        // Номер дня
        const dayNumberSpan = document.createElement('div');
        dayNumberSpan.classList.add('day-number');
        dayNumberSpan.textContent = day;
        cell.appendChild(dayNumberSpan);

        // Задачи этого дня
        const dayEvents = getEventsForDay(currentYear, currentMonth, day);
        
        // Группируем по статусу для лучшей визуализации
        const completedTasks = dayEvents.filter(e => e.status === 'completed');
        const otherTasks = dayEvents.filter(e => e.status !== 'completed');
        
        // Сначала показываем незавершенные задачи
        otherTasks.slice(0, 2).forEach(event => {
            const eventSpan = document.createElement('div');
            eventSpan.classList.add('event-indicator');
            eventSpan.classList.add('event-task');
            eventSpan.textContent = event.title.length > 15 
                ? event.title.substring(0, 15) + '...' 
                : event.title;
            cell.appendChild(eventSpan);
        });
        
        // Если есть завершенные задачи, показываем индикатор
        if (completedTasks.length > 0) {
            const completedSpan = document.createElement('div');
            completedSpan.classList.add('event-indicator');
            completedSpan.style.backgroundColor = '#28a745';
            completedSpan.textContent = `✓ ${completedTasks.length} завершено`;
            cell.appendChild(completedSpan);
        }
        
        // Если задач больше, чем помещается, показываем счетчик
        if (dayEvents.length > 3) {
            const moreSpan = document.createElement('div');
            moreSpan.classList.add('event-indicator');
            moreSpan.style.backgroundColor = '#6c757d';
            moreSpan.textContent = `+${dayEvents.length - 3} еще`;
            cell.appendChild(moreSpan);
        }

        // Обработчик клика по дню
        cell.addEventListener('click', () => {
    document.querySelectorAll('.calendar-day').forEach(el => {
        el.classList.remove('selected');
        // НЕ меняйте style напрямую!
    });
    cell.classList.add('selected');
    // НЕ меняйте style напрямую!
            
            selectedDate = formatDate(currentYear, currentMonth, day);
            
            // Форматируем дату для отображения
            const displayDate = new Date(currentYear, currentMonth, day);
            selectedDateTitleEl.textContent = displayDate.toLocaleDateString('ru-RU', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            
            showEventsForSelectedDay();
        });

        calendarEl.appendChild(cell);
    }

    // Дополняем последнюю строку пустыми ячейками при необходимости
    const totalCells = Math.ceil((startOffset + lastDateOfMonth) / 7) * 7;
    for (let i = startOffset + lastDateOfMonth; i < totalCells; i++) {
        const emptyCell = document.createElement('div');
        emptyCell.classList.add('calendar-day', 'empty');
        calendarEl.appendChild(emptyCell);
    }
    
    // Сбрасываем выбранную дату
    selectedDate = null;
    selectedDateTitleEl.textContent = 'сегодня';
    eventListEl.innerHTML = '<li>Выберите дату в календаре</li>';
}

// Обработчики событий
prevBtn.addEventListener('click', () => {
    currentMonth--;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    }
    renderCalendar();
});

nextBtn.addEventListener('click', () => {
    currentMonth++;
    if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    renderCalendar();
});

// Инициализация
renderCalendar();