<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 min-h-screen font-sans text-slate-900">
    
    <div class="md:flex md:items-center md:justify-between mb-8">
      <div class="min-w-0 flex-1">
        <h2 class="text-2xl font-bold leading-7 text-slate-900 sm:truncate sm:text-3xl sm:tracking-tight">
          Team Directory
        </h2>
        <p class="mt-2 text-sm text-slate-500 max-w-2xl">
          Manage organizational structure, assign leadership, and oversee team memberships.
        </p>
      </div>
      <div class="mt-4 flex md:ml-4 md:mt-0">
        <button
          type="button"
          @click="openCreateModal"
          class="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-bold text-white shadow-lg shadow-slate-200 transition-all hover:bg-slate-800 hover:-translate-y-0.5 active:translate-y-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
        >
          <UserPlusIcon class="h-5 w-5 text-slate-200" aria-hidden="true" />
          <span>Create New Team</span>
        </button>
      </div>
    </div>

    <div v-if="error" class="mb-6 rounded-xl bg-red-50 p-4 border border-red-100 flex items-start gap-3">
      <ExclamationCircleIcon class="h-5 w-5 text-red-600 mt-0.5" aria-hidden="true" />
      <div>
        <h3 class="text-sm font-bold text-red-800">System Error</h3>
        <p class="text-sm text-red-700 mt-1">{{ error }}</p>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="team-panel mb-6">
      <div class="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
        
        <!-- Search Bar -->
        <div class="relative flex-1 max-w-md">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input 
            v-model="searchQuery"
            @input="handleSearch"
            type="text" 
            placeholder="Search teams by name or description..."
            class="block w-full pl-10 pr-4 py-2.5 text-sm border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all"
          >
          <div v-if="searchQuery" class="absolute inset-y-0 right-0 pr-3 flex items-center">
            <button @click="clearSearch" class="text-slate-400 hover:text-slate-600 transition-colors">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Filters -->
        <div class="flex items-center gap-3">
          <div class="relative">
            <select 
              v-model="filterByManager"
              @change="applyFilters"
              class="appearance-none bg-white border border-slate-200 rounded-lg px-4 py-2.5 pr-10 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all"
            >
              <option value="">All Managers</option>
              <option value="assigned">Has Manager</option>
              <option value="unassigned">No Manager</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-400">
              <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          <div class="relative">
            <select 
              v-model="sortBy"
              @change="applySort"
              class="appearance-none bg-white border border-slate-200 rounded-lg px-4 py-2.5 pr-10 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all"
            >
              <option value="name">Sort by Name</option>
              <option value="member_count">Sort by Members</option>
              <option value="created_at">Sort by Date</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-400">
              <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          <button 
            @click="toggleSortDirection"
            class="p-2.5 border border-slate-200 rounded-lg bg-white hover:bg-slate-50 transition-colors"
            :title="sortDirection === 'asc' ? 'Sort Descending' : 'Sort Ascending'"
          >
            <svg v-if="sortDirection === 'asc'" class="h-4 w-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
            </svg>
            <svg v-else class="h-4 w-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
            </svg>
          </button>
          
          <!-- Debug: Refresh button -->
          <button 
            @click="testFilters"
            class="p-2.5 border border-amber-200 rounded-lg bg-amber-50 hover:bg-amber-100 transition-colors text-amber-600"
            title="Test Filters (Debug)"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          
          <!-- Client-side filtering indicator -->
          <span v-if="usingClientSideFiltering" class="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
            <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Client Filter
          </span>
        </div>
      </div>

      <!-- Active Filters Display -->
      <div v-if="hasActiveFilters || (sortBy !== 'name' || sortDirection !== 'asc')" class="mt-4 flex items-center gap-2 flex-wrap section-highlight">
        <span class="text-xs font-medium text-slate-500">Active filters:</span>
        <span v-if="searchQuery" class="inline-flex items-center gap-1 px-2.5 py-1 bg-indigo-100 text-indigo-700 text-xs font-medium rounded-full">
          Search: "{{ searchQuery }}"
          <button @click="clearSearch" class="text-indigo-500 hover:text-indigo-700">
            <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </span>
        <span v-if="filterByManager" class="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-100 text-amber-700 text-xs font-medium rounded-full">
          Manager: {{ filterByManager === 'assigned' ? 'Has Manager' : 'No Manager' }}
          <button @click="clearManagerFilter" class="text-amber-500 hover:text-amber-700">
            <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </span>
        <span v-if="sortBy !== 'name' || sortDirection !== 'asc'" class="inline-flex items-center gap-1 px-2.5 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
          Sort: {{ sortBy }} ({{ sortDirection }})
          <button @click="sortBy = 'name'; sortDirection = 'asc'; fetchTeams()" class="text-green-500 hover:text-green-700">
            <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </span>
        <button @click="clearAllFilters" class="text-xs text-slate-500 hover:text-slate-700 underline">
          Clear all
        </button>
      </div>
    </div>

    <div class="team-panel">
      
      <div class="border-b border-slate-200 bg-slate-50/80 px-6 py-4 hidden md:flex items-center text-xs font-bold uppercase tracking-wider text-slate-500">
        <div class="flex-1 pl-2">Team Details</div>
        <div class="w-1/4">Leadership</div>
        <div class="w-32 text-center">Size</div>
        <div class="w-24 text-right pr-2">Manage</div>
      </div>

      <div v-if="loading && teams.length === 0" class="divide-y divide-slate-100">
        <div v-for="n in 5" :key="n" class="p-6 flex items-center gap-4 animate-pulse">
          <div class="flex-1 space-y-3">
            <div class="h-5 bg-slate-100 rounded w-1/3"></div>
            <div class="h-3 bg-slate-100 rounded w-2/3"></div>
          </div>
          <div class="w-1/4 flex gap-3">
             <div class="h-10 w-10 bg-slate-100 rounded-full"></div>
             <div class="space-y-2 flex-1 pt-1">
                <div class="h-3 bg-slate-100 rounded w-3/4"></div>
                <div class="h-2 bg-slate-100 rounded w-1/2"></div>
             </div>
          </div>
        </div>
      </div>

      <div v-else-if="!loading && teams.length === 0" class="flex flex-col items-center justify-center py-24 text-center">
        <div class="h-16 w-16 bg-slate-50 rounded-full flex items-center justify-center mb-4 ring-1 ring-slate-100">
          <UserGroupIcon class="h-8 w-8 text-slate-300" />
        </div>
        <h3 class="text-lg font-bold text-slate-900">No teams found</h3>
        <p class="mt-1 text-sm text-slate-500">Get started by creating your first team structure.</p>
        <button @click="openCreateModal" class="mt-6 text-sm font-bold text-indigo-600 hover:text-indigo-700 hover:underline">
          Create Team &rarr;
        </button>
      </div>

      <ul v-else role="list" class="divide-y divide-slate-100">
        <li 
          v-for="team in teams" 
          :key="team.id" 
          class="team-list-item group relative"
        >
          <div class="absolute left-0 top-0 bottom-0 w-1 bg-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>

          <div class="px-6 py-5 flex flex-col lg:flex-row lg:items-center gap-4 lg:gap-6">
            
            <!-- Team Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 mb-2">
                <p class="text-base font-bold text-slate-900 truncate group-hover:text-indigo-700 transition-colors">{{ team.name }}</p>
                <span v-if="!team.manager_id" class="inline-flex items-center rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700 border border-amber-100 shrink-0">
                  No Lead
                </span>
              </div>
              <p class="text-sm text-slate-500 font-medium leading-relaxed">{{ team.description || 'No description provided' }}</p>
            </div>

            <!-- Manager Info -->
            <div class="lg:w-1/4 flex items-center gap-3">
              <div class="h-10 w-10 rounded-full bg-gradient-to-br from-slate-100 to-slate-200 border border-slate-200 text-slate-600 flex items-center justify-center text-sm font-semibold shadow-sm group-hover:from-indigo-50 group-hover:to-indigo-100 group-hover:text-indigo-600 transition-all">
                {{ getInitials(team.manager_name) }}
              </div>
              <div class="flex flex-col min-w-0 flex-1">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-semibold text-slate-900 truncate">{{ team.manager_name || 'Unassigned' }}</span>
                  <button 
                    v-if="team.manager_id"
                    @click.stop="unassignManager(team)"
                    class="p-1 rounded text-slate-400 hover:text-red-600 hover:bg-red-50 transition-all opacity-0 group-hover:opacity-100"
                    title="Unassign Manager"
                  >
                    <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <span class="text-xs text-slate-500 font-medium">Team Manager</span>
              </div>
            </div>

            <!-- Members Count -->
            <div class="lg:w-32 flex justify-start lg:justify-center">
              <button 
                @click="manageMembers(team)"
                class="inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 hover:text-indigo-600 hover:ring-indigo-200 hover:bg-indigo-50 hover:shadow-md transition-all"
              >
                <UserGroupIcon class="h-4 w-4 text-slate-500" />
                <span>{{ team.member_count }}</span>
                <span class="hidden sm:inline">{{ team.member_count === 1 ? 'Member' : 'Members' }}</span>
              </button>
            </div>

            <!-- Actions -->
            <div class="lg:w-24 flex items-center justify-start lg:justify-end gap-1">
              <button 
                @click="editTeam(team)" 
                class="p-2.5 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-all" 
                title="Edit Team"
              >
                <PencilIcon class="h-4 w-4" />
              </button>
              <button 
                @click="deleteTeam(team)" 
                class="p-2.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-all" 
                title="Delete Team"
              >
                <TrashIcon class="h-4 w-4" />
              </button>
            </div>

          </div>
        </li>
      </ul>
      
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-6 team-panel flex items-center justify-between px-6 py-4">
      <div class="flex items-center gap-2 text-sm text-slate-600">
        <span>Showing</span>
        <span class="font-semibold text-slate-900">{{ startItem }}</span>
        <span>to</span>
        <span class="font-semibold text-slate-900">{{ endItem }}</span>
        <span>of</span>
        <span class="font-semibold text-slate-900">{{ totalItems }}</span>
        <span>teams</span>
      </div>
      
      <div class="flex items-center gap-1">
        <button 
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-500 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Previous
        </button>
        
        <div class="flex items-center gap-1 mx-2">
          <button 
            v-for="page in visiblePages" 
            :key="page"
            @click="goToPage(page)"
            :class="[
              'inline-flex items-center justify-center w-10 h-10 text-sm font-medium rounded-lg transition-all',
              page === currentPage 
                ? 'bg-indigo-600 text-white shadow-sm' 
                : 'text-slate-500 bg-white border border-slate-200 hover:bg-slate-50 hover:text-slate-700'
            ]"
          >
            {{ page }}
          </button>
        </div>
        
        <button 
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-500 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          Next
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Create/Edit Team Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-slate-900/75 backdrop-blur-sm transition-opacity" @click="closeModal"></div>
      
      <!-- Modal Container -->
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="relative w-full max-w-md transform overflow-hidden rounded-xl bg-white shadow-2xl transition-all max-h-[90vh]">
          
          <!-- Close Button -->
          <div class="absolute right-3 top-3 z-10">
            <button 
              type="button" 
              class="rounded-lg p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all" 
              @click="closeModal"
            >
              <XMarkIcon class="h-4 w-4" />
            </button>
          </div>

          <!-- Modal Content -->
          <div class="px-5 py-5">
            <!-- Header -->
            <div class="mb-5">
              <div class="flex items-center gap-2.5 mb-1">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100">
                  <UserPlusIcon class="h-4 w-4 text-indigo-600" />
                </div>
                <h3 class="text-lg font-bold text-slate-900" id="modal-title">
                  {{ isEditing ? 'Edit Team' : 'Create Team' }}
                </h3>
              </div>
              <p class="text-xs text-slate-500 ml-11">Configure team details and assign leadership.</p>
            </div>
            
            <!-- Form -->
            <div class="space-y-4">
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1.5">Team Name *</label>
                <input 
                  v-model="form.name" 
                  type="text" 
                  class="block w-full rounded-lg border-0 px-3 py-2.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-200 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 text-sm bg-slate-50 focus:bg-white transition-all" 
                  placeholder="e.g. Engineering Team"
                  required
                >
              </div>
              
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1.5">Description</label>
                <textarea 
                  v-model="form.description" 
                  rows="2" 
                  class="block w-full rounded-lg border-0 px-3 py-2.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-200 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 text-sm bg-slate-50 focus:bg-white transition-all resize-none" 
                  placeholder="What does this team do?"
                ></textarea>
              </div>
              
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1.5">Team Manager *</label>
                <div class="relative">
                  <select 
                    v-model="form.manager_id" 
                    class="block w-full rounded-lg border-0 px-3 py-2.5 pr-8 text-slate-900 ring-1 ring-inset ring-slate-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 text-sm bg-slate-50 focus:bg-white transition-all appearance-none"
                    :class="{'ring-red-300 focus:ring-red-500': !form.manager_id && !isEditing}"
                    required
                  >
                    <option v-if="!isEditing" :value="null" disabled>Select a Manager</option>
                    <option v-if="isEditing" :value="null" disabled>Select a Manager</option>
                    <!-- Show currently assigned manager if editing -->
                    <option 
                      v-if="isEditing && form.manager_id && !potentialManagers.find(m => m.id === form.manager_id)"
                      :value="form.manager_id"
                    >
                      {{ usersById[form.manager_id]?.first_name }} {{ usersById[form.manager_id]?.last_name }} (Current)
                    </option>
                    <!-- Show available managers -->
                    <option v-for="user in potentialManagers" :key="user.id" :value="user.id">
                      {{ user.first_name }} {{ user.last_name }}
                    </option>
                  </select>
                  <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-500">
                    <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
                <p v-if="potentialManagers.length === 0 && !isEditing" class="text-xs text-red-600 mt-1">
                  No available managers. All managers are already assigned to teams. Please create a manager account first.
                </p>
                <p v-else-if="potentialManagers.length === 0 && isEditing && !form.manager_id" class="text-xs text-red-600 mt-1">
                  No available managers. Teams must have a manager assigned. Please assign a new manager.
                </p>
                <p v-else-if="!form.manager_id" class="text-xs text-red-600 mt-1">
                  Manager is required to create a team.
                </p>
              </div>
            </div>

            <!-- Actions -->
            <div class="mt-5 flex flex-col-reverse sm:flex-row sm:justify-end gap-2">
              <button 
                type="button" 
                class="inline-flex w-full sm:w-auto justify-center items-center rounded-lg bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50 transition-all"
                @click="closeModal"
              >
                Cancel
              </button>
              <button 
                type="button" 
                class="inline-flex w-full sm:w-auto justify-center items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-slate-800 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                :disabled="submitting || !form.name.trim() || !form.manager_id"
                @click="submitTeam"
              >
                <svg v-if="submitting" class="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span v-if="submitting">Saving...</span>
                <span v-else>{{ isEditing ? 'Save' : 'Create' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Members Management Slide-over -->
    <div v-if="showMembersModal" class="fixed inset-0 z-50" aria-labelledby="slide-over-title" role="dialog" aria-modal="true">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-slate-900/75 backdrop-blur-sm transition-opacity" @click="closeMembersModal"></div>

      <!-- Slide-over Container -->
      <div class="fixed inset-0 overflow-hidden">
        <div class="absolute inset-0 overflow-hidden">
          <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-4 sm:pl-16">
            <div class="pointer-events-auto w-screen max-w-md transform transition-all duration-300 ease-in-out">
              
              <div class="flex h-full flex-col bg-white shadow-2xl">
                
                <!-- Header -->
                <div class="bg-gradient-to-r from-slate-900 to-slate-800 px-6 py-6">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">
                        <UserGroupIcon class="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <h2 class="text-lg font-bold text-white" id="slide-over-title">Team Membership</h2>
                        <p class="text-sm text-slate-300 mt-0.5">Managing {{ activeTeam?.name }}</p>
                      </div>
                    </div>
                    <button 
                      @click="closeMembersModal" 
                      type="button" 
                      class="rounded-lg p-2 text-slate-300 hover:text-white hover:bg-white/10 transition-all"
                    >
                      <XMarkIcon class="h-5 w-5" />
                    </button>
                  </div>
                </div>

                <!-- Content -->
                <div class="flex-1 flex flex-col bg-slate-50 min-h-0">
                  <!-- Fixed Add Member Section -->
                  <div class="p-4 border-b border-slate-200 bg-white">
                    <div class="flex items-center gap-2 mb-3">
                      <UserPlusIcon class="h-4 w-4 text-indigo-600" />
                      <label class="text-sm font-medium text-slate-700">Add Member</label>
                    </div>
                    <div class="flex gap-2">
                      <div class="relative flex-1">
                        <select 
                          v-model="selectedMemberToAdd" 
                          class="block w-full rounded-lg border-0 px-3 py-2 pr-8 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 text-sm bg-slate-50 focus:bg-white appearance-none transition-all"
                        >
                          <option :value="null">Select Employee...</option>
                          <option v-for="user in availableUsers" :key="user.id" :value="user.id">
                            {{ user.first_name }} {{ user.last_name }}
                          </option>
                        </select>
                        <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-500">
                          <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                          </svg>
                        </div>
                      </div>
                      <button 
                        @click="addMember"
                        :disabled="!selectedMemberToAdd || memberActionLoading"
                        class="inline-flex items-center justify-center gap-1 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <svg v-if="memberActionLoading" class="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span v-if="!memberActionLoading">Add</span>
                      </button>
                    </div>
                  </div>
                  
                  <!-- Scrollable Members List -->
                  <div class="flex-1 overflow-y-auto p-4">

                    <div class="flex items-center justify-between mb-3">
                      <h3 class="text-sm font-medium text-slate-700">Members ({{ teamMembers.length }})</h3>
                    </div>
                    
                    <div v-if="teamMembers.length === 0" class="flex flex-col items-center justify-center py-8 rounded-lg border-2 border-dashed border-slate-200 bg-slate-50/50">
                      <div class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 mb-2">
                        <UserGroupIcon class="h-5 w-5 text-slate-400" />
                      </div>
                      <h4 class="text-sm font-medium text-slate-900 mb-1">No members</h4>
                      <p class="text-xs text-slate-500 text-center">Add employees using the form above</p>
                    </div>

                    <ul v-else role="list" class="space-y-2">
                      <li 
                        v-for="member in teamMembers" 
                        :key="member.id" 
                        class="group flex items-center justify-between p-3 rounded-lg bg-white border border-slate-100 shadow-sm hover:border-slate-200 transition-all"
                      >
                        <div class="flex items-center gap-3 min-w-0 flex-1">
                          <div class="h-8 w-8 flex-none rounded-lg bg-gradient-to-br from-indigo-500 to-indigo-600 text-white flex items-center justify-center text-xs font-medium">
                            {{ getInitials(member.first_name + ' ' + member.last_name) }}
                          </div>
                          <div class="min-w-0 flex-1">
                            <p class="text-sm font-medium text-slate-900 truncate">{{ member.first_name }} {{ member.last_name }}</p>
                            <p class="truncate text-xs text-slate-500">{{ member.email }}</p>
                          </div>
                        </div>
                        <button 
                          @click="removeMember(member)"
                          :disabled="memberActionLoading"
                          class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all opacity-0 group-hover:opacity-100 disabled:cursor-not-allowed"
                          title="Remove Member"
                        >
                          <TrashIcon class="h-3 w-3" />
                        </button>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios'
import { 
  PencilIcon, 
  TrashIcon, 
  UserGroupIcon, 
  UserPlusIcon, 
  XMarkIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api'

export default {
  name: 'TeamManagementTab',
  components: {
    PencilIcon,
    TrashIcon,
    UserGroupIcon,
    UserPlusIcon,
    XMarkIcon,
    ExclamationCircleIcon
  },
  data() {
    return {
      teams: [],
      allTeams: [], // Store all teams for client-side filtering
      loading: false,
      error: '',
      
      // Pagination
      currentPage: 1,
      totalPages: 1,
      totalItems: 0,
      perPage: 5,
      
      // Search and Filters
      searchQuery: '',
      filterByManager: '',
      sortBy: 'name',
      sortDirection: 'asc',
      searchTimeout: null,
      usingClientSideFiltering: false,
      
      showModal: false,
      isEditing: false,
      submitting: false,
      form: {
        id: null,
        name: '',
        description: '',
        manager_id: null
      },
      potentialManagers: [],
      
      // Members Management
      showMembersModal: false,
      activeTeam: null,
      teamMembers: [],
      availableUsers: [],
      selectedMemberToAdd: null,
      memberActionLoading: false,
      usersById: {}
    }
  },
  created() {
    this.fetchTeams()
    this.fetchUsers()
  },
  beforeUnmount() {
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout)
    }
  },
  computed: {
    hasActiveFilters() {
      return this.searchQuery || this.filterByManager
    },
    startItem() {
      return (this.currentPage - 1) * this.perPage + 1
    },
    endItem() {
      return Math.min(this.currentPage * this.perPage, this.totalItems)
    },
    visiblePages() {
      const pages = []
      const start = Math.max(1, this.currentPage - 2)
      const end = Math.min(this.totalPages, this.currentPage + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    }
  },
  methods: {
    async fetchTeams() {
      this.loading = true
      this.error = ''

      try {
        const params = {
          page: this.currentPage,
          per_page: this.perPage,
          sort_by: this.sortBy,
          sort_direction: this.sortDirection
        }
        
        // Add search parameter
        if (this.searchQuery && this.searchQuery.trim()) {
          params.search = this.searchQuery.trim()
        }
        
        // Add manager filter parameter
        if (this.filterByManager) {
          params.manager_filter = this.filterByManager
        }
        
        // Debug: Log the parameters being sent
        console.log('Fetching teams with params:', params)
        
        const res = await axios.get(`${API_BASE_URL}/admin/teams`, { 
          params,
          withCredentials: true 
        })
        
        // Debug: Log the response
        console.log('Teams API response:', res.data)
        
        let teams = res.data.teams || []
        this.hydrateTeamManagers(teams)
        
        // Store all teams for client-side operations
        if (!this.allTeams || this.currentPage === 1) {
          this.allTeams = teams
        }
        
        // Fallback: Client-side filtering if backend doesn't support it properly
        const hasActiveFilters = this.searchQuery?.trim() || this.filterByManager || this.sortBy !== 'name' || this.sortDirection !== 'asc'
        const serverPaginated = res.data.total_pages && res.data.total_pages > 1
        
        if (hasActiveFilters && !serverPaginated && this.currentPage === 1) {
          console.log('🔧 Backend might not support filters - applying client-side filtering')
          
          // Get all teams first if we don't have them
          if (this.allTeams.length === 0) {
            this.allTeams = teams
          }
          
          // Apply client-side filters
          teams = this.applyClientSideFilters(this.allTeams)
          this.usingClientSideFiltering = true
          console.log(`🎯 Client-side filtered: showing ${teams.length} teams`)
        } else {
          this.usingClientSideFiltering = false
        }
        
        this.teams = teams
        this.totalPages = res.data.total_pages || Math.ceil(teams.length / this.perPage) || 1
        this.totalItems = res.data.total_items || teams.length || 0
        
      } catch (err) {
        this.error = err.response?.data?.message || err.response?.data?.error || 'Failed to load teams'
        console.error('Teams fetch error:', err.response?.data || err.message)
      } finally {
        this.loading = false
      }
    },

    async fetchUsers() {
      try {
        const res = await axios.get(`${API_BASE_URL}/admin/users`, { withCredentials: true })
        const users = res.data.users || []
        this.availableUsers = users.filter(
          u => !u.roles?.includes('manager') && !u.roles?.includes('hr')
        )
        this.usersById = users.reduce((map, user) => {
          map[user.id] = user
          return map
        }, {})
        this.hydrateTeamManagers(this.teams)
        // Fetch available managers separately
        await this.fetchAvailableManagers()
      } catch (err) {
        console.error('Failed to load users', err)
      }
    },
    async fetchAvailableManagers(excludeTeamId = null) {
      try {
        const params = {}
        if (excludeTeamId) {
          params.exclude_team_id = excludeTeamId
        }
        const res = await axios.get(`${API_BASE_URL}/admin/available-managers`, { 
          params,
          withCredentials: true 
        })
        this.potentialManagers = res.data.managers || []
      } catch (err) {
        console.error('Failed to load available managers', err)
        this.potentialManagers = []
      }
    },
    getInitials(name) {
      if (!name) return '?'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    },
    openCreateModal() {
      this.isEditing = false
      this.form = { id: null, name: '', description: '', manager_id: null }
      this.fetchAvailableManagers() // Refresh available managers
      this.showModal = true
      document.body.classList.add('modal-open')
    },
    editTeam(team) {
      this.isEditing = true
      this.form = {
        id: team.id,
        name: team.name,
        description: team.description,
        manager_id: team.manager_id
      }
      this.fetchAvailableManagers(team.id) // Fetch available managers excluding current team
      this.showModal = true
      document.body.classList.add('modal-open')
    },
    closeModal() {
      this.showModal = false
      document.body.classList.remove('modal-open')
    },
    async submitTeam() {
      // Validate required fields
      if (!this.form.name || !this.form.name.trim()) {
        alert('Team name is required')
        return
      }
      
      if (!this.form.manager_id) {
        alert('Manager is required to create or update a team')
        return
      }
      
      this.submitting = true
      try {
        if (this.isEditing) {
          await axios.put(`${API_BASE_URL}/admin/teams/${this.form.id}`, this.form, { withCredentials: true })
        } else {
          await axios.post(`${API_BASE_URL}/admin/teams`, this.form, { withCredentials: true })
        }
        this.closeModal()
        this.fetchTeams()
        this.fetchAvailableManagers() // Refresh available managers
      } catch (err) {
        alert(err.response?.data?.error || 'Operation failed')
      } finally {
        this.submitting = false
        document.body.classList.remove('modal-open')
      }
    },
    async deleteTeam(team) {
      if (!confirm(`Are you sure you want to delete team "${team.name}"?`)) return
      try {
        await axios.delete(`${API_BASE_URL}/admin/teams/${team.id}`, { withCredentials: true })
        // If we deleted the last item on a page, go to previous page
        if (this.teams.length === 1 && this.currentPage > 1) {
          this.currentPage--
        }
        this.fetchTeams()
      } catch (err) {
        alert('Failed to delete team')
      }
    },
    async manageMembers(team) {
      this.activeTeam = team
      this.showMembersModal = true
      this.selectedMemberToAdd = null
      this.fetchTeamMembers(team.id)
      document.body.classList.add('modal-open')
    },
    async fetchTeamMembers(teamId) {
      try {
        const res = await axios.get(`${API_BASE_URL}/admin/teams/${teamId}/members`, { withCredentials: true })
        this.teamMembers = res.data.members || []
      } catch (err) {
        console.error(err)
      }
    },
    closeMembersModal() {
      this.showMembersModal = false
      this.activeTeam = null
      this.teamMembers = []
      document.body.classList.remove('modal-open')
    },
    async addMember() {
      if (!this.selectedMemberToAdd) return
      this.memberActionLoading = true
      try {
        await axios.post(`${API_BASE_URL}/admin/teams/${this.activeTeam.id}/members`, {
          user_id: this.selectedMemberToAdd
        }, { withCredentials: true })
        this.selectedMemberToAdd = null
        this.fetchTeamMembers(this.activeTeam.id)
        const team = this.teams.find(t => t.id === this.activeTeam.id)
        if (team) team.member_count++
      } catch (err) {
        alert('Failed to add member')
      } finally {
        this.memberActionLoading = false
      }
    },
    async removeMember(member) {
      if (!confirm(`Remove ${member.first_name} from team?`)) return
      this.memberActionLoading = true
      try {
        await axios.delete(`${API_BASE_URL}/admin/teams/${this.activeTeam.id}/members/${member.id}`, { withCredentials: true })
        this.fetchTeamMembers(this.activeTeam.id)
        const team = this.teams.find(t => t.id === this.activeTeam.id)
        if (team) team.member_count--
      } catch (err) {
        alert('Failed to remove member')
      } finally {
        this.memberActionLoading = false
      }
    },
    async unassignManager(team) {
      if (!confirm(`Are you sure you want to unassign the manager from team "${team.name}"?`)) return
      
      try {
        await axios.post(`${API_BASE_URL}/admin/teams/${team.id}/unassign-manager`, {}, { withCredentials: true })
        // Refresh the team data
        this.fetchTeams()
        // Refresh available managers
        this.fetchAvailableManagers()
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to unassign manager')
      }
    },
    hydrateTeamManagers(teams = []) {
      teams.forEach(team => {
        if (team.manager_name && team.manager_name.trim()) return
        if (!team.manager_id) return
        const manager = this.usersById[team.manager_id]
        if (!manager) return
        const fullName = [manager.first_name, manager.last_name].filter(Boolean).join(' ').trim()
        team.manager_name = fullName || manager.username || manager.email || 'Manager'
      })
    },
    
    // Search and Filter Methods
    handleSearch() {
      // Debounce search to avoid too many API calls
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout)
      }
      
      this.searchTimeout = setTimeout(() => {
        console.log('Search triggered with query:', this.searchQuery)
        this.currentPage = 1
        this.fetchTeams()
      }, 300)
    },
    
    clearSearch() {
      this.searchQuery = ''
      this.currentPage = 1
      this.fetchTeams()
    },
    
    applyFilters() {
      console.log('Filter applied:', this.filterByManager)
      this.currentPage = 1
      this.fetchTeams()
    },
    
    clearManagerFilter() {
      this.filterByManager = ''
      this.currentPage = 1
      this.fetchTeams()
    },
    
    clearAllFilters() {
      this.searchQuery = ''
      this.filterByManager = ''
      this.sortBy = 'name'
      this.sortDirection = 'asc'
      this.currentPage = 1
      console.log('All filters cleared')
      this.fetchTeams()
    },
    
    applySort() {
      console.log('Sort applied:', this.sortBy, this.sortDirection)
      this.currentPage = 1
      this.fetchTeams()
    },
    
    toggleSortDirection() {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
      console.log('Sort direction toggled:', this.sortDirection)
      this.currentPage = 1
      this.fetchTeams()
    },
    
    // Pagination Methods
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.currentPage = page
        this.fetchTeams()
      }
    },
    
    // Client-side filtering fallback
    applyClientSideFilters(teams, includePagination = true) {
      let filtered = [...teams]
      
      // Apply search filter
      if (this.searchQuery && this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase().trim()
        filtered = filtered.filter(team => 
          (team.name && team.name.toLowerCase().includes(query)) ||
          (team.description && team.description.toLowerCase().includes(query)) ||
          (team.manager_name && team.manager_name.toLowerCase().includes(query))
        )
      }
      
      // Apply manager filter
      if (this.filterByManager) {
        if (this.filterByManager === 'assigned') {
          filtered = filtered.filter(team => team.manager_id && team.manager_name)
        } else if (this.filterByManager === 'unassigned') {
          filtered = filtered.filter(team => !team.manager_id || !team.manager_name)
        }
      }
      
      // Apply sorting
      filtered.sort((a, b) => {
        let aVal, bVal
        
        switch (this.sortBy) {
          case 'member_count':
            aVal = a.member_count || 0
            bVal = b.member_count || 0
            break
          case 'created_at':
            aVal = new Date(a.created_at || 0)
            bVal = new Date(b.created_at || 0)
            break
          default: // name
            aVal = (a.name || '').toLowerCase()
            bVal = (b.name || '').toLowerCase()
        }
        
        if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1
        if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1
        return 0
      })
      
      // Store total matches before pagination
      this.totalItems = filtered.length
      this.totalPages = Math.ceil(filtered.length / this.perPage)
      
      // Apply pagination if requested
      if (includePagination) {
        const start = (this.currentPage - 1) * this.perPage
        const end = start + this.perPage
        filtered = filtered.slice(start, end)
      }
      
      return filtered
    },
    
    // Debug method to test API manually
    async testFilters() {
      console.log('Current filter state:', {
        searchQuery: this.searchQuery,
        filterByManager: this.filterByManager,
        sortBy: this.sortBy,
        sortDirection: this.sortDirection,
        currentPage: this.currentPage
      })
      await this.fetchTeams()
    }
  }
}
</script>

