<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
/* global defineOptions */
defineOptions({ name: 'LandingPageTestimonials' })

const baseTestimonials = [
  { name: 'Aarav Verma', initials: 'AV', bg: 'bg-indigo-600', role: 'People Ops Lead', quote: 'ALVEON keeps our onboarding and approvals in one smooth flow with no chasing emails.' },
  { name: 'Ishita Rao', initials: 'IR', bg: 'bg-emerald-600', role: 'HR Analyst', quote: 'Dashboards match how we work. Managers regularly check their numbers now.' },
  { name: 'Rohan Mehta', initials: 'RM', bg: 'bg-blue-600', role: 'Payroll Manager', quote: 'Payroll and attendance stay in sync. Fast closures with fewer queries.' },
  { name: 'Neha Kulkarni', initials: 'NK', bg: 'bg-purple-600', role: 'Talent Partner', quote: 'Offers and letters feel polished. Candidates notice the difference.' },
  { name: 'Vikram Singh', initials: 'VS', bg: 'bg-amber-600', role: 'Engineering Manager', quote: 'Approvals are predictable and fast. My team spends time building, not waiting.' },
  { name: 'Kriti Desai', initials: 'KD', bg: 'bg-teal-600', role: 'HRBP', quote: 'The workflows are humane and fast. Feedback loops are finally easy.' },
  { name: 'Arjun Iyer', initials: 'AI', bg: 'bg-cyan-600', role: 'COO', quote: 'Live people metrics without spreadsheets. It changes how we plan.' },
  { name: 'Sanya Kapoor', initials: 'SK', bg: 'bg-rose-600', role: 'L&D Lead', quote: 'Templates and automation lead to less admin and more coaching.' },
]

const marqueeItems = [...baseTestimonials, ...baseTestimonials] // duplicate for seamless loop
</script>

<template>
  <section id="testimonials" class="bg-gradient-to-t from-white to-[#eef2fb] py-[72px] sm:py-24 text-slate-900 overflow-hidden">
    <div class="container">
      <div class="text-center mb-6">
        <p class="text-sm font-semibold tracking-[0.3em] text-slate-500 uppercase">Powering modern teams</p>
        <h2 class="text-4xl sm:text-5xl font-bold mt-2">Feedback from our users</h2>
      </div>

      <div class="relative">
        <div class="marquee-track">
          <div class="marquee-inner">
            <div
              v-for="(item, idx) in marqueeItems"
              :key="idx"
              class="testimonial-chip"
            >
              <div
                class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-white text-sm shrink-0 shadow-sm"
                :class="item.bg"
              >
                {{ item.initials }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-[#0f2738] truncate">{{ item.name }}</p>
                <p class="text-xs text-slate-500 truncate">{{ item.role }}</p>
                <p class="text-sm text-slate-700 mt-1 line-clamp-2">{{ item.quote }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
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

.marquee-track {
  position: relative;
  overflow: hidden;
  mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
}

.marquee-inner {
  display: flex;
  gap: 16px;
  width: max-content;
  animation: marquee 25s linear infinite;
}

.testimonial-chip {
  display: flex;
  gap: 12px;
  align-items: center;
  min-width: 320px;
  max-width: 360px;
  padding: 12px 14px;
  background: white;
  border-radius: 18px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 12px 28px rgba(15, 39, 56, 0.08);
}

@keyframes marquee {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-50%);
  }
}
</style>
