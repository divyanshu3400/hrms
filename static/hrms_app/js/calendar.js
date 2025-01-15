const daysElement = document.querySelector('.days');
const monthYearElement = document.getElementById('event-year-month');
const modal = document.getElementById('myModal');
const modalContent = document.querySelector('.modal-content');

let currentDate = new Date();
const year = currentDate.getFullYear();
const month = ('0' + (currentDate.getMonth() + 1)).slice(-2); // Adding 1 to month as months are 0-indexed
const day = ('0' + currentDate.getDate()).slice(-2);
// Format the date as YYYY-MM-DD
const formattedDate = `${year}-${month}-${day}`;

fetchEvents(formattedDate)

function fetchEvents(formattedDate) {
    const csrftoken = getCookie('csrftoken');
    fetch('/fetch-events/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ date: formattedDate }), // Sending formatted date to the backend
    })
    .then(response => response.json())
    .then(data => {
        renderCalendar(data);
        const attendanceData = constructAttendanceJSON(data);
        generateAttendancePanel(attendanceData);
    })
    .catch(error => console.error('Error fetching events:', error)); 
}

function renderCalendar(events) {
    const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const lastDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
    const lastDay = lastDayOfMonth.getDate();
    const firstDayIndex = firstDayOfMonth.getDay();
    const lastDayIndex = lastDayOfMonth.getDay();
    const prevLastDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 0).getDate();
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

    monthYearElement.innerText = `${months[currentDate.getMonth()]} ${currentDate.getFullYear()}`;

    let days = '';

    for (let x = firstDayIndex; x > 0; x--) {
        days += `<div class="day prev-date">${prevLastDay - x + 1}</div>`;
    }

    for (let i = 1; i <= lastDay; i++) {
        let eventsHtml = '';
        const currentDateStr = currentDate.toISOString().split('T')[0];
        if(events.length > 0)
        {
            for (const event of events) {
                const eventDate = new Date(event.start_date);
                if (eventDate.getDate() === i && eventDate.getMonth() === currentDate.getMonth() && eventDate.getFullYear() === currentDate.getFullYear()) {
                    for (const subEvent of event.events) {
                        eventsHtml += `<div class="event ${subEvent.type}">${subEvent.title}</div>`;
                    }
                }
            }
    
        }
        let dayClass = 'day';
        if (new Date(currentDate.getFullYear(), currentDate.getMonth(), i).getDay() === 0) {
            dayClass += ' sunday';
        } else if (new Date(currentDate.getFullYear(), currentDate.getMonth(), i).getDay() === 6) {
            dayClass += ' saturday';
        }

        if (i === new Date().getDate() && currentDate.getMonth() === new Date().getMonth()) {
            days += `<div class="${dayClass} today" data-day="${i}">${i}<br>${eventsHtml}</div>`;
        } else {
            days += `<div class="${dayClass}" data-day="${i}">${i}<br>${eventsHtml}</div>`;
        }
    }


    for (let j = 1; j <= 6 - lastDayIndex; j++) {
        days += `<div class="day next-date">${j}</div>`;
    }

    daysElement.innerHTML = days;
}

function prevMonth() {
    currentDate.setMonth(currentDate.getMonth() - 1);
    const year = currentDate.getFullYear();
    const month = ('0' + (currentDate.getMonth() + 1)).slice(-2); // Adding 1 to month as months are 0-indexed
    const day = ('0' + currentDate.getDate()).slice(-2);    
    // Format the date as YYYY-MM-DD
    const formattedDate = `${year}-${month}-${day}`;
    updatePanelTitle(formatMonthYear(currentDate));
    fetchEvents(formattedDate)    
}

function nextMonth() {
    currentDate.setMonth(currentDate.getMonth() + 1);
    // Get year, month, and day components
    const year = currentDate.getFullYear();
    const month = ('0' + (currentDate.getMonth() + 1)).slice(-2); // Adding 1 to month as months are 0-indexed
    const day = ('0' + currentDate.getDate()).slice(-2);
    // Format the date as YYYY-MM-DD
    const formattedDate = `${year}-${month}-${day}`;
    updatePanelTitle(formatMonthYear(currentDate));
    fetchEvents(formattedDate);
}


daysElement.addEventListener('click', function(event) {
    const dayElement = event.target.closest('.day');
    if (dayElement) {
        const day = parseInt(dayElement.dataset.day);
        showModal(day, currentDate.getMonth(), currentDate.getFullYear(), dayElement);
    }
});


