<template>
  <div class="hr-search" @click="closePickers">
    <header class="dashboard-header">
      <div class="header-inner mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-4">
        <div class="flex flex-wrap items-center gap-6">
          <router-link class="text-lg font-semibold tracking-tight text-white" to="/hr/dashboard">Employee Search</router-link>
        </div>
        <div class="hidden items-center gap-3 md:flex">
          <router-link class="rounded-full border border-white/40 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10" to="/hr/dashboard">HR Dashboard</router-link>
        </div>
      </div>
    </header>

    <main class="dashboard-main">
      <div class="mx-auto max-w-7xl space-y-6 px-4">
        <section class="rounded-2xl bg-white shadow-card">
          <div class="border-b border-slate-100 px-6 py-4">
            <h2 class="text-lg font-semibold text-slate-900">Search employees</h2>
            <p class="text-sm text-slate-500">Filter by name/email, employee ID, department, role, or status</p>
          </div>
          <form class="grid grid-cols-1 gap-4 px-6 py-5 sm:grid-cols-2 lg:grid-cols-4" @submit.prevent="submitSearch">
            <label class="block space-y-2 text-sm">
              <span class="font-medium text-slate-700">Query</span>
              <input v-model="filters.query" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200" placeholder="Name or email" />
            </label>
            <label class="block space-y-2 text-sm">
              <span class="font-medium text-slate-700">Employee ID</span>
              <input v-model="filters.employee_id" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200" placeholder="e.g. E1234" />
            </label>
            <label class="block space-y-2 text-sm">
              <span class="font-medium text-slate-700">Department</span>
              <input v-model="filters.department" type="text" list="deptOptions" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200" placeholder="e.g. Engineering" />
              <datalist id="deptOptions">
                <option v-for="d in departments" :key="d" :value="d">{{ d }}</option>
              </datalist>
            </label>
            <label class="block space-y-2 text-sm">
              <span class="font-medium text-slate-700">Role</span>
              <input v-model="filters.role" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200" placeholder="e.g. Manager" />
            </label>
            <label class="block space-y-2 text-sm">
              <span class="font-medium text-slate-700">Status</span>
              <select v-model="filters.status" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200">
                <option value="">Any</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="on_leave">On leave</option>
                <option value="offboarded">Offboarded</option>
              </select>
            </label>
            <div class="flex items-end gap-3">
              <button class="rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500" type="submit">Search</button>
              <button class="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100" type="button" @click="resetFilters">Reset</button>
            </div>
          </form>
        </section>

        <section class="rounded-2xl bg-white shadow-card">
          <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">Results</h2>
              <p class="text-sm text-slate-500">{{ totalLabel }}</p>
            </div>
            <div class="text-xs text-slate-500">Page {{ page }} / {{ totalPages }}</div>
          </div>
          <div v-if="loading" class="px-6 py-10 text-center text-sm text-slate-500">Searching employees...</div>
          <div v-else-if="error" class="mx-6 my-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-600">{{ error }}</div>
          <div v-else>
            <div v-if="results.length" class="overflow-x-auto">
              <table class="min-w-full divide-y divide-slate-100 text-left text-sm">
                <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th class="px-4 py-3 font-medium">Name</th>
                    <th class="px-4 py-3 font-medium">Employee ID</th>
                    <th class="px-4 py-3 font-medium">Department</th>
                    <th class="px-4 py-3 font-medium">Role</th>
                    <th class="px-4 py-3 font-medium">Email</th>
                    <th class="px-4 py-3 font-medium">Manager</th>
                    <th class="px-4 py-3 font-medium">Joined</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="emp in results" :key="emp.id || emp.employee_id">
                    <td class="px-4 py-3 text-slate-900">{{ emp.full_name || emp.name }}</td>
                    <td class="px-4 py-3 text-slate-700">{{ emp.employee_id || '-' }}</td>
                    <td class="px-4 py-3 text-slate-700">{{ emp.department || '-' }}</td>
                    <td class="px-4 py-3 text-slate-700">{{ emp.employment_role || emp.job_title || '-' }}</td>
                    <td class="px-4 py-3 text-slate-700">{{ emp.contact?.email || emp.email || '-' }}</td>
                    <td class="px-4 py-3 text-slate-700">{{ emp.manager?.name || '-' }}</td>
                    <td class="px-4 py-3 text-slate-700">{{ formatAbsoluteDate(emp.hire_date) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="px-6 py-10 text-sm text-slate-500">No employees found with the current filters.</p>

            <div class="flex items-center justify-between border-t border-slate-100 px-6 py-4">
              <button class="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 disabled:opacity-60" type="button" :disabled="page <= 1" @click="prevPage">Previous</button>
              <div class="text-xs text-slate-500">Showing {{ showingLabel }}</div>
              <button class="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 disabled:opacity-60" type="button" :disabled="page >= totalPages" @click="nextPage">Next</button>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api'

export default {
  name: 'HrSearch',
  data() {
    return {
      loading: false,
      error: '',
      filters: {
        query: '',
        employee_id: '',
        department: '',
        role: '',
        status: '',
      },
      results: [],
      total: 0,
      page: 1,
      pageSize: 10,
      departments: [],
    }
  },
  computed: {
    totalPages() {
      return Math.max(Math.ceil(this.total / this.pageSize), 1)
    },
    totalLabel() {
      return this.total ? `${this.total} result${this.total === 1 ? '' : 's'} found` : 'No results yet'
    },
    showingLabel() {
      if (!this.total) return '0 of 0'
      const start = (this.page - 1) * this.pageSize + 1
      const end = Math.min(this.total, this.page * this.pageSize)
      return `${start} - ${end} of ${this.total}`
    },
  },
  created() {
    this.loadDepartments()
  },
  methods: {
    async loadDepartments() {
      try {
        const res = await axios.get(`${API_BASE_URL}/admin/departments`, { withCredentials: true })
        const items = Array.isArray(res.data?.departments) ? res.data.departments : []
        this.departments = items
      } catch (error) {
        // Optional endpoint, ignore failures
        this.departments = []
      }
    },
    async submitSearch() {
      this.error = ''
      this.loading = true
      try {
        const params = {
          ...this.filters,
          page: this.page,
          page_size: this.pageSize,
        }
        const res = await axios.get(`${API_BASE_URL}/admin/employees/search`, { params, withCredentials: true })
        this.results = Array.isArray(res.data?.results) ? res.data.results : []
        this.total = typeof res.data?.total === 'number' ? res.data.total : this.results.length
      } catch (error) {
        console.error('Search failed', error)
        this.error = error?.response?.data?.error || error.message || 'Unable to search right now.'
        this.results = []
        this.total = 0
      } finally {
        this.loading = false
      }
    },
    resetFilters() {
      this.filters = { query: '', employee_id: '', department: '', role: '', status: '' }
      this.page = 1
      this.results = []
      this.total = 0
    },
    prevPage() {
      if (this.page <= 1) return
      this.page -= 1
      this.submitSearch()
    },
    nextPage() {
      if (this.page >= this.totalPages) return
      this.page += 1
      this.submitSearch()
    },
    formatAbsoluteDate(value) {
      if (!value) return '-'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return '-'
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
    },
    closePickers() {
      // no-op, reserved for future
    },
  },
}
</script>

<style scoped>
.hr-search {
  min-height: 100vh;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
  color: #1e293b;
}

.dashboard-header {
  background: linear-gradient(115deg, rgba(15, 23, 42, 0.92), rgba(30, 64, 175, 0.88));
  color: #f8fafc;
  border-bottom: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.18);
  backdrop-filter: blur(16px);
}

.dashboard-main { position: relative; z-index: 1; padding-top: 2rem; padding-bottom: 6rem; }

.shadow-card { background: rgba(255, 255, 255, 0.92); border: 1px solid rgba(226, 232, 240, 0.7); box-shadow: 0 22px 48px rgba(15, 23, 42, 0.08); backdrop-filter: blur(14px); }
</style>