<style scoped>
/* Layout helpers */
.team-panel {
  border-radius: 1.75rem;
  border: 1px solid rgba(73, 133, 40, 0.4);
  background: #ffffff;
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
  padding: 1.5rem;
}
.team-panel ul {
  border-radius: 1.5rem;
  overflow: hidden;
}
.section-highlight {
  background: rgba(221, 238, 209, 0.4);
  border-radius: 1rem;
  border: 1px solid rgba(73, 133, 40, 0.25);
  padding: 0.5rem 0.75rem;
}
.team-list-item {
  background: #ffffff;
  border-bottom: 1px solid rgba(73, 133, 40, 0.15);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.team-list-item:hover {
  border-color: rgba(73, 133, 40, 0.35);
  box-shadow: 0 15px 30px rgba(15, 23, 42, 0.08);
}

/* Smooth transitions for all interactive elements */
.transition-all {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Modal backdrop animation */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { 
    opacity: 0;
    transform: scale(0.95);
  }
  to { 
    opacity: 1;
    transform: scale(1);
  }
}

/* Slide-over animation */
@keyframes slideInFromRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

/* Apply animations */
.fixed.inset-0.z-50 {
  animation: fadeIn 0.2s ease-out;
}

.pointer-events-auto.w-screen.max-w-md {
  animation: slideInFromRight 0.3s ease-out;
}

/* Custom scrollbar for members list */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Ensure proper line clamping */
.line-clamp-1 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  line-clamp: 1;
}

/* Loading spinner animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Hover effects for cards */
.group:hover .ring-transparent {
  --tw-ring-color: rgba(99, 102, 241, 0.1);
}

/* Focus styles for accessibility */
.focus-visible\:outline {
  outline: 2px solid transparent;
  outline-offset: 2px;
}

.focus-visible\:outline-2 {
  outline-width: 2px;
}

.focus-visible\:outline-offset-2 {
  outline-offset: 2px;
}

.focus-visible\:outline-slate-900 {
  outline-color: #0f172a;
}

/* Ensure modal fits in viewport */
.max-h-\[90vh\] {
  max-height: 90vh;
}

/* Prevent body scroll when modal is open */
body.modal-open {
  overflow: hidden;
}

/* Mobile-specific improvements */
@media (max-width: 640px) {
  .max-w-md {
    max-width: calc(100vw - 2rem);
  }
  
  .max-h-\[90vh\] {
    max-height: 85vh;
  }
  
  .text-3xl {
    font-size: 1.875rem;
    line-height: 2.25rem;
  }
  
  .px-6 {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}

/* Ensure slide-over members list is scrollable */
.min-h-0 {
  min-height: 0;
}

/* Gradient backgrounds */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}
</style>
