<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
/* global defineOptions */
defineOptions({ name: 'LandingPageBenefits' })
import attendance from '@/assets/landing/benefit-attendance.png'
import payroll from '@/assets/landing/benefit-payroll.png'
import expenses from '@/assets/landing/benefit-selfservice.png'
import analytics from '@/assets/landing/benefit-analytics.png'

const benefits = [
  {
    title: 'Attendance Management',
    description: 'Streamline attendance tracking and simplify reporting.',
    image: attendance,
  },
  {
    title: 'Career Pathway Suggestions',
    description:
      'A person uses a stylus on a tablet to interact with a digital "Career Pathway" feature that creates a personalized plan with recommended courses based on inputs like skills and goals.',
    image: payroll,
  },
  {
    title: 'Ava Chatbot Service',
    description:
      'Ava is an intelligent dynamic chatbot that answers questions using a RAG system and continually learns from newly added content to improve its responses.',
    image: expenses,
  },
  {
    title: 'Dashboard & Analytics',
    description:
      'See trends at a glance with clear dashboards and actionable people insights.',
    image: analytics,
  },
]
</script>

<template>
  <section class="benefits-section py-[72px] sm:py-24 bg-white text-slate-900 relative overflow-hidden">
    <div class="container relative">
      <div class="text-center max-w-3xl mx-auto">
        <h2 class="text-4xl sm:text-5xl font-bold tracking-tight">Benefits of ALVEON</h2>
        <p class="mt-3 text-slate-600">
          Elevated digital functionality for the digitally driven generation.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
        <div
          v-for="benefit in benefits"
          :key="benefit.title"
          class="group relative overflow-hidden rounded-3xl bg-white border border-slate-200 shadow-sm hover:shadow-lg transition-all duration-300 flex flex-col h-full"
        >
          <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-b from-[#eaf1ff] via-transparent to-white pointer-events-none"></div>
          <div class="p-6 pb-4">
            <div
  class="w-full h-40 rounded-2xl overflow-hidden bg-slate-50 border border-slate-100 shadow-inner
         flex items-center justify-center"
>
  <img
    :src="benefit.image"
    :alt="benefit.title"
    class="max-w-full max-h-full object-contain transition-transform duration-300 group-hover:scale-105"
  />
</div>
          </div>
          <div class="px-6 pb-6 flex-1 flex flex-col gap-2 text-left">
            <div class="inline-flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-[#0f2738]/60">
              <span class="w-2 h-2 rounded-full bg-[#0f2738]/70 group-hover:bg-[#3b82f6] transition-colors"></span>
              Alveon Benefit
            </div>
            <h3 class="text-lg font-semibold text-[#0f2738] leading-tight">
              {{ benefit.title }}
            </h3>
            <p class="text-slate-600 text-sm leading-relaxed flex-1">
              {{ benefit.description }}
            </p>
            
          </div>
        </div>
      </div>

      <div class="pattern"></div>
    </div>
  </section>
</template>

<style scoped>
.container {
  max-width: 1800px;
  margin: 0 auto;
}

.benefits-section .pattern {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle at 20% 20%, rgba(15, 39, 56, 0.05), transparent 35%),
    radial-gradient(circle at 80% 0%, rgba(154, 199, 255, 0.08), transparent 35%),
    radial-gradient(circle at 50% 80%, rgba(15, 39, 56, 0.05), transparent 30%);
  pointer-events: none;
  z-index: 0;
}

.benefits-section > .container > * {
  position: relative;
  z-index: 1;
}

@media (max-width: 768px) {
  .container {
    padding: 0 0.75rem;
  }
}
</style>
