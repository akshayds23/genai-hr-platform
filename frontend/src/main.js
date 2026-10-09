import { createApp } from 'vue'
import { MotionPlugin } from '@vueuse/motion'
import Lenis from 'lenis'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import store from './store'
import './assets/tailwind.css'

// Preserve existing token handling for authenticated parts of the app
const storedToken = localStorage.getItem('authToken')
if (storedToken) {
  axios.defaults.headers.common['Authentication-Token'] = storedToken
}

// Configure Lenis smooth scrolling; only enabled on the landing (HomePage) route
let lenisInstance = null
let lenisRafId = null

function enableLenis() {
  // Avoid creating multiple instances and ensure we're in a browser environment
  if (lenisInstance || typeof window === 'undefined') return

  lenisInstance = new Lenis({
    duration: 1.2,
    smoothWheel: true,
    smoothTouch: false,
    // Easing function similar to the original landing implementation
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t))
  })

  const raf = (time) => {
    if (!lenisInstance) return
    lenisInstance.raf(time)
    lenisRafId = requestAnimationFrame(raf)
  }

  lenisRafId = requestAnimationFrame(raf)
}

function disableLenis() {
  if (lenisRafId) {
    cancelAnimationFrame(lenisRafId)
    lenisRafId = null
  }
  if (lenisInstance) {
    lenisInstance.destroy()
  }
  lenisInstance = null
  // Re-enable native scrolling
  if (typeof window !== 'undefined') {
    document.documentElement.style.scrollBehavior = 'auto'
  }
}

const app = createApp(App)
app.use(store)
app.use(router)
app.use(MotionPlugin)

// Mount the app first; then hook into router navigation to toggle Lenis
app.mount('#app')

if (typeof window !== 'undefined') {
  const applyLenisForRoute = (to) => {
    const isLandingRoute = to && (to.name === 'HomePage' || to.path === '/')
    if (isLandingRoute) {
      enableLenis()
    } else {
      disableLenis()
    }
  }

  // Apply on initial load
  applyLenisForRoute(router.currentRoute.value)
  // Apply on subsequent navigations
  router.afterEach((to) => {
    applyLenisForRoute(to)
  })
}
