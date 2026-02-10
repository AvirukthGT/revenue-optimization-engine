<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps(['curve'])

const chartData = computed(() => {
  if (!props.curve || props.curve.length === 0) return { labels: [], datasets: [] }
  
  const labels = props.curve.map(d => `$${d.price.toFixed(2)}`)
  const revenue = props.curve.map(d => d.revenue)

  return {
    labels,
    datasets: [
      {
        label: 'Predicted Revenue',
        borderColor: '#f59e0b', // Amber
        backgroundColor: '#f59e0b88',
        data: revenue,
        tension: 0.4,
        fill: true
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
      legend: { display: false },
      title: { display: true, text: 'Price Elasticity (Revenue Potential)' }
  },
  scales: {
    y: {
      title: { display: true, text: 'Revenue ($)' }
    }
  }
}
</script>

<template>
  <div class="h-64">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>
