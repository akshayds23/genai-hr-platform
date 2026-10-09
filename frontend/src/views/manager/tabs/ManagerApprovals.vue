<template>
  <section
    class="rounded-[28px] border border-[#498528] bg-white/80 
           shadow-[0_24px_60px_rgba(15,23,42,0.12)] backdrop-blur-xl"
  >
    <div>
      <!-- Header -->
      <div
        class="flex flex-col gap-2 border-b border-[#498528]/30 px-6 py-4 
               bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70
               sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
            Approvals
          </p>
          <h2 class="text-lg font-semibold text-slate-900">Pending approvals</h2>
          <p class="text-sm text-slate-500">Requests waiting on a decision</p>
        </div>
        <!-- kept styling simple so color stays the same -->
        <button
          class="text-sm font-semibold text-slate-600 transition hover:text-slate-700"
          type="button"
          @click="$emit('refresh-team-insights')"
        >
          Refresh
        </button>
      </div>

      <!-- List -->
      <div
        v-if="pendingTeamLeaves.length"
        class="divide-y divide-slate-100/80 bg-emerald-50/30"
      >
        <div
          v-for="leave in pendingTeamLeaves"
          :key="leave.id"
          class="flex flex-col gap-3 px-6 py-5 transition-all 
                 md:flex-row md:items-center md:justify-between
                 hover:bg-[#DDEED1]/40"
        >
          <div>
            <p class="text-sm font-semibold text-slate-900">
              {{ leave.employee_name }}
            </p>
            <p class="text-sm text-slate-600">
              {{ formatLeaveType(leave.leave_type) }} | {{ leave.dateRange }}
            </p>
            <p class="text-xs text-slate-400">
              {{ leave.reason || 'Not provided' }}
            </p>
          </div>

          <div class="flex gap-2">
            <!-- REJECT (unchanged colors) -->
            <button
              class="rounded-full border border-rose-500 px-4 py-2 text-sm font-semibold 
                     text-rose-600 transition hover:bg-rose-500 hover:text-white 
                     disabled:opacity-60"
              type="button"
              :disabled="Boolean(processingLeaves[leave.id])"
              @click="$emit('update-leave-status', leave, 'rejected')"
            >
              {{ processingLeaves[leave.id] === 'rejected' ? 'Rejecting...' : 'Reject' }}
            </button>

            <!-- APPROVE (unchanged colors) -->
            <button
              class="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold 
                     text-white transition hover:bg-emerald-500 disabled:opacity-60"
              type="button"
              :disabled="Boolean(processingLeaves[leave.id])"
              @click="$emit('update-leave-status', leave, 'approved')"
            >
              {{ processingLeaves[leave.id] === 'approved' ? 'Approving...' : 'Approve' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <p
        v-else
        class="px-6 py-12 text-sm text-slate-500 text-center 
               rounded-b-[28px] bg-white/90"
      >
        No pending requests from your team.
      </p>
    </div>
  </section>
</template>


<script>
export default {
  name: 'ManagerApprovals',
  props: {
    pendingTeamLeaves: Array,
    processingLeaves: Object,
  },
  emits: ['refresh-team-insights', 'update-leave-status'],
  methods: {
    formatLeaveType(type) {
      if (!type) {
        return 'General';
      }
      const text = type.toString().replace(/[_-]/g, ' ');
      return text.charAt(0).toUpperCase() + text.slice(1);
    },
  }
};
</script>
