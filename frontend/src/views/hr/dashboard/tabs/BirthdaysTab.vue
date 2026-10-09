<template>
  <section class="birthdays-shell p-6 lg:p-10 max-w-7xl mx-auto space-y-6">
    
    <header class="birthdays-header mb-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <span class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500"></span>
          </span>
          <span class="text-xs font-bold uppercase tracking-widest text-rose-600">Employee Wellness</span>
        </div>
        <h2 class="text-3xl font-bold tracking-tight text-slate-900">Celebrations & Birthdays</h2>
        <p class="text-slate-500 mt-2 text-sm leading-relaxed max-w-2xl">
          Track upcoming milestones and ensure every team member feels valued on their special day.
        </p>
      </div>
    </header>

    <div v-if="ctx.birthdayLoading" class="birthdays-card flex flex-col items-center justify-center py-24">
      <div class="animate-spin h-8 w-8 border-4 border-slate-100 border-t-rose-500 rounded-full mb-4"></div>
      <p class="text-xs font-bold uppercase tracking-wide text-slate-400">Syncing Calendar...</p>
    </div>

    <div v-else-if="ctx.birthdayError" class="birthdays-card text-center text-rose-600">
      {{ ctx.birthdayError }}
    </div>

    <div v-else-if="!allBirthdays.length" class="birthdays-card flex flex-col items-center justify-center py-24">
      <div class="w-20 h-20 bg-slate-100 rounded-full shadow-sm flex items-center justify-center mb-6 text-4xl grayscale opacity-50">
        🎂
      </div>
      <h3 class="text-xl font-semibold text-slate-900 mb-2">No birthdays found</h3>
      <p class="text-sm text-slate-500">There are no upcoming birthdays in the system.</p>
    </div>

    <div v-else class="birthdays-list space-y-6">
      <!-- Section 1: Birthdays Today -->
      <div class="birthdays-card overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-rose-50 to-pink-50">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="text-2xl">🎉</span>
              <div>
                <h3 class="text-lg font-bold text-slate-900">Birthdays Today</h3>
                <p class="text-sm text-rose-600">{{ birthdaysToday.length }} celebration{{ birthdaysToday.length !== 1 ? 's' : '' }} today</p>
              </div>
            </div>
            <div class="text-xs text-rose-600 bg-white px-3 py-1.5 rounded-lg border border-rose-200">
              Immediate Action Required
            </div>
          </div>
        </div>

        <div v-if="!birthdaysToday.length" class="px-6 py-12 text-center text-slate-500">
          <div class="w-16 h-16 bg-slate-100 rounded-full shadow-sm flex items-center justify-center mx-auto mb-4 text-3xl grayscale opacity-50">
            🎂
          </div>
          <p class="font-medium">No birthdays today</p>
          <p class="text-sm mt-1">Check back tomorrow or view upcoming birthdays below.</p>
        </div>

        <div v-else>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Employee</th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Team</th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Birthday</th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Turning</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="entry in birthdaysToday" :key="entry.employee_id" class="bg-rose-50/30 hover:bg-rose-50/50 transition-colors">
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-4">
                      <div 
                        class="h-12 w-12 rounded-full shadow-sm flex items-center justify-center text-white text-sm font-bold shrink-0 ring-2 ring-rose-200"
                        :style="{ backgroundColor: getAvatarColor(entry.employee_name) }"
                      >
                        {{ getInitials(entry.employee_name) }}
                      </div>
                      <div>
                        <div class="flex items-center gap-2">
                          <p class="font-semibold text-slate-900">{{ entry.employee_name }}</p>
                          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-rose-100 text-rose-800">
                            🎉 Today!
                          </span>
                        </div>
                        <p class="text-sm text-slate-500">Employee ID: {{ entry.employee_id }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 text-slate-700">
                      {{ entry.team_number ? 'Team ' + entry.team_number : 'General' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <div class="text-sm text-slate-900 font-medium">
                      {{ formatBirthdayDate(entry.next_birthday) }}
                    </div>
                    <div class="text-xs text-slate-500">
                      {{ formatBirthdayYear(entry.next_birthday) }}
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-sm font-semibold bg-blue-50 text-blue-700">
                      {{ entry.turning }} years
                    </span>
                  </td>
                  
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Section 2: Next 30 Days -->
      <div class="birthdays-card overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-yellow-50 to-amber-50">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="text-2xl">📅</span>
              <div>
                <h3 class="text-lg font-bold text-slate-900">Next 30 Days</h3>
                <p class="text-sm text-yellow-700">{{ birthdaysNext30.length }} upcoming birthday{{ birthdaysNext30.length !== 1 ? 's' : '' }}</p>
              </div>
            </div>
            <div class="text-xs text-yellow-700 bg-white px-3 py-1.5 rounded-lg border border-yellow-200">
              Plan Ahead
            </div>
          </div>
        </div>

        <div v-if="!birthdaysNext30.length" class="px-6 py-12 text-center text-slate-500">
          <div class="w-16 h-16 bg-slate-100 rounded-full shadow-sm flex items-center justify-center mx-auto mb-4 text-slate-300">
            <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
          </div>
          <p class="font-medium">No birthdays in the next 30 days</p>
          <p class="text-sm mt-1">Looks like a quiet month ahead.</p>
        </div>

        <div v-else>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Employee</th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Team</th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Birthday</th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Turning</th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Days Until</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="entry in birthdaysNext30" :key="entry.employee_id" class="hover:bg-slate-50 transition-colors">
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-4">
                      <div 
                        class="h-12 w-12 rounded-full shadow-sm flex items-center justify-center text-white text-sm font-bold shrink-0"
                        :style="{ backgroundColor: getAvatarColor(entry.employee_name) }"
                      >
                        {{ getInitials(entry.employee_name) }}
                      </div>
                      <div>
                        <p class="font-semibold text-slate-900">{{ entry.employee_name }}</p>
                        <p class="text-sm text-slate-500">Employee ID: {{ entry.employee_id }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 text-slate-700">
                      {{ entry.team_number ? 'Team ' + entry.team_number : 'General' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <div class="text-sm text-slate-900 font-medium">
                      {{ formatBirthdayDate(entry.next_birthday) }}
                    </div>
                    <div class="text-xs text-slate-500">
                      {{ formatBirthdayYear(entry.next_birthday) }}
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-sm font-semibold bg-blue-50 text-blue-700">
                      {{ entry.turning }} years
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <div class="text-sm font-medium text-yellow-600">
                      {{ formatDaysUntil(entry.days_until) }}
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Section 3: Next 90 Days -->
      <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="text-2xl">🗓️</span>
              <div>
                <h3 class="text-lg font-bold text-slate-900">Next 90 Days</h3>
                <p class="text-sm text-slate-600">{{ birthdaysNext90.length }} birthday{{ birthdaysNext90.length !== 1 ? 's' : '' }} in 3 months</p>
              </div>
            </div>
            <div class="text-xs text-slate-600 bg-white px-3 py-1.5 rounded-lg border">
              Quarterly Overview
            </div>
          </div>
        </div>

        <div v-if="!birthdaysNext90.length" class="px-6 py-12 text-center text-slate-500">
          <div class="w-16 h-16 bg-slate-100 rounded-full shadow-sm flex items-center justify-center mx-auto mb-4 text-slate-300">
            <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
          </div>
          <p class="font-medium">No birthdays in the next 3 months</p>
          <p class="text-sm mt-1">All birthdays are beyond the 90-day window.</p>
        </div>

        <div v-else>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Employee</th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Team</th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Birthday</th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Turning</th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider">Days Until</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="entry in birthdaysNext90" :key="entry.employee_id" class="hover:bg-slate-50 transition-colors">
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-4">
                      <div 
                        class="h-12 w-12 rounded-full shadow-sm flex items-center justify-center text-white text-sm font-bold shrink-0"
                        :style="{ backgroundColor: getAvatarColor(entry.employee_name) }"
                      >
                        {{ getInitials(entry.employee_name) }}
                      </div>
                      <div>
                        <p class="font-semibold text-slate-900">{{ entry.employee_name }}</p>
                        <p class="text-sm text-slate-500">Employee ID: {{ entry.employee_id }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 text-slate-700">
                      {{ entry.team_number ? 'Team ' + entry.team_number : 'General' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <div class="text-sm text-slate-900 font-medium">
                      {{ formatBirthdayDate(entry.next_birthday) }}
                    </div>
                    <div class="text-xs text-slate-500">
                      {{ formatBirthdayYear(entry.next_birthday) }}
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-sm font-semibold bg-blue-50 text-blue-700">
                      {{ entry.turning }} years
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <div class="text-sm font-medium text-slate-600">
                      {{ formatDaysUntil(entry.days_until) }}
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HrDashboardBirthdaysTab',
  inject: ['hrDashboardContext'],
  computed: {
    ctx() {
      return this.hrDashboardContext
    },
    allBirthdays() {
      const today = Array.isArray(this.ctx.birthdayTracker?.today) ? this.ctx.birthdayTracker.today : []
      const upcoming = Array.isArray(this.ctx.birthdayTracker?.upcoming) ? this.ctx.birthdayTracker.upcoming : []
      
      // Combine all birthdays and sort by next_birthday date in descending order (closest first)
      const combined = [...today, ...upcoming]
      
      return combined.sort((a, b) => {
        // Primary sort: days until birthday (ascending - closest first)
        if (a.days_until !== b.days_until) {
          return a.days_until - b.days_until
        }
        // Secondary sort: by name (alphabetical)
        return (a.employee_name || '').localeCompare(b.employee_name || '')
      })
    },
    birthdaysToday() {
      return this.allBirthdays.filter(entry => entry.days_until === 0)
    },
    birthdaysNext30() {
      return this.allBirthdays.filter(entry => entry.days_until > 0 && entry.days_until <= 30)
    },
    birthdaysNext90() {
      return this.allBirthdays.filter(entry => entry.days_until > 30 && entry.days_until <= 90)
    }
  },
  methods: {
    getInitials(name) {
      if (!name) return '??';
      return name
        .split(' ')
        .map(n => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase();
    },
    getAvatarColor(name) {
      const colors = ['#f43f5e', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#6366f1'];
      if (!name) return colors[0];
      let hash = 0;
      for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
      }
      return colors[Math.abs(hash) % colors.length];
    },
    formatBirthdayDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return '-'
      return date.toLocaleDateString(undefined, { 
        month: 'long', 
        day: 'numeric' 
      })
    },
    formatBirthdayYear(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return '-'
      return date.getFullYear().toString()
    },
    formatDaysUntil(days) {
      if (days === 0) return 'Today'
      if (days === 1) return 'Tomorrow'
      if (days < 0) return `${Math.abs(days)} days ago`
      return `In ${days} days`
    },
    getDaysUntilColor(days) {
      if (days === 0) return 'text-rose-600 font-bold'
      if (days <= 7) return 'text-yellow-600 font-semibold'
      return 'text-slate-600'
    }
  }
}
</script>

<style scoped>
.birthdays-shell {
  background: #f6faf6;
  border-radius: 2rem;
  padding: 2rem;
  border: 1px solid rgba(73, 133, 40, 0.2);
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
}
.birthdays-header {
  border-bottom: 1px solid rgba(73, 133, 40, 0.2);
}
.birthdays-card {
  border-radius: 1.5rem;
  border: 1px solid rgba(73, 133, 40, 0.2);
  background: #ffffff;
  padding: 1.5rem;
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
}
.birthdays-card + .birthdays-card {
  margin-top: 1rem;
}
.birthdays-list {
  padding: 0.5rem;
}
.birthdays-card table tr:hover {
  background: rgba(73, 133, 40, 0.05);
}
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
