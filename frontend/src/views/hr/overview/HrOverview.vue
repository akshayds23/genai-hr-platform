<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-3xl font-bold text-slate-900">Analytics Overview</h2>
      <p class="text-sm text-slate-600 mt-1">Recruitment and hiring metrics</p>
    </div>

    <div class="grid gap-6 sm:grid-cols-2">
      <article
        v-for="(item, index) in stats"
        :key="item.label"
        :class="[
          'analytics-card',
          'rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105',
          getCardAccent(index)
        ]"
      >
        <div class="flex items-center justify-center gap-2">
          <div>
            <h1 class="text-black/80 text-sm font-medium">{{ item.label }}</h1>
            <h3 class="text-black 8xl font-bold mt-1">{{ item.value }}</h3>
            <p class="text-black/70 text-xs mt-1">{{ item.subtitle }}</p>
          </div>
          
        </div>
      </article>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HrOverview',
  props: {
    context: {
      type: Object,
      default: () => ({}),
    },
  },
  computed: {
    stats() {
      const analytics = this.context?.analytics || {}
      const matchedCount =
        this.context?.matchedCandidatesCount ??
        this.context?.matchedCandidates?.length ??
        0
      const averageExperienceRaw = Number(analytics.average_experience || 0)
      const roundedAverage =
        averageExperienceRaw > 0
          ? Math.max(1, Math.round(averageExperienceRaw))
          : 0

      return [
        {
          
          label: 'Total Candidates',
          value: analytics.total_candidates || 0,
          subtitle: 'Profiles processed',
        },
        {
          
          label: 'Job Descriptions',
          value: this.context?.jobDescriptions?.length || 0,
          subtitle: 'Active openings',
        },
        {
          
        label: 'Avg Experience',
        value: roundedAverage ? `${roundedAverage} yrs` : '0 yrs',
        subtitle: 'Candidate experience',
      },
        {
          
          label: 'Matched Candidates',
          value: matchedCount,
          subtitle: 'Awaiting review',
        },
      ]
    },
  },
  methods: {
    getCardAccent(index) {
      const accents = [
        'border border-[#dcefdc]',
        'border border-[#d8f0d1]',
        'border border-[#dfeeed]',
        'border border-[#e5f4d5]',
      ]
      return accents[index % accents.length]
    },
  },
}
</script>

<style scoped>
.analytics-card {
  background: #ffffff;
  color: #0f172a;
  border-radius: 1.5rem;
}
.analytics-card h1 {
  color: #0f172a;
}
.analytics-card h3 {
  font-size: 2rem;
}
.analytics-card p {
  color: #4b5563;
}
</style>
