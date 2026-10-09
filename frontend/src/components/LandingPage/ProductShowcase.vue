<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import appScreenshot from '@/assets/landing/app.png'

const appScreenshotRef = ref(null)
const scrollProgress = ref(0)

const handleScroll = () => {
  if (!appScreenshotRef.value) return

  const rect = appScreenshotRef.value.getBoundingClientRect()
  const scrollPercentage =
    1 - rect.bottom / (window.innerHeight + rect.height + 400)
  scrollProgress.value = Math.min(Math.max(scrollPercentage, 0), 1)
}

const normalizedProgress = computed(() => {
  return Math.min(scrollProgress.value / 0.6, 1)
})

const rotateXValue = computed(() => 15 - normalizedProgress.value * 15)
const opacityValue = computed(() => 0.35 + normalizedProgress.value * 0.65)
const scaleValue = computed(() => 0.95 + normalizedProgress.value * 0.05)
const translateYValue = computed(() => 50 - normalizedProgress.value * 50)

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div
    id="product"
    class="text-slate-900 bg-white py-[72px] sm:py-[132px] bg-gradient-to-b from-white to-[#eef3fb] overflow-hidden"
  >
    <div class="container">
      <h2
        class="text-6xl font-bold tracking-tighter text-center"
        v-motion
        :initial="{ opacity: 0 }"
        :enter="{ opacity: 1 }"
        :delay="300"
      >
        Intuitive Dashboard
      </h2>
      <div class="max-w-xl mx-auto">
        <p
          class="mt-5 text-base text-center text-slate-700"
          v-motion
          :initial="{ opacity: 0, y: 50 }"
          :enter="{ opacity: 1, y: 0 }"
          :delay="500"
        >
          Keep offers, onboarding, feedback, and payroll checks in one view. No
          more tabs, no more scattered docs - just a workspace that makes sense.
        </p>
      </div>
      <div
        ref="appScreenshotRef"
        class="mt-14 transform-gpu px-4 py-2 rounded-xl"
        :style="{
          opacity: opacityValue,
          transform: `
            perspective(1000px) 
            rotateX(${rotateXValue}deg)
            scale(${scaleValue})
            translateY(${translateYValue}px)
          `,
          transition: 'all 0.3s ease-out',
        }"
      >
        <img
          class="rounded-xl w-[95vw] mx-auto relative z-10"
          :src="appScreenshot"
          alt="Product dashboard"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.transform-gpu {
  will-change: transform, opacity;
  transform-style: preserve-3d;
  backface-visibility: hidden;
}

img {
  transition: transform 0.3s ease-out, opacity 0.3s ease-out;
  filter: drop-shadow(0 30px 40px rgba(15, 39, 56, 0.2));
}

.container {
  max-width: 1800px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .container {
    padding: 0 0.5rem;
  }
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.floating {
  animation: float 3s ease-in-out infinite;
}
</style>
