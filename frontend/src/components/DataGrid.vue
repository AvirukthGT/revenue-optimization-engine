<script setup>
import { computed } from 'vue'

const props = defineProps(['data'])

const headers = computed(() => {
  if (!props.data || props.data.length === 0) return []
  return Object.keys(props.data[0])
})

const downloadCSV = () => {
  if (!props.data || props.data.length === 0) return
  
  const csvContent = [
    headers.value.join(','),
    ...props.data.map(row => headers.value.map(header => row[header]).join(','))
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', 'revenue_data.csv')
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<template>
  <div class="card data-grid-card">
    <div class="grid-header">
      <div>
        <h3 class="text-sm font-bold uppercase tracking-wider text-muted">Raw Data Explorer</h3>
        <p class="text-xs text-muted" style="margin-top: 4px; opacity: 0.7;">{{ data ? data.length : 0 }} records found</p>
      </div>
      <button @click="downloadCSV" class="btn-export">
        <svg style="width: 16px; height: 16px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
        Export CSV
      </button>
    </div>
    
    <div class="table-container custom-scrollbar">
      <table class="premium-table">
        <thead>
          <tr>
            <th v-for="header in headers" :key="header">
              {{ header.replace(/_/g, ' ') }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in data" :key="i">
            <td v-for="header in headers" :key="header">
              {{ typeof row[header] === 'number' ? 
                 (header.includes('PRICE') || header.includes('REVENUE') ? `$${row[header].toFixed(2)}` : row[header].toLocaleString()) 
                 : row[header] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.data-grid-card {
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 600px;
}

.grid-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
}

.btn-export {
  background: rgba(13, 148, 136, 0.1);
  color: var(--primary);
  border: 1px solid transparent;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-family: 'Outfit', sans-serif;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-export:hover {
  background: var(--primary);
  color: white;
  box-shadow: 0 4px 12px var(--primary-glow);
}

.table-container {
  overflow: auto;
  flex: 1;
}

.premium-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Inter', sans-serif;
  font-size: 0.9rem;
}

.premium-table th {
  background: var(--surface-hover);
  color: var(--text-muted);
  font-family: 'Outfit', sans-serif;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  padding: 1rem 1.5rem;
  text-align: left;
  position: sticky;
  top: 0;
  z-index: 10;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

.premium-table td {
  padding: 1rem 1.5rem;
  color: var(--text-main);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
  transition: background 0.1s;
}

.premium-table tr:hover td {
  background: rgba(13, 148, 136, 0.02);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #475569;
}
</style>

