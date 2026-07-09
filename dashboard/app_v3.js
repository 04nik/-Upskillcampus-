// Dashboard Application Logic

let activeTab = 'forecast';
let selectedJunction = 1;
let trafficChart = null;

// Initialize when DOM content is loaded
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    // 1. Populate Model Performance Table
    populatePerformanceTable();
    
    // 2. Set up event listeners
    const junctionSelect = document.getElementById('junction-select');
    junctionSelect.addEventListener('change', (e) => {
        selectedJunction = parseInt(e.target.value);
        updateDashboard();
    });
    
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            tabButtons.forEach(b => b.classList.remove('active'));
            
            // Handle clicking inner icons safely
            const targetBtn = e.target.closest('.tab-btn');
            targetBtn.classList.add('active');
            
            activeTab = targetBtn.dataset.tab;
            renderSelectedChart();
        });
    });
    
    // 3. Render Initial State
    updateDashboard();
}

function populatePerformanceTable() {
    const tbody = document.getElementById('model-stats-tbody');
    tbody.innerHTML = '';
    
    trafficData.modelStats.forEach(stat => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>Junction ${stat.Junction}</strong></td>
            <td><span class="badge badge-success">${stat.Model_Type}</span></td>
            <td>${stat.MAE.toFixed(2)}</td>
            <td>${stat.RMSE.toFixed(2)}</td>
            <td><strong>${stat.R2.toFixed(4)}</strong></td>
        `;
        tbody.appendChild(tr);
    });
}

function updateDashboard() {
    // 1. Update Metrics Cards
    updateMetrics();
    
    // 2. Render Current Chart Tab
    renderSelectedChart();
    
    // 3. Update Policy Insights
    updateInsights();
}

function updateMetrics() {
    const stats = trafficData.modelStats.find(s => s.Junction === selectedJunction);
    const hourly = trafficData.hourlyProfile[selectedJunction];
    const holiday = trafficData.holidayProfile[selectedJunction];
    
    // Calculate Average Volume
    const avgVolume = Math.round(hourly.reduce((a, b) => a + b, 0) / hourly.length);
    document.getElementById('val-avg-volume').textContent = avgVolume;
    
    // Calculate Peak Traffic
    const peakVolume = Math.max(...hourly);
    const peakHour = hourly.indexOf(peakVolume);
    document.getElementById('val-peak-hour').textContent = peakVolume;
    document.getElementById('trend-peak-hour').textContent = `Peak hour: ${formatHour(peakHour)}`;
    
    // Calculate Holiday Shift
    const avgNormal = holiday.normal.reduce((a,b)=>a+b, 0) / holiday.normal.length;
    const avgHoliday = holiday.holiday.reduce((a,b)=>a+b, 0) / holiday.holiday.length;
    const shiftPercent = ((avgHoliday - avgNormal) / avgNormal) * 100;
    
    const holidayValueEl = document.getElementById('val-holiday-impact');
    const holidayTrendEl = document.getElementById('trend-holiday-impact');
    
    if (shiftPercent < 0) {
        holidayValueEl.textContent = `${Math.abs(shiftPercent).toFixed(1)}%`;
        holidayValueEl.style.color = 'var(--primary)';
        holidayTrendEl.innerHTML = `<i class="fa-solid fa-arrow-trend-down" style="color: var(--primary)"></i> Drop on Holidays`;
    } else {
        holidayValueEl.textContent = `+${shiftPercent.toFixed(1)}%`;
        holidayValueEl.style.color = 'var(--danger)';
        holidayTrendEl.innerHTML = `<i class="fa-solid fa-arrow-trend-up" style="color: var(--danger)"></i> Rise on Holidays`;
    }
    
    // Model R2 Accuracy
    document.getElementById('val-model-accuracy').textContent = `${(stats.R2 * 100).toFixed(1)}%`;
    document.getElementById('trend-model-accuracy').textContent = `R² Score (${stats.Model_Type})`;
}

function updateInsights() {
    const peakHourDesc = document.getElementById('insight-peak-desc');
    const holidayDesc = document.getElementById('insight-holiday-desc');
    const expansionDesc = document.getElementById('insight-expansion-desc');
    
    const peakHourBadge = document.getElementById('insight-peak-badge');
    const holidayBadge = document.getElementById('insight-holiday-badge');
    const expansionBadge = document.getElementById('insight-expansion-badge');
    
    if (selectedJunction === 1) {
        peakHourBadge.textContent = "High Capacity Congestion";
        peakHourDesc.innerHTML = "As the primary arterial route, this junction exhibits severe morning (7 AM - 9 AM) and evening (5 PM - 7 PM) rush hours exceeding <strong>90 vehicles/hour average</strong>. Recommend implementing an adaptive AI traffic light system prioritizing this corridor during peak hours.";
        
        holidayBadge.textContent = "Holiday Traffic Relaxation";
        holidayDesc.innerHTML = "Traffic drops by over <strong>10% on holidays</strong>. This represents the ideal window for periodic structural maintenance, pothole repairs, and landscaping without causing major traffic disruptions.";
        
        expansionBadge.textContent = "Immediate Lane Expansion";
        expansionDesc.innerHTML = "With traffic volume projected to hit capacity limits within 12 months, the city planning office should initiate a feasibility study for an additional flyover or underpass route to siphon off through-traffic.";
    } 
    else if (selectedJunction === 2) {
        peakHourBadge.textContent = "Commercial Corridor Peaks";
        peakHourDesc.innerHTML = "Showcases sustained mid-day traffic (11 AM - 3 PM) and a high evening peak at 6 PM. Heavy shopper and logistical delivery vehicles dictate the pattern. Implement off-peak delivery windows for heavy trucks (only between 10 PM and 7 AM).";
        
        holidayBadge.textContent = "Holiday Surge Warning";
        holidayDesc.innerHTML = "Unlike other junctions, commercial Junction 2 experience a <strong>traffic increase of 4.5% during holidays</strong> due to shopping districts. Extra transit patrols and pre-planned parking routing must be active on holiday weekends.";
        
        expansionBadge.textContent = "Parking Access Operations";
        expansionDesc.innerHTML = "Congestion here is primarily caused by bottlenecking at commercial parking entrances. Recommend constructing decentralized smart parking structures with real-time digital space displays.";
    } 
    else if (selectedJunction === 3) {
        peakHourBadge.textContent = "School & Residential Flow";
        peakHourDesc.innerHTML = "Heavy unidirectional flow towards city center at 8 AM and returning at 5 PM. Highly sensitive to school calendar semesters. Establish safe pedestrian corridors and active school-zone speed restrictions (30 km/h) during rush hours.";
        
        holidayBadge.textContent = "Significant Quiet Periods";
        holidayDesc.innerHTML = "Traffic drops by <strong>18.5% on holidays and weekends</strong>. Noise mitigation barriers should be evaluated here to improve residential life quality during high-volume weekdays.";
        
        expansionBadge.textContent = "Active Transit Integration";
        expansionDesc.innerHTML = "Instead of lane expansion, promote public transport. Introduce dedicated school shuttle routes and bike lanes to reduce short-distance private vehicle school runs.";
    } 
    else if (selectedJunction === 4) {
        peakHourBadge.textContent = "Highway Exit Corridor";
        peakHourDesc.innerHTML = "Exhibits highly variable traffic with late-night truck peaks (9 PM - 2 AM). Congestion is strongly dependent on national freight schedules. Keep signals green-dominant on the highway exit lane to prevent backing up onto the freeway.";
        
        holidayBadge.textContent = "Weekend Vacation Exits";
        holidayDesc.innerHTML = "Traffic increases on long holiday weekends as residents leave the city. Recommend dynamic electronic display signs on the highway approach warning of queue lengths and suggesting alternative exit ramps.";
        
        expansionBadge.textContent = "Interstate Toll Integration";
        expansionDesc.innerHTML = "Integrate automatic RFID tolling gates (FastTag/SmartPass) far ahead of the junction to prevent deceleration bottlenecks from vehicles exit-channeling.";
    }
}

function renderSelectedChart() {
    const ctx = document.getElementById('trafficChart').getContext('2d');
    
    // Destroy previous chart if it exists
    if (trafficChart) {
        trafficChart.destroy();
    }
    
    let chartConfig = {};
    
    const chartColors = {
        primary: '#ec4899',
        primaryGlow: 'rgba(236, 72, 153, 0.4)',
        secondary: '#8b5cf6',
        secondaryGlow: 'rgba(139, 92, 246, 0.4)',
        success: '#10b981',
        grid: 'rgba(255, 255, 255, 0.05)',
        text: '#f8fafc',
        textMuted: '#64748b'
    };

    Chart.defaults.color = chartColors.textMuted;
    Chart.defaults.font.family = "'Outfit', sans-serif";

    if (activeTab === 'forecast') {
        const fcHourly = trafficData.hourlyForecast[selectedJunction];
        const displayLimit = 72; // Show first 3 days (72 hours) in detail
        const xLabels = fcHourly.timestamps.slice(0, displayLimit).map(ts => {
            const date = new Date(ts);
            return date.toLocaleDateString(undefined, {month:'short', day:'numeric'}) + ' ' + formatHour(date.getHours());
        });
        const yForecast = fcHourly.vehicles.slice(0, displayLimit);
        
        chartConfig = {
            type: 'line',
            data: {
                labels: xLabels,
                datasets: [{
                    label: `Hourly Forecast (Junction ${selectedJunction})`,
                    data: yForecast,
                    borderColor: chartColors.primary,
                    borderWidth: 2,
                    pointBackgroundColor: chartColors.primary,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#070714',
                    pointHoverBorderColor: chartColors.primary,
                    pointHoverBorderWidth: 2,
                    pointRadius: 2,
                    fill: true,
                    backgroundColor: createGradient(ctx, 'rgba(236, 72, 153, 0.15)', 'rgba(236, 72, 153, 0.0)'),
                    tension: 0.35
                }]
            },
            options: getChartOptions('Vehicles / Hour (Next 72 Hours)', 'Datetime')
        };
    } 
    else if (activeTab === 'diurnal') {
        const hourly = trafficData.hourlyProfile[selectedJunction];
        const xLabels = Array.from({length: 24}, (_, i) => formatHour(i));
        
        chartConfig = {
            type: 'line',
            data: {
                labels: xLabels,
                datasets: [{
                    label: `Average Diurnal Volume`,
                    data: hourly,
                    borderColor: chartColors.secondary,
                    borderWidth: 3,
                    pointBackgroundColor: chartColors.secondary,
                    pointHoverRadius: 7,
                    pointRadius: 4,
                    fill: true,
                    backgroundColor: createGradient(ctx, 'rgba(139, 92, 246, 0.15)', 'rgba(139, 92, 246, 0.0)'),
                    tension: 0.4
                }]
            },
            options: getChartOptions('Average Number of Vehicles', 'Hour of the Day')
        };
    } 
    else if (activeTab === 'weekly') {
        const weekly = trafficData.weeklyProfile[selectedJunction];
        const xLabels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        
        chartConfig = {
            type: 'bar',
            data: {
                labels: xLabels,
                datasets: [{
                    label: `Average Daily Volume`,
                    data: weekly,
                    backgroundColor: createGradient(ctx, 'rgba(236, 72, 153, 0.8)', 'rgba(244, 63, 94, 0.6)'),
                    borderWidth: 0,
                    borderRadius: 6,
                    barPercentage: 0.6
                }]
            },
            options: getChartOptions('Average Vehicles', 'Day of the Week')
        };
    } 
    else if (activeTab === 'holiday') {
        const hol = trafficData.holidayProfile[selectedJunction];
        const xLabels = Array.from({length: 24}, (_, i) => formatHour(i));
        
        chartConfig = {
            type: 'line',
            data: {
                labels: xLabels,
                datasets: [
                    {
                        label: 'Working Day (Normal)',
                        data: hol.normal,
                        borderColor: '#3b82f6',
                        borderWidth: 2,
                        pointRadius: 2,
                        fill: false,
                        tension: 0.35
                    },
                    {
                        label: 'Holiday / Occasion',
                        data: hol.holiday,
                        borderColor: '#ef4444',
                        borderWidth: 2.5,
                        pointRadius: 3,
                        pointBackgroundColor: '#ef4444',
                        fill: true,
                        backgroundColor: 'rgba(239, 68, 68, 0.05)',
                        tension: 0.35
                    }
                ]
            },
            options: getChartOptions('Average Vehicles', 'Hour of the Day')
        };
    } 
    else if (activeTab === 'history') {
        const hist = trafficData.historicalDaily[selectedJunction];
        
        // Show last 90 days of history for high performance
        const limit = 90;
        const xLabels = hist.dates.slice(-limit);
        const yHist = hist.vehicles.slice(-limit);
        
        chartConfig = {
            type: 'line',
            data: {
                labels: xLabels,
                datasets: [{
                    label: 'Daily Average Vehicles (Last 90 Days)',
                    data: yHist,
                    borderColor: '#10b981',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true,
                    backgroundColor: createGradient(ctx, 'rgba(16, 185, 129, 0.12)', 'rgba(16, 185, 129, 0.0)'),
                    tension: 0.2
                }]
            },
            options: getChartOptions('Daily Average Vehicles', 'Date')
        };
    }
    
    trafficChart = new Chart(ctx, chartConfig);
}

function getChartOptions(yTitle, xTitle) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    boxWidth: 12,
                    font: { size: 12, weight: 600 }
                }
            },
            tooltip: {
                backgroundColor: '#111827',
                titleColor: '#ffffff',
                bodyColor: '#e5e7eb',
                borderColor: 'rgba(255,255,255,0.1)',
                borderWidth: 1,
                padding: 12,
                cornerRadius: 8,
                titleFont: { size: 13, weight: 700 },
                bodyFont: { size: 13 }
            }
        },
        scales: {
            y: {
                grid: { color: 'rgba(255, 255, 255, 0.04)' },
                border: { dash: [4, 4] },
                title: {
                    display: true,
                    text: yTitle,
                    font: { size: 12, weight: 600 }
                },
                ticks: { font: { size: 11 } }
            },
            x: {
                grid: { display: false },
                title: {
                    display: true,
                    text: xTitle,
                    font: { size: 12, weight: 600 }
                },
                ticks: { maxRotation: 45, minRotation: 0, font: { size: 10 } }
            }
        }
    };
}

function createGradient(ctx, colorStart, colorEnd) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, colorStart);
    gradient.addColorStop(1, colorEnd);
    return gradient;
}

function formatHour(h) {
    if (h === 0) return '12 AM';
    if (h === 12) return '12 PM';
    return h < 12 ? `${h} AM` : `${h - 12} PM`;
}
