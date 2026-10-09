<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

import Features from './LandingPage/Features.vue'
import ProductShowcase from './LandingPage/ProductShowcase.vue'
import Testimonials from './LandingPage/Testimonials.vue'
// import FAQs from './LandingPage/FAQs.vue'
import LandingFooter from './LandingPage/Footer.vue'
import Benefits from './LandingPage/Benefits.vue'
import HRSimplified from './LandingPage/HRSimplified.vue'

import logo from '@/assets/alveon-logo.svg'

const isMenuOpen = ref(false)

const sections = [
  { name: 'Features', id: 'features' },
  { name: 'Product', id: 'product' },
  { name: 'Testimonials', id: 'testimonials' },
  { name: 'FAQs', id: 'faqs' },
]

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const handleScroll = (sectionId) => {
  const element = document.getElementById(sectionId)
  if (element) {
    const offset = element.offsetTop - 20
    window.scrollTo({
      top: offset,
      behavior: 'smooth',
    })
  }
  isMenuOpen.value = false
}
</script>

<template>
  <main class="max-w-full mx-auto bg-slate-50 text-slate-900">
    <div class="container">
      <div class="bg-white/95 backdrop-blur-md sticky top-0 z-40 border-b border-slate-200 shadow-sm">
        <div class="px-4">
          <div class="flex items-center justify-between py-3">
            <div class="relative flex items-center gap-3">
              <div class="bg-slate-100 rounded-full p-3 shadow-sm ring-1 ring-[#0f2738]/10">
                <img
                  :src="logo"
                  alt="ALVEON logo"
                  class="w-14 h-14"
                />
              </div>
              <div class="text-left hidden sm:block">
                <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Alveon</p>
              </div>
            </div>
            <nav class="items-center hidden gap-4 sm:flex">
              <button
                v-for="section in sections"
                :key="section.id"
                @click="handleScroll(section.id)"
                class="nav-link"
              >
                {{ section.name }}
              </button>
              <RouterLink to="/login">
                <button
                  class="nav-cta primary"
                >
                  Log In
                </button>
              </RouterLink>
              
            </nav>
            <div class="flex sm:hidden">
              <button
                @click="toggleMenu"
                class="text-[#0f2738] text-xl font-semibold"
                aria-label="Toggle Menu"
              >
                Menu
              </button>
            </div>
          </div>
        </div>

        <transition
          name="mobile-menu"
          enter-active-class="mobile-menu-enter-active"
          leave-active-class="mobile-menu-leave-active"
          enter-from-class="mobile-menu-enter-from"
          leave-to-class="mobile-menu-leave-to"
        >
          <div
            v-if="isMenuOpen"
            class="absolute top-0 left-0 z-50 w-full h-screen bg-white/95 text-slate-800 transition-transform duration-500 ease-in-out backdrop-blur-xl border-b border-slate-200"
          >
            <div class="flex justify-between p-4">
              <img
                :src="logo"
                alt="Logo"
                class="w-12 h-12"
              />
              <button
                @click="toggleMenu"
                class="text-slate-800 focus:outline-none font-semibold"
                aria-label="Close Menu"
              >
                Close
              </button>
            </div>
            <nav class="flex flex-col items-center mt-10 gap-6">
              <button
                v-for="section in sections"
                :key="section.id"
                @click="handleScroll(section.id)"
                class="text-lg text-slate-800"
              >
                {{ section.name }}
              </button>
              <RouterLink to="/login">
                <button
                  class="px-4 py-2 font-medium text-white bg-[#0f2738] rounded-lg w-40 shadow"
                >
                  Log In
                </button>
              </RouterLink>
              
            </nav>
          </div>
        </transition>
      </div>

      <section class="hero-new relative overflow-hidden py-[96px] sm:py-[120px]">
        <div class="hero-grid-overlay"></div>
        <div class="grid-bg"></div>
        <div class="container relative">
          <div class="hero-grid mx-auto">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div class="space-y-8">
                <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-slate-200 shadow-sm text-xs text-blue-700 font-bold">
                  <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                  </span>
                  HR Management System v3.0 Live
                </div>
                <h1 class="text-4xl sm:text-6xl font-black leading-[1.08] text-slate-900">
                  The Future of<br />
                  <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600">Human Resource Management</span>
                </h1>
                <p class="text-lg text-slate-700 max-w-2xl">
                  Orchestrate your entire organization from a single, secure command center. AI-driven analytics meets intuitive people management.
                </p>
                <div class="flex flex-wrap gap-4">
                  
                  <RouterLink to="/login">
                    <button
                      class="px-6 sm:px-8 py-3 sm:py-4 bg-orange-500 text-white font-semibold rounded-xl 
                            border border-orange-600 hover:bg-orange-600 hover:border-orange-700 
                            transition-colors shadow-sm"
                    >
                      Get started
                    </button>
                  </RouterLink>

                </div>
               
              </div>

              <div class="relative flex items-center justify-center">
                <div class="card-chart">
                  <div class="flex justify-between items-center border-b border-slate-100 pb-3 mb-4">
                    <div class="flex gap-2">
                      <div class="w-2.5 h-2.5 rounded-full bg-red-400"></div>
                      <div class="w-2.5 h-2.5 rounded-full bg-yellow-400"></div>
                      <div class="w-2.5 h-2.5 rounded-full bg-green-400"></div>
                    </div>
                    <div class="text-[11px] font-mono text-slate-400">System Status: Optimal</div>
                  </div>
                  <div class="flex items-end gap-2 h-52 px-2">
                    <div v-for="(h, idx) in [35,70,50,85,60,95,75]" :key="idx" class="flex-1 rounded-t-md bg-gradient-to-t from-blue-500/20 to-blue-600" :style="{ height: h + '%' }"></div>
                  </div>
                  <div class="grid grid-cols-2 gap-4 mt-5">
                    <div class="stat-box">
                      <p class="text-xs text-slate-500 mb-1">Active Employees</p>
                      <p class="text-xl font-bold text-slate-900">1,248</p>
                    </div>
                    <div class="stat-box">
                      <p class="text-xs text-slate-500 mb-1">Retention Rate</p>
                      <p class="text-xl font-bold text-emerald-600">96.4%</p>
                    </div>
                  </div>
                </div>
                
              </div>

            </div>
          </div>
        </div>
      </section>
      <div class="py-[20px] bg-white shadow-inner">
        <div class="container trusted-by overflow-hidden"></div>
      </div>
      <Benefits />
      <Features />
      <ProductShowcase />
      <HRSimplified />
      <Testimonials />
      <FAQs />
      <div
        id="call-to-action"
        class="call-to-action py-[72px] text-slate-900 text-center bg-gradient-to-b from-white to-[#e8f2ff]"
      >
        <div class="container">
          <h2 class="text-4xl font-bold">
            Ready to give your team the HR they deserve?
          </h2>
          <p class="mt-4 text-lg text-slate-700 max-w-3xl mx-auto">
            Launch faster hiring, friendlier onboarding, and clearer feedback
            loops from day one.
          </p>

          <div class="mt-8">
            
          </div>
        </div>
      </div>
      <LandingFooter />
    </div>
  </main>
