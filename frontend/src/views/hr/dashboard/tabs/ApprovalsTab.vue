<template>
  <section class="approvals-shell p-6 lg:p-10 max-w-7xl mx-auto">
    
    <header class="approvals-header mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-slate-100 pb-8">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <span class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-indigo-500"></span>
          </span>
          <span class="text-xs font-bold uppercase tracking-widest text-indigo-600">Action Required</span>
        </div>
        <h2 class="text-3xl font-bold tracking-tight text-slate-900">Leave Approvals</h2>
        <p class="text-slate-500 mt-2 text-sm leading-relaxed max-w-2xl">
          Review and adjudicate pending leave requests submitted by management level staff.
        </p>
      </div>
      
      <div class="shrink-0">
        <div class="flex items-center gap-3 bg-white px-5 py-3 rounded-xl border border-slate-200 shadow-sm">
           <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Queue:</span>
           <span class="text-xl font-black text-slate-900 leading-none">
             {{ (ctx.managerLeaves?.length || 0) + (ctx.employeeLeaves?.length || 0) }}
           </span>
        </div>
      </div>
    </header>

      
    
    <div v-if="ctx.employeeLoading" class="flex flex-col items-center justify-center py-16 approvals-section dashed-border">
      <div class="animate-spin h-8 w-8 border-4 border-slate-100 border-t-indigo-600 rounded-full mb-4"></div>
      <p class="text-xs font-bold uppercase tracking-wide text-slate-400">Syncing employee requests...</p>
    </div>

    <div v-else-if="!employeeLeaves.length" class="flex flex-col items-center justify-center py-10 approvals-section text-center">
      <p class="text-sm font-semibold text-slate-800">No leave approvals pending.</p>
      <p class="text-slate-500 max-w-sm mx-auto mt-1 text-xs">Leave requests  will appear here for HR review.</p>
    </div>

    <div v-else class="grid gap-4 approvals-section">
    <article 
      v-for="leave in employeeLeaves" 
      :key="leave.id" 
      class="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-indigo-300 transition-all duration-200 overflow-hidden"
    >
      <div class="flex flex-col lg:flex-row">
        
        <div class="p-6 lg:w-[280px] shrink-0 bg-slate-50/50 border-b lg:border-b-0 lg:border-r border-slate-100 flex flex-col justify-center">
          <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-3">Applicant Details</span>
          <div class="flex items-center gap-4">
            <div 
              class="h-12 w-12 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-sm shrink-0 ring-2 ring-white"
              :style="{ backgroundColor: getAvatarColor(leave.employee_name) }"
            >
              {{ getInitials(leave.employee_name) }}
            </div>
            <div>
              <h3 class="font-bold text-slate-900 text-sm md:text-base leading-tight">{{ leave.employee_name }}</h3>
              
            </div>
          </div>
        </div>

        <div class="flex-1 p-6 flex flex-col justify-center gap-6">
            
            <div class="grid sm:grid-cols-2 gap-6">
              <div>
                <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                  Requested Duration
                </span>
                <div class="inline-flex items-center gap-2 bg-indigo-50 border border-indigo-100 text-indigo-700 px-3 py-2 rounded-lg text-sm font-semibold w-full sm:w-auto">
                  <svg class="w-4 h-4 text-indigo-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 01-2 2z" /></svg>
                  {{ leave.date_range }}
                </div>
              </div>

              <div>
                <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                  Leave Type
                </span>
                <span class="text-sm font-medium text-slate-700">{{ leave.leave_type || 'General Leave' }}</span>
              </div>
            </div>

            <div>
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                Justification
              </span>
              <p class="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100">
                {{ leave.reason || 'No specific reason provided by the applicant.' }}
              </p>
            </div>
        </div>

        <div class="p-6 lg:w-[220px] shrink-0 bg-slate-50/30 border-t lg:border-t-0 lg:border-l border-slate-100 flex flex-col justify-center gap-3">
          <span class="hidden lg:block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1 text-center">
            Action Required
          </span>
          
          <button
            class="w-full group flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-emerald-600 text-white text-sm font-bold shadow-sm hover:bg-emerald-700 hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            type="button"
            :disabled="isProcessing(leave.id)"
            @click="ctx.actOnManagerLeave(leave, 'approve')"
          >
            <span v-if="ctx.processingLeaves[leave.id] === 'approve'" class="animate-spin h-3 w-3 border-2 border-white/30 border-t-white rounded-full"></span>
            <span v-else class="flex items-center gap-2">
              <svg class="w-4 h-4 opacity-90" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" /></svg>
              Approve
            </span>
          </button>
          
          <button
            class="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-slate-200 bg-white text-slate-600 text-sm font-semibold hover:bg-rose-50 hover:text-rose-600 hover:border-rose-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            type="button"
            :disabled="isProcessing(leave.id)"
            @click="ctx.actOnManagerLeave(leave, 'reject')"
          >
            {{ ctx.processingLeaves[leave.id] === 'reject' ? 'Rejecting...' : 'Reject' }}
          </button>
        </div>

      </div>
    </article>
    </div>
    
  </section>
</template>

<script>
export default {
  name: 'HrDashboardApprovalsTab',
  inject: ['hrDashboardContext'],
  computed: {
    ctx() {
      return this.hrDashboardContext
    },
    managerLeaves() {
      return Array.isArray(this.ctx.managerLeaves) ? this.ctx.managerLeaves : []
    },
    employeeLeaves() {
      return Array.isArray(this.ctx.employeeLeaves) ? this.ctx.employeeLeaves : []
    },
  },
  methods: {
    isProcessing(id) {
       return !!this.ctx.processingLeaves[id];
    },
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
      const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f59e0b', '#10b981'];
      if (!name) return colors[0];
      let hash = 0;
      for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
      }
      return colors[Math.abs(hash) % colors.length];
    }
  }
}
</script>

<style scoped>
.approvals-shell {
  background: #f6faf6;
}
.approvals-header {
  border-color: rgba(73, 133, 40, 0.3);
}
.approvals-card {
  border-radius: 2rem;
  border: 1px solid #498528;
  background: #ffffff;
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
  padding: 1.5rem;
}
.approvals-section {
  border-radius: 1.35rem;
  border: 1px solid #498528;
  background: #ffffff;
  padding: 1.25rem;
  box-shadow: inset 0 0 0 1px rgba(73, 133, 40, 0.08);
}
.approvals-section + .approvals-section {
  margin-top: 1rem;
}
.approvals-section .border {
  border-color: rgba(15, 23, 42, 0.07) !important;
}
.approvals-section .text-slate-500 {
  color: #1f4c1c;
}
.approvals-section .grid {
  background: transparent;
}
.dashed-border {
  background-image: url("data:image/svg+xml,%3csvg width='100%25' height='100%25' xmlns='http://www.w3.org/2000/svg'%3e%3crect width='100%25' height='100%25' fill='none' rx='16' ry='16' stroke='%2394a3b8' stroke-width='2' stroke-dasharray='6%2c 10' stroke-dashoffset='0' stroke-linecap='square' opacity='0.3'/%3e%3c/svg%3e");
  border: none; 
}
</style>
