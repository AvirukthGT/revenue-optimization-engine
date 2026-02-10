<script setup>
import { useSimulationStore } from '../stores/simulation'
import Sidebar from '../components/Sidebar.vue'
import DualAxisChart from '../components/DualAxisChart.vue'
import DataGrid from '../components/DataGrid.vue'
import ElasticityCurve from '../components/ElasticityCurve.vue'
import AnalyticsDashboard from '../components/AnalyticsDashboard.vue' // Import new Analytics Component
import { Sun, Moon, Menu } from 'lucide-vue-next'

const store = useSimulationStore()
import { ref } from 'vue'
const activeTab = ref('overview')
const isSidebarOpen = ref(false)
</script>

<template>
  <div class="app-layout">
    <!-- Mobile Overlay -->
    <div :class="['sidebar-overlay', isSidebarOpen ? 'visible' : '']" @click="isSidebarOpen = false"></div>

    <!-- Sidebar (Left Panel) -->
    <aside :class="['sidebar', isSidebarOpen ? 'open' : '']">
      <Sidebar />
    </aside>

    <!-- Main Content Area -->
    <div class="main-content">
      <!-- Top Header (Glass) -->
      <header class="top-header">
        <div style="display: flex; align-items: center; gap: 1rem;">
          <!-- Mobile Menu Button -->
          <button class="btn-icon mobile-only" @click="isSidebarOpen = !isSidebarOpen" style="margin-right: -0.5rem;">
            <Menu style="width: 24px;" />
          </button>

          <div>
            <h1 style="font-size: 1.25rem; font-weight: 700; color: var(--text-main);">Command Center</h1>
            <span class="desktop-only" style="font-size: 0.8rem; color: var(--text-muted);">Real-time Pricing Intelligence</span>
          </div>

          <!-- Tabs (Pills) -->
          <nav class="tabs-nav desktop-only">
            <button @click="activeTab = 'overview'" :class="['tab-btn', activeTab === 'overview' ? 'active' : '']">Overview</button>
            <button @click="activeTab = 'analytics'" :class="['tab-btn', activeTab === 'analytics' ? 'active' : '']">Analytics</button>
            <button @click="activeTab = 'data'" :class="['tab-btn', activeTab === 'data' ? 'active' : '']">Data</button>
          </nav>
        </div>
        
        <div style="display: flex; gap: 1rem; align-items: center;">
             <!-- Tabs for Mobile (Simplified dropdown or scroll?? For now just scroll if needed, hiding for simplicity in this step or keeping visual) -->
             
             <div class="desktop-only" style="display: flex; align-items: center; gap: 6px; background: rgba(16, 185, 129, 0.1); padding: 6px 12px; border-radius: 20px; color: var(--success); font-weight: 600; font-size: 0.85rem;">
                <span style="width: 8px; height: 8px; background: currentColor; border-radius: 50%; display: block;"></span>
                Online
             </div>
             <button @click="store.toggleDarkMode()" class="btn-icon">
                <Moon v-if="!store.isDarkMode" style="width: 20px;" />
                <Sun v-else style="width: 20px;" />
             </button>
        </div>
      </header>
      
      <!-- Mobile Tabs (Visible only on mobile) -->
      <div class="mobile-only" style="padding: 1rem 1rem 0; overflow-x: auto;">
          <nav class="tabs-nav" style="margin: 0; width: 100%; display: flex; justify-content: space-between;">
            <button @click="activeTab = 'overview'" :class="['tab-btn', activeTab === 'overview' ? 'active' : '']" style="flex: 1; justify-content: center; display: flex;">Overview</button>
            <button @click="activeTab = 'analytics'" :class="['tab-btn', activeTab === 'analytics' ? 'active' : '']" style="flex: 1; justify-content: center; display: flex;">Analytics</button>
            <button @click="activeTab = 'data'" :class="['tab-btn', activeTab === 'data' ? 'active' : '']" style="flex: 1; justify-content: center; display: flex;">Data</button>
          </nav>
      </div>

      <!-- Content -->
      <main class="dashboard-container">
        
        <!-- Tab 1: Overview -->
        <div v-if="activeTab === 'overview'" class="fade-in">
          
          <!-- KPI Grid -->
          <div class="kpi-grid">
            <div class="kpi-card">
               <div class="kpi-icon-wrapper">
                 <svg style="width: 24px;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
               </div>
               <span class="label-text">Total Revenue</span>
               <div class="text-2xl" style="margin-top: 4px;">$12,450</div>
               <div class="text-xs text-success" style="margin-top: 8px; font-weight: 600;">▲ 4.5% vs Last Week</div>
            </div>

            <div class="kpi-card">
               <div class="kpi-icon-wrapper" style="color: var(--accent); background: rgba(245, 158, 11, 0.1);">
                 <svg style="width: 24px;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
               </div>
               <span class="label-text">Inventory Level</span>
               <div class="text-2xl" style="margin-top: 4px;">845 units</div>
               <div class="text-xs text-accent" style="margin-top: 8px; font-weight: 600;">Low Stock Alert</div>
            </div>

            <div class="kpi-card">
               <div class="kpi-icon-wrapper" style="color: var(--secondary); background: rgba(99, 102, 241, 0.1);">
                 <svg style="width: 24px;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
               </div>
               <span class="label-text">Market Position</span>
               <div class="text-2xl" style="margin-top: 4px;">Active</div>
               <div class="text-xs text-muted" style="margin-top: 8px;">Gap: <span class="text-danger">-$12.50</span></div>
            </div>
          </div>

          <!-- Alert -->
          <div v-if="store.weather === 'Rain' && store.category === 'eletronicos'" class="card" style="border-left: 4px solid var(--accent); display: flex; gap: 1.5rem; background: linear-gradient(90deg, #fffbeb, #ffffff);">
             <div style="font-size: 2rem;">⚡</div>
             <div>
               <h3 class="text-xl" style="color: var(--text-main);">Storm Surge Opportunity</h3>
               <p class="text-muted" style="margin-top: 4px;">Rainy weather is driving demand for indoor electronics.</p>
               <button class="btn" style="margin-top: 10px; background: var(--accent); color: white; padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.8rem;">Apply +5% Margin Lift</button>
             </div>
          </div>

          <div class="card chart-container">
             <div class="flex-between" style="margin-bottom: 1.5rem;">
               <h3 class="text-xl">Performance Trends</h3>
               <div style="display: flex; gap: 1rem;">
                  <span class="text-xs text-muted flex-center"><span style="width: 8px; height: 8px; background: var(--primary); border-radius: 50%; margin-right: 6px;"></span> Sales Qty</span>
                  <span class="text-xs text-muted flex-center"><span style="width: 8px; height: 8px; background: var(--secondary); border-radius: 50%; margin-right: 6px;"></span> Price</span>
               </div>
             </div>
             <DualAxisChart :history="store.history" />
          </div>
        </div>

        <!-- Tab 2: Analytics -->
        <div v-if="activeTab === 'analytics'" class="fade-in">
           <AnalyticsDashboard />
        </div>

        <!-- Tab 3: Data -->
        <div v-if="activeTab === 'data'" class="fade-in">
           <div class="card" style="padding: 0; overflow: hidden;">
              <DataGrid :data="store.history" />
           </div>
        </div>

      </main>
    </div>
  </div>
</template>

<style scoped>
.mobile-only { display: none; }
.desktop-only { display: flex; }

@media (max-width: 1024px) {
  .mobile-only { display: flex; }
  .desktop-only { display: none; }
}
</style>


