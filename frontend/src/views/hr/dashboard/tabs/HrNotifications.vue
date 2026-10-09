<template>
  <section class="notifications-shell flex h-[calc(100vh-10rem)] w-full flex-col">
    <header class="notifications-header flex flex-wrap items-center justify-between gap-4 border-b px-6 py-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.4em] text-slate-400">Signal</p>
        <h2 class="text-xl font-bold text-slate-900">Notifications</h2>
        <p class="text-sm text-slate-500">Latest system alerts and workflow updates.</p>
      </div>
      <button
        class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
        type="button"
        :disabled="loading"
        @click="$emit('refresh')"
      >
        <span class="h-2 w-2 rounded-full bg-indigo-500" :class="{ 'animate-pulse': loading }"></span>
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </header>
    <div class="flex-1 overflow-y-auto bg-slate-50 px-6 py-6">
      <div
        v-if="loading"
        class="flex h-full items-center justify-center rounded-2xl border border-slate-200 bg-white text-sm text-slate-500"
      >
        Loading notifications...
      </div>
      <div
        v-else-if="error"
        class="flex h-full flex-col items-center justify-center gap-3 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-6 text-center text-sm text-rose-600"
      >
        <p>{{ error }}</p>
        <button
          class="rounded-full bg-rose-600 px-4 py-1.5 text-xs font-semibold uppercase tracking-wide text-white shadow hover:bg-rose-500"
          type="button"
          @click="$emit('refresh')"
        >
          Retry
        </button>
      </div>
      <ul v-else-if="notifications.length" class="space-y-4">
        <li v-for="notification in notifications" :key="notification.id">
          <article
            class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md"
            :class="{ 'opacity-70': notification.isRead }"
          >
            <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p class="text-base font-semibold text-slate-900">{{ notification.title }}</p>
                <p v-if="notification.message" class="mt-1 text-sm text-slate-500">
                  {{ notification.message }}
                </p>
                <p class="mt-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                  {{ formatTimestamp(notification.createdAt) }}
                </p>
              </div>
              <div class="flex flex-wrap gap-2">
                <button
                  v-if="!notification.isRead"
                  class="rounded-full border border-indigo-200 px-3 py-1 text-xs font-semibold text-indigo-600 transition hover:bg-indigo-50"
                  type="button"
                  @click="$emit('mark-read', notification)"
                >
                  Mark read
                </button>
                <span
                  v-else
                  class="rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-400"
                >
                  Read
                </span>
                <button
                  class="rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-500 transition hover:bg-slate-50"
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
      <div
        v-else
        class="flex h-full flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white text-center text-slate-500"
      >
        <p class="text-base font-semibold text-slate-800">No notifications right now</p>
        <p class="mt-2 text-sm">System updates, approvals, and escalations will appear here.</p>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HrNotifications',
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
      return date.toLocaleString('en-IN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'Asia/Kolkata',
      });
    },
  },
};
</script>

<style scoped>
.notifications-shell {
  border-radius: 2rem;
  border: 1px solid rgba(73, 133, 40, 0.3);
  background: #ffffff;
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
}
.notifications-header {
  border-color: rgba(73, 133, 40, 0.35);
  background: #ffffff;
}
.notifications-shell .border {
  border-color: rgba(73, 133, 40, 0.15);
}
</style>
