<script setup>
import hero from '@/assets/landing/hr-simplified.jpg'
import check from '@/assets/landing/icons/check.svg'

const bullets = [
  'Easy access to documents and information.',
  'An employee database that scales.',
  'Smart HR workflows.',
  'Automation of HR processes.',
]
</script>

<template>
  <section class="hr-simplified bg-white text-slate-900 py-[72px] sm:py-24">
    <div class="container grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
      <div class="relative order-2 lg:order-1">
        <div class="bg-[#eaf1ff] rounded-3xl p-4 shadow-sm">
          <img
            :src="hero"
            alt="HR management simplified"
            class="rounded-2xl w-full object-cover"
          />
        </div>
        <div class="absolute -left-6 -top-6 w-16 h-16 bg-[#0f2738] rounded-full opacity-10"></div>
        <div class="absolute -right-4 -bottom-4 w-12 h-12 bg-[#9ac7ff] rounded-full opacity-30"></div>
      </div>

      <div class="space-y-4 order-1 lg:order-2">
        <p class="text-sm uppercase tracking-[0.3em] text-slate-500">ALVEON Platform</p>
        <h2 class="text-4xl sm:text-5xl font-bold tracking-tight">
          HR management simplified
        </h2>
        <p class="text-base sm:text-lg text-slate-600 max-w-xl">
          Adapt to new realities, work faster and smarter. Give your organization a strong,
          flexible HR backbone that scales with every team.
        </p>

        <ul class="space-y-3">
          <li
            v-for="item in bullets"
            :key="item"
            class="flex items-start gap-3 text-slate-700"
          >
            <img :src="check" alt="check" class="w-5 h-5 mt-0.5" />
            <span>{{ item }}</span>
          </li>
        </ul>
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
    padding: 0 0.75rem;
  }
}
</style>