function showModal(day, month, year, element) {
    const rect = element.getBoundingClientRect(); // Get the position of the clicked day element
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
    const top = rect.top + scrollTop; // Calculate the top position relative to the document
    const left = rect.left + scrollLeft; // Calculate the left position relative to the document
    Metro.bottomsheet.toggle('#bottom-sheet', 'grid')
    modalContent.innerHTML = `
        <span class="close">&times;</span>
        <p>Selected Date: ${year}-${month + 1}-${day}</p>
        <p>Put your additional content here.</p>
    `;
    modal.style.top = `${top}px`; // Set the top position of the modal
    modal.style.left = `${left}px`; // Set the left position of the modal
    modal.style.display = 'block'; // Display the modal
}

modal.addEventListener('click', function(event) {
    if (event.target.classList.contains('close') || event.target === modal) {
        modal.style.display = 'none';
    }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        modal.style.display = 'none';
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updatePanelTitle(dateString) {
    console.log("Received dateString:", dateString);
    const attendancePanel = document.getElementById('attendancePanel');
    console.log("attendancePanel:", attendancePanel);
    if (attendancePanel) {
        console.log("Inside the if block");
        attendancePanel.setAttribute('data-title-caption', ` ${dateString}`);
        console.log("Updated data-title-caption:", attendancePanel.getAttribute('data-title-caption'));
    }
}


function formatMonthYear(date) {
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    const year = date.getFullYear();
    const month = monthNames[date.getMonth()];
    return `${month} ${year}`;
}
function constructAttendanceJSON(events) {
    const attendanceData = {
        header: [
            {
                name: "login_time",
                title: "Login Time",
                sortable: true,
                format: "date",
                formatMask: "dd-mm-yyyy HH:MM"
            },
            {
                name: "logout_time",
                title: "Logout Time",
                sortable: true,
                format: "date",
                formatMask: "dd-mm-yyyy HH:MM"
            },
            {
                name: "working_hrs",
                title: "Working Hrs",
                sortable: true
            }
        ],
        data: []
    };

    // Convert events to the format specified in attendance JSON
    events.forEach(event => {
        const loginTime = event.start_date;
        const logoutTime = event.end_date;
        const workingHours = calculateWorkingHours(event.start_time, event.end_time);
        attendanceData.data.push([loginTime, logoutTime, workingHours]);
    });

    return attendanceData;
}

function calculateWorkingHours(startTime, endTime) {
    // Calculate working hours based on startTime and endTime
    // You need to implement this function according to your logic
    // For example, you can use JavaScript's Date object to calculate the difference
    return "8:00"; // Placeholder value
}


function generateTable(attendanceData) {
    console.log(attendanceData);

    // Create table element
    const table = document.createElement('table');
    table.classList.add('table', 'striped', 'table-border', 'mt-4');
    table.setAttribute('data-role', 'table');
    table.setAttribute('data-cls-table-top', 'row');
    table.setAttribute('data-cls-search', 'cell-md-6');
    table.setAttribute('data-cls-rows-count', 'cell-md-6');
    table.setAttribute('data-rows', '5');
    table.setAttribute('data-rows-steps', '5, 10');
    table.setAttribute('data-show-activity', 'false');
    table.setAttribute('data-horizontal-scroll', 'true');

    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    attendanceData.header.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header.title;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create table body
    const tbody = document.createElement('tbody');
    attendanceData.data.forEach(rowData => {
        const tr = document.createElement('tr');
        rowData.forEach(cellData => {
            const td = document.createElement('td');
            td.textContent = cellData;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    // Append the table to the #attendanceTable div
    const attendanceTableDiv = document.getElementById('attendanceTable');
    if (attendanceTableDiv) {
        // Clear existing content
        attendanceTableDiv.innerHTML = '';
        // Append the table
        attendanceTableDiv.appendChild(table);
    }
}

function generateAttendancePanel(attendanceData) {
    // Create attendancePanel div
    const attendancePanelDiv = document.createElement('div');
    attendancePanelDiv.id = 'attendancePanel';
    attendancePanelDiv.setAttribute('data-role', 'panel');
    attendancePanelDiv.setAttribute('data-title-caption',`Attendance ${formatMonthYear(currentDate)}`);
    attendancePanelDiv.setAttribute('data-collapsible', 'true');
    attendancePanelDiv.setAttribute('data-title-icon', "<span class='mif-table'></span>");
    attendancePanelDiv.classList.add('mt-4');

    // Create attendanceTable div
    const attendanceTableDiv = document.createElement('div');
    attendanceTableDiv.id = 'attendanceTable';

    // Append attendanceTableDiv to attendancePanelDiv
    attendancePanelDiv.appendChild(attendanceTableDiv);

    // Insert attendancePanelDiv into cell2 div
    const cell2Div = document.getElementById('cell2');
    if (cell2Div) {
        // Clear existing content
        cell2Div.innerHTML = '';
        // Append the attendancePanelDiv to cell2Div
        cell2Div.appendChild(attendancePanelDiv);
    }
    generateTable(attendanceData); // You need to pass the attendance data to this function
}
