<template>
  <section class="space-y-6">
    <section
      class="hero-panel relative overflow-hidden rounded-[32px]"
    >
      <div class="grid gap-8 lg:grid-cols-2 lg:items-center p-8 lg:p-10">
        <div class="space-y-7">
          <p class="text-xs font-semibold uppercase tracking-[0.45em] text-slate-500">People operations</p>
          <h2 class="text-3xl font-semibold leading-tight text-slate-900 drop-sm">HR command center</h2>
          <p class="text-sm text-slate-700">{{ commandCenterSubtitle }}</p>
          <div
            class="hero-illustration relative overflow-hidden rounded-[28px] border border-[#498528]/60 shadow-[0_25px_60px_rgba(15,23,42,0.1)] transition hover:scale-[1.01]"
          >
            <img src="@/assets/Hr.svg" alt="HR illustration" class="block w-full object-cover" />
          </div>
        </div>

        <div class="space-y-6">
          <div class="space-y-3">
            <div class="flex items-center justify-between gap-3">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">Quick actions</p>
                <p class="text-sm font-semibold text-slate-900">Sync people insights</p>
              </div>
              <span class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">{{ lastSyncNote }}</span>
            </div>
            <div class="flex flex-wrap gap-3 pt-2">
              <button class="hero-cta-btn hero-cta-sync" type="button" @click="refreshDirectory">
                <ArrowPathIcon class="h-4 w-4" />
                Sync directory
              </button>
              <button class="hero-cta-btn hero-cta-add" type="button" @click="goToUserDirectory">
                <PlusIcon class="h-4 w-4" />
                Add user
              </button>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <article
              v-for="stat in heroStats"
              :key="stat.label"
              class="hero-stat-card"
              :class="`hero-stat-${stat.intent}`"
            >
              <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-500">{{ stat.label }}</p>
              <p class="text-2xl font-semibold text-slate-900 mt-3 break-words">{{ stat.value }}</p>
              <p class="text-xs text-slate-600 mt-1">{{ stat.context }}</p>
            </article>
          </div>
        </div>
      </div>
    </section>

    <div class="grid gap-6 lg:grid-cols-3">
      <article class="card-shell overview-card tinted-surface" aria-label="Analytics performance overview panel">
        <HrOverview :context="ctx.overviewContext" />
      </article>

      <article
        class="card-shell snapshot-card pulse-card"
        aria-label="Pulse board live metrics"
      >
        <div class="flex flex-col items-center justify-center">
          <h3 class="text-2xl font-semibold text-slate-900">Pulse board</h3>
          <p class="text-xs text-slate-500 mt-1">Live indicators from people operations</p>
        </div>

        <dl class="mt-6 space-y-4 flex flex-col items-center justify-center">
          <div
            v-for="metric in snapshotMetrics"
            :key="metric.label"
            class="metric-pill group transition-colors cursor-default w-full max-w-[260px]"
          >
            <dt class="text-sm font-semibold text-slate-700">{{ metric.label }}</dt>
            <dd class="text-2xl font-bold text-slate-900 mt-1">{{ metric.value }}</dd>
            
          </div>
        </dl>
      </article>
    </div>

    <article class="card-shell query-console tinted-surface" aria-label="Talent intelligence console">
      <header class="flex flex-wrap items-center justify-between gap-4 border-b border-[#498528]/70 pb-6 mb-6">
        <div>
          <h2 class="text-2xl font-semibold text-slate-900">Talent intelligence workspace</h2>
        </div>
        <button class="secondary-btn" type="button" @click="ctx.resetSearch">Reset filters</button>
      </header>

      <form class="grid gap-4 md:grid-cols-2 xl:grid-cols-3" @submit.prevent="ctx.onSearchSubmit">
        <label class="filter-field">
          <span>Name or email :</span>
          <input v-model="ctx.filters.query" class="filter-input" type="search" placeholder="Search people" />
        </label>
        <label class="filter-field">
          <span>Employee ID :</span>
          <input v-model="ctx.filters.employee_id" class="filter-input" type="text" placeholder="ID" />
        </label>
        <label class="filter-field">
          <span>Department :</span>
          <select v-model="ctx.filters.department" class="filter-input cursor-pointer">
            <option value="">All departments :</option>
            <option v-for="dept in ctx.departments" :key="dept" :value="dept">{{ dept }}</option>
          </select>
        </label>
        <label class="filter-field">
          <span>Role :</span>
          <input v-model="ctx.filters.role" class="filter-input" type="text" placeholder="Role" />
        </label>
        <label class="filter-field">
          <span>Status :</span>
          <select v-model="ctx.filters.status" class="filter-input cursor-pointer">
            <option value="">All</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="on_leave">On leave</option>
            <option value="offboarded">Offboarded</option>
          </select>
        </label>
        <div class="flex items-end">
          <button
            class="primary-btn w-full"
            type="submit"
            :disabled="ctx.loadingResults"
          >
            {{ ctx.loadingResults ? 'Searching…' : 'Run search' }}
          </button>
        </div>
      </form>

      <div class="mt-8 rounded-2xl overflow-hidden themed-panel">
        <div class="flex flex-wrap items-center justify-between gap-2 border-b border-[#498528]/80 bg-[#ecfef2] px-5 py-3">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-[#1f4c1c]">Search results</p>
            <p class="text-sm font-semibold text-[#1f4c1c]">{{ ctx.showingLabel }}</p>
          </div>
          <span class="live-badge">
            <span class="relative flex h-2 w-2">
              <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
            </span>
            {{ ctx.loadingResults ? 'Refreshing dataset…' : 'Live data' }}
          </span>
        </div>
        <div v-if="ctx.loadingResults" class="p-8 text-center text-[#2f4c1c]">Refreshing search results…</div>
        <div v-else-if="searchPreview.length" class="overflow-x-auto">
          <table class="results-table">
            <thead>
              <tr class="results-header">
                <th scope="col">Person</th>
                <th scope="col">Department</th>
                <th scope="col">Role</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="person in searchPreview"
                :key="person.id || person.employee_id || person.email"
                class="group results-row"
              >
                <td>
                  <div class="font-semibold text-slate-900 group-hover:text-blue-700 transition-colors">
                    {{ personName(person) }}
                  </div>
                  <p class="text-xs text-slate-500">{{ person.email || '—' }}</p>
                </td>
                <td class="text-sm text-slate-600">{{ person.department || 'Unassigned' }}</td>
                <td class="text-sm text-slate-600">{{ formatStatus(person.employment_role || person.role) }}</td>
                <td>
                  <span
                    :class="[
                      'inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold border',
                      statusClass(person.status),
                    ]"
                  >
                    {{ formatStatus(person.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="pagination-row flex items-center justify-between">
            <span class="text-xs font-semibold uppercase tracking-[0.3em] text-[#1f4c1c]">Page {{ ctx.page || 1 }} of {{ ctx.totalPages || 1 }}</span>
            <div class="flex items-center gap-2">
              <button
                class="themed-pill"
                type="button"
                :disabled="(ctx.page || 1) <= 1 || ctx.loadingResults"
                @click="ctx.prevPage"
              >
                Previous
              </button>
              <button
                class="themed-pill"
                type="button"
                :disabled="ctx.page >= ctx.totalPages || ctx.loadingResults"
                @click="ctx.nextPage"
              >
                Next
              </button>
            </div>
          </div>
        </div>
        <p v-else class="p-8 text-center text-[#2f4c1c]">Run a search to populate this snapshot.</p>
      </div>
    </article>

    <div class="grid items-stretch gap-6 lg:grid-cols-2">
      <article
        v-if="approvalsQueue.length"
        class="card-shell insight-card tinted-surface"
        aria-label="Manager approvals queue"
      >
        <header class="flex items-center justify-between">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">Approvals queue</h3>
          </div>
          <span class="flex h-6 w-6 items-center justify-center rounded-full bg-amber-100 text-xs font-bold text-amber-700">
            {{ approvalsQueue.length }}
          </span>
        </header>
        <div class="mt-2 space-y-3">
            <div
              v-for="leave in approvalsQueue"
              :key="leave.id"
              class="list-card group flex items-center justify-between"
            >
            <div>
              <p class="text-sm font-semibold text-slate-900">{{ leave.manager_name }}</p>
              <p class="text-xs text-slate-500">
                {{ leave.employee_name || leave.employee || 'Team member' }} — {{ leave.date_range }}
              </p>
            </div>
            <span class="rounded-full border border-amber-100 bg-amber-50 px-2 py-1 text-[10px] font-bold uppercase text-amber-700">
              {{ (leave.leave_type || 'Pending').replace(/_/g, ' ') }}
            </span>
          </div>
        </div>
      </article>

      <article
        v-if="hasMilestones"
        class="card-shell insight-card tinted-surface"
        aria-label="Culture milestones overview"
      >
        <header class="flex items-center justify-between">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">Upcoming birthdays</h3>
          </div>
        </header>
        <div class="mt-2 grid gap-5">
          <div v-if="milestoneBirthdays.length">
            <ul class="space-y-2">
              <li
                v-for="entry in milestoneBirthdays"
                :key="entry.id || entry.user_id || entry.email"
                class="flex items-center justify-between rounded-lg themed-entry p-2 border"
              >
                <div class="flex items-center gap-2">
                  <div class="h-2 w-2 rounded-full bg-rose-400"></div>
                  <span class="text-sm font-semibold text-slate-700">
                    {{ entry.full_name || entry.name || entry.employee_name || 'Teammate' }}
                  </span>
                </div>
                <span class="text-xs font-medium text-[#1f4c1c] bg-[#ecfef2] border border-[#498528]/40 px-2 py-0.5 rounded">
                  {{ formatBirthday(entry) }}
                </span>
              </li>
            </ul>
          </div>
          <div v-if="offboardingSnapshots.length">
            <p class="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-2">
              Offboarding in flight
            </p>
            <ul class="space-y-2">
              <li
                v-for="row in offboardingSnapshots"
                :key="row.user?.id || row.user?.email"
                class="rounded-xl themed-entry px-3 py-3 shadow-sm"
              >
                <div class="flex justify-between items-center mb-2">
                  <p class="text-sm font-semibold text-slate-900">
                    {{ row.user?.first_name || row.user?.full_name || row.user?.username || 'Employee' }}
                  </p>
                  <span class="text-xs font-bold text-rose-600">
                    {{ row.percent_complete || 0 }}%
                  </span>
                </div>
                  <div class="h-1.5 w-full rounded-full bg-[#dfeeed] overflow-hidden">
                  <div
                    class="h-full rounded-full bg-rose-500"
                    :style="{ width: (row.percent_complete || 0) + '%' }"
                  ></div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </article>
    </div>

    <article v-if="questionQueue.length" class="card-shell tinted-surface" aria-label="Employee escalation inbox">
      <header class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 class="text-xl font-semibold text-slate-900">Employee escalation inbox</h3>
        </div>
        <span class="status-pill">
          {{ questionQueue.length }} open
        </span>
      </header>
      <div class="mt-6 overflow-hidden rounded-2xl themed-panel">
        <div class="overflow-x-auto">
          <table class="results-table">
            <thead>
              <tr class="results-header">
                <th scope="col">Subject</th>
                <th scope="col">From</th>
                <th scope="col">Received</th>
                <th scope="col">Preview</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="question in questionQueue" :key="question.id" class="results-row">
                <td class="font-semibold text-slate-900">{{ question.subject || 'Question' }}</td>
                <td class="text-sm text-slate-600">{{ question.asked_by || 'Employee' }}</td>
                <td class="text-sm text-slate-500">{{ formatDate(question.created_at || question.updated_at) }}</td>
                <td class="text-sm text-slate-600 italic truncate max-w-xs">{{ question.body || question.question }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </article>
  </section>
</template>

<script>
import { ArrowPathIcon, PlusIcon } from '@heroicons/vue/24/outline'
import HrOverview from '../../overview/HrOverview.vue'
import { getKolkataMonthKey } from '@/utils/kolkataTime'

export default {
  name: 'HrDashboardOverviewTab',
  components: {
    HrOverview,
    ArrowPathIcon,
    PlusIcon,
  },
  inject: ['hrDashboardContext'],
  computed: {
    ctx() {
      return this.hrDashboardContext
    },
    commandCenterSubtitle() {
      const total = Number(this.ctx.total) || 0
      if (total) {
        return `Monitoring ${total.toLocaleString('en-IN')} people insights across the organisation`
      }
      return 'Monitoring live people signals and approvals'
    },
    lastSyncNote() {
      const last = this.ctx.directoryMeta?.last_synced_at || this.ctx.lastSyncedAt
      if (last) {
        return `Synced ${this.formatDate(last)}`
      }
      return 'Sync weekly to stay current'
    },
     
    approvalsQueue() {
      const managerLeaves = Array.isArray(this.ctx.managerLeaves) ? this.ctx.managerLeaves : []
      const employeeLeaves = Array.isArray(this.ctx.employeeLeaves) ? this.ctx.employeeLeaves : []
      return [...managerLeaves, ...employeeLeaves]
    },
    questionQueue() {
      return Array.isArray(this.ctx.questions) ? this.ctx.questions : []
    },
    milestoneBirthdays() {
      const tracker = this.ctx.birthdayTracker || {}
      const today = Array.isArray(tracker.today) ? tracker.today : []
      const upcoming = Array.isArray(tracker.upcoming) ? tracker.upcoming : []
      return [...today, ...upcoming].slice(0, 4)
    },
    offboardingSnapshots() {
      return Array.isArray(this.ctx.offboardingReport) ? this.ctx.offboardingReport.slice(0, 2) : []
    },
    heroStats() {
      const approvals = this.approvalsQueue.length
      const escalations = this.questionQueue.length
      const lifecycle = this.milestoneBirthdays.length + this.offboardingSnapshots.length
      const jdCount = Array.isArray(this.ctx.jobDescriptions) ? this.ctx.jobDescriptions.length : 0

      return [
        {
          label: 'Manager approvals',
          value: approvals,
          context: approvals ? 'Needs HR review' : 'Inbox clear',
          intent: approvals ? 'warning' : 'success',
        },
        {
          label: 'Employee questions',
          value: escalations,
          context: escalations ? 'Escalations awaiting reply' : 'No live escalations',
          intent: escalations ? 'warning' : 'success',
        },
        {
          label: 'Lifecycle moments',
          value: lifecycle,
          context: lifecycle
            ? `${this.milestoneBirthdays.length} celebrations · ${this.offboardingSnapshots.length} transitions`
            : 'No live moments',
          intent: 'neutral',
        },
        {
          label: 'Role templates ready',
          value: jdCount,
          context: jdCount ? 'Ready for matching' : 'Upload new JDs',
          intent: 'neutral',
        },
      ]
    },
    pipelineBreakdown() {
      const summary = this.ctx.resumeSummary || {}
      const derivedTotal = (summary.pending || 0) + (summary.shortlisted || 0) + (summary.rejected || 0)
      const total = summary.total || derivedTotal
      const safeTotal = total || 1
      return [
        { label: 'Pending review', count: summary.pending || 0 },
        { label: 'Shortlisted', count: summary.shortlisted || 0 },
        { label: 'Rejected', count: summary.rejected || 0 },
      ].map((segment) => ({
        ...segment,
        percent: Math.min(100, Math.round(((segment.count || 0) / safeTotal) * 100)),
      }))
    },
    hasMilestones() {
      return this.milestoneBirthdays.length > 0 || this.offboardingSnapshots.length > 0
    },
    snapshotMetrics() {
      return [
        {
          label: 'People dataset',
          value: this.ctx.total || 0,
          hint: 'Active directory snapshots',
        },
        {
          label: 'Pending approvals',
          value: ((this.ctx.managerLeaves || []).length + (this.ctx.employeeLeaves || []).length),
          hint: 'Leaves waiting for HR',
        },
        {
          label: 'Escalations',
          value: (this.ctx.questions || []).length,
          hint: 'Inbox items',
        },
        {
          label: 'Offboarding journeys',
          value: (this.ctx.offboardingReport || []).length,
          hint: 'Live transitions',
        },
      ]
    },
    recentMatches() {
      return Array.isArray(this.ctx.matchResults) ? this.ctx.matchResults : []
    },
    searchPreview() {
      const list = Array.isArray(this.ctx.results) ? this.ctx.results : []
      const pageSize = Number(this.ctx.pageSize) || 5
      return list.slice(0, pageSize)
    },
    analyticsTimeline() {
      const grouped = new Map()
      this.recentMatches?.forEach((item) => {
        const date = new Date(item.created_at || item.createdAt || new Date())
        const key = getKolkataMonthKey(date)
        if (!key) {
          return
        }
        if (!grouped.has(key)) {
          grouped.set(key, {
            key,
            label: date.toLocaleString('en-IN', { month: 'short', timeZone: 'Asia/Kolkata' }),
            approved: 0,
            pending: 0,
            rejected: 0,
          })
        }
        const bucket = grouped.get(key)
        const status = (item.status || '').toString().toLowerCase()
        if (status === 'approved') {
          bucket.approved += 1
        } else if (status === 'pending') {
          bucket.pending += 1
        } else {
          bucket.rejected += 1
        }
      })
      const ordered = Array.from(grouped.values()).sort((a, b) => a.key.localeCompare(b.key))
      return ordered.slice(-6)
    },
    hasValidAnalyticsData() {
      return this.analyticsTimeline.some((entry) => this.getTotal(entry) > 0)
    },
    maxStackValue() {
      if (!this.hasValidAnalyticsData) return 10
      const totals = this.analyticsTimeline.map((entry) => this.getTotal(entry))
      const max = Math.max(...totals, 1)
      return Math.ceil(max / 5) * 5
    },
  },
  methods: {
    goToUserDirectory() {
      if (this.ctx && typeof this.ctx.launchUserDirectory === 'function') {
        this.ctx.launchUserDirectory('create')
        return
      }
      if (this.ctx && typeof this.ctx.setActiveTab === 'function') {
        this.ctx.setActiveTab('userManagement')
      }
    },
    refreshDirectory() {
      if (this.ctx && typeof this.ctx.launchUserDirectory === 'function') {
        this.ctx.launchUserDirectory('refresh')
        return
      }
      if (this.ctx && typeof this.ctx.setActiveTab === 'function') {
        this.ctx.setActiveTab('userManagement')
      }
    },
    statusBadgeColor(intent) {
      if (intent === 'warning') return 'bg-[#ffe6d9]'
      if (intent === 'success') return 'bg-[#dfeeed]'
      return 'bg-[#ecfef2]'
    },
    personName(person) {
      if (!person) return 'Unknown'
      const full = [person.first_name, person.last_name].filter(Boolean).join(' ')
      return person.full_name || person.name || full || person.username || person.email || 'Unknown'
    },
    formatStatus(status) {
      return (status || 'unknown').replace(/_/g, ' ')
    },
    statusClass(status) {
      const normalized = (status || '').toLowerCase()
      if (normalized === 'active') return 'bg-[#dfeeed] text-[#0d4426] border-[#498528]'
      if (normalized === 'on_leave') return 'bg-[#fff7ed] text-[#7c4c00] border-[#f59e0b]'
      if (normalized === 'inactive' || normalized === 'offboarded') return 'bg-[#ffe6ec] text-[#781225] border-[#ec4899]'
      return 'bg-[#ecf6ef] text-[#1f4c1c] border-[#8ec68e]'
    },
    formatDate(value) {
      if (!value) return 'Just now'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return 'Recently'
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    },
    formatBirthday(entry) {
      if (typeof this.ctx.formatBirthdayEntry === 'function') {
        return this.ctx.formatBirthdayEntry(entry)
      }
      return entry?.next_birthday || 'Soon'
    },
    getTotal(entry) {
      return (entry.approved || 0) + (entry.pending || 0) + (entry.rejected || 0)
    },
    getBarHeight(value) {
      if (!value || !this.maxStackValue) return '2%'
      const pct = Math.min((value / this.maxStackValue) * 100, 100)
      return `${Math.max(pct, 2)}%`
    },
  },
}
</script>

<style scoped>
.hero-panel {
  background: #ffffff;
  border-radius: 2rem;
  border: 1px solid #498528;
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.15);
}
.hero-illustration {
  background: #ffffff;
  border-radius: 1.75rem;
  border: 1px solid rgba(73, 133, 40, 0.45);
  box-shadow: inset 0 10px 40px rgba(255, 255, 255, 0.9);
}
.hero-cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border-radius: 999px;
  padding: 0.6rem 1.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hero-cta-btn:hover {
  transform: translateY(-1px);
}
.hero-cta-sync {
  border: 1px solid rgba(15, 23, 42, 0.12);
  background: rgba(255, 255, 255, 0.95);
  color: #0f172a;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.1);
}
.hero-cta-add {
  background: #0f8d6d;
  color: #ffffff;
  box-shadow: 0 15px 30px rgba(15, 23, 42, 0.25);
}
.hero-stat-card {
  border-radius: 1.5rem;
  border: 1px solid rgba(73, 133, 40, 0.35);
  padding: 1rem;
  min-height: 120px;
  background: #dfeeed;
  color: #1f4c1c;
  box-shadow: 0 20px 35px rgba(15, 23, 42, 0.08);
}
.hero-stat-success {
  background: linear-gradient(135deg, rgba(220, 252, 231, 0.95), rgba(16, 185, 129, 0.25));
}
.hero-stat-warning {
  background: linear-gradient(135deg, rgba(246, 253, 255, 0.95), rgba(16, 185, 129, 0.2));
}
.hero-stat-neutral {
  background: linear-gradient(135deg, rgba(237, 250, 255, 0.95), rgba(16, 185, 129, 0.15));
}
.card-shell {
  border-radius: 1.5rem;
  border: 1px solid #498528;
  background: #ffffff;
  padding: 1.5rem;
  box-shadow: 0 25px 50px rgba(15, 23, 42, 0.08);
  color: #0f1f15;
}
.tinted-surface {
  background: rgba(221, 238, 209, 0.3);
}
.overview-card {
  grid-column: span 2;
}
.snapshot-card {
  grid-column: span 1;
  background: #ffffff;
  color: #0f172a;
}
.pulse-card .metric-pill {
  border-radius: 1.25rem;
  border: 1px solid rgba(73, 133, 40, 0.35);
  padding: 1rem;
  background: rgba(255, 255, 255, 0.95);
  transition: transform 0.2s ease;
}
.pulse-card .metric-pill:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 1);
}
.query-console {
  background: #ffffff;
  border: 1px solid #498528;
  box-shadow: 0 25px 45px rgba(15, 23, 42, 0.08);
}
.primary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 0.65rem 1.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  background: #0f8d6d;
  color: #ffffff;
  box-shadow: 0 15px 25px rgba(15, 23, 42, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 18px 30px rgba(15, 23, 42, 0.35);
}
.secondary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 0.55rem 1.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  background: #ffffff;
  border: 1px solid #498528;
  color: #0f1d1a;
  transition: background 0.2s ease;
}
.secondary-btn:hover {
  background: #ecfdf5;
}
.results-table {
  width: 100%;
  border-collapse: collapse;
  background: transparent;
}
.results-table th,
.results-table td {
  padding: 0.9rem 1.25rem;
  border-bottom: 1px solid rgba(73, 133, 40, 0.2);
}
.results-table tbody tr:last-child td {
  border-bottom: none;
}
.results-header {
  background: rgba(73, 133, 40, 0.08);
}
.results-header th {
  color: #0f3e1f;
}
.results-row {
  background: rgba(255, 255, 255, 0.7);
  transition: background 0.2s ease;
}
.results-row:hover {
  background: rgba(255, 255, 255, 0.9);
}
.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 1rem;
  border-radius: 999px;
  border: 1px solid rgba(73, 133, 40, 0.4);
  background: #ffffff;
  color: #1f4c1c;
  font-size: 0.65rem;
  font-weight: 600;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}
.pagination-row {
  border-top: 1px solid rgba(73, 133, 40, 0.2);
  background: rgba(255, 255, 255, 0.75);
  padding: 1rem 1.25rem;
}
.themed-pill {
  border-radius: 999px;
  border: 1px solid #498528;
  background: #ffffff;
  color: #0f4c1c;
  padding: 0.35rem 1.15rem;
  font-size: 0.75rem;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.themed-pill:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.themed-entry {
  background: #ffffff;
  border: 1px solid rgba(73, 133, 40, 0.25);
  box-shadow: 0 15px 30px rgba(15, 23, 42, 0.08);
  color: #0f2f1d;
}
.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid rgba(73, 133, 40, 0.35);
  background: #ffffff;
  color: #1f4c1c;
  padding: 0.25rem 0.9rem;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.12em;
}
</style>


