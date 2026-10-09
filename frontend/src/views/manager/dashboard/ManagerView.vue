<template>
<div class="min-h-screen bg-[#f9f9f9] text-slate-900 flex w-full font-sans" @click="closeNotifications">
  <aside
    :class="[
      'hidden lg:flex bg-white/95 text-slate-700 flex-col fixed inset-y-0 border-r border-slate-200 shadow-[0_25px_60px_rgba(15,23,42,0.12)] z-40 transition-all duration-300',
      sidebarCollapsed ? 'w-20' : 'w-72'
    ]"
  >
    <div class="relative border-b border-slate-200/80 p-6 bg-white/90">
      <button
        class="absolute -right-3 top-6 rounded-full bg-slate-100 border border-slate-300 text-slate-500 p-1.5 transition hover:bg-slate-200 hover:shadow"
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
        <h1 class="mt-1 text-xl font-bold text-slate-900">Manager Hub</h1>
        <p class="mt-1 text-sm text-slate-500">Lead teams with clarity and keep approvals flowing.</p>
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

      // --- SPECIAL RESIGN BUTTON ---
      item.value === 'resign'
        ? activeTab === 'resign'
          ? 'bg-rose-100 text-rose-900 border-rose-300 font-semibold shadow-sm'
          : 'bg-white/80 text-rose-600 border-transparent hover:border-rose-300 hover:text-rose-900'
        :

      // --- DEFAULT COLOR THEME SAME AS EMPLOYEE DASHBOARD ---
      activeTab === item.value
        ? 'bg-slate-100 text-slate-900 border-slate-300 font-semibold shadow-sm'
        : 'bg-white/80 text-slate-600 border-transparent hover:border-slate-200 hover:text-slate-900',

      item.value === 'resign' && resignDisabled ? 'cursor-not-allowed opacity-60' : ''
    ]"
  >

    <div :class="['flex items-center gap-3', sidebarCollapsed ? '' : 'flex-1']">
      
      <!-- ICON COLOR SYSTEM IDENTICAL TO EMPLOYEE UI -->
      <span
        :class="[
          'flex h-9 w-9 items-center justify-center border transition-all duration-200 rounded-lg',

          // --- RESIGN ---
          item.value === 'resign'
            ? activeTab === 'resign'
              ? 'border-rose-500 bg-rose-600 text-white'
              : 'border-transparent bg-rose-500 text-white group-hover:bg-rose-600'

          // --- OVERVIEW (BLUE) ---
          : item.value === 'overview'
            ? activeTab === 'overview'
              ? 'border-blue-500 bg-blue-600 text-white'
              : 'border-transparent bg-blue-500 text-white group-hover:bg-blue-600'

          // --- PROJECTS (PURPLE) ---
          : item.value === 'projects'
            ? activeTab === 'projects'
              ? 'border-purple-500 bg-purple-600 text-white'
              : 'border-transparent bg-purple-500 text-white group-hover:bg-purple-600'

          // --- PEOPLE / TEAM (SKY BLUE) ---
          : item.value === 'people'
            ? activeTab === 'people'
              ? 'border-sky-500 bg-sky-600 text-white'
              : 'border-transparent bg-sky-500 text-white group-hover:bg-sky-600'

          // --- LEAVES (GREEN) ---
          : item.value === 'leaves'
            ? activeTab === 'leaves'
              ? 'border-green-500 bg-green-600 text-white'
              : 'border-transparent bg-green-500 text-white group-hover:bg-green-600'

          // --- APPROVALS (AMBER) ---
          : item.value === 'approvals'
            ? activeTab === 'approvals'
              ? 'border-amber-500 bg-amber-600 text-white'
              : 'border-transparent bg-amber-500 text-white group-hover:bg-amber-600'

          // --- SUPPORT (YELLOW/AMBER LIGHT) ---
          : item.value === 'support'
            ? activeTab === 'support'
              ? 'border-amber-500 bg-amber-600 text-white'
              : 'border-transparent bg-amber-500 text-white group-hover:bg-amber-600'

          // --- CHATBOT (INDIGO) ---
          : item.value === 'chatbot'
            ? activeTab === 'chatbot'
              ? 'border-indigo-500 bg-indigo-600 text-white'
              : 'border-transparent bg-indigo-500 text-white group-hover:bg-indigo-600'

          // --- CAREER (PINK) ---
          : item.value === 'career'
            ? activeTab === 'career'
              ? 'border-pink-500 bg-pink-600 text-white'
              : 'border-transparent bg-pink-500 text-white group-hover:bg-pink-600'

          // --- NOTIFICATIONS (ROSE) ---
          : item.value === 'notifications'
            ? activeTab === 'notifications'
              ? 'border-rose-500 bg-rose-600 text-white'
              : 'border-transparent bg-rose-500 text-white group-hover:bg-rose-600'

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
    <div class="p-4 border-t border-emerald-100/70 space-y-3 bg-white/90">
      <div
        :class="[
          'flex items-center gap-3 rounded-xl border border-emerald-100 bg-white/90 p-3 shadow-sm',
          sidebarCollapsed ? 'justify-center' : ''
        ]"
      >
        <button
          :class="[
            'flex items-center gap-2 rounded-xl bg-transparent text-sm font-semibold text-emerald-700 transition hover:bg-emerald-50 hover:text-emerald-900 focus:outline-none focus:ring-2 focus:ring-emerald-200',
            sidebarCollapsed ? 'h-12 w-12 justify-center p-0' : 'w-full px-4 py-2'
          ]"
          type="button"
          :title="sidebarCollapsed ? 'Logout' : ''"
          @click="logout"
        >
          <ArrowRightOnRectangleIcon class="h-5 w-5 text-emerald-500" aria-hidden="true" />
          <span v-if="!sidebarCollapsed">Logout</span>
        </button>
      </div>
    </div>
  </aside>

  <div :class="['flex-1 w-full flex flex-col min-h-screen transition-all duration-300', sidebarCollapsed ? 'lg:ml-20' : 'lg:ml-72']">
    <header class="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div class="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 md:px-8">
        <div class="flex w-full flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div class="mx-auto flex flex-col items-center text-center lg:flex-1">
            <p class="text-xs uppercase tracking-[0.35em] text-slate-500 font-semibold">Manager workspace</p>
            <p class="text-sm text-slate-500">Quick access to projects, people updates, and leave analytics.</p>
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
                class="absolute -right-1 -top-1 inline-flex min-h-[20px] min-w-[20px] items-center justify-center rounded-full bg-slate-700 px-1 text-xs font-semibold text-white"
              >
                {{ unreadNotificationCount }}
              </span>
            </button>
            <div
              v-if="showNotifications"
              class="absolute right-0 z-50 mt-3 w-[320px] origin-top-right rounded-2xl border border-slate-200 bg-white text-slate-900 shadow-xl"
              @click.self="closeNotifications"
            >
              <div class="flex items-center justify-between border-b border-slate-100 px-4 py-3">
                <h3 class="text-sm font-semibold text-slate-800">Notifications</h3>
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
                      class="relative flex gap-3 rounded-lg border border-slate-100 px-3 py-2 transition hover:border-slate-200 hover:bg-slate-50"
                      :class="{ 'border-slate-200 bg-slate-50': !item.isRead }"
                    >
                      <button
                        class="absolute -right-1 -top-1 h-5 w-5 rounded-full bg-slate-200 text-xs font-semibold text-slate-600 transition hover:bg-slate-300"
                        type="button"
                        @click.stop="dismissNotification(item)"
                      >
                        -
                      </button>
                      <div class="flex-1" @click.stop="markNotificationRead(item)">
                        <p class="text-sm font-semibold text-slate-800">{{ item.title }}</p>
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
              @click.stop="openProfileModal"
            >
              <img
                :src="profileAvatarSrc"
                alt="Profile avatar"
                class="h-9 w-9 rounded-full object-cover"
              />
              <div class="hidden text-left sm:block">
                <p class="text-sm font-semibold text-slate-900">{{ displayName }}</p>
                <p class="text-xs text-slate-500">{{ teamLabel }}</p>
              </div>
            </button>
            
          </div>
        </div>
      </div>
      <div class="flex gap-2 overflow-x-auto border-t border-slate-200/60 px-4 py-3 md:px-8 lg:hidden bg-white">
        <button
          v-for="item in navItems"
          :key="`mobile-${item.value}`"
          type="button"
          @click.stop="handleNavClick(item)"
          :disabled="item.value === 'resign' && resignDisabled"
          :class="[
            'flex items-center gap-2 rounded-full border px-4 py-1.5 text-sm font-semibold transition',
            item.value === 'resign'
              ? 'border-rose-200 bg-white text-rose-600 hover:border-rose-300 hover:text-rose-900'
              : activeTab === item.value
              ? 'border-slate-400 bg-slate-100 text-slate-900'
              : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900',
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
          ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
          : 'border-slate-200 bg-white text-slate-700',
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
        class="mx-auto flex max-w-3xl flex-col items-center gap-4 rounded-3xl border border-slate-200 bg-white p-10 text-center shadow-[0_22px_48px_rgba(15,23,42,0.08)]"
      >
        <span class="h-12 w-12 animate-spin rounded-full border-4 border-slate-200 border-t-slate-500"></span>
        <p class="text-sm text-slate-500">Loading your manager dashboard...</p>
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
            @click="fetchManagerData"
          >
            Retry
          </button>
        </div>

        <ManagerOverview
          v-if="activeTab === 'overview'"
          :display-name="displayName"
          :headline-text="headlineText"
          :manager-workspace-highlights="managerWorkspaceHighlights"
          :manager-hero-stats="managerHeroStats"
          :manager-stat-cards="managerStatCards"
          :today-label="todayLabel"
          @set-active-tab="setActiveTab"
          @go-to-chatbot="openChatbot"
        />

        <ManagerChatbot
          v-else-if="activeTab === 'chatbot'"
          :chatbot-headline="chatbotHeadline"
          :chatbot-subtitle="chatbotSubtitle"
          :chat-history="chatHistory"
          :chatbot-status-label="chatbotStatusLabel"
          :chatbot-reference="chatbotReference"
          :chatbot-reference-source="chatbotReferenceSource"
          :chatbot-reference-visible="chatbotReferenceVisible"
          :chatbot-ticket-id="chatbotTicketId"
          :chatbot-reply="chatbotReply"
          :chatbot-loading="chatbotLoading"
          :chatbot-prompt="chatbotPrompt"
          :chatbot-needs-escalation="chatbotNeedsEscalation"
          :pending-escalation-question="pendingEscalationQuestion"
          :chatbot-escalating="chatbotEscalating"
          @update:chatbot-prompt="chatbotPrompt = $event"
          @reset-chatbot="resetChatbot"
          @submit-chatbot-prompt="submitChatbotPrompt"
          @confirm-escalation="confirmChatbotEscalation"
          @cancel-escalation="cancelChatbotEscalation"
        />

        <ManagerSupportTab
          v-else-if="activeTab === 'support'"
          :questions="hrQuestions"
          :loading="hrQuestionsLoading"
          :error="hrQuestionsError"
          @refresh="loadHrQuestions(true)"
          @open-chatbot="openChatbot"
        />

        <ManagerCareer
          v-else-if="activeTab === 'career'"
          :career-form="careerForm"
          :career-form-error="careerFormError"
          :submitting-career-form="submittingCareerForm"
          :show-career-recommendation="showCareerRecommendation"
          :career-recommendation="careerRecommendation"
          :downloading-career-pdf="downloadingCareerPdf"
          @update:career-form="careerForm = $event"
          @update:show-career-recommendation="showCareerRecommendation = $event"
          @reset-career-form="resetCareerForm"
          @submit-career-form="submitCareerForm"
          @download-career-pdf="downloadCareerPdf"
        />

        <ManagerProjects
          v-else-if="activeTab === 'projects'"
          :project-announcement="projectAnnouncement"
          @open-project-modal="openProjectModal"
          @confirm-remove-project="confirmRemoveProject"
        />

        <ManagerPeople
          v-else-if="activeTab === 'people'"
          :team-members="activeTeamMembers"
          :team-empty-message="teamEmptyMessage"
          :birthday-window="birthdayWindow"
          :today-birthdays="todayBirthdays"
          :upcoming-birthdays="upcomingBirthdays"
          :team-offboarding="teamOffboarding"
          :team-label="teamLabel"
          :team-manager-id="teamManagerId"
        />

        <ManagerLeaveManagement
          v-else-if="activeTab === 'leaves'"
          :total-leave-requests="totalLeaveRequests"
          :leave-remaining-days="leaveRemainingDays"
          :leave-allowance-days="leaveAllowanceDays"
          :leave-used-days="leaveUsedDays"
          :leave-summary-rows="leaveSummaryRows"
          :recent-leaves="recentLeaves"
          :leave-summary-cards="leaveSummaryCards"
          :show-leave-analytics="showLeaveAnalytics"
          :leave-analytics-monthly="leaveAnalyticsMonthly"
          :leave-status-chips="leaveStatusChips"
          :team-status-chips="teamStatusChips"
          @open-leave-modal="openLeaveModal"
        />

          <ManagerApprovals
            v-else-if="activeTab === 'approvals'"
            :pending-team-leaves="pendingTeamLeaves"
            :processing-leaves="processingLeaves"
            @refresh-team-insights="refreshTeamInsights"
            @update-leave-status="updateLeaveStatus"
          />
        <ManagerNotifications
          v-else-if="activeTab === 'notifications'"
          :notifications="normalizedNotifications"
            :loading="notificationsLoading"
            :error="notificationsError"
            @refresh="loadNotifications(true)"
            @mark-read="markNotificationRead"
            @dismiss="dismissNotification"
          />
        </template>
      </main>
    </div>

