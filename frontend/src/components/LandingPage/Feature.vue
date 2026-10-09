<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
/* global defineOptions, defineProps */
defineOptions({ name: 'LandingPageFeature' })
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Props for the Feature component
defineProps(['emoji', 'title', 'description'])

// Reactive state for mouse position and mask
const border = ref(null)
const offsetX = ref(-100)
const offsetY = ref(-100)

const maskImage = computed(
  () =>
    `radial-gradient(100px 100px at ${offsetX.value}px ${offsetY.value}px, black, transparent)`
)

const updateMousePosition = (e) => {
  const borderRect = border.value.getBoundingClientRect()
  offsetX.value = e.clientX - borderRect.x
  offsetY.value = e.clientY - borderRect.y
}

// Lifecycle hooks
onMounted(() => {
  window.addEventListener('mousemove', updateMousePosition)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', updateMousePosition)
})
</script>

<template>
  <div
    class="relative px-5 py-10 text-center border border-slate-200 rounded-xl sm:flex-1 bg-white shadow-sm cyber-card overflow-hidden"
  >
    <div
      v-motion
      :initial="{
        opacity: 0,
        y: 50,
      }"
      :visible-once="{
        opacity: 1,
        y: 0,
      }"
      :leave="{
        y: -100,
        opacity: 0,
        transition: {
          duration: 1000,
        },
      }"
      :focused="{
        scale: 1.1,
      }"
      :delay="200"
      :duration="600"
      class="absolute inset-[-1px] border-2 border-[#9ac7ff] rounded-xl neon-border"
      ref="border"
      :style="{ WebkitMaskImage: maskImage, maskImage: maskImage }"
    ></div>
    <h1
      v-motion
      :initial="{
        opacity: 0,
        y: 50,
      }"
      :visible-once="{
        opacity: 1,
        y: 0,
      }"
      :leave="{
        y: -100,
        opacity: 0,
        transition: {
          duration: 1000,
        },
      }"
      :focused="{
        scale: 1.1,
      }"
      :delay="200"
      :duration="600"
      class="text-5xl text-[#0f2738]"
    >
      {{ emoji }}
    </h1>
    <h3
      v-motion
      :initial="{
        opacity: 0,
        y: 50,
      }"
      :visible-once="{
        opacity: 1,
        y: 0,
      }"
      :leave="{
        y: -100,
        opacity: 0,
        transition: {
          duration: 1000,
        },
      }"
      :focused="{
        scale: 1.1,
      }"
      :delay="200"
      :duration="600"
      class="mt-6 font-bold text-slate-900"
    >
      {{ title }}
    </h3>
    <p
      v-motion
      :initial="{
        opacity: 0,
        y: 50,
      }"
      :visible-once="{
        opacity: 1,
        y: 0,
      }"
      :leave="{
        y: -100,
        opacity: 0,
        transition: {
          duration: 1000,
        },
      }"
      :focused="{
        scale: 1.1,
      }"
      :delay="200"
      :duration="600"
      class="mt-2 text-slate-600"
    >
      {{ description }}
    </p>
  </div>
</template>

<style scoped>
.cyber-card::before,
.cyber-card::after {
  content: '';
  position: absolute;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(58, 129, 246, 0.15), transparent 60%);
  transition: transform 0.4s ease, opacity 0.4s ease;
}

.cyber-card::before {
  top: -40px;
  left: -40px;
}

.cyber-card::after {
  bottom: -50px;
  right: -30px;
}

.cyber-card:hover::before {
  transform: translateY(12px);
  opacity: 0.9;
}

.cyber-card:hover::after {
  transform: translateY(-12px);
  opacity: 0.9;
}

.neon-border {
  box-shadow: 0 0 22px rgba(154, 199, 255, 0.35);
}
</style>
