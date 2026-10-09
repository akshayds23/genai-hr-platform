<template>

<div class="min-h-screen bg-white text-slate-900 flex w-full font-sans" @click="closeNotifications">
  <aside
    :class="[
      'hidden lg:flex bg-white/95 text-slate-900 flex-col fixed inset-y-0 border-r border-slate-200 -[0_25px_60px_rgba(15,23,42,0.15)] z-40 transition-all duration-300',
      sidebarCollapsed ? 'w-20' : 'w-72'
    ]"
  >
    <div class="relative border-b border-slate-200/70 p-6 bg-white/90">
      <button
        class="absolute -right-3 top-6 rounded-full bg-slate-50 border border-slate-200 text-slate-600 p-1.5 transition hover:bg-slate-100 hover:shadow"
        type="button"
        aria-label="Toggle sidebar"
        @click.stop="toggleSidebar"
      >
        <span class="text-xs font-bold">{{ sidebarCollapsed ? '»' : '«' }}</span>
      </button>
      <router-link
        :class="[
          'inline-flex items-center transition-all duration-200',
          sidebarCollapsed ? 'w-full justify-center' : 'mb-4'
        ]"
        to=""
        aria-label="Alveon home"
      >
        <BrandLogo size="sm" :hide-text="sidebarCollapsed" />
      </router-link>
      <div v-if="!sidebarCollapsed">
        <h1 class="mt-1 text-xl font-bold text-slate-900">Employee Hub</h1>
        <p class="mt-1 text-sm text-slate-500">All your day-to-day essentials.</p>
      </div>
    </div>
    <nav class="flex-1 overflow-y-auto p-4 space-y-2 bg-slate-50/70">
      <button
        v-for="item in navItems"
        :key="item.value"
        type="button"
        @click.stop="handleNavClick(item)"
        :title="sidebarCollapsed ? item.label : ''"
        :disabled="item.value === 'resign' && resignDisabled"
        :class="[
          'group relative w-full flex items-center text-left transition-all duration-200 rounded-none',
          sidebarCollapsed ? 'justify-center px-2 py-3 border-l-0' : 'justify-between px-4 py-3 border-l-4',
          item.value === 'resign'
            ? activeTab === item.value
              ? 'bg-rose-100 text-rose-900 border-rose-300 font-semibold shadow-sm'
              : 'bg-white/80 text-rose-600 border-transparent hover:border-rose-300 hover:text-rose-900'
            : activeTab === item.value
            ? 'bg-slate-100 text-slate-900 border-slate-300 font-semibold shadow-sm'
            : 'bg-white/80 text-slate-600 border-transparent hover:border-slate-200 hover:text-slate-900',
          item.value === 'resign' && resignDisabled ? 'cursor-not-allowed opacity-60' : ''
        ]"
      >
        <div :class="['flex items-center gap-3', sidebarCollapsed ? '' : 'flex-1']">
          <span
  :class="[
    'flex h-9 w-9 items-center justify-center border transition-all duration-200 rounded-lg',

    // --- RESIGN ---
    item.value === 'resign'
      ? activeTab === item.value
        ? 'border-red-500 bg-red-600 text-white'
        : 'border-transparent bg-red-500 text-white group-hover:bg-red-600 group-hover:text-white'

      // --- OVERVIEW (Blue) ---
      : item.value === 'overview'
      ? activeTab === 'overview'
        ? 'border-blue-500 bg-blue-600 text-white'
        : 'border-transparent bg-blue-500 text-white group-hover:bg-blue-600'

      // --- TEAM PROJECTS (Purple) ---
      : item.value === 'teamProjects'
      ? activeTab === 'teamProjects'
        ? 'border-purple-500 bg-purple-600 text-white'
        : 'border-transparent bg-purple-500 text-white group-hover:bg-purple-600'

      // --- LEAVE (Green) ---
      : item.value === 'leave'
      ? activeTab === 'leave'
        ? 'border-green-500 bg-green-600 text-white'
        : 'border-transparent bg-green-500 text-white group-hover:bg-green-600'

      // --- SUPPORT (Amber/Yellow) ---
      : item.value === 'support'
      ? activeTab === 'support'
        ? 'border-amber-500 bg-amber-600 text-white'
        : 'border-transparent bg-amber-500 text-white group-hover:bg-amber-600'

      // --- ASK AVA CHATBOT (Indigo) ---
      : item.value === 'chatbot'
      ? activeTab === 'chatbot'
        ? 'border-indigo-500 bg-indigo-600 text-white'
        : 'border-transparent bg-indigo-500 text-white group-hover:bg-indigo-600'

      // --- NOTIFICATIONS (Red) ---
      : item.value === 'notifications'
      ? activeTab === 'notifications'
        ? 'border-rose-500 bg-rose-600 text-white'
        : 'border-transparent bg-rose-500 text-white group-hover:bg-rose-600'

      // --- CAREER (Pink) ---
      : item.value === 'career'
      ? activeTab === 'career'
        ? 'border-pink-500 bg-pink-600 text-white'
        : 'border-transparent bg-pink-500 text-white group-hover:bg-pink-600'

      // --- FEEDBACK (Sky Blue) ---
      : item.value === 'feedback'
      ? activeTab === 'feedback'
        ? 'border-sky-500 bg-sky-600 text-white'
        : 'border-transparent bg-sky-500 text-white group-hover:bg-sky-600'

      // --- DEFAULT ---
      : 'border-slate-200 bg-slate-100 text-slate-600 group-hover:bg-slate-200'
  ]"
>
  <SidebarIcon :name="item.icon || item.value" />
</span>
          <span
            v-if="!sidebarCollapsed"
            :class="[
              'font-semibold tracking-tight',
              item.value === 'resign' ? 'text-rose-700' : 'text-slate-900'
            ]"
          >
            {{ item.label }}
          </span>
        </div>
      </button>
    </nav>
    <div class="p-4 border-t border-slate-200/70 space-y-3 bg-white/90">
      <div
        :class="[
          'flex items-center gap-3 rounded-xl border border-slate-200 bg-white/90 p-3 shadow-sm',
          sidebarCollapsed ? 'justify-center' : ''
        ]"
      >
        <button
          :class="[
            'flex items-center gap-2 rounded-xl bg-transparent text-sm font-semibold text-slate-700 transition hover:bg-slate-50 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-200',
            sidebarCollapsed ? 'h-12 w-12 justify-center p-0' : 'w-full px-4 py-2'
          ]"
          type="button"
          :title="sidebarCollapsed ? 'Logout' : ''"
          @click="logout"
        >
          <ArrowRightOnRectangleIcon class="h-5 w-5 text-slate-500" aria-hidden="true" />
          <span v-if="!sidebarCollapsed">Logout</span>
        </button>
      </div>
    </div>
  </aside>

  <div :class="['flex-1 w-full flex flex-col min-h-screen transition-all duration-300', sidebarCollapsed ? 'lg:ml-20' : 'lg:ml-72']">
    <header class="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div class="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 md:px-8">
        <div class="flex w-full flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div class="mx-auto flex flex-col items-center text-center lg:flex-1">
            <p class="text-xs uppercase tracking-[0.35em] text-slate-500 font-semibold">Employee Workspace</p>
            <!-- <h1 class="text-2xl font-semibold text-slate-900">Daily ritual &amp; insights</h1> -->
            <p class="text-sm text-slate-600">Stay on top of projects, leave, team updates, and HR support.</p>
          </div>
          <div class="flex flex-wrap items-center gap-3">
            <div class="relative">
              <button
                class="relative flex h-11 w-11 items-center justify-center rounded-full border border-slate-200 bg-white text-xl text-slate-600 shadow-sm transition hover:bg-slate-50"
                type="button"
                aria-label="Notifications"
                @click.stop="toggleNotifications"
              >
                &#128276;
                <span
                  v-if="unreadNotificationCount"
                  class="absolute -right-1 -top-1 inline-flex min-h-[20px] min-w-[20px] items-center justify-center rounded-full bg-slate-900 px-1 text-xs font-semibold text-white"
                >
                  {{ unreadNotificationCount }}
                </span>
              </button>
              <div
                v-if="showNotifications"
                class="absolute right-0 z-50 mt-3 w-[320px] origin-top-right rounded-2xl border border-slate-200 bg-white text-slate-900 shadow-xl"
                @click.self="closeNotifications"
              >
                <div class="flex items-center justify-between border-b border-slate-200 px-4 py-3">
                  <h3 class="text-sm font-semibold text-slate-900">Notifications</h3>
                  <button class="text-lg leading-none text-slate-400 transition hover:text-slate-600" type="button" @click="closeNotifications">&times;</button>
                </div>
                <div class="max-h-80 overflow-y-auto p-4">
                  <div v-if="notificationsLoading" class="py-6 text-center text-sm text-slate-500">Loading alerts...</div>
                  <div v-else-if="notificationsError" class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-600">
                    {{ notificationsError }}
                  </div>
                  <ul v-else-if="notificationBellItems.length" class="space-y-3">
                    <li v-for="item in notificationBellItems" :key="item.id">
                      <div
                        class="relative flex gap-3 rounded-lg border border-slate-200 px-3 py-2 transition hover:border-slate-300 hover:bg-slate-50"
                        :class="{ 'border-slate-300 bg-slate-50': !item.isRead }"
                      >
                        <button
                          class="absolute -right-1 -top-1 h-5 w-5 rounded-full bg-slate-100 text-xs font-semibold text-slate-600 transition hover:bg-slate-200"
                          type="button"
                          @click.stop="dismissNotification(item)"
                        >
                          -
                        </button>
                        <div class="flex-1" @click.stop="markNotificationRead(item)">
                          <p class="text-sm font-semibold text-slate-900">{{ item.title }}</p>
                          <p v-if="item.message" class="mt-1 text-xs text-slate-500">{{ item.message }}</p>
                          <time v-if="item.createdAt" class="mt-2 block text-xs text-slate-400">
                            {{ formatRelativeDate(item.createdAt) }}
                          </time>
                        </div>
                      </div>
                    </li>
                  </ul>
                  <p v-else class="py-6 text-center text-sm text-slate-500">You're all caught up.</p>
                </div>
              </div>
            </div>
            <button
  class="flex items-center gap-3 rounded-full px-3 py-1.5 text-sm font-semibold text-white 
         bg-[#99CDD8] hover:bg-[#7FBBC7] shadow-sm hover:shadow-md 
         transition-all duration-300"
  type="button"
  @click.stop="openProfileModal"
>
              <img
                :src="profileAvatarSrc"
                alt="Profile avatar"
                class="h-9 w-9 rounded-full object-cover"
              />
              <div class="hidden text-left sm:block">
                <p class="text-sm font-semibold text-slate-900">{{ displayName }}</p>
                <p class="text-xs text-slate-600">{{ displayJobTitle || 'Employee' }}</p>
              </div>
            </button>
            
          </div>
        </div>
      </div>
      <div class="flex gap-2 overflow-x-auto px-4 py-3 md:px-8 lg:hidden bg-white">

        <button
          v-for="item in navItems"
          :key="`mobile-${item.value}`"
          type="button"
          @click.stop="handleNavClick(item)"
          :disabled="item.value === 'resign' && resignDisabled"
          :class="[
            'flex items-center gap-2 rounded-full border px-4 py-1.5 text-sm font-semibold transition',
            activeTab === item.value
              ? 'border-slate-300 bg-slate-100 text-slate-900'
              : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:text-slate-900'
            ,
            item.value === 'resign' && resignDisabled ? 'cursor-not-allowed opacity-60' : ''
          ]"
        >
          <span>{{ item.label }}</span>
        </button>
      </div>
    </header>

    <div
      v-if="toast"
      :class="[
        'fixed top-24 right-4 z-50 flex items-start gap-3 rounded-2xl border px-4 py-3 shadow-lg backdrop-blur',
        toast.type === 'error'
          ? 'border-rose-200 bg-rose-50 text-rose-700'
          : toast.type === 'success'
          ? 'border-slate-200 bg-slate-50 text-slate-900'
          : 'border-slate-200 bg-slate-50 text-slate-900',
      ]"
    >
      <div class="text-sm font-medium leading-snug">
        <p>{{ toast.message }}</p>
      </div>
      <button class="text-xl leading-none text-current hover:text-slate-900" type="button" @click="dismissToast">
        &times;
      </button>
    </div>

    <main class="flex-1 w-full max-w-7xl mx-auto space-y-8 px-4 py-8 md:px-8">
      <div
        v-if="loading"
        class="mx-auto flex max-w-3xl flex-col items-center gap-4 rounded-3xl border border-slate-200 bg-white/90 p-10 text-center shadow-[0_22px_48px_rgba(15,23,42,0.12)]"
      >
        <span class="h-12 w-12 animate-spin rounded-full border-4 border-slate-200 border-t-slate-500"></span>
        <p class="text-sm text-slate-600">Loading your employee dashboard...</p>
      </div>

      <template v-else>
        <div
          v-if="error"
          class="mx-auto flex flex-col gap-4 rounded-2xl border border-rose-200 bg-rose-50 px-6 py-5 text-rose-700 md:flex-row md:items-center md:justify-between"
        >
          <span>{{ error }}</span>
          <button
            class="inline-flex items-center justify-center rounded-full bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-400"
            type="button"
            @click="fetchDashboard"
          >
            Retry
          </button>
        </div>

        <EmployeeOverviewTab v-if="activeTab === 'overview'" />

        <TeamProjectsTab v-else-if="activeTab === 'teamProjects'" />

        <LeaveTab v-else-if="activeTab === 'leave'" />

        <ChatbotTab v-else-if="activeTab === 'chatbot'" />

        <NotificationsTab
          v-else-if="activeTab === 'notifications'"
          :notifications="normalizedNotifications"
          :loading="notificationsLoading"
          :error="notificationsError"
          @refresh="loadNotifications(true)"
          @mark-read="markNotificationRead"
          @dismiss="dismissNotification"
        />

        <CareerTab v-else-if="activeTab === 'career'" />

        <FeedbackTab v-else-if="activeTab === 'feedback'" />
        <SupportTab v-else-if="activeTab === 'support'" />
    </template>
  </main>
