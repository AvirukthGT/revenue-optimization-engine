<script setup>
import { useSimulationStore } from '../stores/simulation'
import { storeToRefs } from 'pinia'
import { watch, computed } from 'vue'

const store = useSimulationStore()
const { category, weather, ourPrice, competitorPrice, isWeekend, prediction } = storeToRefs(store)

// Compute rounded competitor price for display to avoid "2398.64990234375" ugliness
const displayCompetitorPrice = computed({
  get: () => parseFloat(competitorPrice.value).toFixed(2),
  set: (val) => competitorPrice.value = Number(val)
})

watch([category, weather, ourPrice, isWeekend], () => {
  store.runSimulation()
})

store.fetchHistory()
</script>

<template>
  <div style="display: flex; flex-direction: column; gap: 2rem;">
    
    <!-- Header Logo Area -->
    <div style="display: flex; align-items: center; gap: 1rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
      <div style="width: 40px; height: 40px; background: linear-gradient(135deg, var(--primary), var(--secondary)); border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px var(--primary-glow);">
         <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
      </div>
      <div>
        <h2 style="font-size: 1.1rem; font-weight: 700; color: white; letter-spacing: -0.01em;">RevOpt</h2>
        <div style="font-size: 0.75rem; color: var(--text-muted-on-dark); text-transform: uppercase; letter-spacing: 0.1em;">Engine v2.1</div>
      </div>
    </div>

    <!-- Category -->
    <div class="form-group">
      <label class="label-text">Target Category</label>
      <select v-model="category" @change="store.fetchHistory()" class="input-control">
        <option value="eletronicos">Electronics</option>
        <option value="telefonia">Telephony</option>
        <option value="audio">Audio</option>
        <option value="informatica_acessorios">IT Accessories</option>
        <option value="relogios_presentes">Watches & Gifts</option>
      </select>
    </div>

    <!-- Weather -->
    <div class="form-group">
      <label class="label-text">Market Conditions</label>
      <div style="display: flex; background: rgba(0,0,0,0.2); padding: 4px; border-radius: 10px;">
        <button 
          v-for="w in ['Clear', 'Rain', 'Cloudy']" 
          :key="w"
          @click="weather = w"
          :style="{
            flex: 1,
            padding: '8px',
            borderRadius: '8px',
            border: 'none',
            background: weather === w ? 'var(--primary)' : 'transparent',
            color: weather === w ? 'white' : 'var(--text-muted-on-dark)',
            fontSize: '0.85rem',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }"
        >
          {{ w }}
        </button>
      </div>
    </div>

    <!-- Competitor -->
    <div class="form-group">
      <label class="label-text">Competitor Index ($)</label>
      <input type="number" v-model="displayCompetitorPrice" class="input-control" step="0.01" />
    </div>

    <!-- Our Price -->
    <div class="form-group">
      <div class="flex-between mb-2">
        <label class="label-text" style="margin: 0;">Strategy Price</label>
        <div style="background: rgba(13, 148, 136, 0.2); color: var(--primary); padding: 2px 8px; border-radius: 6px; font-family: monospace; font-weight: bold;">
          ${{ ourPrice }}
        </div>
      </div>
      <input 
        type="range" 
        v-model.number="ourPrice" 
        min="50" 
        max="1000" 
        step="1" 
        style="width: 100%; cursor: pointer; height: 6px; border-radius: 4px; appearance: none; background: rgba(255,255,255,0.2);"
      />
    </div>

    <!-- Prediction Card (Glass) -->
    <div v-if="prediction" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1.2rem; margin-top: auto;">
      <div class="flex-between mb-2">
         <span class="label-text" style="margin: 0; color: var(--secondary);">Projected Revenue</span>
         <span style="width: 8px; height: 8px; background: var(--success); border-radius: 50%; box-shadow: 0 0 10px var(--success);"></span>
      </div>
      
      <div style="font-size: 2rem; font-weight: 700; color: white;">
        ${{ prediction.predicted_revenue.toFixed(0) }}
      </div>
      
      <div style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-muted-on-dark); display: flex; align-items: center; gap: 0.5rem;">
         <span>📦 Vol: {{ prediction.predicted_quantity.toFixed(0) }}</span>
      </div>
    </div>

    <button @click="store.runSimulation()" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">
      Run Simulation
    </button>
  </div>
</template>

<style scoped>
/* No component-specific styles needed, using global semantic classes */
</style>


