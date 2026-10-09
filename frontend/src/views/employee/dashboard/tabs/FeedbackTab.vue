<template>
  <section
    class="rounded-[28px] border border-[#498528] bg-white/80 
           shadow-[0_32px_80px_rgba(15,23,42,0.18)] backdrop-blur-xl p-4"
  >
    <AnonymousFeedback />
  </section>
</template>

<script>
import AnonymousFeedback from '@/components/AnonymousFeedback.vue'

export default {
  name: 'EmployeeFeedbackTab',
  components: { AnonymousFeedback },
}
</script>
