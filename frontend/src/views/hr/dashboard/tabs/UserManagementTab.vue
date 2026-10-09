<template>
  <section class="min-h-screen bg-[#f5faf5] pb-12 font-sans text-slate-900 user-shell">
    
    <header class="relative mx-auto max-w-7xl px-6 lg:px-8">
      <div class="rounded-[32px] border border-[#498528] bg-white p-8 shadow-[0_30px_70px_rgba(15,23,42,0.15)] lg:p-10">
        <div class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div class="space-y-2">
            <div class="flex items-center gap-3">
              <span class="flex h-10 w-10 items-center justify-center rounded-lg border border-[#498528] bg-[#ecfdf5] text-emerald-700">
                <UsersIcon class="h-5 w-5" />
              </span>
            </div>
            <h1 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Mission Control</h1>
            <p class="text-sm text-slate-500">Manage the people who keep the company running with focused filters and clean actions.</p>
          </div>
          
          <div class="flex flex-wrap items-center gap-3">
            <button
              class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 shadow-sm transition hover:bg-slate-50"
              type="button"
              @click="resetFilters"
            >
              <ArrowPathIcon class="h-4 w-4 text-emerald-600 transition-transform group-hover:rotate-180" />
              <span>Refresh</span>
            </button>
            <button
              class="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-emerald-500/30 transition hover:bg-emerald-500 hover:-translate-y-0.5"
              type="button"
              @click="openCreateModal"
            >
              <PlusIcon class="h-5 w-5" />
              Add User
            </button>
          </div>
        </div>

        <dl class="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-3 lg:w-full">
          <div class="rounded-2xl border border-slate-100 bg-[#ecfdf5] px-4 py-3 stats-chip">
            <dt class="truncate text-xs font-medium text-slate-500">Total Employees</dt>
            <dd class="mt-1 text-2xl font-bold text-slate-900">{{ meta.total || 0 }}</dd>
          </div>
          <div class="rounded-2xl border border-slate-100 bg-[#ecfdf5] px-4 py-3 stats-chip">
            <dt class="truncate text-xs font-medium text-slate-500">Active on this segment</dt>
            <dd class="mt-1 text-2xl font-bold text-emerald-600">{{ activeCount }}</dd>
          </div>
        </dl>
      </div>
      </header>

    <main class="relative mx-auto -mt-8 max-w-7xl px-4 sm:px-6 lg:px-8">
      
      <div class="rounded-[32px] border border-[#498528] bg-white p-2 shadow-[0_25px_60px_rgba(15,23,42,0.1)] user-panel">
        <div class="rounded-[28px] border border-slate-100 bg-slate-50/50 p-6 lg:p-8">
          <div class="grid gap-8 lg:grid-cols-12">
            <div class="lg:col-span-4 space-y-6">
              <div>
                <h3 class="flex items-center gap-2 text-lg font-bold text-slate-900">
                  <AdjustmentsHorizontalIcon class="h-5 w-5 text-indigo-500" />
                  Refine Audience
                </h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-500">
                  Slice the dataset by role, department, or status using the controls.
                </p>
              </div>

              <div v-if="activeFilterChips.length" class="flex flex-wrap gap-2">
                <span
                  v-for="chip in activeFilterChips"
                  :key="chip.key"
                  class="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700 border border-indigo-100"
                >
                  {{ chip.label }}: {{ chip.value }}
                  <button @click="clearSpecificFilter(chip.key)" class="ml-1 text-indigo-400 hover:text-indigo-900">×</button>
                </span>
              </div>
            </div>

            <form class="lg:col-span-8 space-y-5" @submit.prevent="applyFilters">
              <div class="relative flex items-center">
                <input
                  v-model="filters.query"
                  type="text"
                  placeholder="Search by name, email, or employee ID..."
                  class="peer block w-full rounded-2xl border-0 bg-white py-4 pl-12 pr-4 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-200 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm sm:leading-6"
                >
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
                  <MagnifyingGlassIcon class="h-5 w-5 text-slate-400 peer-focus:text-indigo-500" />
                </div>
                <div class="absolute inset-y-0 right-2 flex items-center">
                  <button type="submit" class="rounded-xl bg-slate-900 px-4 py-2 text-xs font-bold text-white hover:bg-slate-800 transition">
                    Search
                  </button>
                </div>
              </div>

              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                 <div class="relative">
                  <label class="mb-1 block text-xs font-semibold text-slate-500">Department</label>
                  <select v-model="filters.department" @change="applyFilters" class="w-full appearance-none rounded-xl border-0 bg-white py-3 pl-4 pr-10 text-slate-900 ring-1 ring-inset ring-slate-200 focus:ring-2 focus:ring-indigo-500 sm:text-sm">
                    <option value="">All Departments</option>
                    <option v-for="dept in departments" :key="dept.name" :value="dept.name">{{ dept.name }}</option>
                  </select>
                  <ChevronDownIcon class="pointer-events-none absolute bottom-3 right-3 h-5 w-5 text-slate-400" />
                </div>
                
                <div class="relative">
                  <label class="mb-1 block text-xs font-semibold text-slate-500">System Role</label>
                  <select v-model="filters.role" @change="applyFilters" class="w-full appearance-none rounded-xl border-0 bg-white py-3 pl-4 pr-10 text-slate-900 ring-1 ring-inset ring-slate-200 focus:ring-2 focus:ring-indigo-500 sm:text-sm">
                    <option value="">All Roles</option>
                    <option v-for="role in availableRoles" :key="role.name" :value="role.name">{{ roleLabel(role) }}</option>
                  </select>
                  <ChevronDownIcon class="pointer-events-none absolute bottom-3 right-3 h-5 w-5 text-slate-400" />
                </div>
              </div>

              <div class="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-3">
                 <span class="text-xs font-bold text-slate-500">Status Focus</span>
                 <div class="flex gap-2">
                    <button 
                      v-for="status in statusQuickFilters" 
                      :key="status.value"
                      type="button"
                      @click="setStatusFilter(status.value)"
                      :class="[
                        'rounded-lg px-3 py-1.5 text-xs font-bold transition-all',
                        filters.status === status.value || (!filters.status && status.value === '')
                          ? 'bg-slate-900 text-white shadow-md' 
                          : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                      ]"
                    >
                      {{ status.label }}
                    </button>
                 </div>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="mt-8 overflow-hidden rounded-3xl border border-[#498528] bg-white shadow-sm user-panel">
        <div class="border-b border-slate-100 px-6 py-4 flex items-center justify-between bg-slate-50/50">
           <h3 class="font-bold text-slate-900">Workforce Feed</h3>
           <p class="text-xs font-medium text-slate-500">Showing {{ pageLabel }} records</p>
        </div>
        
        <div class="overflow-x-auto">
          <table class="min-w-full text-left text-sm whitespace-nowrap user-table">
            <thead class="bg-slate-50 text-xs font-bold uppercase tracking-wider text-slate-500">
              <tr>
                <th class="px-6 py-4">Employee</th>
                <th class="px-6 py-4">Department</th>
                <th class="px-6 py-4">System Role</th>
                <th class="px-6 py-4">Status</th>
                <th class="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 bg-white">
              <tr 
                v-for="user in users" 
                :key="user.id" 
                class="user-row group"
              >
                <td class="px-6 py-4">
                  <div class="flex items-center gap-4">
                    <div 
                      class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-sm font-bold shadow-sm ring-1 ring-black/5"
                      :style="{ backgroundColor: getAvatarColor(user.id), color: '#1e293b' }"
                    >
                      {{ getInitials(user) }}
                    </div>
                    <div>
                      <div class="font-bold text-slate-900">{{ displayName(user) }}</div>
                      <div class="text-xs text-slate-500">{{ user.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div v-if="user.department" class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-slate-50 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                     {{ user.department }}
                  </div>
                  <span v-else class="text-slate-400 italic">Unassigned</span>
                </td>
                <td class="px-6 py-4 text-slate-600 font-medium">
                   {{ formatRoles(user.roles) }}
                </td>
                <td class="px-6 py-4">
                  <span 
                    :class="[
                      'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-bold',
                      user.active 
                        ? 'bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-600/20' 
                        : 'bg-rose-50 text-rose-700 ring-1 ring-inset ring-rose-600/20'
                    ]"
                  >
                    <span :class="['h-1.5 w-1.5 rounded-full', user.active ? 'bg-emerald-500' : 'bg-rose-500']"></span>
                    {{ user.active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button
                    v-if="!user.offboarding_complete"
                    @click="openEditModal(user)"
                    class="text-slate-400 hover:text-indigo-600 font-medium text-xs transition-colors mr-3"
                  >
                    Edit
                  </button>
                  <button @click="promptDelete(user)" class="text-slate-400 hover:text-rose-600 font-medium text-xs transition-colors">Delete</button>
                </td>
              </tr>
              
              <tr v-if="!users.length && !loading">
                 <td colspan="5" class="py-12 text-center">
                    <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
                       <MagnifyingGlassIcon class="h-6 w-6 text-slate-400" />
                    </div>
                    <h3 class="mt-2 text-sm font-semibold text-slate-900">No users found</h3>
                    <p class="mt-1 text-sm text-slate-500">Adjust filters or search query.</p>
                 </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="border-t border-slate-100 bg-slate-50 px-4 py-4">
          <div class="flex flex-col gap-3 text-xs font-semibold uppercase tracking-wider text-slate-500 md:flex-row md:items-center md:justify-between">
             <span>Page {{ meta.page || 1 }} of {{ totalPages }}</span>
             <div class="flex items-center justify-center gap-3">
               <button
                 type="button"
                 class="rounded-full border border-slate-200 bg-white px-4 py-2 text-[11px] font-bold text-slate-600 transition hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-50"
                 :disabled="!hasPrevPage || loading"
                 @click="changePage((meta.page || 1) - 1)"
               >
                 Previous
               </button>
               <button
                 type="button"
                 class="rounded-full border border-slate-200 bg-white px-4 py-2 text-[11px] font-bold text-slate-600 transition hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-50"
                 :disabled="!hasNextPage || loading"
                 @click="changePage((meta.page || 1) + 1)"
               >
                 Next
               </button>
             </div>
          </div>
        </div>
      </div>
    </main>

    <div v-if="formModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4" @click.self="closeForm">
      <div class="w-full max-w-2xl rounded-2xl bg-white shadow-2xl overflow-hidden animate-pop">
        <div class="bg-slate-50 px-6 py-4 border-b border-slate-100 flex justify-between items-center">
           <h3 class="text-lg font-bold text-slate-900">{{ formMode === 'create' ? 'Create New Account' : 'Edit Account' }}</h3>
           <button @click="closeForm" class="text-slate-400 hover:text-slate-600 text-2xl leading-none">&times;</button>
        </div>
        <form @submit.prevent="submitForm" class="p-6 space-y-5">
           <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div class="space-y-1">
                 <label class="text-xs font-bold text-slate-500 uppercase">Username *</label>
                 <input v-model="formData.username" class="modal-input" required placeholder="jdoe">
              </div>
              <div class="space-y-1">
                 <label class="text-xs font-bold text-slate-500 uppercase">Email *</label>
                 <input v-model="formData.email" type="email" class="modal-input" required placeholder="email@company.com">
              </div>
              <div class="space-y-1">
                 <label class="text-xs font-bold text-slate-500 uppercase">{{ formMode === 'create' ? 'Password *' : 'New Password' }}</label>
                 <input v-model="formData.password" type="password" class="modal-input" :required="formMode === 'create'">
              </div>
              <div class="space-y-1">
                 <label class="text-xs font-bold text-slate-500 uppercase">Department</label>
                 <select v-model="formData.department" class="modal-input">
                    <option value="">Unassigned</option>
                    <option v-for="dept in departments" :key="dept.name" :value="dept.name">{{ dept.name }}</option>
                 </select>
              </div>
              <div class="space-y-1">
                 <label class="text-xs font-bold text-slate-500 uppercase">Birthday</label>
                 <input v-model="formData.birth_date" type="date" class="modal-input">
              </div>
              <div class="space-y-1">
                 <label class="text-xs font-bold text-slate-500 uppercase">Hire Date</label>
                 <input v-model="formData.hire_date" type="date" class="modal-input">
              </div>
              <div class="space-y-1">
                 <label class="text-xs font-bold text-slate-500 uppercase">First Name</label>
                 <input v-model="formData.first_name" class="modal-input">
              </div>
               <div class="space-y-1">
                 <label class="text-xs font-bold text-slate-500 uppercase">Last Name</label>
                 <input v-model="formData.last_name" class="modal-input">
              </div>
           </div>

           <div class="p-4 bg-slate-50 rounded-xl border border-slate-100">
              <span class="text-xs font-bold uppercase text-slate-500 mb-2 block">System Role</span>
              <div class="space-y-3">
                 <label v-for="role in availableRoles" :key="role.name" class="flex items-center gap-3 cursor-pointer p-2 rounded-lg hover:bg-white transition">
                    <input type="radio" v-model="formData.role" :value="role.name" class="text-indigo-600 focus:ring-indigo-500">
                    <div class="flex-1">
                      <span class="text-sm font-medium text-slate-700">{{ roleLabel(role) }}</span>
                      <p class="text-xs text-slate-500">{{ getRoleDescription(role.name) }}</p>
                    </div>
                 </label>
              </div>
           </div>

           <div class="flex items-center gap-3">
              <input id="modal-active" type="checkbox" v-model="formData.active" class="rounded border-slate-300 text-emerald-500 focus:ring-emerald-500 h-5 w-5">
              <label for="modal-active" class="text-sm font-bold text-slate-700">Account is Active</label>
           </div>
           
           <p v-if="formError" class="text-sm text-rose-600 bg-rose-50 p-3 rounded-lg">{{ formError }}</p>

           <div class="pt-2 flex justify-end gap-3">
              <button type="button" @click="closeForm" class="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
              <button type="submit" :disabled="formSubmitting" class="px-6 py-2 text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 rounded-lg shadow-lg shadow-slate-900/20 disabled:opacity-70">
                 {{ formSubmitting ? 'Saving...' : 'Save User' }}
              </button>
           </div>
        </form>
      </div>
    </div>

    <div v-if="deleteModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4" @click.self="closeDelete">
       <div class="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl text-center animate-pop">
          <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-rose-100 mb-4">
             <svg class="h-8 w-8 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
          </div>
          <h3 class="text-xl font-bold text-slate-900">Confirm Deletion</h3>
          <p class="mt-2 text-sm text-slate-500">
             Are you sure you want to delete <strong>{{ deleteTarget && displayName(deleteTarget) }}</strong>? This cannot be undone.
          </p>
          <p v-if="deleteError" class="mt-2 text-xs text-rose-600">{{ deleteError }}</p>
          <div class="mt-6 flex flex-col gap-2">
             <button @click="confirmDelete" :disabled="deleteLoading" class="w-full py-3 rounded-xl bg-rose-600 text-white font-bold hover:bg-rose-700 shadow-lg shadow-rose-600/30">
                {{ deleteLoading ? 'Deleting...' : 'Yes, Delete Account' }}
             </button>
             <button @click="closeDelete" class="w-full py-3 rounded-xl bg-white border border-slate-200 text-slate-700 font-bold hover:bg-slate-50">Cancel</button>
          </div>
       </div>
    </div>

  </section>
</template>

<script>
import axios from 'axios'
import {
  AdjustmentsHorizontalIcon,
  ArrowPathIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  ChevronDownIcon,
  UsersIcon,
} from '@heroicons/vue/24/outline'

const ROWS_PER_PAGE = 10
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api'

const defaultFormState = () => ({
  id: null,
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  department: '',
  birth_date: '',
  hire_date: '',
  role: 'employee', // Single role instead of array
  active: true,
})

export default {
  name: 'UserManagement',
  components: {
    AdjustmentsHorizontalIcon,
    ArrowPathIcon,
    MagnifyingGlassIcon,
    PlusIcon,
    ChevronDownIcon,
    UsersIcon,
  },
  data() {
    return {
      loading: false,
      users: [],
      meta: {
        page: 1,
        per_page: ROWS_PER_PAGE,
        total: 0,
        pages: 1,
      },
      filters: {
        query: '',
        department: '',
        role: '',
        status: '',
      },
      departments: [],
      roles: [],
      
      // Modal States
      formModalOpen: false,
      formMode: 'create',
      formSubmitting: false,
      formError: '',
      formData: defaultFormState(),
      
      deleteModalOpen: false,
      deleteTarget: null,
      deleteLoading: false,
      deleteError: '',
    }
  },
  computed: {
    currentUser() {
      // Get current user info from localStorage or session
      const userStr = localStorage.getItem('user') || sessionStorage.getItem('user')
      try {
        return userStr ? JSON.parse(userStr) : null
      } catch {
        return null
      }
    },
    activeCount() {
      // Use the current page's batch to estimate how many are active
      return this.users.filter(u => u.active).length
    },
    pageLabel() {
      const total = Number(this.meta.total) || 0
      if (!total) {
        return '0 of 0'
      }
      const perPage = Number(this.meta.per_page) || ROWS_PER_PAGE
      const page = Number(this.meta.page) || 1
      const start = (page - 1) * perPage + 1
      const end = Math.min(page * perPage, total)
      return `${start}-${end} of ${total}`
    },
    totalPages() {
      const pages = Number(this.meta.pages) || 0
      return Math.max(1, pages)
    },
    hasPrevPage() {
      return (Number(this.meta.page) || 1) > 1
    },
    hasNextPage() {
      return (Number(this.meta.page) || 1) < this.totalPages
    },
    statusQuickFilters() {
      return [
        { label: 'All', value: '' },
        { label: 'Active', value: 'active' },
        { label: 'Inactive', value: 'inactive' },
      ]
    },
    availableRoles() {
      // Filter out HR role from available roles
      return this.roles.filter(role => role.name !== 'hr')
    },
    activeFilterChips() {
      const chips = []
      if (this.filters.query) chips.push({ label: 'Search', value: this.filters.query, key: 'query' })
      if (this.filters.department) chips.push({ label: 'Dept', value: this.filters.department, key: 'department' })
      if (this.filters.role) chips.push({ label: 'Role', value: this.roleLabel(this.filters.role), key: 'role' })
      if (this.filters.status) chips.push({ label: 'Status', value: this.filters.status === 'active' ? 'Active' : 'Inactive', key: 'status' })
      return chips
    },
  },
  created() {
    this.bootstrap()
  },
  methods: {
    async bootstrap() {
      await Promise.allSettled([this.fetchUsers(1), this.fetchDepartments(), this.fetchRoles()])
    },
    async fetchUsers(page = 1) {
      this.loading = true
      
      try {
        const params = { page, per_page: ROWS_PER_PAGE, ...this.filters }
        const res = await axios.get(`${API_BASE_URL}/super-admin/users`, { params, withCredentials: true })
        const nextUsers = Array.isArray(res.data?.results) ? res.data.results : []

        const meta = res.data?.meta || {}
        const totalFromMeta = Number(meta.total)
        const normalizedPerPage = Number(meta.per_page) || ROWS_PER_PAGE
        const total = Number.isFinite(totalFromMeta) ? totalFromMeta : nextUsers.length
        const computedPages = Math.max(1, Math.ceil((total || nextUsers.length || 0) / normalizedPerPage))
        const pagesFromMeta = Number(meta.pages)
        const pages = Number.isFinite(pagesFromMeta) && pagesFromMeta > 0 ? pagesFromMeta : computedPages
        const pageFromMeta = Number(meta.page)
        const currentPage = Number.isFinite(pageFromMeta) && pageFromMeta >= 1 ? pageFromMeta : Math.max(1, page)

        this.users = nextUsers
        this.meta = {
          page: currentPage,
          total: Number.isFinite(total) ? total : 0,
          per_page: normalizedPerPage,
          pages,
        }

      } catch (error) {
        console.error(error)
        this.users = []
        this.meta = {
          page: 1,
          per_page: ROWS_PER_PAGE,
          total: 0,
          pages: 1,
        }
      } finally {
        this.loading = false
      }
    },
    async fetchDepartments() {
       try {
          const res = await axios.get(`${API_BASE_URL}/super-admin/departments`, { withCredentials: true })
          this.departments = res.data?.departments || []
       } catch (e) { this.departments = [] }
    },
    async fetchRoles() {
       try {
          const res = await axios.get(`${API_BASE_URL}/super-admin/roles`, { withCredentials: true })
          this.roles = res.data?.roles || [
             { name: 'employee' }, { name: 'manager' }, { name: 'hr' }
          ]
       } catch (e) { this.roles = [] }
    },
    applyFilters() {
       this.fetchUsers(1)
    },
    resetFilters() {
      this.filters = { query: '', department: '', role: '', status: '' }
       this.fetchUsers(1)
    },
    clearSpecificFilter(key) {
      this.filters[key] = ''
      this.applyFilters()
    },
    setStatusFilter(val) {
      this.filters.status = val
      this.applyFilters()
    },
    changePage(targetPage) {
       const pageNumber = Number(targetPage) || 1
       const currentPage = Number(this.meta.page) || 1
       if (
         pageNumber === currentPage ||
         pageNumber < 1 ||
         pageNumber > this.totalPages ||
         this.loading
       ) {
          return
       }
       this.fetchUsers(pageNumber)
    },
    
    // CRUD Operations
    openCreateModal() {
       this.formMode = 'create'
       this.formData = defaultFormState()
       this.formError = ''
       this.formModalOpen = true
    },
    openEditModal(user) {
       this.formMode = 'edit'
       this.formData = {
          ...user,
          password: '', // Don't fill password on edit
          role: (user.roles && user.roles.length > 0) ? user.roles[0] : 'employee' // Use first role or default to employee
       }
       this.formError = ''
       this.formModalOpen = true
    },
    closeForm() {
       this.formModalOpen = false
    },
    async submitForm() {
       this.formSubmitting = true
       this.formError = ''
       
       // Client-side validation: prevent HR role assignment
       if (this.formData.role === 'hr') {
         this.formError = 'You cannot assign HR roles to users.'
         this.formSubmitting = false
         return
       }
       
       try {
          const payload = { ...this.formData }
          if (!payload.password) delete payload.password
          
          // Convert single role to array for backend compatibility
          payload.roles = [payload.role]
          delete payload.role
          
          if (this.formMode === 'create') {
             await axios.post(`${API_BASE_URL}/super-admin/users`, payload, { withCredentials: true })
          } else {
             await axios.put(`${API_BASE_URL}/super-admin/users/${payload.id}`, payload, { withCredentials: true })
          }
          this.closeForm()
          this.fetchUsers(Number(this.meta.page) || 1) // Refresh list
       } catch (error) {
          this.formError = error.response?.data?.error || 'Failed to save user'
       } finally {
          this.formSubmitting = false
       }
    },
    promptDelete(user) {
       this.deleteTarget = user
       this.deleteError = ''
       this.deleteModalOpen = true
    },
    closeDelete() {
       this.deleteModalOpen = false
       this.deleteTarget = null
    },
    async confirmDelete() {
       if (!this.deleteTarget) return
       this.deleteLoading = true
       try {
          await axios.delete(`${API_BASE_URL}/super-admin/users/${this.deleteTarget.id}`, { withCredentials: true })
          this.closeDelete()
          this.fetchUsers(Number(this.meta.page) || 1)
       } catch (error) {
          this.deleteError = 'Failed to delete user'
       } finally {
          this.deleteLoading = false
       }
    },

    // Helpers
    roleLabel(role) {
       const r = typeof role === 'string' ? role : role?.name
       if (!r) return ''
       return r.charAt(0).toUpperCase() + r.slice(1).replace(/_/g, ' ')
    },
    formatRoles(roles) {
       if (!roles || !roles.length) return '—'
       return roles.map(r => this.roleLabel(r)).join(', ')
    },
    getInitials(user) {
       const f = user.first_name || user.username || 'U'
       const l = user.last_name || ''
       return (f[0] + (l[0] || '')).toUpperCase()
    },
    getAvatarColor(id) {
       // Punchy pastels
       const colors = ['#bfdbfe', '#bbf7d0', '#fbcfe8', '#ddd6fe', '#fde68a', '#c7d2fe', '#fed7aa']
       return colors[(id || 0) % colors.length]
    },
    displayName(user) {
       if (user.first_name || user.last_name) return [user.first_name, user.last_name].join(' ')
       return user.username || user.email
    },
    getRoleDescription(roleName) {
       const descriptions = {
         employee: 'Standard employee access with basic features',
         manager: 'Management access with team oversight capabilities'
       }
       return descriptions[roleName] || 'System role with specific permissions'
    }
  }
}
</script>

<style scoped>
.user-shell {
  background: #f5faf5;
}
.stats-chip {
  background: #ecfdf5;
  border-radius: 1rem;
  padding: 0.65rem 1rem;
  border: 1px solid rgba(73, 133, 40, 0.25);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
}
.user-panel {
  border-radius: 2rem;
  border: 1px solid rgba(73, 133, 40, 0.4);
  background: #ffffff;
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
}
.user-table {
  border-collapse: separate;
  border-spacing: 0;
  width: 100%;
}
.user-table thead {
  background: rgba(237, 250, 255, 0.95);
}
.user-row {
  transition: background 0.2s, box-shadow 0.2s;
}
.user-row:hover {
  background: rgba(255, 255, 255, 0.9);
  box-shadow: inset 0 0 0 1px rgba(73, 133, 40, 0.15);
}
/* Custom Input Style for Modal */
.modal-input {
  width: 100%;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  color: #1e293b;
  transition: all 0.2s;
}
.modal-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
}

/* Animation */
.animate-pop {
  animation: pop 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes pop {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
</style>
