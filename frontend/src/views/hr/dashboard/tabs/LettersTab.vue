<template>
  <section class="letters-shell p-8">
    <HrLetters :context="{ showToast: ctx.showToast }" />
  </section>
</template>

<script>
import HrLetters from '../../letters/HrLetters.vue'

export default {
  name: 'HrDashboardLettersTab',
  components: {
    HrLetters,
  },
  inject: ['hrDashboardContext'],
  computed: {
    ctx() {
      return this.hrDashboardContext
    },
  },
}
</script>

<style scoped>
.letters-shell {
  background: #f6faf6;
  border-radius: 2rem;
  border: 1px solid rgba(73, 133, 40, 0.3);
  box-shadow: 0 25px 45px rgba(15, 23, 42, 0.08);
}
</style>
