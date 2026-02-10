<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

const loading = ref(true)
const charts = ref({})
const categories = ref([])
const selectedCategory = ref('All')

// brand colors
const themeColors = ['#0d9488', '#6366f1', '#f59e0b', '#ef4444', '#10b981']

// Safe formatter helper
const safeCurrency = (val) => {
  if (typeof val !== 'number') return val
  return val >= 1000 ? `$${(val/1000).toFixed(1)}k` : `$${val.toFixed(0)}`
}

const safePercent = (val) => {
  if (typeof val !== 'number') return val
  return `${val.toFixed(1)}%`
}

// Tooltip formatter (2 decimals)
const tooltipCurrency = (val) => {
  if (typeof val !== 'number') return val
  return `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const tooltipPercent = (val) => {
  if (typeof val !== 'number') return val
  return `${val.toFixed(2)}%`
}

// Common polished options to remove "Excel look"
const commonOptions = {
  chart: { 
    toolbar: { show: false }, 
    background: 'transparent',
    fontFamily: 'Outfit, sans-serif',
    zoom: { enabled: false }
  },
  dataLabels: { enabled: false },
  grid: { 
    borderColor: 'rgba(255,255,255,0.05)', 
    strokeDashArray: 4,
    xaxis: { lines: { show: false } }   
  },
  theme: { mode: 'light' }, 
  stroke: { curve: 'smooth', width: 2 },
  xaxis: { 
    axisBorder: { show: false }, 
    axisTicks: { show: false },
    labels: { style: { colors: '#64748b', fontSize: '12px' } } 
  },
  yaxis: { 
    labels: { style: { colors: '#64748b', fontSize: '12px' }, formatter: safeCurrency } 
  }
}

const series = ref({
  weather: [],
  price: [],
  day: [],
  trend: [],
  catRevenue: [],
  lift: []
})

const finalOptions = ref({
  weather: { 
    ...commonOptions,
    chart: { type: 'bar', height: 350, toolbar: { show: false }, background: 'transparent', fontFamily: 'Outfit' },
    title: { text: 'Avg Revenue by Weather', style: { color: '#64748b' } },
    plotOptions: { bar: { borderRadius: 4, horizontal: true, distributed: true } },
    colors: themeColors,
    legend: { show: false },
    yaxis: { labels: { formatter: safeCurrency } },
    tooltip: { y: { formatter: tooltipCurrency } }
  },
  day: { 
    ...commonOptions,
    chart: { type: 'bar', height: 350, toolbar: { show: false }, background: 'transparent', fontFamily: 'Outfit' },
    title: { text: 'Avg Sales by Day of Week', style: { color: '#64748b' } },
    plotOptions: { bar: { borderRadius: 4, horizontal: false, distributed: true } },
    colors: themeColors,
    legend: { show: false },
    tooltip: { y: { formatter: tooltipCurrency } }
  },
  trend: { 
    ...commonOptions,
    chart: { type: 'area', height: 350, toolbar: { show: false }, background: 'transparent', fontFamily: 'Outfit' },
    colors: ['#0ea5e9'],
    fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05, stops: [0, 100] } },
    title: { text: 'Daily Revenue Trend', style: { color: '#64748b' } },
    xaxis: { 
      type: 'datetime', 
      categories: [],
      labels: { style: { colors: '#64748b' }, format: 'dd MMM' }
    },
    tooltip: { x: { format: 'dd MMM yyyy' }, y: { formatter: tooltipCurrency } }
  },
  catRevenue: { 
    ...commonOptions,
    chart: { type: 'bar', height: 350, toolbar: { show: false }, background: 'transparent', fontFamily: 'Outfit' },
    plotOptions: { bar: { borderRadius: 4, horizontal: true, distributed: true, dataLabels: { position: 'bottom' } } },
    colors: themeColors,
    legend: { show: false },
    title: { text: 'Total Revenue by Category', style: { color: '#64748b' } },
    xaxis: { categories: [], labels: { formatter: safeCurrency } },
    dataLabels: { 
      enabled: true, 
      textAnchor: 'start', 
      style: { colors: ['#fff'] }, 
      formatter: safeCurrency,
      offsetX: 0
    },
    tooltip: { y: { formatter: tooltipCurrency } }
  },
  lift: { 
    ...commonOptions,
    chart: { type: 'bar', height: 350, toolbar: { show: false }, background: 'transparent', fontFamily: 'Outfit' },
    title: { text: 'Rain Lift Impact (%)', style: { color: '#64748b' } },
    plotOptions: { 
      bar: { 
        horizontal: true, 
        borderRadius: 4, 
        colors: { ranges: [{ from: -100, to: 0, color: '#ef4444' }, { from: 0, to: 100, color: '#10b981' }] } 
      } 
    },
    xaxis: { categories: [], labels: { formatter: (val) => typeof val === 'number' ? `${val.toFixed(0)}%` : val } },
    tooltip: { y: { formatter: tooltipPercent } },
    dataLabels: { enabled: true, formatter: safePercent }
  }
})

const fetchData = async () => {
  loading.value = true
  try {
    const params = selectedCategory.value !== 'All' ? { category: selectedCategory.value } : {}
    const { data } = await axios.get('/api/analytics/dashboard', { params })
    
    // Update categories list only if empty (first load)
    if (categories.value.length === 0 && data.all_categories) {
      categories.value = ['All', ...data.all_categories]
    }

    // 1. Weather Bar Chart
    series.value.weather = [{
      name: 'Avg Revenue',
      data: Object.entries(data.weather_distribution).map(([key, val]) => ({ x: key, y: val }))
    }]

    // 2. Day of Week Bar Chart
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    series.value.day = [{
      name: 'Avg Revenue',
      data: days.map(d => ({ x: d, y: data.day_distribution[d] || 0 }))
    }]

    // 3. Trend
    series.value.trend = [{ name: 'Revenue', data: data.daily_trend.revenue }]
    finalOptions.value.trend = { ...finalOptions.value.trend, xaxis: { ...finalOptions.value.trend.xaxis, categories: data.daily_trend.dates } }

    // 4. Category Revenue
    series.value.catRevenue = [{ name: 'Revenue', data: data.category_revenue.revenue }]
    finalOptions.value.catRevenue = { ...finalOptions.value.catRevenue, xaxis: { ...finalOptions.value.catRevenue.xaxis, categories: data.category_revenue.categories } }

    // 5. Lift
    series.value.lift = [{ name: 'Lift %', data: data.rain_lift.lift }]
    finalOptions.value.lift = { ...finalOptions.value.lift, xaxis: { ...finalOptions.value.lift.xaxis, categories: data.rain_lift.categories } }

  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

watch(selectedCategory, () => {
  fetchData()
})

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div v-if="loading" style="display: flex; justify-content: center; padding: 4rem;">
    <div style="width: 40px; height: 40px; border: 4px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite;"></div>
  </div>
  
  <div v-else class="fade-in">
    <!-- Filter Bar -->
    <div style="display: flex; justify-content: flex-end; margin-bottom: 1.5rem;">
      <div style="position: relative;">
        <select v-model="selectedCategory" class="form-select" style="padding: 0.5rem 2.5rem 0.5rem 1rem; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-card); color: var(--text-main); cursor: pointer; appearance: none;">
           <!-- Custom arrow handled by CSS or just simplistic -->
           <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
        <span style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: var(--text-muted);">▼</span>
      </div>
    </div>

    <div class="analytics-grid">
    <!-- Row 1: Key Distributions -->
    <div class="card">
       <apexchart type="bar" height="300" :options="finalOptions.weather" :series="series.weather"></apexchart>
    </div>
    <div class="card">
       <apexchart type="bar" height="300" :options="finalOptions.day" :series="series.day"></apexchart>
    </div>
    
    <!-- Row 2: Trend & Categories -->
    <div class="card" style="grid-column: span 2;">
       <apexchart type="area" height="350" :options="finalOptions.trend" :series="series.trend"></apexchart>
    </div>

    <!-- Row 3: Revenue & Lift -->
    <div class="card">
       <apexchart type="bar" height="350" :options="finalOptions.catRevenue" :series="series.catRevenue"></apexchart>
    </div>
    <div class="card">
       <apexchart type="bar" height="350" :options="finalOptions.lift" :series="series.lift"></apexchart>
    </div>
  </div>
  </div>
</template>

<style scoped>
.analytics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}
@media (max-width: 1024px) {
  .analytics-grid { grid-template-columns: 1fr; }
  .card { grid-column: auto !important; }
}

@keyframes spin { to { transform: rotate(360deg); } }

:deep(.apexcharts-tooltip) {
  color: #333 !important;
}
:deep(.apexcharts-tooltip-title) {
  background: #f3f4f6 !important;
  color: #111 !important;
}
:deep(.apexcharts-text) {
  fill: #64748b !important;
}
</style>
