<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
/* global defineOptions */
defineOptions({ name: 'LandingPageFeatures' })
import Feature from './Feature.vue'
import check from '@/assets/landing/icons/check.svg'
import attendanceImg from '@/assets/landing/feature-attendance.jpg'

const features = [
  {
    emoji: '⚡',
    title: 'Workflow automation',
    description:
      'Onboarding, leave, approvals, and letters in one seamless flow so managers stay focused on people, not paperwork.',
  },
  {
    emoji: '📊',
    title: 'Role-smart dashboards',
    description:
      'HR, managers, and employees each see the insights and actions that matter to them with clear guardrails.',
  },
  {
    emoji: '🤝',
    title: 'Progress tracking',
    description:
      'Stay ahead of engagement and performance trends with live analytics and simple summaries anyone can read.',
  },
]

const timeAttendanceBullets = [
  'Enhanced employee accountability',
  'Accurate payroll processing',
  'Flexible, instantaneous attendance recording',
  'Attendance policies that are transparent and consistent',
]

</script>

<template>
  <div id="features" class="bg-[#f5f7fb] text-slate-900 py-[72px] sm:py-24">
    <div class="container relative overflow-hidden">
      <h2
        class="text-5xl font-bold tracking-tighter text-center sm:text-4xl"
        v-motion
        :visible-once="{
          opacity: 1,
          y: 0,
        }"
        :focused="{
          scale: 1.1,
        }"
        :delay="200"
        :duration="500"
      >
        Supercharge your people ops
      </h2>
      <div class="max-w-xl mx-auto">
        <p
          class="mt-5 text-xl text-center text-slate-700"
          v-motion
          :visible-once="{
            opacity: 1,
            y: 0,
          }"
          :focused="{
            scale: 1.1,
          }"
          :delay="200"
          :duration="500"
        >
          Designed to feel modern, fast, and friendly so you can ship HR
          improvements without slowing down.
        </p>
      </div>
      <div
        class="absolute -rotate-[50deg] w-[250px] h-[400px] left-16 bottom-0 bg-[#cfe4ff7a] blur-[75px] rounded-[400px] pointer-events-none"
      ></div>
      <div
        class="absolute rotate-[50deg] w-[250px] h-[400px] right-16 bottom-0 bg-[#cfe4ff7a] blur-[75px] rounded-[400px] pointer-events-none"
      ></div>
      <div class="flex flex-col gap-6 mt-16 sm:flex-row px-10 z-10 static">
        <Feature
          v-for="feature in features"
          :key="feature.title"
          :emoji="feature.emoji"
          :title="feature.title"
          :description="feature.description"
        />
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center mt-20 px-6 md:px-12 time-attendance">
        <div class="space-y-4">
          <p class="text-xs uppercase tracking-[0.25em] text-[#0f2738]/70">Time and Attendance</p>
          <h3 class="text-3xl md:text-4xl font-bold tracking-tight text-[#0f2738]">
            Time and attendance that stays accurate and effortless
          </h3>
          <p class="text-slate-700 leading-relaxed">
            Allow time for greatness and unlock higher productivity through our integrated time and attendance
            management. Create a seamless onboarding experience and build delightful employee journeys from day one.
          </p>
          <ul class="space-y-3">
            <li v-for="item in timeAttendanceBullets" :key="item" class="flex items-start gap-3 text-slate-700">
              <img :src="check" alt="check" class="w-5 h-5 mt-0.5" />
              <span>{{ item }}</span>
            </li>
          </ul>
        </div>
        <div class="relative group">
          <div class="absolute -left-6 -top-6 w-24 h-24 bg-[#9ac7ff]/30 rounded-full blur-3xl transition-all duration-500 group-hover:scale-125"></div>
          <div class="absolute -right-4 -bottom-4 w-32 h-32 bg-[#0f2738]/10 rounded-full blur-3xl transition-all duration-500 group-hover:scale-125"></div>
          <div class="relative rounded-3xl overflow-hidden shadow-lg border border-slate-200 bg-white transition-all duration-500 group-hover:shadow-2xl group-hover:scale-105 group-hover:-translate-y-2">
            <img
              :src="attendanceImg"
              alt="Time and attendance dashboard"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            />
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1800px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .container {
    padding: 0 0.5rem;
  }
}

.time-attendance {
  background: white;
  border-radius: 28px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(15, 39, 56, 0.06);
}

</style>
