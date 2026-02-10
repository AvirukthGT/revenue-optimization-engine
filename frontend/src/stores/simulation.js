import { defineStore } from 'pinia'
import axios from 'axios'

export const useSimulationStore = defineStore('simulation', {
    state: () => ({
        // Inputs
        category: 'eletronicos',
        weather: 'Clear',
        competitorPrice: 300.00,
        ourPrice: 250.00,
        isWeekend: false,

        // Outputs
        prediction: null,
        history: [],
        elasticityCurve: [],

        // UI State
        isLoading: false,
        error: null,
        isDarkMode: false
    }),

    actions: {
        toggleDarkMode() {
            this.isDarkMode = !this.isDarkMode
            if (this.isDarkMode) {
                document.documentElement.classList.add('dark')
            } else {
                document.documentElement.classList.remove('dark')
            }
        },

        async fetchHistory() {
            this.isLoading = true
            try {
                const response = await axios.get(`/api/history/${this.category}`)
                // Take last 30 days for the chart
                this.history = response.data.slice(0, 30).reverse()

                // Auto-set competitor price to latest if available
                if (this.history.length > 0) {
                    const latest = this.history[this.history.length - 1]
                    if (latest.COMPETITOR_PRICE) {
                        this.competitorPrice = latest.COMPETITOR_PRICE
                    }
                }
            } catch (err) {
                console.error("Failed to fetch history:", err)
                this.error = "Could not load historical data."
            } finally {
                this.isLoading = false
            }
        },

        async runSimulation() {
            // Don't set global loading here to keep UI snappy (optimistic UI?)
            // Actually, let's just do it
            try {
                const payload = {
                    category: this.category,
                    weather: this.weather,
                    our_price: this.ourPrice,
                    competitor_price: this.competitorPrice,
                    is_weekend: this.isWeekend
                }

                const response = await axios.post('/api/predict', payload)
                this.prediction = response.data

                // Trigger elasticity check after main prediction
                this.calculateElasticity()

            } catch (err) {
                console.error("Simulation failed:", err)
                this.error = "Simulation failed."
            }
        },

        async calculateElasticity() {
            // Generate 10 price points from -50% to +50% of base price
            const basePrice = this.ourPrice
            const points = []

            for (let i = 0.5; i <= 1.5; i += 0.1) {
                points.push(basePrice * i)
            }

            const curve = []

            // Run parallel requests (or serial if backend is weak, let's do parallel)
            const promises = points.map(price => {
                return axios.post('/api/predict', {
                    category: this.category,
                    weather: this.weather,
                    our_price: price,
                    competitor_price: this.competitorPrice,
                    is_weekend: this.isWeekend
                }).then(res => ({ price, revenue: res.data.predicted_revenue }))
            })

            const results = await Promise.all(promises)
            this.elasticityCurve = results.sort((a, b) => a.price - b.price)
        }
    }
})