</template>

<style scoped>
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: transform 0.3s ease;
}
.mobile-menu-enter-from,
.mobile-menu-leave-to {
  transform: translateX(100%);
}

.container {
  max-width: 1800px;
  margin: 0 auto;
}

.hero-content h1 {
  font-family: 'Golos Text', 'Inter', 'Instrument Serif', sans-serif;
  letter-spacing: -4px;
}

.nav-link {
  padding: 10px 14px;
  border-radius: 999px;
  color: #0f2738;
  background: transparent;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.nav-link:hover {
  border-color: rgba(15, 39, 56, 0.12);
  box-shadow: 0 4px 14px rgba(15, 39, 56, 0.08);
  transform: translateY(-2px);
}

.nav-cta {
  padding: 10px 16px;
  border-radius: 14px;
  font-weight: 700;
  transition: all 0.2s ease;
  border: 1px solid #0f2738;
}

.nav-cta.primary {
  background: linear-gradient(120deg, #0f2738, #1f4872);
  color: white;
  box-shadow: 0 8px 20px rgba(15, 39, 56, 0.25);
}

.nav-cta.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 26px rgba(15, 39, 56, 0.35);
}

.nav-cta.ghost {
  background: white;
  color: #0f2738;
}

.nav-cta.ghost:hover {
  background: #f3f6fb;
  transform: translateY(-2px);
}

.hero-new {
  background: linear-gradient(180deg, #f9fbff 0%, #eef3ff 40%, #e8f0ff 100%);
}

.hero-grid {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 0 1.5rem;
}

.hero-grid-overlay,
.grid-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.hero-grid-overlay {
  opacity: 0.05;
  background-image: linear-gradient(#0f2738 1px, transparent 1px), linear-gradient(90deg, #0f2738 1px, transparent 1px);
  background-size: 70px 70px;
  z-index: 0;
}

.grid-bg {
  background: radial-gradient(circle at 20% 20%, rgba(147, 197, 253, 0.25), transparent 35%),
    radial-gradient(circle at 80% 40%, rgba(165, 180, 252, 0.25), transparent 35%),
    radial-gradient(circle at 40% 80%, rgba(226, 232, 240, 0.2), transparent 35%);
  z-index: 0;
}

.badge-pill {
  box-shadow: 0 10px 30px rgba(15, 39, 56, 0.08);
}

.hero-cta {
  background: linear-gradient(135deg, #0f2738 0%, #1f4c7a 60%, #0f2738 100%);
  border: 1.5px solid #0f2738;
  box-shadow: 0 10px 24px rgba(15, 39, 56, 0.25);
  min-width: 170px;
}

.hero-cta:hover {
  box-shadow: 0 16px 34px rgba(15, 39, 56, 0.32);
}

.call-to-action {
  background: linear-gradient(to bottom, #ffffff 0%, #e8f2ff 100%);
}

.ellipse {
  background: radial-gradient(closest-side, #f2f6fb 82%, #b8d7ff);
}

.trusted-by h2 {
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  font-weight: 400;
  color: #0f2738;
  opacity: 0.8;
}

.images {
  margin-top: 32px;
  padding-bottom: 58px;
  position: relative;
}

.trusted-logo {
  width: 180px;
  opacity: 0.95;
  filter: grayscale(100%);
  transition: all 0.4s ease;
  padding: 12px 18px;
  border-radius: 14px;
  background: #f6f9ff;
  border: 1px solid #d7e3f5;
}

.trusted-logo:hover {
  filter: grayscale(0%);
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 10px 24px rgba(15, 39, 56, 0.18);
  opacity: 1;
}


.card-chart {
  position: relative;
  z-index: 1;
  backdrop-filter: blur(12px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(15, 39, 56, 0.05);
  border-radius: 24px;
  padding: 22px;
  box-shadow: 0 24px 48px rgba(15, 39, 56, 0.1);
  background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(233, 242, 255, 0.9));
  width: 100%;
}

.mini-card {
  background: white;
  border-radius: 16px;
  padding: 12px;
  border: 1px solid #e5edfb;
  box-shadow: 0 10px 24px rgba(15, 39, 56, 0.06);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.stat-chip {
  padding: 8px 12px;
  background: white;
  border-radius: 999px;
  font-size: 12px;
  color: #0f2738;
  border: 1px solid #dbe7ff;
  box-shadow: 0 8px 18px rgba(15, 39, 56, 0.08);
}

@media (max-width: 768px) {
  .images img {
    width: 80px;
  }

  .images::before {
    left: -5%;
  }

  .images::after {
    right: -5%;
  }
}
</style>





