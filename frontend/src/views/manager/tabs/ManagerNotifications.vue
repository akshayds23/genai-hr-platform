<template>
  <section
    class="flex h-[calc(100vh-10rem)] w-full flex-col overflow-hidden
           rounded-[32px] border border-[#498528] bg-white/80
           shadow-[0_32px_80px_rgba(15,23,42,0.18)] backdrop-blur-xl"
  >
    <!-- HEADER -->
    <header
      class="flex flex-wrap items-center justify-between gap-4 
             border-b border-[#498528]/30 
             bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70 
             px-6 py-4"
    >
      <div>
        <p class="text-[11px] font-semibold uppercase tracking-[0.4em] text-slate-400">
          Signal
        </p>
        <h2 class="text-xl font-bold text-slate-900">Notifications</h2>
        <p class="text-sm text-slate-500">
          Latest workflow alerts and policy messages.
        </p>
      </div>
      <button
        class="inline-flex items-center gap-2 rounded-full border border-[#498528]/30 
               bg-white/80 px-4 py-2 text-xs font-semibold uppercase tracking-wide 
               text-slate-700 shadow-sm transition-all hover:bg-[#DDEED1]/60 
               hover:text-[#2F4C1C] disabled:opacity-60"
        type="button"
        :disabled="loading"
        @click="$emit('refresh')"
      >
        <span
          class="h-2 w-2 rounded-full bg-indigo-500"
          :class="{ 'animate-pulse': loading }"
        ></span>
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </header>

    <!-- BODY -->
    <div
      class="flex-1 overflow-y-auto bg-gradient-to-b 
             from-slate-50 via-emerald-50/30 to-slate-50 px-6 py-6"
    >
      <!-- LOADING -->
      <div
        v-if="loading"
        class="flex h-full items-center justify-center rounded-2xl 
               border border-[#498528]/25 bg-white/90 
               text-sm text-slate-500"
      >
        Loading notifications...
      </div>

      <!-- ERROR -->
      <div
        v-else-if="error"
        class="flex h-full flex-col items-center justify-center gap-3 
               rounded-2xl border border-rose-200 bg-rose-50 px-4 py-6 
               text-center text-sm text-rose-600"
      >
        <p>{{ error }}</p>
        <button
          class="rounded-full bg-rose-600 px-4 py-1.5 text-xs font-semibold 
                 uppercase tracking-wide text-white shadow hover:bg-rose-500"
          type="button"
          @click="$emit('refresh')"
        >
          Retry
        </button>
      </div>

      <!-- LIST -->
      <ul v-else-if="notifications.length" class="space-y-4">
        <li v-for="notification in notifications" :key="notification.id">
          <article
            class="rounded-[24px] border border-slate-100 bg-white/95 p-4 shadow-sm 
                   transition hover:-translate-y-[1px] hover:shadow-md 
                   hover:border-[#498528]/40"
            :class="{ 'opacity-70': notification.isRead }"
          >
            <div
              class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between"
            >
              <div>
                <p class="text-base font-semibold text-slate-900">
                  {{ notification.title }}
                </p>
                <p
                  v-if="notification.message"
                  class="mt-1 text-sm text-slate-500"
                >
                  {{ notification.message }}
                </p>
                <p
                  class="mt-2 text-xs font-semibold uppercase tracking-wide 
                         text-slate-400"
                >
                  {{ formatTimestamp(notification.createdAt) }}
                </p>
              </div>
              <div class="flex flex-wrap gap-2">
                <button
                  v-if="!notification.isRead"
                  class="rounded-full border border-indigo-200 bg-white/90 
                         px-3 py-1 text-xs font-semibold text-indigo-600 
                         transition hover:bg-indigo-50"
                  type="button"
                  @click="$emit('mark-read', notification)"
                >
                  Mark read
                </button>
                <span
                  v-else
                  class="rounded-full border border-slate-200 bg-slate-50/80 
                         px-3 py-1 text-xs font-semibold text-slate-400"
                >
                  Read
                </span>
                <button
                  class="rounded-full border border-slate-200 bg-white/90 
                         px-3 py-1 text-xs font-semibold text-slate-500 
                         transition hover:bg-slate-50"
                  type="button"
                  @click="$emit('dismiss', notification)"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </article>
        </li>
      </ul>

      <!-- EMPTY STATE -->
      <div
        v-else
        class="flex h-full flex-col items-center justify-center rounded-2xl 
               border border-[#498528]/25 bg-white/90 
               text-center text-slate-500"
      >
        <p class="text-base font-semibold text-slate-800">
          No notifications right now
        </p>
        <p class="mt-2 text-sm">
          Approvals, policy updates, and team alerts will surface here automatically.
        </p>
      </div>
    </div>
  </section>
</template>


<script>
export default {
  name: 'ManagerNotifications',
  props: {
    notifications: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
    error: {
      type: String,
      default: '',
    },
  },
  emits: ['refresh', 'mark-read', 'dismiss'],
  methods: {
    formatTimestamp(value) {
      if (!value) {
        return '';
      }
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) {
        return '';
      }
      return date.toLocaleString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    },
  },
};
</script>