<div v-if="showProjectModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 px-4 py-8" @click.self="closeProjectModal">
      <div class="w-full max-w-lg rounded-2xl bg-white shadow-2xl">
        <div class="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-4">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">
              {{ projectModalMode === 'edit' ? 'Edit project update' : 'Create project update' }}
            </h2>
            <p class="text-sm text-slate-500">Share the latest project focus or announcement with your team.</p>
          </div>
          <button class="text-2xl leading-none text-slate-400 transition hover:text-slate-600" type="button" @click="closeProjectModal">-</button>
        </div>
        <form class="space-y-4 px-6 py-5" @submit.prevent="saveProjectAnnouncement">
          <label class="block space-y-2 text-sm">
            <span class="font-medium text-slate-700">Title</span>
            <input
              v-model="projectForm.title"
              type="text"
              class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200"
              placeholder="e.g. Q3 product launch alignment"
              required
            >
          </label>
          <label class="block space-y-2 text-sm">
            <span class="font-medium text-slate-700">Description</span>
            <textarea
              v-model="projectForm.description"
              rows="4"
              class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200"
              placeholder="Outline goals, checkpoints, or updates for the team"
              required
            ></textarea>
          </label>
          <p v-if="projectFormError" class="text-sm font-medium text-rose-600">{{ projectFormError }}</p>
          <div class="flex justify-end gap-3">
            <button class="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100" type="button" @click="closeProjectModal">
              Cancel
            </button>
            <button class="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-slate-50" type="submit">
              {{ projectModalMode === 'edit' ? 'Save changes' : 'Create update' }}
            </button>
          </div>
        </form>
      </div>
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
                  :min="minLeaveStartDate"
                  required
                  class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200"
                >
              </label>
              <label class="block space-y-2 text-sm">
                <span class="font-medium text-slate-700">End date</span>
                <input
                  v-model="leaveForm.end_date"
                  type="date"
                  :min="minLeaveEndDate"
                  required
                  class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-200"
                >
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

    

    

    <div v-if="showProfileModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 px-4 py-8" @click.self="closeProfileModal">
      <div class="w-full max-w-xl rounded-2xl bg-white shadow-2xl">
        <div class="flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 px-6 py-4">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Profile details</h2>
            <p class="text-xs text-slate-500">Keep your job title and contact info aligned with your team.</p>
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
                <span class="text-xs font-semibold uppercase tracking-wide text-slate-400">{{ field.label }}</span>
                <span class="text-sm font-medium text-slate-700">{{ field.value }}</span>
              </div>
            </div>
            <p v-else class="rounded-xl border border-slate-100 bg-slate-50 px-4 py-6 text-center text-sm text-slate-500">
              Profile information is not available right now.
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
import ManagerOverview from '@/views/manager/tabs/ManagerOverview.vue';
import ManagerChatbot from '@/views/manager/tabs/ManagerChatbot.vue';
import profileAvatarUrl from '@/assets/Profile.png';
import ManagerCareer from '@/views/manager/tabs/ManagerCareer.vue';
import ManagerProjects from '@/views/manager/tabs/ManagerProjects.vue';
import ManagerPeople from '@/views/manager/tabs/ManagerPeople.vue';
import ManagerLeaveManagement from '@/views/manager/tabs/ManagerLeaveManagement.vue';
import ManagerApprovals from '@/views/manager/tabs/ManagerApprovals.vue';
import ManagerSupportTab from '@/views/manager/tabs/ManagerSupportTab.vue';
import ManagerNotifications from '@/views/manager/tabs/ManagerNotifications.vue';
import {
  parseKolkataISODate,
  formatKolkataDateForInput,
  getKolkataToday,
  getKolkataTomorrow,
  addKolkataDays,
} from '@/utils/kolkataTime';

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api';
const AUTH_HEADER = 'Authentication-Token';
const PROJECT_ANNOUNCEMENT_STORAGE_KEY = 'employee:project-announcement';
const MANAGER_TAB_STORAGE_KEY = 'manager:active-tab';
const OFFBOARDING_LEAVE_TYPES = ['resignation', 'offboarding'];

