<template>
  <div class="space-y-6">
    <!-- Leave Balance & Request Section -->
    <section
      class="rounded-[28px] bg-white/80 border border-[#498528] shadow-[0_24px_60px_rgba(15,23,42,0.12)] overflow-hidden backdrop-blur-xl"
    >
      <header
        class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 
               border-b border-[#498528]/30 
               px-6 py-5 
               bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70"
      >
        <div class="flex items-center gap-4">
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center 
                   rounded-2xl bg-[#DDEED1] text-[#2F4C1C] 
                   ring-1 ring-inset ring-[#498528]/40"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
              Leave center
            </p>
            <h2 class="text-base font-bold text-slate-900 leading-tight">
              Leave Management
            </h2>
            <p class="text-xs font-medium text-slate-500 mt-0.5">
              Balance, analytics, and request management.
            </p>
          </div>
        </div>

        <!-- keeping original button color, only theme around it -->
        <button
          type="button"
          @click.stop="$emit('open-leave-modal')"
          class="inline-flex items-center justify-center gap-2 rounded-full 
                 bg-slate-900 px-4 py-2 text-xs font-bold uppercase tracking-wide 
                 text-white shadow-md 
                 transition-transform active:scale-95 hover:bg-slate-800 
                 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:ring-offset-2"
        >
          <svg
            class="w-4 h-4 text-slate-300"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          <span>Request Leave</span>
        </button>
      </header>

      <div
        class="grid grid-cols-1 lg:grid-cols-3 divide-y lg:divide-y-0 lg:divide-x divide-slate-100/70"
      >
        <!-- Leave Balance Circle -->
        <div
          class="p-6 lg:p-8 flex flex-col items-center justify-center text-center 
                 bg-gradient-to-br from-slate-50/60 via-white to-emerald-50/50"
        >
          <div class="relative h-40 w-40">
            <svg class="h-full w-full -rotate-90 transform" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke="#e5e7eb"
                stroke-width="6"
              />
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke="currentColor"
                stroke-width="6"
                stroke-linecap="round"
                class="text-emerald-500 transition-all duration-1000 ease-out drop-shadow-sm"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="dashOffset"
              />
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <span
                class="text-3xl font-bold tracking-tight text-slate-900 tabular-nums"
              >
                {{ safeLeaveRemainingDays }}
              </span>
              <span
                class="text-[10px] font-bold uppercase tracking-[0.25em] text-slate-500"
              >
                Days Left
              </span>
            </div>
          </div>

          <div class="mt-6 grid grid-cols-2 gap-6 w-full max-w-[240px]">
            <div
              class="text-center p-3 bg-[#DDEED1]/70 rounded-[16px] border border-[#498528]/25"
            >
              <p
                class="text-[10px] font-bold uppercase tracking-[0.25em] text-slate-500"
              >
                Allowance
              </p>
              <p class="mt-1 text-lg font-bold text-[#2F4C1C]">
                {{ safeLeaveAllowanceDays }}
              </p>
            </div>
            <div
              class="text-center p-3 bg-[#DDEED1]/70 rounded-[16px] border border-[#498528]/25"
            >
              <p
                class="text-[10px] font-bold uppercase tracking-[0.25em] text-slate-500"
              >
                Used
              </p>
              <p class="mt-1 text-lg font-bold text-[#2F4C1C]">
                {{ safeLeaveUsedDays }}
              </p>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="col-span-1 lg:col-span-2 p-0 flex flex-col h-full">
          <div
            class="px-6 py-4 border-b border-[#498528]/20 
                   bg-gradient-to-r from-white via-emerald-50/40 to-slate-50/60 
                   flex items-center justify-between"
          >
            <h3
              class="text-[11px] font-bold uppercase tracking-[0.35em] text-slate-500"
            >
              Recent activity
            </h3>

            <div class="hidden sm:flex items-center gap-2">
              <div
                v-for="row in leaveSummaryRows"
                :key="row.status"
                class="flex items-center gap-1.5 px-2.5 py-1 rounded-full 
                       bg-white/80 border border-[#498528]/25 shadow-sm"
              >
                <span
                  class="h-1.5 w-1.5 rounded-full"
                  :class="getStatusDotColor(row.status)"
                ></span>
                <span class="text-[10px] font-semibold text-slate-600">
                  {{ row.count }} {{ formatStatus(row.status) }}
                </span>
              </div>
            </div>
          </div>

          <div
            v-if="recentLeaves.length"
            class="flex-1 overflow-y-auto max-h-[340px] 
                   scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent"
          >
            <ul class="divide-y divide-slate-100/80">
              <li
                v-for="leave in recentLeaves"
                :key="leave.id || leave.dateRange"
                class="group flex flex-col sm:flex-row sm:items-center justify-between 
                       gap-3 p-4 hover:bg-[#DDEED1]/40 transition-all duration-200"
              >
                <div class="flex items-start gap-3 min-w-0 flex-1">
                  <div
                    class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full 
                           bg-[#DDEED1] text-lg border border-[#498528]/30
                           group-hover:bg-white group-hover:shadow-md transition-all"
                  >
                    {{ getLeaveIcon(leave.leave_type) }}
                  </div>

                  <div class="min-w-0 flex-1">
                    <h4
                      class="text-sm font-semibold text-slate-900 
                             group-hover:text-[#2F4C1C] transition-colors truncate"
                    >
                      {{ leave.request_type || formatLeaveType(leave.leave_type) }}
                    </h4>
                    <p class="text-xs text-slate-500 font-medium mt-0.5">
                      {{ leave.dateRange }}
                    </p>
                    <p class="text-xs text-slate-400 mt-1 sm:hidden">
                      {{ leave.duration || 'View details' }}
                    </p>
                  </div>
                </div>

                <div
                  class="flex items-center justify-between sm:justify-end w-full sm:w-auto 
                         gap-3 sm:gap-4 sm:pl-0"
                >
                  <span
                    class="hidden sm:inline text-xs font-medium text-slate-500 tabular-nums"
                  >
                    <!-- {{ leave.duration || 'View details' }} -->
                  </span>
                  <span
                    :class="[
                      'inline-flex items-center rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide border shrink-0',
                      getStatusStyles(leave.statusClass),
                    ]"
                  >
                    {{ formatStatus(leave.status) }}
                  </span>
                </div>
              </li>
            </ul>
          </div>

          <div
            v-else
            class="flex-1 flex flex-col items-center justify-center p-12 
                   text-center text-slate-400"
          >
            <svg
              class="w-12 h-12 text-slate-200 mb-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <p class="text-sm">No recent leave history found.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Analytics Section -->
    <section
      class="rounded-[28px] bg-white/80 border border-[#498528] shadow-[0_24px_60px_rgba(15,23,42,0.12)] overflow-hidden backdrop-blur-xl"
    >
      <div
        class="px-6 py-5 border-b border-[#498528]/30 
               flex flex-col md:flex-row md:items-center justify-between gap-4
               bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70"
      >
        <div>
          <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
            Analytics
          </p>
          <h2 class="text-base font-bold text-slate-900">Leave Analytics</h2>
          <p class="text-xs text-slate-500 mt-0.5">
            Status and type breakdown for recent requests
          </p>
        </div>

        <!-- summary cards -->
        <div
          v-if="leaveSummaryCards.length"
          class="flex items-center gap-3 md:gap-6 overflow-x-auto pb-2 md:pb-0 hide-scrollbar"
        >
          <article
            v-for="card in leaveSummaryCards"
            :key="card.id"
            class="min-w-[110px] rounded-2xl border border-[#498528]/30 
                   bg-[#DDEED1]/70 px-4 py-3 text-center shrink-0"
          >
            <p
              class="text-[10px] font-bold uppercase tracking-[0.25em] 
                     text-[#2F4C1C]/80"
            >
              {{ card.label }}
            </p>
            <div class="mt-1 flex items-baseline gap-1.5 justify-center">
              <span class="text-xl font-bold text-[#2F4C1C] tabular-nums">
                {{ card.value }}
              </span>
              <span
                v-if="card.subtext"
                class="text-[10px] font-medium text-slate-600 truncate"
              >
                {{ card.subtext }}
              </span>
            </div>
          </article>
        </div>
      </div>

      <div
        v-if="showLeaveAnalytics && (leaveStatusDistribution.length || leaveTypeDistribution.length || leaveStatusChips.length || teamStatusChips.length)"
        class="px-6 py-6 space-y-8 bg-emerald-50/40"
      >
        <!-- ROW 1: two big donut charts (status + leave types) -->
        <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <!-- Status Split donut -->
          <div
            class="rounded-2xl border border-[#498528]/30 bg-white/80 p-6 shadow-sm 
                   flex flex-col items-center"
          >
            <div class="w-full flex items-center justify-between mb-4">
              <div>
                <h4
                  class="text-xs font-bold uppercase tracking-[0.25em] text-slate-500"
                >
                  Status split
                </h4>
                <p class="text-xs text-slate-400">Recent leave requests</p>
              </div>
              <span class="text-xs font-semibold text-slate-600">
                {{ totalAnalyticsRequests }} total
              </span>
            </div>

            <div class="flex items-center justify-center my-4">
              <div
                class="relative h-40 w-40 rounded-full border border-slate-100"
                :style="{ background: pieGradient }"
              >
                <div
                  class="absolute inset-9 flex flex-col items-center justify-center 
                         rounded-full bg-white/85 text-center text-[11px] 
                         font-semibold text-slate-500 leading-tight"
                >
                  <span class="uppercase tracking-[0.25em] text-[10px]">
                    Status
                  </span>
                  <span class="mt-1 text-base font-bold text-slate-900 tabular-nums">
                    {{ totalAnalyticsRequests }}
                  </span>
                  <span class="text-[10px] text-slate-400">requests</span>
                </div>
              </div>
            </div>

            <div class="mt-2 w-full space-y-2">
              <div
                v-for="segment in leaveStatusDistribution"
                :key="segment.key"
                class="flex items-center justify-between text-xs"
              >
                <div class="flex items-center gap-2">
                  <span
                    class="h-2.5 w-2.5 rounded-full ring-1 ring-inset ring-slate-200"
                    :style="{ backgroundColor: segment.color }"
                  ></span>
                  <span class="font-semibold text-slate-600">
                    {{ segment.label }}
                  </span>
                </div>
                <span class="text-slate-500">
                  {{ segment.value }} ({{ segment.percent }}%)
                </span>
              </div>
              <p
                v-if="!leaveStatusDistribution.length"
                class="text-[11px] text-slate-400"
              >
                Not enough data to calculate status split yet.
              </p>
            </div>
          </div>

          <!-- Leave types donut -->
          <div
            class="rounded-2xl border border-[#498528]/30 bg-white/80 p-6 shadow-sm 
                   flex flex-col items-center"
          >
            <div class="w-full flex items-center justify-between mb-4">
              <div>
                <h4
                  class="text-xs font-bold uppercase tracking-[0.25em] text-slate-500"
                >
                  Leave types
                </h4>
                <p class="text-xs text-slate-400">Based on recent leaves</p>
              </div>
              <span class="text-xs font-semibold text-slate-600">
                {{ totalTypeRequests }} total
              </span>
            </div>

            <div class="flex items-center justify-center my-4">
              <div
                class="relative h-40 w-40 rounded-full border border-slate-100"
                :style="{ background: typePieGradient }"
              >
                <div
                  class="absolute inset-9 flex flex-col items-center justify-center 
                         rounded-full bg-white/85 text-center text-[11px] 
                         font-semibold text-slate-500 leading-tight"
                >
                  <span class="uppercase tracking-[0.25em] text-[10px]">
                    Types
                  </span>
                  <span class="mt-1 text-base font-bold text-slate-900 tabular-nums">
                    {{ leaveTypeDistribution.length || 0 }}
                  </span>
                  <span class="text-[10px] text-slate-400">categories</span>
                </div>
              </div>
            </div>

            <div class="mt-2 w-full space-y-2">
              <div
                v-for="segment in leaveTypeDistribution"
                :key="segment.key"
                class="flex items-center justify-between text-xs"
              >
                <div class="flex items-center gap-2">
                  <span
                    class="h-2.5 w-2.5 rounded-full ring-1 ring-inset ring-slate-200"
                    :style="{ backgroundColor: segment.color }"
                  ></span>
                  <span class="font-semibold text-slate-600">
                    {{ segment.label }}
                  </span>
                </div>
                <span class="text-slate-500">
                  {{ segment.value }} ({{ segment.percent }}%)
                </span>
              </div>
              <p
                v-if="!leaveTypeDistribution.length"
                class="text-[11px] text-slate-400"
              >
                Not enough data to calculate leave types yet.
              </p>
            </div>
          </div>
        </div>

        <!-- ROW 2: your status + team overview -->
        <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <!-- Your Request Status -->
          <div
            class="rounded-2xl border border-[#498528]/30 bg-white/80 p-4 shadow-sm"
          >
            <h4
              class="text-xs font-bold uppercase tracking-[0.25em] text-slate-500 mb-4"
            >
              Your Request Status
            </h4>
            <div class="space-y-3">
              <div
                v-for="chip in leaveStatusChips"
                :key="chip.key"
                class="flex items-center justify-between group cursor-default"
              >
                <div class="flex items-center gap-2">
                  <span
                    class="h-2 w-2 rounded-full ring-2 ring-offset-2 ring-offset-slate-50 
                           transition-all group-hover:ring-offset-slate-100"
                    :class="getStatusColor(chip.key)"
                  ></span>
                  <span
                    class="text-sm font-medium text-slate-600 
                           group-hover:text-slate-900 transition-colors"
                  >
                    {{ chip.label }}
                  </span>
                </div>
                <span
                  class="text-sm font-bold text-slate-900 tabular-nums bg-white 
                         px-2 py-0.5 rounded shadow-sm border border-slate-100"
                >
                  {{ chip.value }}
                </span>
              </div>
              <p
                v-if="!leaveStatusChips.length"
                class="text-[11px] text-slate-400"
              >
                No personal requests in this period.
              </p>
            </div>
          </div>

          <!-- Team Overview -->
          <div
            class="rounded-2xl border border-[#498528]/30 bg-white/80 p-4 shadow-sm"
          >
            <h4
              class="text-xs font-bold uppercase tracking-[0.25em] text-slate-500 mb-4"
            >
              Team Overview
            </h4>
            <div
              v-if="teamStatusChips.length"
              class="grid grid-cols-1 sm:grid-cols-2 gap-3"
            >
              <div
                v-for="chip in teamStatusChips"
                :key="chip.key"
                class="rounded-2xl border border-[#498528]/25 
                       bg-gradient-to-br from-white to-[#DDEED1]/40 
                       p-3 shadow-sm hover:shadow-md hover:border-[#498528]/50 
                       transition-all duration-200"
              >
                <span
                  class="block text-xl font-bold text-[#2F4C1C] mb-1 tabular-nums"
                >
                  {{ chip.value }}
                </span>
                <span
                  class="text-[10px] font-medium uppercase tracking-[0.2em] text-slate-500"
                >
                  {{ chip.label }}
                </span>
              </div>
            </div>
            <p
              v-else
              class="text-[11px] text-slate-400"
            >
              No team-level analytics available yet.
            </p>
          </div>
        </div>
      </div>

      <div v-else class="p-12 text-center bg-emerald-50/40">
        <p class="text-sm text-slate-500">
          No analytics data available for this period.
        </p>
      </div>
    </section>
  </div>
</template>


<script>
export default {
  name: 'ManagerLeaveManagement',
  props: {
    // From ManagerLeaveApply
    totalLeaveRequests: Number,
    leaveRemainingDays: { type: Number, default: 0 },
    leaveAllowanceDays: { type: Number, default: 0 },
    leaveUsedDays: Number,
    leaveSummaryRows: { type: Array, default: () => [] },
    recentLeaves: { type: Array, default: () => [] },
    
    // From ManagerLeaveInsights
    leaveSummaryCards: { type: Array, default: () => [] },
    showLeaveAnalytics: { type: Boolean, default: false },
    leaveAnalyticsMonthly: { type: Array, default: () => [] }, // no longer used in UI but kept for API compatibility
    leaveStatusChips: { type: Array, default: () => [] },
    teamStatusChips: { type: Array, default: () => [] },
  },
  emits: ['open-leave-modal'],
  computed: {
    // Safe getters for leave data
    safeLeaveRemainingDays() {
      return this.leaveRemainingDays ?? 0;
    },
    safeLeaveAllowanceDays() {
      return this.leaveAllowanceDays ?? 0;
    },
    safeLeaveUsedDays() {
      return this.leaveUsedDays ?? 0;
    },
    
    // SVG Math for the donut chart
    circumference() {
      return 2 * Math.PI * 40; // r=40
    },
    dashOffset() {
      const total = this.safeLeaveAllowanceDays || 1; // prevent div/0
      const remaining = this.safeLeaveRemainingDays;
      const percentage = Math.min(Math.max(remaining / total, 0), 1);
      return this.circumference * (1 - percentage);
    },

    // Status distribution (for status donut)
    leaveStatusDistribution() {
      const rows = Array.isArray(this.leaveSummaryRows) ? this.leaveSummaryRows : [];
      const total = rows.reduce((sum, row) => sum + (row.count || 0), 0) || 1;
      const palette = {
        approved: '#22c55e',
        pending: '#fcd34d',
        rejected: '#f87171',
        cancelled: '#94a3b8',
      };
      return rows
        .map((row) => {
          const key = (row.status || 'unknown').toLowerCase();
          const value = row.count || 0;
          return {
            key,
            label: this.formatStatus(key),
            value,
            percent: Math.round((value / total) * 100),
            color: palette[key] || '#cbd5f5',
          };
        })
        .filter((segment) => segment.value > 0);
    },
    totalAnalyticsRequests() {
      return this.leaveStatusDistribution.reduce(
        (sum, segment) => sum + segment.value,
        0,
      );
    },
    pieGradient() {
      const segments = this.leaveStatusDistribution;
      if (!segments.length) {
        return 'conic-gradient(#e5e7eb 0deg, #e5e7eb 360deg)';
      }
      let currentAngle = 0;
      const stops = [];
      segments.forEach(({ percent, color }) => {
        const angle = (percent / 100) * 360;
        const endAngle = currentAngle + Math.max(angle, 1);
        stops.push(`${color} ${currentAngle}deg ${endAngle}deg`);
        currentAngle = endAngle;
      });
      if (currentAngle < 360) {
        stops.push(`#e2e8f0 ${currentAngle}deg 360deg`);
      }
      return `conic-gradient(${stops.join(', ')})`;
    },

    // Leave type distribution (for second donut, based on recentLeaves)
    leaveTypeDistribution() {
      const leaves = Array.isArray(this.recentLeaves) ? this.recentLeaves : [];
      const byType = new Map();

      leaves.forEach((leave) => {
        const rawType = leave.leave_type || 'other';
        const key = rawType.toString().toLowerCase();
        const label = this.formatLeaveType(rawType);
        const current = byType.get(key) || { key, label, value: 0 };
        current.value += 1;
        byType.set(key, current);
      });

      const segments = Array.from(byType.values());
      const total = segments.reduce((sum, seg) => sum + seg.value, 0) || 1;

      const palette = ['#22c55e', '#0ea5e9', '#a855f7', '#f97316', '#e11d48', '#6366f1'];

      return segments
        .map((seg, index) => ({
          ...seg,
          percent: Math.round((seg.value / total) * 100),
          color: palette[index % palette.length],
        }))
        .filter((seg) => seg.value > 0);
    },
    totalTypeRequests() {
      return this.leaveTypeDistribution.reduce((sum, seg) => sum + seg.value, 0);
    },
    typePieGradient() {
      const segments = this.leaveTypeDistribution;
      if (!segments.length) {
        return 'conic-gradient(#e5e7eb 0deg, #e5e7eb 360deg)';
      }
      let currentAngle = 0;
      const stops = [];
      segments.forEach(({ percent, color }) => {
        const angle = (percent / 100) * 360;
        const endAngle = currentAngle + Math.max(angle, 1);
        stops.push(`${color} ${currentAngle}deg ${endAngle}deg`);
        currentAngle = endAngle;
      });
      if (currentAngle < 360) {
        stops.push(`#e2e8f0 ${currentAngle}deg 360deg`);
      }
      return `conic-gradient(${stops.join(', ')})`;
    },
  },
  methods: {
    // Methods from ManagerLeaveApply
    formatLeaveType(type) {
      if (!type) return 'General';
      const text = type.toString().replace(/[_-]/g, ' ');
      return text.charAt(0).toUpperCase() + text.slice(1);
    },
    formatStatus(status) {
      if (!status) return 'Unknown';
      return status.toString().charAt(0).toUpperCase() + status.toString().slice(1).toLowerCase();
    },
    // Visual helper for status dots in the header
    getStatusDotColor(status) {
      const s = status?.toLowerCase();
      if (s === 'approved') return 'bg-emerald-500';
      if (s === 'pending') return 'bg-amber-500';
      if (s === 'rejected') return 'bg-rose-500';
      return 'bg-slate-400';
    },
    // Returns full styles for badges
    getStatusStyles(statusClass) {
      switch (statusClass) {
        case 'success': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
        case 'warning': return 'bg-amber-50 text-amber-700 border-amber-200';
        case 'danger': return 'bg-rose-50 text-rose-700 border-rose-200';
        default: return 'bg-slate-50 text-slate-600 border-slate-200';
      }
    },
    // Adds a little flavor to the list
    getLeaveIcon(type) {
      const t = type?.toLowerCase() || '';
      if (t.includes('sick')) return '🤒';
      if (t.includes('holiday') || t.includes('annual')) return '🌴';
      if (t.includes('parental')) return '👶';
      if (t.includes('wfh')) return '🏠';
      return '📅';
    },
    getStatusColor(key) {
      const map = {
        approved: 'bg-emerald-500 ring-emerald-200',
        pending: 'bg-amber-400 ring-amber-200',
        rejected: 'bg-rose-400 ring-rose-200',
        cancelled: 'bg-slate-400 ring-slate-200',
      };
      return map[key] || map.cancelled;
    },
  },
};
</script>

<style scoped>
/* Utility for hiding scrollbars in the top stats row 
   while maintaining scroll functionality.
*/
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Custom scrollbar for the activity list */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: #e2e8f0;
  border-radius: 3px;
}
.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background-color: #cbd5e1;
}

/* Smooth transitions for interactive elements */
.transition-all {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Ensure proper text rendering */
.tabular-nums {
  font-variant-numeric: tabular-nums;
}

/* Custom gradient backgrounds */
.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}

/* Mobile-first responsive design improvements */
@media (max-width: 640px) {
  .grid-cols-1 {
    gap: 1rem;
  }
  
  .text-3xl {
    font-size: 2rem;
    line-height: 1.2;
  }
  
  .h-40.w-40 {
    height: 8rem;
    width: 8rem;
  }
}
</style>
