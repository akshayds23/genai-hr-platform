<template>
  <section class="group/card relative overflow-hidden rounded-2xl bg-white border border-slate-200 shadow-sm transition-shadow duration-300 hover:shadow-md">
    
    <header class="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-start gap-4">
        <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 ring-1 ring-inset ring-indigo-100">
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
          </svg>
        </div>
        
        <div class="flex flex-col">
          <h2 class="text-base font-bold text-slate-900">Priority Announcements</h2>
          <p class="text-sm text-slate-500">Align the team on current objectives.</p>
        </div>
      </div>

      <button 
        class="inline-flex shrink-0 items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 active:scale-95"
        type="button"
        @click="$emit('open-project-modal', 'create')"
      >
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" /></svg>
        <span>{{ projectAnnouncement ? 'New Update' : 'Post Update' }}</span>
      </button>
    </header>

    <div class="px-6 pb-6">
      
      <article 
        v-if="projectAnnouncement" 
        class="relative mt-2 overflow-hidden rounded-xl bg-slate-50 border border-slate-100 p-5 transition-all focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2"
        tabindex="0"
      >
        <div class="absolute inset-y-0 left-0 w-1 bg-indigo-500"></div>

        <div class="flex items-start justify-between pl-3">
          <span class="inline-flex items-center gap-2 rounded-full bg-white py-1 pl-2 pr-3 text-[11px] font-bold uppercase tracking-wider text-indigo-700 shadow-sm ring-1 ring-slate-900/5">
            <span class="relative flex h-2 w-2">
              <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-indigo-400 opacity-75"></span>
              <span class="relative inline-flex h-2 w-2 rounded-full bg-indigo-500"></span>
            </span>
            Live Now
          </span>

          <div class="flex items-center gap-2">
            <button 
              type="button"
              @click="$emit('open-project-modal', 'edit')"
              class="inline-flex items-center gap-1 rounded-full border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-indigo-200 hover:bg-white hover:text-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
              <span>Edit</span>
            </button>
            <button 
              type="button"
              @click="$emit('confirm-remove-project')"
              class="inline-flex items-center gap-1 rounded-full border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-rose-200 hover:bg-white hover:text-rose-600 focus:outline-none focus:ring-2 focus:ring-rose-500"
            >
              <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
              <span>Delete</span>
            </button>
          </div>
        </div>

        <div class="pl-3 mt-3">
          <h3 class="text-lg font-bold text-slate-900 tracking-tight">{{ projectAnnouncement.title }}</h3>
          <div class="mt-2 prose prose-sm prose-slate max-w-none text-slate-600 leading-7">
            {{ projectAnnouncement.description }}
          </div>

        </div>
      </article>

      <div 
        v-else 
        class="group/empty flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50/50 py-10 text-center transition-all duration-300 hover:border-indigo-400 hover:bg-indigo-50/30 cursor-pointer"
        @click="$emit('open-project-modal', 'create')"
        role="button"
        tabindex="0"
        @keydown.enter="$emit('open-project-modal', 'create')"
      >
        <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-white shadow-sm ring-1 ring-slate-900/5 group-hover/empty:scale-110 transition-transform">
          <svg class="h-6 w-6 text-slate-400 group-hover/empty:text-indigo-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" /></svg>
        </div>
        <h3 class="text-sm font-semibold text-slate-900">No Active Announcements</h3>
        <p class="mt-1 max-w-[280px] text-xs text-slate-500">Create a new update to align your team.</p>
      </div>

    </div>
  </section>
</template>

<script>
// (Script logic remains consistent with your original, 
// just ensure your date formatter handles edge cases robustly)
export default {
  name: 'ManagerProjects',
  props: {
    projectAnnouncement: Object,
  },
  emits: ['open-project-modal', 'confirm-remove-project'],
  methods: {
    formatRelativeDate(value) {
      if (!value) return '';
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return '';
      const diffMs = Date.now() - date.getTime();
      const minutes = Math.round(diffMs / 60000);
      if (minutes < 1) return 'Just now';
      if (minutes < 60) return `${minutes} min${minutes === 1 ? '' : 's'} ago`;
      const hours = Math.round(minutes / 60);
      if (hours < 24) return `${hours} hr${hours === 1 ? '' : 's'} ago`;
      const days = Math.round(hours / 24);
      if (days < 7) return `${days} day${days === 1 ? '' : 's'} ago`;
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    },
  }
};
</script>