export default {
  name: 'ManagerDashboard',
  props: {
    mode: {
      type: String,
      default: 'dashboard',
      validator: (value) => ['dashboard', 'leaves'].includes(value),
    },
  },
  components: {
    BrandLogo,
    SidebarIcon,
    ArrowRightOnRectangleIcon,
    ManagerOverview,
    ManagerChatbot,
    ManagerCareer,
    ManagerProjects,
      ManagerPeople,
      ManagerLeaveManagement,
      ManagerApprovals,
      ManagerSupportTab,
      ManagerNotifications,
    },
  data() {
    return {
      loading: false,
      error: '',
      profile: null,
      stats: [],
      teamOverview: null,
      teamLeaveSummary: {
        total: 0,
        by_status: {},
      },
      pendingTeamLeaves: [],
      processingLeaves: {},
      upcomingEvents: [],
      notifications: [],
      projectAnnouncement: null,
      leaveBalance: null,
      leaveSummary: null,
      leaveAnalytics: {
        monthly: [],
        status_breakdown: {},
        team_status_breakdown: {},
      },
      recentLeaves: [],
      showLeaveModal: false,
      leaveForm: {
        leave_type: 'annual',
        start_date: '',
        end_date: '',
        reason: '',
      },
      leaveFormError: '',
      submittingLeave: false,
      showNotifications: false,
      notificationsLoading: false,
      notificationsError: '',
      showProjectModal: false,
      projectForm: {
        title: '',
        description: '',
      },
      projectModalMode: 'create',
      profileAvatarSrc: profileAvatarUrl,
      projectFormError: '',
      chatbot: null,
      chatbotPrompt: '',
      chatbotReply: '',
      chatbotStatus: '',
      chatbotReference: '',
      chatbotReferenceSource: '',
      chatbotTicketId: null,
      chatbotLoading: false,
      chatHistory: [],
      hrQuestions: [],
      hrQuestionsLoading: false,
      hrQuestionsError: '',
      lastHrQuestionsLoadedAt: 0,
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
      resignForm: {
        last_day: '',
        notice_period: '',
        reason: '',
        handover_plan: '',
        notes: '',
      },
      resignFormError: '',
      resignationDetails: null,
      teamOffboarding: [],
      birthdayTracker: null,
      toast: null,
      toastTimer: null,
      currentUserName: 'Manager',
      sidebarCollapsed: false,
      activeTab: this.mode === 'leaves' ? 'leaves' : (localStorage.getItem(MANAGER_TAB_STORAGE_KEY) || 'overview'),
      lastLoadTime: 0,
    };
  },
  watch: {
    mode(value) {
      this.activeTab = value === 'leaves' ? 'leaves' : 'overview';
    },
    'leaveForm.start_date'(newVal) {
      if (!newVal) {
        return;
      }
      const tomorrow = this.getTomorrowISODate();
      const minimumEnd = newVal > tomorrow ? newVal : tomorrow;
      if (!this.leaveForm.end_date || this.leaveForm.end_date < minimumEnd) {
        this.leaveForm.end_date = minimumEnd;
      }
    },
    'resignForm.notice_period'(newVal) {
      if (!newVal) {
        this.resignForm.last_day = '';
        return;
      }
      const mapping = { '2 weeks': 14, '30 days': 30, '60 days': 60 };
      const days = mapping[newVal];
      if (!days) return;
      const today = new Date();
      today.setHours(0,0,0,0);
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
      today.setHours(0,0,0,0);
      if (selected.getTime() < today.getTime()) {
        this.resignFormError = 'Last working day cannot be before today.';
        return;
      }
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
    computed: {
      navItems() {
        return [
          { value: 'overview', label: 'Overview', icon: 'overview' },
          {
            value: 'projects',
            label: 'Projects',
            icon: 'projects',
            badge: () => (this.projectAnnouncement ? 1 : null),
          },
          { value: 'people', label: 'People', icon: 'people' },
          { value: 'leaves', label: 'Leave Management', icon: 'leaveInsights' },
          { value: 'approvals', label: 'Approvals', icon: 'approvals' },
          { value: 'notifications', label: 'Notifications', icon: 'notifications' },
          { value: 'chatbot', label: 'Ask Ava', icon: 'chatbot' },
          { value: 'support', label: 'HR Support', icon: 'support' },
          { value: 'career', label: 'Career Growth', icon: 'career' },
          { value: 'resign', label: 'Resign', icon: 'resign' },
        ];
    },
    resignDisabled() {
      return Boolean(this.resignationDetails);
    },
    displayName() {
      if (this.profile && this.profile.full_name) {
        return this.profile.full_name;
      }
      return this.currentUserName;
    },
    initials() {
      const parts = (this.displayName || '').trim().split(/\s+/);
      const letters = parts.slice(0, 2).map((part) => part.charAt(0).toUpperCase());
      return letters.join('') || 'M';
    },
    teamMembers() {
      if (this.teamOverview && Array.isArray(this.teamOverview.members)) {
        return this.teamOverview.members;
      }
      return [];
    },
    activeTeamMembers() {
      return this.teamMembers.filter((member) => this.isActiveMember(member));
    },
    teamLabel() {
      if (!this.teamOverview) {
        return 'Unassigned';
      }
      return this.teamOverview.team_name || this.teamOverview.team_number || 'Unassigned';
    },
    teamManagerId() {
      const managerField =
        (this.teamOverview && (this.teamOverview.manager_id || this.teamOverview.manager?.id)) || null;
      if (managerField) {
        return managerField;
      }
      if (this.profile) {
        return this.profile.employee_id || this.profile.id || null;
      }
      return null;
    },
    pendingCount() {
      return (this.teamLeaveSummary.by_status && this.teamLeaveSummary.by_status.pending) || this.pendingTeamLeaves.length;
    },
    managerStatCards() {
      if (Array.isArray(this.stats) && this.stats.length) {
        return this.stats.map((item) => ({
          title: item.title || 'Metric',
          value: typeof item.value === 'number' ? item.value : 0,
          subtext: item.subtext || '',
          icon: item.icon || '•',
        }));
      }
      const totalMembers =
        this.teamOverview && typeof this.teamOverview.total_members === 'number'
          ? this.teamOverview.total_members
          : this.teamMembers.length || 0;
      return [
        {
          title: 'Pending approvals',
          value: this.pendingCount,
          subtext: 'Waiting on manager decision',
          icon: 'PA',
        },
        {
          title: 'Leave balance',
          value: this.leaveRemainingDays != null ? this.leaveRemainingDays : 0,
          subtext: this.leaveAllowanceDays ? `of ${this.leaveAllowanceDays} days` : 'Remaining days',
          icon: 'LB',
        },
        {
          title: 'Team members',
          value: totalMembers,
          subtext: 'Active teammates',
          icon: 'TM',
        },
      ];
    },
    todayLabel() {
      return this.formatAbsoluteDate(new Date());
    },
    managerWorkspaceHighlights() {
      const highlights = [];
      const pending = this.pendingCount || 0;
      highlights.push({
        id: 'approvals',
        label: 'Approvals queue',
        title: pending > 0 ? `${pending} to review` : 'All approvals clear',
      });
      const pendingLeaves = Array.isArray(this.pendingTeamLeaves) ? this.pendingTeamLeaves : [];
      const getStartDate = (leave) => {
        if (!leave) {
          return null;
        }
        if (leave.startDate instanceof Date && !Number.isNaN(leave.startDate.getTime())) {
          return leave.startDate;
        }
        if (leave.start_date) {
          const parsed = this.parseISODate(leave.start_date);
          if (parsed && !Number.isNaN(parsed.getTime())) {
            return parsed;
          }
        }
        return null;
      };
      const sortedPending = pendingLeaves
        .slice()
        .sort((a, b) => {
          const startA = getStartDate(a);
          const startB = getStartDate(b);
          const aTime = startA ? startA.getTime() : Number.MAX_SAFE_INTEGER;
          const bTime = startB ? startB.getTime() : Number.MAX_SAFE_INTEGER;
          return aTime - bTime;
        });
      const nextLeave = sortedPending.find((item) => getStartDate(item)) || sortedPending[0] || null;
      const nextLeaveDateRaw = nextLeave ? this.formatAbsoluteDate(getStartDate(nextLeave)) : '';
      const nextLeaveDate = nextLeaveDateRaw && nextLeaveDateRaw !== '-' ? nextLeaveDateRaw : '';
      highlights.push({
        id: 'next-leave',
        label: 'Next leave',
        title: nextLeave
          ? `${nextLeave.employee_name || 'Team member'}${nextLeaveDate ? ` | ${nextLeaveDate}` : ''}`
          : 'No upcoming leaves',
      });
      const totalMembers =
        this.teamOverview && typeof this.teamOverview.total_members === 'number'
          ? this.teamOverview.total_members
          : this.teamMembers.length;
      highlights.push({
        id: 'team-size',
        label: 'Team strength',
        title: totalMembers ? `${totalMembers} teammates` : 'Assign your roster',
      });
      return highlights;
    },
    managerHeroStats() {
      const pending = this.pendingCount || 0;
      const byStatus = (this.teamLeaveSummary && this.teamLeaveSummary.by_status) || {};
      const approved = byStatus.approved || 0;
      const rejected = byStatus.rejected || 0;
      const total =
        typeof this.teamLeaveSummary.total === 'number'
          ? this.teamLeaveSummary.total
          : approved + rejected + pending;
      const rosterCount =
        this.teamOverview && typeof this.teamOverview.total_members === 'number'
          ? this.teamOverview.total_members
          : this.teamMembers.length;
      const upcomingEvents = Array.isArray(this.upcomingEvents) ? this.upcomingEvents : [];
      const nextEvent = upcomingEvents.length ? upcomingEvents[0] : null;
      const nextEventTitle =
        (nextEvent && (nextEvent.title || nextEvent.event_name || nextEvent.event || nextEvent.name)) || '';
      const nextEventDateRaw = nextEvent
        ? nextEvent.date_label ||
          this.formatAbsoluteDate(nextEvent.date || nextEvent.event_date || nextEvent.start_date)
        : '';
      const nextEventDate = nextEventDateRaw && nextEventDateRaw !== '-' ? nextEventDateRaw : '';
      const nextEventNote =
        nextEventTitle && nextEventDate
          ? `${nextEventTitle} | ${nextEventDate}`
          : nextEventTitle || nextEventDate || '';
      return [
        {
          id: 'queue',
          label: 'Queue',
          value: pending,
          context: pending === 1 ? 'request awaiting decision' : 'requests awaiting decision',
          note: pending ? 'Action needed' : 'All approvals cleared',
          intent: pending ? 'warning' : 'success',
        },
        {
          id: 'team',
          label: 'Team',
          value: rosterCount || '--',
          context: rosterCount ? 'Active teammates' : 'Assign your roster',
          note: nextEventNote,
          intent: nextEventNote ? 'neutral' : 'muted',
        },
        {
          id: 'leave-flow',
          label: 'Leave flow',
          value: total ? `${approved}/${total}` : '0/0',
          context: 'Approved / total requests',
          note: rejected ? `${rejected} rejected` : '',
          intent: rejected ? 'warning' : 'neutral',
        },
      ];
    },
    leaveSummaryCards() {
      const cards = [];
      const balance = this.leaveSummary && this.leaveSummary.balance ? this.leaveSummary.balance : this.leaveBalance;
      const byStatus = (this.leaveSummary && this.leaveSummary.by_status) || {};
      const totalRequests = this.leaveSummary && typeof this.leaveSummary.total === 'number' ? this.leaveSummary.total : 0;
      if (balance) {
        cards.push({
          id: 'remaining',
          label: 'Remaining leave',
          value: this.leaveRemainingDays ?? 0,
          subtext: balance.allowance_days ? `of ${balance.allowance_days} days` : null,
        });
        cards.push({
          id: 'used',
          label: 'Days used',
          value: this.leaveUsedDays ?? 0,
          subtext: 'This year',
        });
      }
      cards.push({
        id: 'total-requests',
        label: 'Total requests',
        value: totalRequests,
        subtext: 'Submitted by you',
      });
      cards.push({
        id: 'active-requests',
        label: 'Active requests',
        value: byStatus.pending || 0,
        subtext: 'Waiting on decision',
      });
      return cards;
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
    showLeaveAnalytics() {
      return (this.leaveAnalyticsMonthly && this.leaveAnalyticsMonthly.length > 0) || this.leaveStatusChips.length > 0 || this.teamStatusChips.length > 0;
    },
    leaveAnalyticsMonthly() {
      if (!this.leaveAnalytics || !Array.isArray(this.leaveAnalytics.monthly)) {
        return [];
      }
      return this.leaveAnalytics.monthly.map((entry) => ({
        key: entry.key,
        label: entry.label,
        approved: entry.approved || 0,
        pending: entry.pending || 0,
        rejected: entry.rejected || 0,
      }));
    },
    maxLeaveAnalyticsValue() {
      const values = this.leaveAnalyticsMonthly.flatMap((entry) => [entry.approved, entry.pending, entry.rejected]);
      return Math.max(...values, 1);
    },
    leaveStatusChips() {
      if (!this.leaveAnalytics || !this.leaveAnalytics.status_breakdown) {
        return [];
      }
      const mapping = this.leaveAnalytics.status_breakdown;
      const order = ['approved', 'pending', 'rejected', 'cancelled'];
      return Object.keys(mapping)
        .sort((a, b) => {
          const ia = order.indexOf(a);
          const ib = order.indexOf(b);
          if (ia === -1 && ib === -1) {
            return a.localeCompare(b);
          }
          if (ia === -1) return 1;
          if (ib === -1) return -1;
          return ia - ib;
        })
        .map((key) => ({
          key,
          label: `${key.charAt(0).toUpperCase()}${key.slice(1)}`,
          value: mapping[key],
        }));
    },
    teamStatusChips() {
      if (!this.leaveAnalytics || !this.leaveAnalytics.team_status_breakdown) {
        return [];
      }
      const mapping = this.leaveAnalytics.team_status_breakdown;
      const order = ['approved', 'pending', 'rejected', 'cancelled'];
      return Object.keys(mapping)
        .sort((a, b) => {
          const ia = order.indexOf(a);
          const ib = order.indexOf(b);
          if (ia === -1 && ib === -1) {
            return a.localeCompare(b);
          }
          if (ia === -1) return 1;
          if (ib === -1) return -1;
          return ia - ib;
        })
        .map((key) => ({
          key,
          label: `${key.charAt(0).toUpperCase()}${key.slice(1)}`,
          value: mapping[key],
        }));
    },
    headlineText() {
      if (this.teamMembers.length) {
        return `Overseeing ${this.teamMembers.length} teammates with ${this.pendingCount} pending requests.`;
      }
      return 'Assign teammates to manage their requests and staffing here.';
    },
    teamEmptyMessage() {
      if (this.teamOverview && this.teamOverview.empty_message) {
        return this.teamOverview.empty_message;
      }
      return 'Assign teammates to this squad to track their requests here.';
    },
    birthdayWindow() {
      if (this.teamOverview) {
        const window =
          this.teamOverview.birthday_window ||
          this.teamOverview.birthdayWindow ||
          (this.teamOverview.birthdays && this.teamOverview.birthdays.window_days);
        if (window) {
          return window;
        }
      }
      return (this.birthdayTracker && this.birthdayTracker.window_days) || 30;
    },
    todayBirthdays() {
      const overviewBirthdays = this.teamOverview && this.teamOverview.birthdays;
      if (overviewBirthdays && Array.isArray(overviewBirthdays.today)) {
        return overviewBirthdays.today;
      }
      if (this.birthdayTracker && Array.isArray(this.birthdayTracker.today)) {
        return this.birthdayTracker.today;
      }
      return [];
    },
    upcomingBirthdays() {
      const overviewBirthdays = this.teamOverview && this.teamOverview.birthdays;
      if (overviewBirthdays && Array.isArray(overviewBirthdays.upcoming)) {
        return overviewBirthdays.upcoming.slice(0, 6);
      }
      if (this.birthdayTracker && Array.isArray(this.birthdayTracker.upcoming)) {
        return this.birthdayTracker.upcoming.slice(0, 6);
      }
      return [];
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
    chatbotHeadline() {
      if (this.chatbot && this.chatbot.headline) {
        return this.chatbot.headline;
      }
      return 'Ava, your HR co-pilot';
    },
    chatbotSubtitle() {
      if (this.chatbot && this.chatbot.subtitle) {
        return this.chatbot.subtitle;
      }
      return 'Quick answers on policy, approvals, and people support.';
    },
    chatbotStatusLabel() {
        if (!this.chatbotStatus) {
          return '';
        }
        const lookup = {
          pending: 'We have flagged this for HR follow-up. Expect a response soon.',
          auto_answered: 'Answered using verified HR guidance.',
          error: 'We ran into an issue processing that question. Please try again.',
          needs_confirmation: 'We could not find a source. Forward to HR?',
          out_of_scope: 'This looks outside HR scope. Escalate if you still need help.',
        };
        return lookup[this.chatbotStatus] || this.chatbotStatus;
      },
    chatbotReferenceVisible() {
      return this.chatbotReference || this.chatbotReferenceSource || this.chatbotTicketId;
    },
    profileFields() {
      if (!this.profile) {
        return [];
      }
      return [
         { label: 'Address', value: this.profile.contact?.address || '-' },
        { label: 'Department', value: this.profile.department || '-' },
        { label: 'Role', value: this.profile.employment_role || '-' },
        // {
        //   label: 'Manager',
        //   value: this.profile.manager && this.profile.manager.name ? this.profile.manager.name : '-',
        // },
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
      this.loadUserFromStorage();
      this.loadProjectAnnouncement();
      this.fetchManagerData();
      this.loadNotifications(true);
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
  
  methods: {
    handleNavClick(item) {
      if (item && item.value === 'resign') {
        if (this.resignDisabled) {
          return;
        }
        this.openResignModal();
        return;
      }
      this.setActiveTab((item && item.value) || 'overview');
    },
    isActiveMember(member) {
      if (!member) {
        return false;
      }
      if (member.active === false || member.is_active === false) {
        return false;
      }
      const blockedStatuses = new Set(['inactive', 'offboarded', 'terminated', 'archived']);
      const statusCandidates = [
        member.status,
        member.state,
        member.status_label,
        member.stage,
        member.employment_status,
      ];
      const normalized = statusCandidates
        .filter(Boolean)
        .map((value) => String(value).trim().toLowerCase());
      return !normalized.some((value) => blockedStatuses.has(value));
    },
      setActiveTab(value) {
        this.activeTab = value || 'overview';
        localStorage.setItem(MANAGER_TAB_STORAGE_KEY, this.activeTab);
        
        // Load birthday data only when switching to People tab
        if (this.activeTab === 'people' && !this.birthdayTracker) {
          this.loadBirthdayTracker();
        }
        if (this.activeTab === 'support') {
          this.loadHrQuestions(false);
        }
        if (this.activeTab === 'notifications') {
          this.loadNotifications(true);
        }
      },
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    openProjectModal(mode = 'create') {
      this.projectModalMode = mode;
      if (mode === 'edit' && this.projectAnnouncement) {
        this.projectForm = {
          title: this.projectAnnouncement.title || '',
          description: this.projectAnnouncement.description || '',
        };
      } else {
        this.projectForm = {
          title: '',
          description: '',
        };
      }
      this.projectFormError = '';
      this.showProjectModal = true;
    },
    closeProjectModal() {
      this.showProjectModal = false;
      this.projectFormError = '';
      this.projectForm = {
        title: '',
        description: '',
      };
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
    setProjectAnnouncementFromPayload(payload, { persist = false } = {}) {
      const normalized = this.normalizeProjectAnnouncement(payload);
      this.projectAnnouncement = normalized;
      if (persist) {
        this.persistProjectAnnouncement(normalized);
      }
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
    loadProjectAnnouncement() {
      try {
        const raw = localStorage.getItem(PROJECT_ANNOUNCEMENT_STORAGE_KEY);
        this.setProjectAnnouncementFromPayload(raw ? JSON.parse(raw) : null);
      } catch (error) {
        console.warn('Unable to parse project announcement from storage', error);
        this.projectAnnouncement = null;
      }
    },
    handleStorageEvent(event) {
      if (!event || event.key !== PROJECT_ANNOUNCEMENT_STORAGE_KEY) {
        return;
      }
      try {
        this.setProjectAnnouncementFromPayload(event.newValue ? JSON.parse(event.newValue) : null);
      } catch (error) {
        console.warn('Unable to apply project announcement from storage event', error);
      }
    },
    async saveProjectAnnouncement() {
      this.projectFormError = '';
      const title = (this.projectForm.title || '').trim();
      const description = (this.projectForm.description || '').trim();
      if (!title) {
        this.projectFormError = 'Please add a title for the update.';
        return;
      }
      if (!description) {
        this.projectFormError = 'Please add a description for the update.';
        return;
      }
      const payload = { title, description };
      try {
        const response = await axios.put(
          `${API_BASE_URL}/manager/project-announcement`,
          payload,
          { withCredentials: true },
        );
        const announcement = response.data?.project_announcement || {
          ...payload,
          lastUpdated: new Date().toISOString(),
        };
        this.setProjectAnnouncementFromPayload(announcement, { persist: true });
        this.closeProjectModal();
        this.showToast('Project announcement saved for your team.', 'success');
      } catch (error) {
        console.error('Failed to save project announcement', error);
        const message =
          (error.response && (error.response.data?.error || error.response.data?.message)) ||
          error.message ||
          'Unable to save the project announcement right now.';
        this.projectFormError = message;
      }
    },
    confirmRemoveProject() {
      if (!this.projectAnnouncement) {
        return;
      }
      const shouldRemove =
        typeof window === 'undefined' ? true : window.confirm('Remove the current project announcement?');
      if (shouldRemove) {
        this.removeProjectAnnouncement();
      }
    },
    async removeProjectAnnouncement() {
      try {
        await axios.delete(`${API_BASE_URL}/manager/project-announcement`, {
          withCredentials: true,
        });
      } catch (error) {
        console.error('Failed to remove project announcement', error);
        const message =
          (error.response && (error.response.data?.error || error.response.data?.message)) ||
          error.message ||
          'Unable to remove the project announcement right now.';
        this.showToast(message, 'error');
        return;
      }
      this.setProjectAnnouncementFromPayload(null, { persist: true });
      this.showToast('Project announcement removed.', 'info');
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
    async fetchManagerData(force = false) {
      // Avoid duplicate calls if already loading or recently loaded
      if (!force && (this.loading || (this.profile && Date.now() - this.lastLoadTime < 30000))) {
        return;
      }
      
      this.loading = true;
      this.error = '';
      const startTime = Date.now();
      try {
        const dashboardRes = await axios.get(`${API_BASE_URL}/manager/dashboard`, { withCredentials: true });
        const dashboard = dashboardRes.data || {};
        this.profile = dashboard.profile || null;
        this.stats = Array.isArray(dashboard.stats) ? dashboard.stats : [];
        this.leaveSummary = dashboard.leave_summary || null;
        this.leaveBalance =
          dashboard.leave_balance ||
          (this.leaveSummary && this.leaveSummary.balance) ||
          this.leaveBalance;
        this.leaveAnalytics = dashboard.leave_analytics || {
          monthly: [],
          status_breakdown: {},
          team_status_breakdown: {},
        };
        this.recentLeaves = Array.isArray(dashboard.recent_leaves)
          ? dashboard.recent_leaves
              .map((item) => this.decoratePersonalLeave(item))
              .filter((leave) => !this.isOffboardingLeave(leave))
          : [];
        this.teamOverview = dashboard.team_overview || null;
        this.teamLeaveSummary = dashboard.team_leave_summary || { total: 0, by_status: {} };
        this.pendingTeamLeaves = Array.isArray(dashboard.pending_team_leaves)
          ? dashboard.pending_team_leaves.map((item) => this.decorateTeamLeave(item))
          : [];
        this.processingLeaves = {};
        this.teamOffboarding = Array.isArray(dashboard.team_offboarding) ? dashboard.team_offboarding : [];
        this.upcomingEvents = dashboard.upcoming_events || [];
        this.notifications = dashboard.notifications || [];
        const incomingAnnouncement = Object.prototype.hasOwnProperty.call(dashboard, 'project_announcement')
          ? dashboard.project_announcement
          : undefined;
        if (incomingAnnouncement && (incomingAnnouncement.title || incomingAnnouncement.description)) {
          this.setProjectAnnouncementFromPayload(incomingAnnouncement, { persist: true });
        } else if (!this.projectAnnouncement) {
          this.loadProjectAnnouncement();
        }
        this.chatbot = dashboard.chatbot || null;
        this.resignationDetails = dashboard.resignation || null;
        await this.loadHrQuestions(true);
        if (this.profile && this.profile.job_title && !this.careerForm.current_role) {
          this.careerForm.current_role = this.profile.job_title;
        }
        if (this.profile && this.profile.full_name) {
          this.currentUserName = this.profile.full_name;
        }
        // Birthday data will be loaded on-demand when People tab is accessed
        
        // Track load time for performance monitoring
        this.lastLoadTime = Date.now();
        const loadDuration = this.lastLoadTime - startTime;
        if (loadDuration > 1000) {
          console.warn(`Manager dashboard loaded slowly: ${loadDuration}ms`);
        }
      } catch (error) {
        console.error('Failed to load manager dashboard', error);
        const responsePayload = error.response && error.response.data ? error.response.data : {};
        const message =
          responsePayload.error ||
          responsePayload.message ||
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
        if (!force && this.notifications.length) {
          return;
        }
        this.notificationsLoading = true;
        this.notificationsError = '';
        try {
          const response = await axios.get(`${API_BASE_URL}/notifications`, {
            params: { limit: 50 },
            withCredentials: true,
          });
          const data = response.data || {};
          const items = Array.isArray(data.notifications) ? data.notifications : [];
          this.notifications = items;
        } catch (error) {
          console.error('Failed to load notifications', error);
          const message =
            (error.response && (error.response.data?.error || error.response.data?.message)) ||
            error.message ||
            'Unable to load notifications.';
          this.notificationsError = message;
          if (force) {
            this.notifications = [];
          }
        } finally {
          this.notificationsLoading = false;
        }
      },
    async markNotificationRead(notification, { remove = false } = {}) {
      if (!notification || !notification.id) {
        return;
      }
      if (!notification.isRead) {
        try {
          await axios.post(
            `${API_BASE_URL}/notifications/${notification.id}/read`,
            {},
            { withCredentials: true },
          );
        } catch (error) {
          console.error('Failed to mark notification as read', error);
        }
      }
        this.notifications = this.notifications.map((item) =>
          item.id === notification.id ? { ...item, is_read: true, isRead: true } : item,
        );
      if (remove) {
        this.notifications = this.notifications.filter((item) => item.id !== notification.id);
      }
    },
    async dismissNotification(notification) {
      await this.markNotificationRead(notification, { remove: true });
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
    async loadHrQuestions(force = false) {
      if (this.hrQuestionsLoading) {
        return;
      }
      const now = Date.now();
      if (!force && this.hrQuestions.length && now - this.lastHrQuestionsLoadedAt < 60000) {
        return;
      }
      this.hrQuestionsLoading = true;
      this.hrQuestionsError = '';
      try {
        const response = await axios.get(`${API_BASE_URL}/hr/questions`, {
          params: { status: 'pending,resolved' },
          withCredentials: true,
        });
        const data = response.data || {};
        const questions = Array.isArray(data.questions) ? data.questions : [];
        this.hrQuestions = questions.map((item) => this.decorateHrQuestion(item)).filter(Boolean);
        this.lastHrQuestionsLoadedAt = Date.now();
      } catch (error) {
        console.error('Failed to load HR questions', error);
        const message =
          (error.response && (error.response.data?.error || error.response.data?.message)) ||
          error.message ||
          'Unable to load HR questions.';
        this.hrQuestionsError = message;
        if (force) {
          this.hrQuestions = [];
        }
      } finally {
        this.hrQuestionsLoading = false;
      }
    },
    openLeaveModal() {
      this.leaveFormError = '';
      const todayISO = this.getTodayISODate();
      if (!this.leaveForm.start_date || this.leaveForm.start_date < todayISO) {
        this.leaveForm.start_date = todayISO;
      }
      const defaultEnd =
        this.leaveForm.end_date && this.leaveForm.end_date >= this.leaveForm.start_date
          ? this.leaveForm.end_date
          : this.addDaysToISODate(this.leaveForm.start_date, 1) || this.getTomorrowISODate();
      this.leaveForm.end_date = defaultEnd;
      this.showLeaveModal = true;
    },
    closeLeaveModal() {
      this.showLeaveModal = false;
      this.leaveFormError = '';
      this.leaveForm = { leave_type: 'annual', start_date: '', end_date: '', reason: '' };
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
      const minEnd = this.leaveForm.start_date > this.getTomorrowISODate() ? this.leaveForm.start_date : this.getTomorrowISODate();
      if (this.leaveForm.end_date < minEnd) {
        this.leaveFormError = `End date must be on or after ${this.formatAbsoluteDate(minEnd)}.`;
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
        await this.fetchManagerData();
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
      this.editableProfile = {
        first_name: this.rawProfile?.first_name || nameParts[0] || '',
        last_name: this.rawProfile?.last_name || nameParts.slice(1).join(' ') || '',
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
      if (!this.editableProfile.first_name && !this.rawProfile) {
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
    openResignModal() {
      if (this.resignDisabled) {
        return;
      }
      this.resignFormError = '';
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
      // Validate last working day is not in the past
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
        // ignore parsing errors
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
          this.showToast('Resignation request submitted to HR.', 'info')
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
    openChatbot() {
        this.resetChatbot()
        this.setActiveTab('chatbot');
      },
      resetChatbot() {
        this.chatbotPrompt = ''
        this.chatbotReply = ''
        this.chatbotStatus = ''
        this.chatbotReference = ''
        this.chatbotReferenceSource = ''
        this.chatbotTicketId = null
        this.chatHistory = []
        this.chatbotLoading = false
        this.chatbotNeedsEscalation = false
        this.pendingEscalationQuestion = ''
        this.chatbotEscalating = false
        this.chatbotConversationId = null
      },
    async submitChatbotPrompt() {
        const prompt = (this.chatbotPrompt || '').trim();
        if (!prompt) {
          return;
        }
        const userMessage = {
          sender: 'user',
          content: prompt,
          timestamp: new Date().toISOString(),
        };
        this.chatHistory = [...this.chatHistory, userMessage];
        this.chatbotLoading = true;
        try {
          const response = await axios.post(
            `${API_BASE_URL}/genai/chat`,
            { message: prompt, auto_escalate: false },
            { withCredentials: true },
          );
          const payload = response.data || {};
          const normalize = (entry) => ({
            sender: entry.sender || 'assistant',
            content: entry.content || '',
            timestamp: entry.timestamp || new Date().toISOString(),
          });
          
          // Handle the response from genai/chat endpoint
          const assistantMessage = normalize({
            sender: 'assistant',
            content: payload.response || 'HR bot has recorded your message.',
          });
          this.chatHistory = [...this.chatHistory, assistantMessage];
          this.chatbotReply = payload.response || '';
          this.chatbotStatus = payload.status || '';
          this.chatbotReference = payload.reference || '';
          this.chatbotReferenceSource = payload.reference_source || '';
          this.chatbotTicketId = payload.question_id || null;
          this.chatbotConversationId = payload.conversation_id || this.chatbotConversationId;
          
          // Handle escalation if needed
          const escalationStatuses = ['needs_confirmation', 'out_of_scope'];
          const shouldOfferEscalation =
            escalationStatuses.includes(this.chatbotStatus) ||
            (!this.chatbotReply && this.chatbotStatus !== 'pending');
          if (shouldOfferEscalation) {
            this.pendingEscalationQuestion = prompt;
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
          this.pendingEscalationQuestion = prompt;
          this.chatbotNeedsEscalation = true;
          this.chatHistory = [
            ...this.chatHistory,
            {
              sender: 'assistant',
              content: 'Something went wrong while reaching HR. Please try again shortly or escalate to HR.',
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
    openCareerModal() {
        this.careerFormError = ''
        if (this.profile && this.profile.job_title && !this.careerForm.current_role) {
          this.careerForm.current_role = this.profile.job_title
        }
        this.setActiveTab('career');
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
      this.careerFormError = '';
      if (!this.careerForm.target_role.trim()) {
        this.careerFormError = 'Please share the target role or aspiration.';
        return;
      }
      this.submittingCareerForm = true;
        try {
          // Call backend GenAI endpoint to get recommendation
          const payload = {
            current_role: this.careerForm.current_role,
            target_role: this.careerForm.target_role,
            strengths: this.careerForm.strengths,
            focus_areas: this.careerForm.focus_areas,
            learning_style: this.careerForm.learning_style,
            timeline: this.careerForm.timeline,
            support_needed: this.careerForm.guidance_goal,
          };

          const res = await axios.post(`${API_BASE_URL}/genai/careerpath`, payload, { withCredentials: true });
          const recommendation = res.data?.recommendation || '';
          if (!recommendation) {
            this.careerFormError = 'No recommendation returned. Please try again.';
            return;
          }

          // Show recommendation below the form and keep form values
          this.careerRecommendation = recommendation;
          this.showCareerRecommendation = true;
          this.showToast('Personalised recommendation ready.', 'success');
      } catch (error) {
        console.error('Failed to prepare career guidance', error);
        const serverMsg = error?.response?.data?.error || error?.response?.data?.message || error?.message;
        this.careerFormError = serverMsg || 'Unable to prepare guidance right now. Please try again.';
      } finally {
        this.submittingCareerForm = false;
      }
    },

    async downloadCareerPdf() {
      if (!this.careerRecommendation) return;
      this.downloadingCareerPdf = true;
      try {
        const res = await axios.post(`${API_BASE_URL}/genai/careerpath/pdf`, { recommendation: this.careerRecommendation }, {
          responseType: 'blob',
          withCredentials: true,
        });
        const blob = new Blob([res.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'careerplan.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        console.error('Failed to download career PDF', err);
        this.showToast('Unable to download PDF right now.', 'error');
      } finally {
        this.downloadingCareerPdf = false;
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
        employment_role: user.employment_role ?? existing.employment_role,
        employee_id: user.employee_id ?? existing.employee_id,
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
    async refreshTeamInsights() {
      try {
        const dashboardRes = await axios.get(`${API_BASE_URL}/manager/dashboard`, { withCredentials: true });
        const dashboard = dashboardRes.data || {};
        if (dashboard.team_leave_summary) {
          this.teamLeaveSummary = dashboard.team_leave_summary;
        }
        if (Array.isArray(dashboard.pending_team_leaves)) {
          this.pendingTeamLeaves = dashboard.pending_team_leaves.map((item) => this.decorateTeamLeave(item));
        }
        this.processingLeaves = {};
        if (Array.isArray(dashboard.team_offboarding)) {
          this.teamOffboarding = dashboard.team_offboarding;
        }
        if (dashboard.leave_summary) {
          this.leaveSummary = dashboard.leave_summary;
          if (dashboard.leave_summary.balance) {
            this.leaveBalance = dashboard.leave_summary.balance;
          }
        }
        if (dashboard.leave_analytics) {
          this.leaveAnalytics = dashboard.leave_analytics;
        }
        if (Array.isArray(dashboard.stats)) {
          this.stats = dashboard.stats;
        }
        if (Array.isArray(dashboard.notifications)) {
          this.notifications = dashboard.notifications;
        }
        await this.loadBirthdayTracker();
      } catch (error) {
        console.error('Failed to refresh team insights', error);
        this.showToast('Unable to refresh team data right now.', 'error');
        if (error.response && error.response.status === 401) {
          this.redirectToLogin();
        }
      }
    },
    async loadBirthdayTracker() {
      try {
        const response = await axios.get(`${API_BASE_URL}/birthday-tracker`, {
          params: { scope: 'team', days: 60 },
          withCredentials: true,
        });
        this.birthdayTracker = response.data || null;
      } catch (error) {
        console.warn('Unable to load birthday tracker', error);
        if (!this.birthdayTracker) {
          this.birthdayTracker = null;
        }
      }
    },
    // Load birthday tracker asynchronously without blocking main loading
    loadBirthdayTrackerAsync() {
      // Use a small delay to ensure main content loads first
      setTimeout(() => {
        this.loadBirthdayTracker();
      }, 100);
    },
    decorateTeamLeave(leave) {
      const startDate = this.parseISODate(leave.start_date);
      const endDate = this.parseISODate(leave.end_date);
      return {
        ...leave,
        startDate,
        endDate,
        dateRange: this.formatDateRange(startDate, endDate),
      };
    },
    decoratePersonalLeave(leave) {
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
    decorateHrQuestion(question) {
      if (!question) {
        return null;
      }
      const createdAt = question.created_at || question.createdAt || null;
      const updatedAt = question.updated_at || question.updatedAt || null;
      const answer = question.answer || question.resolution_note || '';
      return {
        ...question,
        createdAt,
        updatedAt,
        submittedAtReadable: createdAt ? this.formatAbsoluteDate(createdAt) : '-',
        updatedAtReadable: updatedAt ? this.formatRelativeDate(updatedAt) : '',
        statusClass: this.statusToClass(question.status),
        statusText: this.formatStatus(question.status),
        hasAnswer: Boolean((answer || '').trim()),
        answer,
        requesterName: this.lookupUserName(question.user_id, `User #${question.user_id || ''}`),
        responderName: question.resolved_by
          ? this.lookupUserName(question.resolved_by, 'HR Specialist')
          : 'HR Specialist',
      };
    },
    parseISODate(value) {
      const parsed = parseKolkataISODate(value);
      if (parsed) {
        return parsed;
      }
      const fallback = new Date(value);
      return Number.isNaN(fallback.getTime()) ? null : fallback;
    },
    formatDateRange(start, end) {
      if (!start) {
        return '-';
      }
      const from = this.formatAbsoluteDate(start);
      if (!end || start.getTime() === end.getTime()) {
        return from;
      }
      return `${from} - ${this.formatAbsoluteDate(end)}`;
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
    addDaysToISODate(value, days = 1) {
      const base = this.parseISODate(value);
      if (!base) {
        return '';
      }
      const updated = addKolkataDays(base, days);
      return formatKolkataDateForInput(updated);
    },
    getAnalyticsBarHeight(value) {
      if (!value) {
        return '0%';
      }
      const denominator = this.maxLeaveAnalyticsValue || 1;
      const ratio = Math.min(value / denominator, 1);
      const height = Math.max(ratio * 100, 6);
      return `${height}%`;
    },
    formatAbsoluteDate(value) {
      if (!value) {
        return '-';
      }
      const date = value instanceof Date ? value : this.parseISODate(value);
      if (!date || Number.isNaN(date.getTime())) {
        return '-';
      }
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
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
        return `${minutes} min${minutes === 1 ? '' : 's'} ago`;
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
    formatLeaveType(type) {
      if (!type) {
        return 'General';
      }
      const text = type.toString().replace(/[_-]/g, ' ');
      return text.charAt(0).toUpperCase() + text.slice(1);
    },
    formatStatus(status) {
      if (!status) {
        return 'Unknown';
      }
      const text = status.toString().toLowerCase();
      return text.charAt(0).toUpperCase() + text.slice(1);
    },
    statusToClass(status) {
      const value = (status || '').toString().toLowerCase();
      if (value === 'approved' || value === 'resolved') {
        return 'success';
      }
      if (value === 'pending' || value === 'in_progress') {
        return 'warning';
      }
      if (value === 'rejected' || value === 'cancelled') {
        return 'danger';
      }
      return 'neutral';
    },
    lookupUserName(userId, fallback = '') {
      if (!userId) {
        return fallback || '';
      }
      const profileId = this.profile && (this.profile.id || this.profile.user_id);
      if (profileId && profileId === userId) {
        return 'You';
      }
      const roster = Array.isArray(this.teamMembers) ? this.teamMembers : [];
      const match = roster.find((member) => {
        const identifiers = [member.id, member.user_id, member.employee_id];
        return identifiers.some((value) => value === userId);
      });
      if (match) {
        return match.name || match.full_name || match.employee_name || fallback || `User #${userId}`;
      }
      return fallback || `User #${userId}`;
    },
        async updateLeaveStatus(leave, nextStatus) {
      if (!leave || !leave.id) {
        return;
      }
      const confirmationMessage =
        nextStatus === 'approved'
          ? `Approve ${leave.employee_name}'s leave request?`
          : `Reject ${leave.employee_name}'s leave request?`;
      if (!window.confirm(confirmationMessage)) {
        return;
      }
      this.processingLeaves = { ...this.processingLeaves, [leave.id]: nextStatus };
      try {
        await axios.patch(
          `${API_BASE_URL}/leave/${leave.id}/status`,
          {
            status: nextStatus,
            comment: nextStatus === 'approved' ? 'Approved by manager' : 'Rejected by manager',
          },
          { withCredentials: true },
        );
        this.showToast(
          `Leave ${nextStatus === 'approved' ? 'approved' : 'rejected'} for ${leave.employee_name}.`,
          'success',
        );
        await this.refreshTeamInsights();
      } catch (error) {
        console.error('Unable to update leave status', error);
        const responsePayload = error.response && error.response.data ? error.response.data : {};
        const message =
          responsePayload.error ||
          responsePayload.message ||
          error.message ||
          'Unable to update leave status right now.';
        this.showToast(message, 'error');
      } finally {
        const next = { ...this.processingLeaves };
        delete next[leave.id];
        this.processingLeaves = next;
      }
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
    redirectToLogin() {
      localStorage.removeItem('currentUser');
      localStorage.removeItem('authToken');
      localStorage.removeItem('activeUserRole');
      delete axios.defaults.headers.common[AUTH_HEADER];
      this.$router.push({ name: 'LoginPage', query: { redirect: this.$route.fullPath } });
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
        delete axios.defaults.headers.common[AUTH_HEADER];
        this.$router.push({ name: 'HomePage' });
      }
    },
  },
};
</script>

<style scoped>
.analytics-chart {
  display: flex;
  align-items: flex-end;
  gap: 18px;
  height: 220px;
}

.analytics-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  min-width: 48px;
}

.analytics-stack {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  width: 100%;
  gap: 4px;
  height: 170px;
}

.analytics-bar {
  width: 22px;
  border-radius: 999px;
  transition: height 0.2s ease, transform 0.2s ease;
}

.analytics-bar-approved,
.analytics-bar-pending,
.analytics-bar-rejected {
  background: linear-gradient(180deg, #f5f5f5 0%, #e4e4e7 100%);
}

.analytics-column:hover .analytics-bar {
  transform: translateY(-4px);
}

.analytics-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #475569;
}

.status-breakdown {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-breakdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  background-color: #e2e8f0;
  color: #1e293b;
}

.status-value {
  font-size: 0.85rem;
  font-weight: 600;
  color: #0f172a;
}

.status-chip-approved,
.status-chip-pending,
.status-chip-rejected {
  background: rgba(226, 232, 240, 0.4);
  color: #1f2937;
}

.status-chip-cancelled {
  background: rgba(148, 163, 184, 0.2);
  color: #475569;
}

.status-pill {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-pill-pending,
.status-pill-approved,
.status-pill-rejected {
  background: rgba(226, 232, 240, 0.6);
  color: #1e293b;
}

.status-pill-completed {
  background: rgba(148, 163, 184, 0.25);
  color: #334155;
}

.status-pill-active {
  background: rgba(226, 232, 240, 0.4);
  color: #1e293b;
}

</style>