</div>
<div v-if="showLeaveModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 px-4 py-8" @click.self="closeLeaveModal">
      <div class="w-full max-w-xl rounded-2xl bg-white shadow-2xl">
        <div class="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-4">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">New leave request</h2>
            <p class="text-sm text-slate-500">Let your manager know when you'll be away</p>
          </div>
          <button class="text-2xl leading-none text-slate-400 transition hover:text-slate-600" type="button" @click="closeLeaveModal">-</button>
        </div>
        <div class="px-6 py-5">
          <aside v-if="leaveBalance" class="mb-5 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
            <p>
              <strong>{{ leaveRemainingDays }}</strong>
              of {{ leaveAllowanceDays }} days remaining this year.
            </p>
            <p v-if="leaveUsedDays" class="mt-1 text-xs text-slate-600">
              {{ leaveUsedDays }} day{{ leaveUsedDays === 1 ? '' : 's' }} used so far.
            </p>
          </aside>
          <form class="space-y-4" @submit.prevent="submitLeaveForm">
            <label class="block space-y-2 text-sm">
              <span class="font-medium text-slate-700">Leave type</span>
              <select
                v-model="leaveForm.leave_type"
                class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200"
              >
                <option value="annual">Annual leave</option>
                <option value="sick">Sick leave</option>
                <option value="casual">Casual leave</option>
                <option value="unpaid">Unpaid leave</option>
                <option value="general">Other</option>
              </select>
            </label>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label class="block space-y-2 text-sm">
                <span class="font-medium text-slate-700">Start date</span>
                <input
                  v-model="leaveForm.start_date"
                  type="date"
                  required
                  :min="minLeaveStartDate"
                  class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200"
                >
                <span class="text-[11px] font-medium uppercase tracking-wide text-slate-400">
                  Earliest: {{ formatAbsoluteDate(minLeaveStartDate) }}
                </span>
              </label>
              <label class="block space-y-2 text-sm">
                <span class="font-medium text-slate-700">End date</span>
                <input
                  v-model="leaveForm.end_date"
                  type="date"
                  required
                  :min="minLeaveEndDate"
                  class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200"
                >
                <span class="text-[11px] font-medium uppercase tracking-wide text-slate-400">
                  Earliest: {{ formatAbsoluteDate(minLeaveEndDate) }}
                </span>
              </label>
            </div>
            <label class="block space-y-2 text-sm">
              <span class="font-medium text-slate-700">Reason</span>
              <textarea
                v-model="leaveForm.reason"
                rows="3"
                class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200"
                placeholder="Share context for your manager"
              ></textarea>
            </label>
            <p v-if="leaveFormError" class="text-sm font-medium text-rose-600">{{ leaveFormError }}</p>
            <div class="flex justify-end gap-3">
              <button class="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100" type="button" @click="closeLeaveModal">
                Cancel
              </button>
              <button
                class="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                type="submit"
                :disabled="submittingLeave"
              >
                {{ submittingLeave ? 'Submitting...' : 'Submit request' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div v-if="showFeedbackModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 px-4 py-8" @click.self="closeFeedbackModal">
      <div class="w-full max-w-lg rounded-2xl bg-white shadow-2xl">
        <div class="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-4">
          <h2 class="text-lg font-semibold text-slate-900">Share feedback</h2>
          <button class="text-2xl leading-none text-slate-400 transition hover:text-slate-600" type="button" @click="closeFeedbackModal">-</button>
        </div>
        <form class="space-y-4 px-6 py-5" @submit.prevent="submitFeedback">
          <label class="block space-y-2 text-sm">
            <span class="font-medium text-slate-700">Subject</span>
            <input v-model="feedbackForm.subject" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200" placeholder="e.g. Workspace experience">
          </label>
          <label class="block space-y-2 text-sm">
            <span class="font-medium text-slate-700">Rating</span>
            <select v-model="feedbackForm.rating" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200">
              <option disabled value="">Select rating</option>
              <option value="5">Excellent</option>
              <option value="4">Good</option>
              <option value="3">Average</option>
              <option value="2">Needs improvement</option>
              <option value="1">Poor</option>
            </select>
          </label>
          <label class="block space-y-2 text-sm">
            <span class="font-medium text-slate-700">Message</span>
            <textarea v-model="feedbackForm.message" rows="4" required class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200" placeholder="Share your thoughts"></textarea>
          </label>
          <p v-if="feedbackError" class="text-sm font-medium text-rose-600">{{ feedbackError }}</p>
          <div class="flex justify-end gap-3">
            <button class="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100" type="button" @click="closeFeedbackModal">
              Cancel
            </button>
            <button class="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60" type="submit" :disabled="submittingFeedback">
              {{ submittingFeedback ? 'Sending...' : 'Send feedback' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showProfileModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 px-4 py-8" @click.self="closeProfileModal">
      <div class="w-full max-w-xl rounded-2xl bg-white shadow-2xl">
        <div class="flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 px-6 py-4">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Profile details</h2>
            <p class="text-xs text-slate-500">Keep your contact and job information up to date.</p>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="!editingProfile && profileFields.length"
              class="rounded-full border border-slate-200 px-3 py-1.5 text-xs font-semibold uppercase tracking-wide text-slate-600 transition hover:bg-slate-100"
              type="button"
              @click="startEditingProfile"
            >
              Edit details
            </button>
            <button class="text-2xl leading-none text-slate-400 transition hover:text-slate-600" type="button" @click="closeProfileModal">-</button>
          </div>
        </div>
        <div class="space-y-3 px-6 py-5 text-sm text-slate-600">
          <template v-if="editingProfile">
            <form class="space-y-4" @submit.prevent="saveProfileDetails">
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <label class="block text-sm">
                  <span class="font-medium text-slate-700">First name</span>
                  <input v-model="editableProfile.first_name" type="text" class="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200" />
                </label>
                <label class="block text-sm">
                  <span class="font-medium text-slate-700">Last name</span>
                  <input v-model="editableProfile.last_name" type="text" class="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200" />
                </label>
              </div>
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <!-- <label class="block text-sm">
                  <span class="font-medium text-slate-700">Job title</span>
                  <input v-model="editableProfile.job_title" type="text" class="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200" />
                </label> -->
                <!-- <label class="block text-sm">
                  <span class="font-medium text-slate-700">Department</span>
                  <input v-model="editableProfile.department" type="text" class="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200" />
                </label> -->
              </div>
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <!-- <label class="block text-sm">
                  <span class="font-medium text-slate-700">Team / squad</span>
                  <input v-model="editableProfile.team_number" type="text" class="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200" />
                </label> -->
                <label class="block text-sm">
                  <span class="font-medium text-slate-700">Phone</span>
                  <input v-model="editableProfile.phone" type="text" class="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200" />
                </label>
              </div>
              <label class="block text-sm">
                <span class="font-medium text-slate-700">Address</span>
                <textarea v-model="editableProfile.address" rows="2" class="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200"></textarea>
              </label>
              <p v-if="profileFormError" class="text-sm font-medium text-rose-600">{{ profileFormError }}</p>
              <div class="flex justify-end gap-3">
                <button class="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100" type="button" @click="cancelEditingProfile">
                  Cancel
                </button>
                <button class="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60" type="submit" :disabled="profileSaving">
                  {{ profileSaving ? 'Saving...' : 'Save changes' }}
                </button>
              </div>
            </form>
          </template>
          <template v-else>
            <div v-if="profileFields.length" class="space-y-3">
              <div
                v-for="field in profileFields"
                :key="field.label"
                class="flex items-start justify-between gap-4 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3"
              >
                <span class="text-xs font-semibold uppercase tracking-wide text-slate-500">{{ field.label }}</span>
                <span class="text-sm text-slate-700">{{ field.value }}</span>
              </div>
            </div>
            <p v-else class="rounded-xl border border-slate-100 bg-slate-50 px-4 py-6 text-center text-sm text-slate-500">
              Profile details are not available.
            </p>
          </template>
        </div>
      </div>
    </div>

    <div v-if="showResignModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 px-4 py-8" @click.self="closeResignModal">
      <div class="w-full max-w-2xl rounded-2xl bg-white shadow-2xl">
        <div class="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-4">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Resignation request</h2>
            <p class="text-sm text-slate-500">Share details so HR can support your transition</p>
          </div>
          <button class="text-2xl leading-none text-slate-400 transition hover:text-slate-600" type="button" @click="closeResignModal">-</button>
        </div>
        <div class="px-6 pt-5">
          <div class="flex items-center justify-center rounded-3xl border border-rose-100 bg-rose-50/70 p-4">
            <svg
              class="h-32 w-32"
              viewBox="0 0 200 180"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
              focusable="false"
            >
              <rect x="18" y="150" width="164" height="14" rx="7" fill="#fee2e2" />
              <rect x="126" y="24" width="50" height="124" rx="10" fill="#fff1f2" stroke="#fb7185" stroke-width="4" />
              <circle cx="148" cy="86" r="5" fill="#fb7185" />
              <circle cx="86" cy="54" r="14" fill="#fed7aa" />
              <path d="M70 80C70 70.059 78.059 62 88 62C97.941 62 106 70.059 106 80V110C106 114.418 102.418 118 98 118H78C73.582 118 70 114.418 70 110V80Z" fill="#fb7185" opacity="0.9" />
              <path d="M98 98L126 110" stroke="#f43f5e" stroke-width="6" stroke-linecap="round" />
              <path d="M78 98L58 116" stroke="#f43f5e" stroke-width="6" stroke-linecap="round" />
              <path d="M88 118L106 142" stroke="#fb7185" stroke-width="6" stroke-linecap="round" />
              <path d="M78 118L64 146" stroke="#fb7185" stroke-width="6" stroke-linecap="round" />
              <path d="M150 132L170 122L150 112" stroke="#fb7185" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </div>
        </div>
        <form class="space-y-4 px-6 py-5" @submit.prevent="submitResignForm">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <label class="block space-y-2 text-sm">
              <span class="font-medium text-slate-700">Last working day</span>
              <input
                v-model="resignForm.last_day"
                type="date"
                required
                :min="minResignLastDay"
                :disabled="true"
                class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200"
              >
              <span class="text-[11px] font-medium uppercase tracking-wide text-slate-400">
                Earliest: {{ formatAbsoluteDate(minResignLastDay) }}
              </span>
            </label>
            <label class="block space-y-2 text-sm">
              <span class="font-medium text-slate-700">Notice period</span>
              <select v-model="resignForm.notice_period" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200">
                <option value="">Select</option>
                <option value="2 weeks">2 weeks</option>
                <option value="30 days">30 days</option>
                <option value="60 days">60 days</option>
                <option value="Other">Other</option>
              </select>
            </label>
          </div>
          <label class="block space-y-2 text-sm">
            <span class="font-medium text-slate-700">Reason</span>
            <textarea v-model="resignForm.reason" rows="3" required class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200"></textarea>
          </label>
          <label class="block space-y-2 text-sm">
            <span class="font-medium text-slate-700">Handover plan</span>
            <textarea v-model="resignForm.handover_plan" rows="2" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200" placeholder="Outline any key handover tasks"></textarea>
          </label>
          <label class="block space-y-2 text-sm">
            <span class="font-medium text-slate-700">Additional notes</span>
            <textarea v-model="resignForm.notes" rows="2" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200"></textarea>
          </label>
          <p v-if="resignFormError" class="text-sm font-medium text-rose-600">{{ resignFormError }}</p>
          <div class="flex justify-end gap-3">
            <button class="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100" type="button" @click="closeResignModal">
              Cancel
            </button>
            <button class="rounded-full bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-400" type="submit">
              Submit notice
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>



<script>
import axios from 'axios';
import { ArrowRightOnRectangleIcon } from '@heroicons/vue/24/outline';
import BrandLogo from '@/components/BrandLogo.vue';
import SidebarIcon from '@/components/SidebarIcon.vue';
import profileAvatarUrl from '@/assets/Profile.png';
import EmployeeOverviewTab from './tabs/EmployeeOverviewTab.vue';
import TeamProjectsTab from './tabs/TeamProjectsTab.vue';
import LeaveTab from './tabs/LeaveTab.vue';
import SupportTab from './tabs/SupportTab.vue';
import ChatbotTab from './tabs/ChatbotTab.vue';
import CareerTab from './tabs/CareerTab.vue';
import FeedbackTab from './tabs/FeedbackTab.vue';
import NotificationsTab from './tabs/NotificationsTab.vue';
import {
  parseKolkataISODate,
  formatKolkataDateForInput,
  getKolkataToday,
  getKolkataTomorrow,
  addKolkataDays,
  startOfKolkataDay,
} from '@/utils/kolkataTime';

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api';
const AUTH_HEADER = 'Authentication-Token';
const PROJECT_ANNOUNCEMENT_STORAGE_KEY = 'employee:project-announcement';
const ACTIVE_TAB_STORAGE_KEY = 'employee:active-tab';
const ALLOWED_TABS = ['overview', 'teamProjects', 'leave', 'support', 'chatbot', 'notifications', 'career', 'feedback'];
const OFFBOARDING_LEAVE_TYPES = ['resignation', 'offboarding'];

export default {
  name: 'EmployeeDashboard',
  components: {
    BrandLogo,
    SidebarIcon,
    ArrowRightOnRectangleIcon,
    EmployeeOverviewTab,
    TeamProjectsTab,
    LeaveTab,
    SupportTab,
    ChatbotTab,
    NotificationsTab,
    CareerTab,
    FeedbackTab,
  },
  provide() {
    return {
      employeeDashboardContext: this,
    };
  },
  data() {
    return {
      loading: false,
      error: '',
      profile: null,
      stats: [],
      leaveSummary: null,
      recentLeaves: [],
      upcomingEvents: [],
      notifications: [],
      showNotifications: false,
      notificationsLoading: false,
      notificationsError: '',
      hrQuestions: [],
      hrQuestionsLoading: false,
      hrQuestionsError: '',
      projectAssignments: null,
      projectAnnouncement: null,
      teamOverview: null,
      chatbot: null,
      offboarding: null,
      showLeaveModal: false,
      leaveForm: {
        leave_type: 'annual',
        start_date: '',
        end_date: '',
        reason: '',
      },
      leaveFormError: '',
      submittingLeave: false,
      withdrawProcessing: {},
      showFeedbackModal: false,
      feedbackForm: {
        subject: '',
        rating: '',
        message: '',
      },
        feedbackError: '',
        submittingFeedback: false,
      chatbotPrompt: '',
      chatbotReply: '',
      chatbotStatus: '',
      chatbotReference: '',
      chatbotReferenceSource: '',
      chatbotTicketId: null,
      chatbotLoading: false,
      chatbotConversationId: null,
      chatbotNeedsEscalation: false,
      pendingEscalationQuestion: '',
      chatbotEscalating: false,
        chatHistory: [],
        careerForm: {
          current_role: '',
          target_role: '',
          strengths: '',
          focus_areas: '',
          learning_style: 'online',
          timeline: '6-12',
          guidance_goal: '',
        },
        careerRecommendation: '',
        showCareerRecommendation: false,
        downloadingCareerPdf: false,
      careerFormError: '',
      submittingCareerForm: false,
      showProfileModal: false,
      editingProfile: false,
      profileSaving: false,
      profileFormError: '',
      editableProfile: {
        first_name: '',
        last_name: '',
        job_title: '',
        department: '',
        team_number: '',
        phone: '',
        address: '',
      },
      rawProfile: null,
      showResignModal: false,
      profileAvatarSrc: profileAvatarUrl,
        resignForm: {
          last_day: '',
          notice_period: '',
          reason: '',
          handover_plan: '',
          notes: '',
        },
        resignFormError: '',
        resignationDetails: null,
        toast: null,
        toastTimer: null,
        currentUserName: 'Employee',
        sidebarCollapsed: false,
        activeTab: 'overview',
      };
  },
  computed: {
    navItems() {
      return [
        { value: 'overview', label: 'Overview', icon: 'overview' },
        {
          value: 'teamProjects',
          label: 'Team & Projects',
          icon: 'projects',
          badge: () => {
            const projects = this.activeProjectCount ? `${this.activeProjectCount} projects` : '';
            const teammates = this.teamMembers.length ? `${this.teamMembers.length} teammates` : '';
            return [projects, teammates].filter(Boolean).join(' · ') || null;
          },
        },
        {
          value: 'leave',
          label: 'Leave Requests',
          icon: 'leave',
          badge: () => (this.recentLeaves.length ? this.recentLeaves.length : null),
        },
        {
          value: 'support',
          label: 'Support',
          icon: 'support',
          badge: () => (this.hrQuestions.length ? this.hrQuestions.length : null),
        },
        { value: 'chatbot', label: 'Ask Ava', icon: 'chatbot' },
        {
          value: 'notifications',
          label: 'Notifications',
          icon: 'notifications',
          badge: () => (this.unreadNotificationCount ? Math.min(this.unreadNotificationCount, 99) : null),
        },
        { value: 'career', label: 'Career Growth', icon: 'career' },
        { value: 'feedback', label: 'Give Feedback', icon: 'feedback' },
        { value: 'resign', label: 'Resign', icon: 'resign' },
      ]
    },
    displayName() {
      if (this.profile && this.profile.full_name) {
        return this.profile.full_name;
      }
      return this.currentUserName;
    },
    displayJobTitle() {
      return this.profile && this.profile.job_title ? this.profile.job_title : '';
    },
    initials() {
      const parts = (this.displayName || '').trim().split(/\s+/);
      const letters = parts.slice(0, 2).map((part) => part.charAt(0).toUpperCase());
      return letters.join('') || 'E';
    },
    overviewSubtitle() {
      const job = this.displayJobTitle;
      const department = this.profile && this.profile.department ? this.profile.department : '';
      if (job && department) {
        return `${job} | ${department}`;
      }
      if (job) {
        return job;
      }
      if (department) {
        return `Department ${department}`;
      }
      return 'Stay on top of your projects, leave, and HR updates.';
    },
    activeProjectCount() {
      if (this.projectAssignments && typeof this.projectAssignments.active_count === 'number') {
        return this.projectAssignments.active_count;
      }
      return 0;
    },
    insightCards() {
  const remaining = this.leaveRemainingDays;
  const used = this.leaveUsedDays;
  const allowance = this.leaveAllowanceDays;
  const total = this.totalLeaveRequests;

  const remainingNumber = typeof remaining === 'number' ? remaining : null;
  const usedNumber = typeof used === 'number' ? used : null;
  const allowanceNumber = typeof allowance === 'number' ? allowance : null;
  const totalNumber = typeof total === 'number' ? total : null;

  const usedPercent =
    allowanceNumber && usedNumber !== null && allowanceNumber > 0
      ? Math.min(100, Math.round((usedNumber / allowanceNumber) * 100))
      : null;

  const recentLeave = Array.isArray(this.recentLeaves) && this.recentLeaves.length
    ? this.recentLeaves[0]
    : null;

  const recentLeaveDate = recentLeave?.start_date
    ? this.formatAbsoluteDate(recentLeave.start_date)
    : null;

  return [
    {
      id: 'leave-remaining',
      label: 'Remaining leave',
      value: remainingNumber !== null ? remainingNumber : '--',
      subline: allowanceNumber ? `of ${allowanceNumber} days` : null,
      description:
        allowanceNumber !== null && remainingNumber !== null
          ? `${allowanceNumber - remainingNumber} days already used.`
          : 'Track your PTO use weekly to stay aligned.',
      trend:
        remainingNumber !== null
          ? remainingNumber <= 3
            ? 'Plan a recharge soon'
            : 'Balance looks healthy'
          : 'Awaiting HR sync',
      icon: '🌿',
      badgeBg: 'border border-slate-300 bg-slate-50 text-slate-700',
    },

    {
      id: 'leave-used',
      label: 'Days used',
      value: usedNumber !== null ? usedNumber : '--',
      subline: usedNumber !== null ? 'This year' : null,
      description: recentLeaveDate
        ? `Last request kicked off ${recentLeaveDate}.`
        : 'Log time off early for approvals.',
      trend: usedPercent !== null ? `${usedPercent}% of allowance utilized` : null,
      icon: '🗓️',
      badgeBg: 'border border-slate-300 bg-slate-50/80 text-slate-700',
    },

    {
      id: 'leave-total',
      label: 'Total requests',
      value: totalNumber !== null ? totalNumber : '--',
      subline: totalNumber === 1 ? 'Request filed' : 'Requests filed',
      description:
        totalNumber !== null
          ? 'Keep approvals transparent with quick updates.'
          : 'Submit requests to kickstart the review flow.',
      trend:
        totalNumber !== null
          ? totalNumber > 5
            ? 'High cadence of PTO'
            : 'Light request volume'
          : null,
      icon: null,
      badgeBg: 'border border-slate-300 bg-slate-50 text-slate-700',
    },
  ];

    },
    workspaceHighlights() {
      const announcement = this.projectAnnouncement || null;
      const upcomingEvents = Array.isArray(this.upcomingEvents) ? this.upcomingEvents : [];
      const nextEvent = upcomingEvents.length ? upcomingEvents[0] : null;
      const nextEventDate = nextEvent
        ? nextEvent.date_label || this.formatAbsoluteDate(nextEvent.date || nextEvent.event_date || nextEvent.start_date)
        : '';
      const nextEventBits = [
        nextEventDate,
        nextEvent ? nextEvent.time || nextEvent.time_label : '',
        nextEvent ? nextEvent.location || nextEvent.location_label : '',
      ].filter(Boolean);
      const nextEventDescription = nextEvent
        ? nextEventBits.join(' · ') || 'Details coming soon'
        : 'Add events to stay prepared for the week.';
      const remaining = this.leaveRemainingDays;
      const announcementDescription =
        (announcement && this.limitText(announcement.description, 140)) ||
        'Prioritize blockers, async updates, and clarity for the week.';
      const highlightIcons = {
        objective: '🎯',
        'next-event': '📅',
        balance: '🌿',
      };
      return [
        {
          id: 'objective',
          label: 'Current objective',
          title: (announcement && announcement.title) || 'Maintain sprint health',
          description: announcementDescription,
          icon: highlightIcons.objective,
        },
        {
          id: 'next-event',
          label: 'Next milestone',
          title: (nextEvent && nextEvent.title) || 'No upcoming events',
          description: nextEventDescription,
          icon: highlightIcons['next-event'],
        },
        {
          id: 'balance',
          label: 'Wellness watch',
          title: typeof remaining === 'number' ? `${remaining} days remaining` : 'Plan your recharge',
          description:
            typeof remaining === 'number'
              ? 'Use your balance intentionally for focus weeks and rest.'
              : 'Submit leave plans early to protect your wellness days.',
          icon: highlightIcons.balance,
        },
      ];
    },
    leaveSummaryRows() {
      const summary = (this.leaveSummary && this.leaveSummary.by_status) || {};
      const order = ['approved', 'pending', 'rejected', 'cancelled'];
      const ordered = order.filter((status) => summary[status]).map((status) => ({ status, count: summary[status] }));
      const others = Object.keys(summary)
        .filter((status) => !order.includes(status))
        .map((status) => ({ status, count: summary[status] }));
      return [...ordered, ...others];
    },
    totalLeaveRequests() {
      return this.leaveSummary && typeof this.leaveSummary.total === 'number' ? this.leaveSummary.total : 0;
    },
    leaveBalance() {
      return this.leaveSummary && this.leaveSummary.balance ? this.leaveSummary.balance : null;
    },
    leaveRemainingDays() {
      return this.leaveBalance ? this.leaveBalance.remaining_days : null;
    },
    leaveUsedDays() {
      return this.leaveBalance ? this.leaveBalance.used_days : null;
    },
    leaveAllowanceDays() {
      return this.leaveBalance ? this.leaveBalance.allowance_days : null;
    },
    minLeaveStartDate() {
      return this.getTodayISODate();
    },
    minLeaveEndDate() {
      const tomorrow = this.getTomorrowISODate();
      if (this.leaveForm && this.leaveForm.start_date) {
        return this.leaveForm.start_date > tomorrow ? this.leaveForm.start_date : tomorrow;
      }
      return tomorrow;
    },
    minResignLastDay() {
      return this.getTodayISODate();
    },
    unreadNotificationCount() {
      if (!Array.isArray(this.notifications)) {
        return 0;
      }
      return this.notifications.filter((item) => item && item.is_read === false).length;
    },
    normalizedNotifications() {
      if (!Array.isArray(this.notifications)) {
        return [];
      }
      const normalized = this.notifications.map((item) => ({
        id: item.id,
        title: item.title || 'Notification',
        message: item.message || '',
        createdAt: item.created_at || item.createdAt || null,
        isRead: item.is_read === undefined ? Boolean(item.isRead) : item.is_read === true,
        category: item.category || 'general',
        metadata: item.metadata || null,
      }));
      return normalized.sort((a, b) => {
        const aTime = a.createdAt ? new Date(a.createdAt).getTime() : 0;
        const bTime = b.createdAt ? new Date(b.createdAt).getTime() : 0;
        return bTime - aTime;
      });
    },
    notificationBellItems() {
      return this.normalizedNotifications.filter((item) => !item.isRead);
    },
    projectList() {
      return this.projectAssignments && Array.isArray(this.projectAssignments.assignments)
        ? this.projectAssignments.assignments
        : [];
    },
    projectSummaryText() {
      if (!this.projectAssignments) {
        return '';
      }
      const active = this.projectAssignments.active_count || 0;
      const total = this.projectAssignments.history_count || 0;
      if (!active && !total) {
        return '';
      }
      return `${active} active | ${total} total`;
    },
    teamMembers() {
      return this.teamOverview && Array.isArray(this.teamOverview.members) ? this.teamOverview.members : [];
    },
    teamEmptyMessage() {
      if (this.teamOverview && this.teamOverview.empty_message) {
        return this.teamOverview.empty_message;
      }
      return 'No teammates listed.';
    },
    chatbotHeadline() {
      if (this.chatbot) {
        return this.chatbot.headline || this.chatbot.subtitle || 'I can help with policy and leave questions!';
      }
      return 'I can help with policy and leave questions!';
    },
    chatbotSubtitle() {
      return this.chatbot && this.chatbot.subtitle ? this.chatbot.subtitle : '';
    },
    chatbotStatusLabel() {
      if (!this.chatbotStatus) {
        return '';
      }
      const mapping = {
        pending: 'We have escalated this question to HR for a personalised response.',
        auto_answered: 'Answered using verified HR policies.',
        error: 'We ran into an issue processing the question.',
        needs_confirmation: 'I need your permission to forward this to HR.',
      };
      return mapping[this.chatbotStatus] || this.chatbotStatus;
    },
    chatbotReferenceVisible() {
      return false;
    },
    showOffboardingCard() {
      return Boolean(this.resignationDetails);
    },
    offboardingCard() {
      if (this.resignationDetails) {
        return this.resignationDetails;
      }
      if (this.offboarding && this.offboarding.status && this.offboarding.status !== 'active') {
        return {
          status_label: this.offboarding.status_label || 'Offboarding in progress',
          message: this.offboarding.message || 'Please follow the shared exit checklist.',
          last_day: this.offboarding.last_updated || null,
          notice_period: this.offboarding.notice_period || null,
          handover_plan: null,
          notes: this.offboarding.pending_tasks ? `Tasks pending: ${this.offboarding.pending_tasks}` : null,
        };
      }
      return null;
    },
    resignDisabled() {
      if (this.resignationDetails) {
        return true;
      }
      if (this.offboarding && this.offboarding.status && this.offboarding.status !== 'active') {
        return true;
      }
      return false;
    },
    profileFields() {
      if (!this.profile) {
        return [];
      }
      return [
        { label: 'Address', value: this.profile.contact?.address || '-' },
        { label: 'Department', value: this.profile.department || '-' },

        { label: 'Role', value: this.profile.employment_role || '-' },
        {
          label: 'Manager',
          value: this.profile.manager && this.profile.manager.name ? this.profile.manager.name : '-',
        },
        { label: 'Joined', value: this.formatAbsoluteDate(this.profile.hire_date) },
        {
          label: 'Tenure',
          value: this.profile.tenure && this.profile.tenure.label ? this.profile.tenure.label : '-',
        },
        { label: 'Email', value: this.profile.contact?.email || '-' },
        { label: 'Phone', value: this.profile.contact?.phone || '-' },
      ];
    },
  },
  created() {
    this.restoreActiveTab();
    this.loadUserFromStorage();
    this.loadProjectAnnouncement();
    this.fetchDashboard();
  },
  mounted() {
    if (typeof window !== 'undefined') {
      window.addEventListener('storage', this.handleStorageEvent);
    }
  },
  beforeUnmount() {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
      this.toastTimer = null;
    }
    if (typeof window !== 'undefined') {
      window.removeEventListener('storage', this.handleStorageEvent);
    }
  },
  watch: {
    'resignForm.notice_period'(newVal) {
      if (!newVal) {
        this.resignForm.last_day = '';
        return;
      }
      // Map notice labels to days
      const mapping = {
        '2 weeks': 14,
        '30 days': 30,
        '60 days': 60,
      };
      const days = mapping[newVal];
      if (!days) {
        // 'Other' or unknown — don't auto-set a date
        return;
      }
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const target = new Date(today);
      target.setDate(target.getDate() + days);
      const yyyy = target.getFullYear();
      const mm = String(target.getMonth() + 1).padStart(2, '0');
      const dd = String(target.getDate()).padStart(2, '0');
      const newDateStr = `${yyyy}-${mm}-${dd}`;
      if (this.resignForm.last_day !== newDateStr) {
        this.resignForm.last_day = newDateStr;
      }
    },
    'resignForm.last_day'(newVal) {
      if (!newVal) {
        this.resignForm.notice_period = '';
        return;
      }
      // Parse selected date and compute difference from today
      const parts = newVal.split('-');
      if (parts.length < 3) {
        this.resignForm.notice_period = '';
        return;
      }
      const year = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10) - 1;
      const day = parseInt(parts[2], 10);
      const selected = new Date(year, month, day);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const diffMs = selected.getTime() - today.getTime();
      const days = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
      let derived = '';
      if (days <= 14) derived = '2 weeks';
      else if (days <= 30) derived = '30 days';
      else if (days <= 60) derived = '60 days';
      else if (days > 60) derived = 'Other';
      if (this.resignForm.notice_period !== derived) {
        this.resignForm.notice_period = derived;
      }
    },
  },
  methods: {
    handleNavClick(item) {
      if (item?.value === 'resign') {
        if (this.resignDisabled) {
          return
        }
        this.openResignModal()
        return
      }
      const nextTab = item?.value || 'overview'
      this.setActiveTab(nextTab)
      if (nextTab === 'notifications') {
        this.loadNotifications(true)
      }
    },
    goToLeaveSection() {
      this.setActiveTab('leave')
    },
    goToChatbot() {
      this.setActiveTab('chatbot')
    },
    limitText(value, limit = 140) {
      if (value === null || value === undefined) {
        return '';
      }
      const text = String(value).replace(/\s+/g, ' ').trim();
      if (!text) {
        return '';
      }
      if (!Number.isFinite(limit) || limit <= 0) {
        return text;
      }
      return text.length > limit ? `${text.slice(0, limit - 3)}...` : text;
    },
    loadUserFromStorage() {
      const raw = localStorage.getItem('currentUser');
      if (raw) {
        try {
          const parsed = JSON.parse(raw);
          const nameParts = [parsed.first_name, parsed.last_name].filter(Boolean);
          const fallback = parsed.full_name || parsed.username || parsed.email || this.currentUserName;
          this.currentUserName = nameParts.length ? nameParts.join(' ') : fallback;
        } catch (error) {
          console.warn('Unable to parse cached user', error);
        }
      }

      const savedToken = localStorage.getItem('authToken');
      if (savedToken) {
        axios.defaults.headers.common[AUTH_HEADER] = savedToken;
      } else {
        delete axios.defaults.headers.common[AUTH_HEADER];
      }
    },
    normalizeProjectAnnouncement(payload) {
      if (!payload) {
        return null;
      }
      let source = payload;
      if (typeof source === 'string') {
        const trimmed = source.trim();
        if (!trimmed) {
          return null;
        }
        try {
          source = JSON.parse(trimmed);
        } catch (error) {
          source = { description: trimmed };
        }
      }
      const title =
        typeof source.title === 'string'
          ? source.title.trim()
          : typeof source.project_title === 'string'
          ? source.project_title.trim()
          : '';
      const descriptionRaw =
        typeof source.description === 'string'
          ? source.description
          : typeof source.project_description === 'string'
          ? source.project_description
          : typeof source.body === 'string'
          ? source.body
          : '';
      const description = descriptionRaw.trim();
      if (!title && !description) {
        return null;
      }
      return {
        title,
        description,
        lastUpdated:
          source.lastUpdated ||
          source.last_updated ||
          source.updated_at ||
          source.timestamp ||
          new Date().toISOString(),
      };
    },
    persistProjectAnnouncement(payload) {
      try {
        if (payload) {
          localStorage.setItem(PROJECT_ANNOUNCEMENT_STORAGE_KEY, JSON.stringify(payload));
        } else {
          localStorage.removeItem(PROJECT_ANNOUNCEMENT_STORAGE_KEY);
        }
      } catch (error) {
        console.warn('Unable to persist project announcement', error);
      }
    },
    setProjectAnnouncement(payload, { persist = false } = {}) {
      const normalized = this.normalizeProjectAnnouncement(payload);
      this.projectAnnouncement = normalized;
      if (persist) {
        this.persistProjectAnnouncement(normalized);
      }
    },
    loadProjectAnnouncement() {
      try {
        const raw = localStorage.getItem(PROJECT_ANNOUNCEMENT_STORAGE_KEY);
        this.setProjectAnnouncement(raw ? JSON.parse(raw) : null);
      } catch (error) {
        console.warn('Unable to parse project announcement from local storage', error);
        this.projectAnnouncement = null;
      }
    },
    async fetchProjectAnnouncementFallback() {
      try {
        const response = await axios.get(`${API_BASE_URL}/employee/project-announcement`, {
          withCredentials: true,
        });
        const payload = response.data?.project_announcement;
        if (payload && (payload.title || payload.description)) {
          this.setProjectAnnouncement(payload, { persist: true });
          return;
        }
      } catch (error) {
        console.warn('Unable to load project announcement fallback', error);
      }
      if (!this.projectAnnouncement) {
        this.loadProjectAnnouncement();
      }
    },
    handleStorageEvent(event) {
      if (!event) {
        return;
      }
      if (event.key === PROJECT_ANNOUNCEMENT_STORAGE_KEY) {
        try {
          this.setProjectAnnouncement(event.newValue ? JSON.parse(event.newValue) : null);
        } catch (error) {
          console.warn('Unable to parse project announcement from storage event', error);
        }
      }
    },
    async fetchDashboard() {
      this.loading = true;
      this.error = '';
      try {
        const response = await axios.get(`${API_BASE_URL}/employee/dashboard`, { withCredentials: true });
        const data = response.data || {};
        this.profile = data.profile || null;
        this.leaveSummary = data.leave_summary || null;
        this.recentLeaves = (data.recent_leaves || [])
          .map((leave) => this.decorateLeave(leave))
          .filter((leave) => !this.isOffboardingLeave(leave));
        this.upcomingEvents = data.upcoming_events || [];
        this.notifications = data.notifications || [];
        this.projectAssignments = data.project_assignments || null;
        this.teamOverview = data.team_overview || null;
        this.chatbot = data.chatbot || null;
        this.offboarding = data.offboarding || null;
        const incomingAnnouncement = data.project_announcement;
        if (incomingAnnouncement && (incomingAnnouncement.title || incomingAnnouncement.description)) {
          this.setProjectAnnouncement(incomingAnnouncement, { persist: true });
        } else {
          await this.fetchProjectAnnouncementFallback();
        }
        await this.loadHrQuestions();
        if (this.profile && this.profile.job_title && !this.careerForm.current_role) {
          this.careerForm.current_role = this.profile.job_title;
        }
      } catch (error) {
        console.error('Failed to load dashboard', error);
        const message =
          (error.response && (error.response.data?.error || error.response.data?.message)) ||
          error.message ||
          'Unable to load dashboard right now.';
        this.error = message;
        if (error.response && error.response.status === 401) {
          this.redirectToLogin();
        }
      } finally {
        this.loading = false;
      }
    },
    async loadNotifications(force = false) {
      if (this.notificationsLoading) {
        return;
      }
      if (!force && this.notifications.length && !this.unreadNotificationCount) {
        return;
      }
      this.notificationsLoading = true;
      this.notificationsError = '';
      try {
        const response = await axios.get(`${API_BASE_URL}/notifications`, {
          withCredentials: true,
        });
        const data = response.data || {};
        this.notifications = data.notifications || [];
      } catch (error) {
        console.error('Failed to load notifications', error);
        const message =
          (error.response && (error.response.data?.error || error.response.data?.message)) ||
          error.message ||
          'Unable to load notifications.';
        this.notificationsError = message;
      } finally {
        this.notificationsLoading = false;
      }
    },
    async markNotificationRead(notification, { remove = false } = {}) {
      if (!notification) {
        return;
      }
      if (!notification.isRead) {
        try {
          await axios.post(
            `${API_BASE_URL}/notifications/${notification.id}/read`,
            {},
            { withCredentials: true }
          );
        } catch (error) {
          console.error('Failed to mark notification as read', error);
        }
      }
      this.notifications = this.notifications.map((item) =>
        item.id === notification.id
          ? { ...item, is_read: true, isRead: true }
          : item
      );
      if (remove) {
        this.notifications = this.notifications.filter((item) => item.id !== notification.id);
      }
    },
    async toggleNotifications() {
      if (this.showNotifications) {
        this.showNotifications = false;
        return;
      }
      this.showNotifications = true;
      await this.loadNotifications(true);
    },
    closeNotifications() {
      this.showNotifications = false;
    },
    async dismissNotification(notification) {
      await this.markNotificationRead(notification, { remove: true });
    },
    async loadHrQuestions() {
      this.hrQuestionsLoading = true;
      this.hrQuestionsError = '';
      try {
        const response = await axios.get(`${API_BASE_URL}/hr/questions`, {
          params: { status: 'pending,resolved' },
          withCredentials: true,
        });
        const data = response.data || {};
        const questions = Array.isArray(data.questions) ? data.questions : [];
        this.hrQuestions = questions.map((item) => this.decorateHrQuestion(item));
      } catch (error) {
        console.error('Failed to load HR questions', error);
        const message =
          (error.response && (error.response.data?.error || error.response.data?.message)) ||
          error.message ||
          'Unable to load HR questions.';
        this.hrQuestionsError = message;
        this.hrQuestions = [];
      } finally {
        this.hrQuestionsLoading = false;
      }
    },
    decorateHrQuestion(question) {
      const createdAt = question.created_at || question.createdAt || null;
      const updatedAt = question.updated_at || question.updatedAt || null;
      return {
        ...question,
        createdAt,
        updatedAt,
        submittedAtReadable: createdAt ? this.formatAbsoluteDate(createdAt) : '-',
        updatedAtReadable: updatedAt ? this.formatRelativeDate(updatedAt) : '',
        statusClass: this.statusToClass(question.status),
        hasAnswer: Boolean(question.answer),
      };
    },
    redirectToLogin() {
      localStorage.removeItem('currentUser');
      localStorage.removeItem('activeUserRole');
      this.$router.push({ name: 'LoginPage', query: { redirect: this.$route.fullPath } });
    },
    formatStatus(status) {
      if (!status) {
        return 'Unknown';
      }
      const text = status.toString().toLowerCase();
      return text.charAt(0).toUpperCase() + text.slice(1);
    },
    formatLeaveType(type) {
      if (!type) {
        return 'General';
      }
      const text = type.toString().replace(/[_-]/g, ' ');
      return text.charAt(0).toUpperCase() + text.slice(1);
    },
    decorateLeave(leave) {
      const startDate = this.parseISODate(leave.start_date);
      const endDate = this.parseISODate(leave.end_date);
      return {
        ...leave,
        startDate,
        endDate,
        dateRange: this.formatDateRange(startDate, endDate),
        statusClass: this.statusToClass(leave.status),
      };
    },
    isOffboardingLeave(leave) {
      if (!leave) {
        return false;
      }
      const type = (
        (leave.leave_type || leave.request_type || '')
          .toString()
          .trim()
          .toLowerCase()
      );
      return OFFBOARDING_LEAVE_TYPES.includes(type);
    },
    parseISODate(value) {
      const parsed = parseKolkataISODate(value);
      if (parsed) {
        return parsed;
      }
      const fallback = new Date(value);
      return Number.isNaN(fallback.getTime()) ? null : fallback;
    },
    formatDateForInput(date) {
      return formatKolkataDateForInput(date);
    },
    getTodayISODate() {
      const today = getKolkataToday();
      return formatKolkataDateForInput(today);
    },
    getTomorrowISODate() {
      const tomorrow = getKolkataTomorrow();
      return formatKolkataDateForInput(tomorrow);
    },
    addDaysToISODate(isoValue, days = 1) {
      const base = this.parseISODate(isoValue);
      if (!base) {
        return '';
      }
      const updated = addKolkataDays(base, days);
      return formatKolkataDateForInput(updated);
    },
    formatDateRange(start, end) {
      if (!start) {
        return '-';
      }
      const from = this.formatAbsoluteDate(start);
      if (!end) {
        return from;
      }
      if (start.getTime() === end.getTime()) {
        return from;
      }
      return `${from} - ${this.formatAbsoluteDate(end)}`;
    },
    formatAbsoluteDate(value) {
      if (!value) {
        return '-';
      }
      const date = value instanceof Date ? value : this.parseISODate(value);
      if (!date || Number.isNaN(date.getTime())) {
        return '-';
      }
      return date.toLocaleDateString('en-IN', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        timeZone: 'Asia/Kolkata',
      });
    },
    formatRelativeDate(value) {
      if (!value) {
        return '';
      }
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) {
        return '';
      }
      const diffMs = Date.now() - date.getTime();
      const minutes = Math.round(diffMs / 60000);
      if (minutes < 1) {
        return 'Just now';
      }
      if (minutes < 60) {
        return `${minutes} min ago`;
      }
      const hours = Math.round(minutes / 60);
      if (hours < 24) {
        return `${hours} hr${hours === 1 ? '' : 's'} ago`;
      }
      const days = Math.round(hours / 24);
      if (days < 7) {
        return `${days} day${days === 1 ? '' : 's'} ago`;
      }
      return this.formatAbsoluteDate(date);
    },
    truncateText(text, limit = 120) {
      if (!text) {
        return '';
      }
      const value = text.toString();
      if (value.length <= limit) {
        return value;
      }
      return `${value.slice(0, limit).trim()}...`;
    },
    statusToClass(status) {
      const text = (status || '').toString().toLowerCase();
      if (text === 'approved') {
        return 'success';
      }
      if (text === 'pending') {
        return 'warning';
      }
      if (text === 'rejected' || text === 'cancelled') {
        return 'danger';
      }
      return 'muted';
    },
    canWithdraw(leave) {
      const status = (leave.status || '').toString().toLowerCase();
      if (status !== 'pending') {
        return false;
      }
      if (!leave.startDate) {
        return true;
      }
      const today = startOfKolkataDay(new Date());
      return today ? leave.startDate.getTime() >= today.getTime() : false;
    },
    openLeaveModal() {
      this.leaveFormError = '';
      const todayISO = this.getTodayISODate();
      if (!this.leaveForm.start_date || this.leaveForm.start_date < todayISO) {
        this.leaveForm.start_date = todayISO;
      }
      const nextDay = this.addDaysToISODate(this.leaveForm.start_date, 1) || this.getTomorrowISODate();
      if (!this.leaveForm.end_date || this.leaveForm.end_date < this.leaveForm.start_date) {
        this.leaveForm.end_date = nextDay;
      }
      this.showLeaveModal = true;
    },
    closeLeaveModal() {
      this.showLeaveModal = false;
      this.leaveFormError = '';
      this.leaveForm = { leave_type: 'annual', start_date: '', end_date: '', reason: '' };
    },
    openCareerModal() {
      this.careerFormError = ''
      if (this.profile && this.profile.job_title && !this.careerForm.current_role) {
        this.careerForm.current_role = this.profile.job_title
      }
      this.activeTab = 'career'
    },
    resetCareerForm() {
      this.careerFormError = ''
      this.submittingCareerForm = false
      this.careerForm = {
        current_role: this.profile && this.profile.job_title ? this.profile.job_title : '',
        target_role: '',
        strengths: '',
        focus_areas: '',
        learning_style: 'online',
        timeline: '6-12',
        guidance_goal: '',
      }
    },
    async submitCareerForm() {
      this.careerFormError = ''
      if (!this.careerForm.target_role) {
        this.careerFormError = 'Please share the role you are aiming for.'
        return
      }
      this.submittingCareerForm = true
      try {
        const payload = {
          current_role: this.careerForm.current_role,
          target_role: this.careerForm.target_role,
          strengths: this.careerForm.strengths,
          focus_areas: this.careerForm.focus_areas,
          learning_style: this.careerForm.learning_style,
          timeline: this.careerForm.timeline,
          support_needed: this.careerForm.guidance_goal,
        }

        const res = await axios.post(`${API_BASE_URL}/genai/careerpath`, payload, { withCredentials: true })
        const recommendation = res.data?.recommendation || ''
        if (!recommendation) {
          this.careerFormError = 'No recommendation returned. Please try again.'
          return
        }

        this.careerRecommendation = recommendation
        this.showCareerRecommendation = true
        this.showToast('Personalised recommendation ready.', 'success')
      } catch (error) {
        console.error('Failed to generate career plan', error);
        const serverMsg = error?.response?.data?.error || error?.response?.data?.message || error?.message;
        this.careerFormError = serverMsg || 'Unable to prepare a plan right now. Please try again.';
      } finally {
        this.submittingCareerForm = false;
      }
    },

    async downloadCareerPdf() {
      if (!this.careerRecommendation) return
      this.downloadingCareerPdf = true
      try {
        const res = await axios.post(`${API_BASE_URL}/genai/careerpath/pdf`, { recommendation: this.careerRecommendation }, {
          responseType: 'blob',
          withCredentials: true,
        })
        const blob = new Blob([res.data], { type: 'application/pdf' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'careerplan.pdf'
        document.body.appendChild(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Failed to download career PDF', err)
        this.showToast('Unable to download PDF right now.', 'error')
      } finally {
        this.downloadingCareerPdf = false
      }
    },
    async submitLeaveForm() {
      this.leaveFormError = '';
      if (!this.leaveForm.start_date || !this.leaveForm.end_date) {
        this.leaveFormError = 'Please choose a start and end date.';
        return;
      }
      const todayISO = this.getTodayISODate();
      if (this.leaveForm.start_date < todayISO) {
        this.leaveFormError = 'Start date cannot be before today.';
        return;
      }
      if (this.leaveForm.end_date < this.leaveForm.start_date) {
        this.leaveFormError = 'End date cannot be earlier than start date.';
        return;
      }
      const requiredEnd = this.minLeaveEndDate;
      if (this.leaveForm.end_date < requiredEnd) {
        this.leaveFormError = `End date must be on or after ${this.formatAbsoluteDate(requiredEnd)}.`;
        return;
      }
      this.submittingLeave = true;
      try {
        await axios.post(
          `${API_BASE_URL}/leave/apply`,
          {
            leave_type: this.leaveForm.leave_type,
            start_date: this.leaveForm.start_date,
            end_date: this.leaveForm.end_date,
            reason: this.leaveForm.reason,
          },
          { withCredentials: true },
        );
        this.showToast('Leave request submitted.', 'success');
        this.closeLeaveModal();
        await this.fetchDashboard();
      } catch (error) {
        console.error('Failed to submit leave request', error);
        const message =
          (error.response && (error.response.data?.error || error.response.data?.message)) ||
          error.message ||
          'Unable to submit leave request.';
        this.leaveFormError = message;
      } finally {
        this.submittingLeave = false;
      }
    },
    async withdrawLeave(leave) {
      if (!leave || !leave.id) {
        return;
      }
      if (!window.confirm('Withdraw this leave request?')) {
        return;
      }
      this.withdrawProcessing = { ...this.withdrawProcessing, [leave.id]: true };
      try {
        await axios.post(`${API_BASE_URL}/leave/${leave.id}/cancel`, {}, { withCredentials: true });
        this.showToast('Leave request withdrawn.', 'success');
        await this.fetchDashboard();
      } catch (error) {
        console.error('Failed to withdraw leave', error);
        const message =
          (error.response && (error.response.data?.error || error.response.data?.message)) ||
          error.message ||
          'Unable to withdraw leave request.';
        this.showToast(message, 'error');
      } finally {
        const next = { ...this.withdrawProcessing };
        delete next[leave.id];
        this.withdrawProcessing = next;
      }
    },
    openFeedback() {
      this.feedbackError = '';
      this.showFeedbackModal = true;
    },
    closeFeedbackModal() {
      this.showFeedbackModal = false;
      this.feedbackError = '';
      this.feedbackForm = { subject: '', rating: '', message: '' };
    },
    async submitFeedback() {
      this.feedbackError = '';
      if (!this.feedbackForm.message) {
        this.feedbackError = 'Please add a message.';
        return;
      }
      this.submittingFeedback = true;
      try {
        await axios.post(
          `${API_BASE_URL}/employee/feedback`,
          {
            subject: this.feedbackForm.subject || 'General',
            rating: this.feedbackForm.rating || null,
            message: this.feedbackForm.message,
          },
          { withCredentials: true },
        );
        this.showToast('Thanks for sharing your feedback!', 'success');
        this.closeFeedbackModal();
      } catch (error) {
        console.error('Failed to submit feedback', error);
        const message =
          (error.response && (error.response.data?.error || error.response.data?.message)) ||
          error.message ||
          'Unable to send feedback.';
        this.feedbackError = message;
      } finally {
        this.submittingFeedback = false;
      }
    },
    openChatbot() {
      this.resetChatbot()
      this.activeTab = 'chatbot'
    },
    resetChatbot() {
      this.chatbotPrompt = ''
      this.chatbotReply = ''
      this.chatbotLoading = false
      this.chatbotStatus = ''
      this.chatbotReference = ''
      this.chatbotReferenceSource = ''
      this.chatbotTicketId = null
      this.chatHistory = []
      this.pendingEscalationQuestion = ''
      this.chatbotNeedsEscalation = false
      this.chatbotConversationId = null
      this.chatbotEscalating = false
    },
    async submitChatbotPrompt() {
      if (!this.chatbotPrompt) {
        return;
      }
      const submittedQuestion = this.chatbotPrompt;
      const pendingMessage = {
        sender: 'user',
        content: submittedQuestion,
        timestamp: new Date().toISOString(),
      };
      this.chatHistory = [...this.chatHistory, pendingMessage];
      this.chatbotLoading = true;
      this.chatbotNeedsEscalation = false;
      this.pendingEscalationQuestion = '';
      try {
        const response = await axios.post(
          `${API_BASE_URL}/employee/chatbot`,
          { message: submittedQuestion },
          { withCredentials: true },
        );
        const payload = response.data || {};
        const previousHistory = Array.isArray(this.chatHistory) ? [...this.chatHistory] : [];
        const normalizeTimestamp = (value) => {
          if (!value) {
            return new Date().toISOString();
          }
          const strValue = typeof value === 'string' ? value : String(value);
          const hasTimezoneSuffix = /([zZ]|[+-]\d\d:\d\d)$/.test(strValue);
          const parsed = new Date(hasTimezoneSuffix ? strValue : `${strValue}Z`);
          if (Number.isNaN(parsed.getTime())) {
            return new Date().toISOString();
          }
          return parsed.toISOString();
        };
        const usedPreviousIndexes = new Set();
        const findPreviousUserMatch = (entry) => {
          for (let i = previousHistory.length - 1; i >= 0; i -= 1) {
            if (usedPreviousIndexes.has(i)) {
              continue;
            }
            const candidate = previousHistory[i];
            if (!candidate || candidate.sender !== 'user') {
              continue;
            }
            const sameContent = (candidate.content || '') === (entry.content || '');
            if (sameContent) {
              usedPreviousIndexes.add(i);
              return candidate;
            }
          }
          return null;
        };
        const normalizeMessage = (entry) => ({
          sender: entry.sender || 'assistant',
          content: entry.content || '',
          timestamp: normalizeTimestamp(entry.timestamp),
        });
        if (Array.isArray(payload.messages) && payload.messages.length) {
          this.chatHistory = payload.messages.map((entry) => {
            const normalized = normalizeMessage(entry);
            if (normalized.sender === 'user') {
              const previousMatch = findPreviousUserMatch(normalized);
              if (previousMatch && previousMatch.timestamp) {
                return { ...normalized, timestamp: previousMatch.timestamp };
              }
            }
            return normalized;
          });
        } else {
          const assistantMessage = normalizeMessage({
            sender: 'assistant',
            content: payload.response || 'HR bot has recorded your message.',
          });
          this.chatHistory = [...this.chatHistory, assistantMessage];
        }
        this.chatbotReply =
          payload.response ||
          (Array.isArray(payload.messages)
            ? payload.messages
                .filter((msg) => msg.sender !== 'user')
                .map((msg) => msg.content)
                .filter(Boolean)
                .pop() || ''
            : '');
        this.chatbotStatus = payload.status || '';
        this.chatbotReference = payload.reference || '';
        this.chatbotReferenceSource = payload.reference_source || '';
        this.chatbotTicketId = payload.question_log_id || null;
        this.chatbotConversationId = payload.conversation_id || this.chatbotConversationId;
        const unresolvedStatuses = ['needs_confirmation', 'out_of_scope'];
        if (unresolvedStatuses.includes(this.chatbotStatus)) {
          this.pendingEscalationQuestion = submittedQuestion;
          this.chatbotNeedsEscalation = true;
        } else {
          this.pendingEscalationQuestion = '';
          this.chatbotNeedsEscalation = false;
        }
        if (this.chatbotStatus === 'pending') {
          this.showToast('Your question has been escalated to HR. We will follow up soon.', 'info');
        }
        this.chatbotPrompt = '';
      } catch (error) {
        console.error('Chatbot request failed', error);
        const message =
          (error.response && (error.response.data?.error || error.response.data?.message)) ||
          error.message ||
          'Unable to send message right now.';
        this.showToast(message, 'error');
        this.chatbotStatus = 'error';
        this.chatbotReference = '';
        this.chatbotReferenceSource = '';
        this.chatbotTicketId = null;
        this.chatHistory = [
          ...this.chatHistory,
          {
            sender: 'assistant',
            content: 'Something went wrong while reaching HR. Please try again shortly.',
            timestamp: new Date().toISOString(),
          },
        ];
      } finally {
        this.chatbotLoading = false;
      }
    },
    async confirmChatbotEscalation() {
        if (!this.pendingEscalationQuestion || this.chatbotEscalating) {
          return;
        }
        this.chatbotEscalating = true;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/employee/chatbot/escalate`,
          {
            message: this.pendingEscalationQuestion,
            conversation_id: this.chatbotConversationId || null,
          },
          { withCredentials: true },
        );
        const payload = response.data || {};
        const messages = Array.isArray(payload.messages) ? payload.messages : [];
        if (messages.length) {
          const normalized = messages.map((entry) => ({
            sender: entry.sender || 'assistant',
            content: entry.content || '',
            timestamp: entry.timestamp || new Date().toISOString(),
          }));
          this.chatHistory = [...this.chatHistory, ...normalized];
        }
        this.chatbotStatus = payload.status || 'pending';
        this.chatbotReference = payload.reference || '';
        this.chatbotReferenceSource = payload.reference_source || '';
        this.chatbotTicketId = payload.question_log_id || null;
        this.chatbotConversationId = payload.conversation_id || this.chatbotConversationId;
        this.chatbotNeedsEscalation = false;
        this.pendingEscalationQuestion = '';
        this.showToast('Your question was forwarded to HR.', 'info');
      } catch (error) {
        console.error('Failed to escalate chatbot question', error);
        const message =
          (error.response && (error.response.data?.error || error.response.data?.message)) ||
          error.message ||
          'Unable to forward the question to HR.';
        this.showToast(message, 'error');
      } finally {
        this.chatbotEscalating = false;
      }
    },
    cancelChatbotEscalation() {
      if (!this.chatbotNeedsEscalation) {
        return;
      }
      this.chatbotNeedsEscalation = false;
      this.pendingEscalationQuestion = '';
      this.showToast('Okay, I will not forward that question.', 'info');
    },
    openProfileModal() {
      this.profileFormError = ''
      this.profileSaving = false
      this.editingProfile = false
      this.showProfileModal = true
      this.populateEditableProfile()
    },
    closeProfileModal() {
      this.showProfileModal = false;
      this.editingProfile = false
      this.profileSaving = false
      this.profileFormError = ''
    },
    async populateEditableProfile() {
      const snapshot = this.profile || {}
      const contact = snapshot.contact || {}
      const nameParts = (snapshot.full_name || '').trim().split(/\s+/).filter(Boolean)
      const fallbackFirst = this.rawProfile?.first_name || nameParts[0] || ''
      const fallbackLast = this.rawProfile?.last_name || nameParts.slice(1).join(' ') || ''
      this.editableProfile = {
        first_name: fallbackFirst,
        last_name: fallbackLast,
        job_title: snapshot.job_title || this.rawProfile?.job_title || '',
        department: snapshot.department || this.rawProfile?.department || '',
        team_number: snapshot.team_number || this.rawProfile?.team_number || '',
        phone: contact.phone || this.rawProfile?.phone || '',
        address: contact.address || this.rawProfile?.address || '',
      }
      try {
        const response = await axios.get(`${API_BASE_URL}/me`, { withCredentials: true })
        const user = response.data && response.data.user
        if (user) {
          this.rawProfile = user
          this.editableProfile = {
            first_name: user.first_name || '',
            last_name: user.last_name || '',
            job_title: user.job_title || '',
            department: user.department || '',
            team_number: user.team_number || '',
            phone: user.phone || '',
            address: user.address || '',
          }
        }
      } catch (error) {
        console.warn('Unable to load profile details', error)
      }
    },
    startEditingProfile() {
      this.editingProfile = true
      if (!this.editableProfile || !this.editableProfile.first_name) {
        this.populateEditableProfile()
      }
    },
    cancelEditingProfile() {
      this.editingProfile = false
      this.profileFormError = ''
      this.profileSaving = false
      this.populateEditableProfile()
    },
    async saveProfileDetails() {
      this.profileFormError = ''
      const payload = {
        first_name: this.editableProfile.first_name?.trim() || '',
        last_name: this.editableProfile.last_name?.trim() || '',
        job_title: this.editableProfile.job_title?.trim() || '',
        department: this.editableProfile.department?.trim() || '',
        team_number: this.editableProfile.team_number?.trim() || '',
        phone: this.editableProfile.phone?.trim() || '',
        address: this.editableProfile.address?.trim() || '',
      }
      this.profileSaving = true
      try {
        const response = await axios.put(`${API_BASE_URL}/me`, payload, { withCredentials: true })
        const updatedUser = response.data && (response.data.user || response.data.profile)
        if (updatedUser) {
          this.applyUpdatedProfile(updatedUser)
        }
        this.editingProfile = false
        this.showToast('Profile updated successfully.', 'success')
      } catch (error) {
        console.error('Failed to update profile', error)
        this.profileFormError =
          (error.response && (error.response.data?.error || error.response.data?.message)) ||
          error.message ||
          'Unable to update profile right now.'
      } finally {
        this.profileSaving = false
      }
    },
    applyUpdatedProfile(user) {
      this.rawProfile = user
      const fullNameParts = [user.first_name, user.last_name].filter((part) => part && part.trim())
      const fullName = fullNameParts.join(' ') || user.username || user.email
      const existing = this.profile || {}
      const contact = existing.contact || {}
      this.profile = {
        ...existing,
        full_name: fullName || existing.full_name,
        job_title: user.job_title ?? existing.job_title,
        department: user.department ?? existing.department,
        team_number: user.team_number ?? existing.team_number,
        employee_id: user.employee_id ?? existing.employee_id,
        employment_role: user.employment_role ?? existing.employment_role,
        contact: {
          ...contact,
          email: user.email || contact.email,
          phone: user.phone || contact.phone,
          address: user.address || contact.address,
        },
      }
      if (fullName) {
        this.currentUserName = fullName
      }
    },
    openResignModal() {
      if (this.resignDisabled) {
        return;
      }
      this.resignFormError = '';
      const todayISO = this.getTodayISODate();
      if (!this.resignForm.last_day || this.resignForm.last_day < todayISO) {
        this.resignForm.last_day = todayISO;
      }
      this.showResignModal = true;
    },
    closeResignModal() {
      this.showResignModal = false;
      this.resignFormError = '';
    },
    submitResignForm() {
      this.resignFormError = ''
      if (!this.resignForm.last_day) {
        this.resignFormError = 'Please select your planned last working day.'
        return
      }
      // Last working day must not be in the past
      try {
        const parts = (this.resignForm.last_day || '').split('-')
        if (parts.length === 3) {
          const selected = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10))
          const today = new Date();
          today.setHours(0,0,0,0);
          if (selected.getTime() < today.getTime()) {
            this.resignFormError = 'Last working day cannot be before today.'
            return
          }
        }
      } catch (e) {
        // ignore parsing errors; validation will block submission if needed
      }
      if (!this.resignForm.reason.trim()) {
        this.resignFormError = 'Please share a short reason for resigning.'
        return
      }
      const payload = {
        last_day: this.resignForm.last_day,
        reason: this.resignForm.reason.trim(),
      }
      const token = localStorage.getItem('authToken')
      const headers = token ? { 'Authentication-Token': token } : {}
      this.loading = true
      axios
        .post(`${API_BASE_URL}/offboarding/resign`, payload, { headers })
        .then(() => {
          // Use the returned tasks / leave request if needed
          this.showToast('Resignation request submitted to HR.', 'success')
          this.resignationDetails = {
            status_label: 'Offboarding started',
            message: 'Your resignation has been recorded. HR will contact you.',
            last_day: this.resignForm.last_day,
            reason: this.resignForm.reason.trim(),
          }
          this.closeResignModal()
          this.resignForm = {
            last_day: '',
            notice_period: '',
            reason: '',
            handover_plan: '',
            notes: '',
          }
        })
        .catch((error) => {
          const errMsg = error?.response?.data?.error || error.message || 'Failed to submit resignation'
          this.resignFormError = errMsg
        })
        .finally(() => {
        this.loading = false
      })
    },
    setActiveTab(value) {
      const nextTab = this.isValidTab(value) ? value : 'overview';
      this.activeTab = nextTab;
      this.persistActiveTab(nextTab);
    },
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    showToast(message, type = 'info', duration = 4000) {
      if (this.toastTimer) {
        clearTimeout(this.toastTimer);
        this.toastTimer = null;
      }
      this.toast = { message, type };
      this.toastTimer = setTimeout(() => {
        this.toast = null;
        this.toastTimer = null;
      }, duration);
    },
    dismissToast() {
      if (this.toastTimer) {
        clearTimeout(this.toastTimer);
        this.toastTimer = null;
      }
      this.toast = null;
    },
    async logout() {
      try {
        await axios.post(`${API_BASE_URL}/logout`, {}, { withCredentials: true });
      } catch (error) {
        console.warn('Logout request failed', error);
      } finally {
        localStorage.removeItem('currentUser');
        localStorage.removeItem('authToken');
        localStorage.removeItem('activeUserRole');
        localStorage.removeItem(ACTIVE_TAB_STORAGE_KEY);
        delete axios.defaults.headers.common[AUTH_HEADER];
        this.$router.push({ name: 'HomePage' });
      }
    },
    isValidTab(value) {
      return ALLOWED_TABS.includes(value);
    },
    canUseStorage() {
      return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
    },
    persistActiveTab(value) {
      if (!this.canUseStorage()) {
        return;
      }
      try {
        window.localStorage.setItem(ACTIVE_TAB_STORAGE_KEY, value);
      } catch (error) {
        console.warn('Unable to persist active tab', error);
      }
    },
    restoreActiveTab() {
      if (!this.canUseStorage()) {
        return;
      }
      try {
        const stored = window.localStorage.getItem(ACTIVE_TAB_STORAGE_KEY);
        if (stored && this.isValidTab(stored)) {
          this.activeTab = stored;
        }
      } catch (error) {
        console.warn('Unable to restore active tab', error);
      }
    },
  },
};
</script>

