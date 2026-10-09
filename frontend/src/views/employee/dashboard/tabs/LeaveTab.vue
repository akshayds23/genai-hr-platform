<template>
  <section class="space-y-10">
    <!-- Leave Management Panel -->
    <!-- Leave Balance & Request Section -->
    <section
      class="rounded-[28px] bg-white/80 border border-[#498528] shadow-[0_24px_60px_rgba(15,23,42,0.12)] 
             overflow-hidden backdrop-blur-xl"
    >
      <header
        class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 
               border-b border-[#498528]/30 
               bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70 px-6 py-5"
      >
        <div class="flex items-center gap-4">
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl 
                   bg-[#DDEED1] text-[#2F4C1C] ring-1 ring-inset ring-[#498528]/40"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
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
            <h2 class="text-base font-bold text-slate-900 leading-tight mt-1">
              Leave Management
            </h2>
            <p class="text-xs font-medium text-slate-500 mt-0.5">
              Balance, analytics, and request management.
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="ctx.openLeaveModal"
          class="inline-flex items-center justify-center gap-2 rounded-full 
                 bg-[#F04770] px-5 py-2 text-xs font-bold uppercase tracking-wide text-white 
                 shadow-md hover:bg-[#C93A5B] hover:shadow-lg 
                 transition-all duration-300 active:scale-95 
                 focus:outline-none focus:ring-2 focus:ring-[#F04770]/70 focus:ring-offset-2"
        >
          <svg class="w-4 h-4 text-rose-50" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
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
              <circle cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" stroke-width="6" />
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
              <span class="text-3xl font-bold tracking-tight text-slate-900 tabular-nums">
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
            <h3 class="text-[11px] font-bold uppercase tracking-[0.35em] text-slate-500">
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
                  {{ row.count }} {{ ctx.formatStatus(row.status) }}
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
                class="group flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 
                       hover:bg-[#DDEED1]/40 transition-all duration-200"
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
                      {{ leave.request_type || ctx.formatLeaveType(leave.leave_type) }}
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
                  class="flex items-center justify-between sm:justify-end w-full sm:w-auto gap-3 sm:gap-4 sm:pl-0"
                >
                  <span class="hidden sm:inline text-xs font-medium text-slate-500 tabular-nums">
                    <!-- {{ leave.duration || 'View details' }} -->
                  </span>
                  <span
                    :class="[
                      'inline-flex items-center rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide border shrink-0',
                      getStatusStyles(leave.statusClass),
                    ]"
                  >
                    {{ ctx.formatStatus(leave.status) }}
                  </span>
                </div>
              </li>
            </ul>
          </div>

          <div
            v-else
            class="flex-1 flex flex-col items-center justify-center p-12 text-center text-slate-400"
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

    <!-- Analytics panel -->
    <section
      class="rounded-[28px] border border-[#498528] bg-white/80 
             shadow-[0_24px_60px_rgba(15,23,42,0.12)] overflow-hidden backdrop-blur-xl"
    >
      <div
        class="flex flex-col gap-4 border-b border-[#498528]/30 px-6 py-5 
               bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70 
               md:flex-row md:items-center md:justify-between"
      >
        <div>
          <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
            Analytics
          </p>
          <h2 class="text-base font-semibold text-slate-900 mt-1">Leave analytics</h2>
          <p class="text-sm text-slate-500">
            Status and type breakdown for recent requests
          </p>
        </div>

        <div
          v-if="leaveSummaryCards.length"
          class="hide-scrollbar flex items-center gap-3 overflow-x-auto pb-1"
        >
          <article
            v-for="card in leaveSummaryCards"
            :key="card.id"
            class="min-w-[120px] rounded-2xl border border-[#498528]/30 bg-[#DDEED1]/70 px-4 py-3 text-center"
          >
            <p class="text-[10px] font-bold uppercase tracking-[0.25em] text-[#2F4C1C]/80">
              {{ card.label }}
            </p>

            <div class="mt-1 flex items-baseline gap-1 justify-center">
              <span class="text-xl font-semibold text-[#2F4C1C] tabular-nums">
                {{ card.value }}
              </span>
              <span
                v-if="card.subtext"
                class="text-[11px] font-medium text-slate-600"
              >
                {{ card.subtext }}
              </span>
            </div>
          </article>
        </div>
      </div>

      <div
        v-if="leaveStatusDistribution.length || leaveTypeDistribution.length || teamStatusChips.length"
        class="px-6 py-6 space-y-8 bg-emerald-50/40"
      >
        <!-- ROW 1: two BIG donut charts side by side -->
        <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <!-- Donut 1: Status Split -->
          <div
            class="rounded-2xl border border-[#498528]/30 bg-white/80 p-6 shadow-sm 
                   flex flex-col items-center"
          >
            <div class="w-full flex items-center justify-between mb-4">
              <div>
                <h4 class="text-xs font-bold uppercase tracking-[0.25em] text-slate-500">
                  Status split
                </h4>
                <p class="text-xs text-slate-400">Recent leave requests</p>
              </div>
              <span class="text-xs font-semibold text-slate-600">
                {{ totalAnalyticsRequests }} total
              </span>
            </div>

            <!-- big donut -->
            <div class="flex items-center justify-center my-4">
              <div
                class="relative h-40 w-40 rounded-full border border-slate-100"
                :style="{ background: pieGradient }"
              >
                <div
                  class="absolute inset-9 flex flex-col items-center justify-center rounded-full 
                         bg-white/85 text-center text-[11px] font-semibold text-slate-500 leading-tight"
                >
                  <span class="uppercase tracking-[0.25em] text-[10px]">Status</span>
                  <span class="mt-1 text-base font-bold text-slate-900 tabular-nums">
                    {{ totalAnalyticsRequests }}
                  </span>
                  <span class="text-[10px] text-slate-400">requests</span>
                </div>
              </div>
            </div>

            <!-- legend under donut -->
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
              <p v-if="!leaveStatusDistribution.length" class="text-[11px] text-slate-400">
                Not enough data to calculate status split yet.
              </p>
            </div>
          </div>

          <!-- Donut 2: Leave types (same style) -->
          <div
            class="rounded-2xl border border-[#498528]/30 bg-white/80 p-6 shadow-sm 
                   flex flex-col items-center"
          >
            <div class="w-full flex items-center justify-between mb-4">
              <div>
                <h4 class="text-xs font-bold uppercase tracking-[0.25em] text-slate-500">
                  Leave types
                </h4>
                <p class="text-xs text-slate-400">Last 2 months</p>
              </div>
              <span class="text-xs font-semibold text-slate-600">
                {{ totalTypeRequests }} total
              </span>
            </div>

            <!-- big donut -->
            <div class="flex items-center justify-center my-4">
              <div
                class="relative h-40 w-40 rounded-full border border-slate-100"
                :style="{ background: typePieGradient }"
              >
                <div
                  class="absolute inset-9 flex flex-col items-center justify-center rounded-full 
                         bg-white/85 text-center text-[11px] font-semibold text-slate-500 leading-tight"
                >
                  <span class="uppercase tracking-[0.25em] text-[10px]">Types</span>
                  <span class="mt-1 text-base font-bold text-slate-900 tabular-nums">
                    {{ leaveTypeDistribution.length || 0 }}
                  </span>
                  <span class="text-[10px] text-slate-400">categories</span>
                </div>
              </div>
            </div>

            <!-- legend under donut (same style as status) -->
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
              <p v-if="!leaveTypeDistribution.length" class="text-[11px] text-slate-400">
                Not enough data to calculate leave types yet.
              </p>
            </div>
          </div>
        </div>

        <!-- ROW 2: planning insights only (no duplicate status counts) -->
        <div
          v-if="teamStatusChips.length"
          class="rounded-2xl border border-[#498528]/30 bg-white/80 p-4 shadow-sm"
        >
          <h4 class="text-xs font-bold uppercase tracking-[0.25em] text-slate-500">
            Planning insights
          </h4>
          <div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div
              v-for="chip in teamStatusChips"
              :key="chip.key"
              class="rounded-2xl border border-[#498528]/25 
                     bg-gradient-to-br from-white to-[#DDEED1]/40 p-3 shadow-sm"
            >
              <p class="text-2xl font-semibold text-[#2F4C1C] tabular-nums">
                {{ chip.value }}
              </p>
              <p
                class="text-[11px] font-medium uppercase tracking-[0.25em] text-slate-500"
              >
                {{ chip.label }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div
        v-else
        class="bg-[#DDEED1]/40 px-6 py-12 text-center text-sm text-slate-500"
      >
        Not enough history to visualize trends yet. Submit requests to see charts here.
      </div>
    </section>
  </section>
</template>


<script>
import { getKolkataMonthKey, startOfKolkataDay } from '@/utils/kolkataTime';

export default {
  name: 'LeaveTab',
  inject: ['employeeDashboardContext'],
  computed: {
    ctx() {
      return this.employeeDashboardContext;
    },
    recentLeaves() {
      return Array.isArray(this.ctx.recentLeaves) ? this.ctx.recentLeaves : [];
    },
    leaveSummaryRows() {
      const rows = this.ctx.leaveSummaryRows;
      return Array.isArray(rows) ? rows : [];
    },
    withdrawProcessing() {
      return this.ctx.withdrawProcessing || {};
    },
    safeLeaveRemainingDays() {
      const value = this.ctx.leaveRemainingDays;
      return typeof value === 'number' ? value : 0;
    },
    safeLeaveAllowanceDays() {
      const value = this.ctx.leaveAllowanceDays;
      return typeof value === 'number' ? value : 0;
    },
    safeLeaveUsedDays() {
      const value = this.ctx.leaveUsedDays;
      return typeof value === 'number' ? value : 0;
    },
    circumference() {
      return 2 * Math.PI * 40;
    },
    dashOffset() {
      const total =
        this.safeLeaveAllowanceDays ||
        this.safeLeaveUsedDays + this.safeLeaveRemainingDays ||
        1;
      const percentage = Math.min(
        Math.max(this.safeLeaveRemainingDays / (total || 1), 0),
        1,
      );
      return this.circumference * (1 - percentage);
    },
    leaveSummaryCards() {
      const cards = [];
      cards.push({
        id: 'total',
        label: 'Total requests',
        value: this.ctx.totalLeaveRequests || 0,
      });
      if (this.safeLeaveAllowanceDays) {
        cards.push({
          id: 'balance',
          label: 'Balance left',
          value: `${this.safeLeaveRemainingDays}d`,
          subtext: `of ${this.safeLeaveAllowanceDays}d`,
        });
      }
      if (this.safeLeaveUsedDays) {
        cards.push({
          id: 'used',
          label: 'Days used',
          value: `${this.safeLeaveUsedDays}d`,
        });
      }
      const pending = this.statusCount('pending');
      if (pending) {
        cards.push({
          id: 'pending',
          label: 'Pending approvals',
          value: pending,
        });
      }
      cards.push({
        id: 'recent',
        label: 'Recent activity',
        value: this.recentLeaves.length,
        subtext: 'Last 6 entries',
      });
      return cards;
    },
    leaveStatusChips() {
      const statuses = ['approved', 'pending', 'rejected', 'cancelled'];
      return statuses
        .map((key) => ({
          key,
          label: this.ctx.formatStatus(key),
          value: this.statusCount(key),
        }))
        .filter((chip) => chip.value > 0);
    },
    teamStatusChips() {
      const today = startOfKolkataDay(new Date());
      const upcoming = this.recentLeaves.filter(
        (leave) => today && leave.startDate && leave.startDate >= today,
      ).length;
      const withdrawable = this.recentLeaves.filter((leave) =>
        this.ctx.canWithdraw(leave),
      ).length;
      const history = this.recentLeaves.length;
      return [
        { key: 'upcoming', label: 'Upcoming days off', value: upcoming },
        { key: 'withdrawable', label: 'Cancelable requests', value: withdrawable },
        { key: 'history', label: 'Requests logged', value: history },
      ].filter((chip) => chip.value > 0);
    },
    analyticsTimeline() {
      const grouped = new Map();
      this.recentLeaves.forEach((leave) => {
        const date =
          leave.startDate || (leave.start_date ? new Date(leave.start_date) : null);
        if (!date || Number.isNaN(date.getTime())) {
          return;
        }
        const key = getKolkataMonthKey(date);
        if (!key) {
          return;
        }
        if (!grouped.has(key)) {
          grouped.set(key, {
            key,
            label: date.toLocaleString('en-IN', {
              month: 'short',
              timeZone: 'Asia/Kolkata',
            }),
            approved: 0,
            pending: 0,
            rejected: 0,
          });
        }
        const bucket = grouped.get(key);
        const status = (leave.status || '').toString().toLowerCase();
        if (status === 'approved') {
          bucket.approved += 1;
        } else if (status === 'pending') {
          bucket.pending += 1;
        } else if (status === 'rejected' || status === 'cancelled') {
          bucket.rejected += 1;
        } else {
          bucket.pending += 1;
        }
      });
      const ordered = Array.from(grouped.values()).sort((a, b) =>
        a.key.localeCompare(b.key),
      );
      // Only keep last 2 months
      return ordered.slice(-2);
    },
    hasValidAnalyticsData() {
      return this.analyticsTimeline.some((entry) => this.getTotal(entry) > 0);
    },
    maxStackValue() {
      if (!this.hasValidAnalyticsData) {
        return 10;
      }
      const totals = this.analyticsTimeline.map((entry) => this.getTotal(entry));
      const max = Math.max(...totals, 1);
      return Math.ceil(max / 5) * 5;
    },
    leaveStatusDistribution() {
      const rows = this.leaveSummaryRows;
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
            label: this.ctx.formatStatus(key),
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

    // 🔹 Leave type analytics for last 2 months
    leaveTypeDistribution() {
      const timelineKeys = new Set(this.analyticsTimeline.map((e) => e.key));
      if (!timelineKeys.size) {
        return [];
      }

      const byType = new Map();

      this.recentLeaves.forEach((leave) => {
        const date =
          leave.startDate || (leave.start_date ? new Date(leave.start_date) : null);
        if (!date || Number.isNaN(date.getTime())) return;

        const monthKey = getKolkataMonthKey(date);
        if (!timelineKeys.has(monthKey)) return;

        const rawType = leave.leave_type || 'other';
        const key = rawType.toString().toLowerCase();
        const label = this.ctx.formatLeaveType
          ? this.ctx.formatLeaveType(rawType)
          : rawType;

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
    statusCount(status) {
      const target = (status || '').toString().toLowerCase();
      const row = this.leaveSummaryRows.find(
        (item) => (item.status || '').toLowerCase() === target,
      );
      return row ? row.count || 0 : 0;
    },
    getStatusDotColor(status) {
      const s = (status || '').toString().toLowerCase();
      if (s === 'approved') return 'bg-emerald-500';
      if (s === 'pending') return 'bg-amber-500';
      if (s === 'rejected' || s === 'cancelled') return 'bg-rose-500';
      return 'bg-slate-400';
    },
    getStatusStyles(statusClass) {
      switch (statusClass) {
        case 'success':
          return 'border-emerald-200 bg-emerald-50 text-emerald-700';
        case 'warning':
          return 'border-amber-200 bg-amber-50 text-amber-700';
        case 'danger':
          return 'border-rose-200 bg-rose-50 text-rose-700';
        default:
          return 'border-slate-200 bg-slate-50 text-slate-600';
      }
    },
    getStatusColor(key) {
      const map = {
        approved: 'bg-emerald-500',
        pending: 'bg-amber-400',
        rejected: 'bg-rose-400',
        cancelled: 'bg-slate-400',
      };
      return map[key] || 'bg-slate-400';
    },
    getLeaveIcon(type) {
      const text = (type || '').toString().toLowerCase();
      if (text.includes('sick')) return '🤒';
      if (text.includes('holiday') || text.includes('annual')) return '🌴';
      if (text.includes('parental')) return '👶';
      if (text.includes('wfh')) return '🏠';
      return '📅';
    },
    getTotal(entry) {
      return (entry.approved || 0) + (entry.pending || 0) + (entry.rejected || 0);
    },
     getBarHeight(value) {
      if (!value || !this.maxStackValue) {
        return '6%'; // slightly bigger minimum so single requests are visible
      }
      const pct = Math.min((value / this.maxStackValue) * 100, 100);
      return `${Math.max(pct, 6)}%`;
    },
    handleWithdraw(leave) {
      if (!leave) {
        return;
      }
      this.ctx.withdrawLeave(leave);
    },
  },
};
</script>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

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

.tabular-nums {
  font-variant-numeric: tabular-nums;
}
</style>
