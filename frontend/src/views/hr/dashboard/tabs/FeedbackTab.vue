<template>
  <section class="feedback-shell p-6 lg:p-10 max-w-7xl mx-auto min-h-screen space-y-6">
    
    <header class="feedback-header mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <span class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-blue-500"></span>
          </span>
          <span class="text-xs font-bold uppercase tracking-widest text-blue-600">Voice of Employee</span>
        </div>
        <h2 class="text-3xl font-bold tracking-tight text-slate-900">Anonymous Feedback</h2>
        <p class="text-slate-500 mt-2 text-sm leading-relaxed max-w-2xl">
          Review candid submissions, track sentiment, and address workplace concerns.
        </p>
      </div>
      
      <div class="flex items-center gap-3">
        
        <button 
          @click="loadFeedbacks" 
          class="p-2 bg-white border border-slate-200 rounded-lg text-slate-500 hover:text-blue-600 hover:border-blue-200 transition shadow-sm"
          title="Refresh Data"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
        </button>
      </div>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Total Volume</p>
          <p class="text-2xl font-black text-slate-900 mt-1">{{ stats.total_feedbacks }}</p>
        </div>
        <div class="h-10 w-10 rounded-full bg-slate-50 flex items-center justify-center text-slate-400">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase tracking-wider text-amber-500">Action Required</p>
          <p class="text-2xl font-black text-slate-900 mt-1">{{ stats.unread_feedbacks }}</p>
        </div>
        <div class="h-10 w-10 rounded-full bg-amber-50 flex items-center justify-center text-amber-500">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Sentiment Score</p>
          <p class="text-2xl font-black text-slate-900 mt-1">{{ stats.average_rating }}<span class="text-sm text-slate-400 font-medium">/5</span></p>
        </div>
        <div class="h-10 w-10 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-500">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Topics</p>
          <p class="text-2xl font-black text-slate-900 mt-1">{{ Object.keys(stats.category_breakdown).length }}</p>
        </div>
        <div class="h-10 w-10 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-500">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" /></svg>
        </div>
      </div>
    </div>

    <div class="feedback-panel overflow-hidden">
      
      <div class="feedback-card-header p-4 border-b border-slate-100 bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="flex items-center gap-2">
          <h3 class="font-bold text-slate-700">Submissions</h3>
          <span class="px-2 py-0.5 rounded-md bg-slate-200 text-slate-600 text-xs font-bold">{{ filteredFeedbacks.length }}</span>
        </div>

        <div class="flex gap-3">
          <select 
            v-model="filterStatus" 
            class="pl-3 pr-8 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition"
          >
            <option value="">All Status</option>
            <option value="true">Unread Only</option>
            <option value="false">Read Only</option>
          </select>

          <select 
            v-model="filterCategory" 
            class="pl-3 pr-8 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition"
          >
            <option value="">All Topics</option>
            <option v-for="cat in Object.keys(stats.category_breakdown)" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="p-20 text-center">
        <div class="animate-spin w-8 h-8 border-4 border-slate-100 border-t-blue-600 rounded-full mx-auto mb-4"></div>
        <p class="text-xs font-bold uppercase tracking-wide text-slate-400">Fetching Data...</p>
      </div>

      <div v-else-if="!filteredFeedbacks.length" class="p-20 text-center">
        <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
        </div>
        <p class="font-bold text-slate-900">No Feedback Found</p>
        <p class="text-sm text-slate-500 mt-1">Try adjusting your filters or check back later.</p>
      </div>

      <div v-else class="divide-y divide-slate-100">
        <div 
          v-for="feedback in filteredFeedbacks" 
          :key="feedback.id" 
          class="group p-6 hover:bg-slate-50/50 transition-colors cursor-pointer relative"
          :class="{ 'bg-blue-50/30': !feedback.is_read }"
          @click="showDetails(feedback)"
        >
          <div v-if="!feedback.is_read" class="absolute left-0 top-0 bottom-0 w-1 bg-blue-500"></div>

          <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <span 
                  v-if="!feedback.is_read" 
                  class="h-2 w-2 rounded-full bg-blue-500"
                  title="Unread"
                ></span>
                <h4 class="text-lg font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                  {{ feedback.title || 'Untitled Submission' }}
                </h4>
                <span class="px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wide bg-slate-100 text-slate-500 border border-slate-200">
                  {{ feedback.category }}
                </span>
              </div>
              
              <p class="text-sm text-slate-600 line-clamp-2 leading-relaxed mb-3">
                {{ feedback.feedback_text }}
              </p>

              <div class="flex items-center gap-4 text-xs text-slate-400 font-medium">
                <span>{{ formatDate(feedback.created_at) }}</span>
                <div v-if="feedback.rating" class="flex items-center gap-1 text-amber-500 bg-amber-50 px-2 py-0.5 rounded-full">
                  <span>{{ feedback.rating }}.0</span>
                  <svg class="w-3 h-3 fill-current" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <button 
                v-if="!feedback.is_read"
                @click.stop="markAsRead(feedback.id)"
                class="px-3 py-1.5 rounded-lg border border-blue-200 bg-blue-50 text-blue-700 text-xs font-bold hover:bg-blue-100 transition whitespace-nowrap"
              >
                Mark Read
              </button>
              <button class="p-2 text-slate-300 hover:text-slate-500 rounded-full hover:bg-slate-200 transition">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="totalPages > 1" class="px-6 py-4 border-t border-slate-100 flex items-center justify-between bg-slate-50/50">
        <span class="text-xs text-slate-500 font-medium">Page {{ currentPage }} of {{ totalPages }}</span>
        <div class="flex gap-2">
          <button
            class="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-600 text-xs font-bold hover:bg-slate-50 hover:border-slate-300 transition disabled:opacity-50"
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            Previous
          </button>
          <button
            class="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-600 text-xs font-bold hover:bg-slate-50 hover:border-slate-300 transition disabled:opacity-50"
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <div v-if="selectedFeedback" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity" @click="selectedFeedback = null"></div>
      
      <div class="relative w-full max-w-2xl transform overflow-hidden rounded-3xl bg-white shadow-2xl transition-all flex flex-col max-h-[85vh]">
        
        <div class="px-8 py-6 border-b border-slate-100 bg-slate-50/50 flex justify-between items-start">
          <div>
            <div class="flex items-center gap-3 mb-1">
              <h3 class="text-xl font-bold text-slate-900">{{ selectedFeedback.title }}</h3>
              <span v-if="!selectedFeedback.is_read" class="px-2 py-0.5 bg-blue-100 text-blue-700 text-[10px] font-bold uppercase rounded-md tracking-wide">New</span>
            </div>
            <p class="text-sm text-slate-500">Submitted on {{ formatDate(selectedFeedback.created_at) }}</p>
          </div>
          <button @click="selectedFeedback = null" class="text-slate-400 hover:text-slate-600 transition">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <div class="p-8 overflow-y-auto">
          
          <div class="flex gap-4 mb-6">
             <div class="flex-1 p-4 bg-slate-50 rounded-xl border border-slate-100">
                <span class="block text-xs font-bold uppercase text-slate-400 mb-1">Category</span>
                <span class="font-semibold text-slate-700">{{ selectedFeedback.category }}</span>
             </div>
             <div v-if="selectedFeedback.rating" class="flex-1 p-4 bg-amber-50 rounded-xl border border-amber-100">
                <span class="block text-xs font-bold uppercase text-amber-400 mb-1">Rating</span>
                <div class="flex items-center gap-1 font-bold text-amber-600">
                   <span>{{ selectedFeedback.rating }}/5</span>
                   <svg class="w-4 h-4 fill-current" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                </div>
             </div>
          </div>

          <div>
            <h4 class="text-sm font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-2 mb-4">Feedback Content</h4>
            <div class="prose prose-slate prose-sm max-w-none text-slate-600 whitespace-pre-wrap leading-relaxed">
              {{ selectedFeedback.feedback_text }}
            </div>
          </div>
        </div>

        <div class="px-8 py-5 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
          <button 
            @click="selectedFeedback = null"
            class="px-5 py-2.5 rounded-xl border border-slate-200 bg-white text-sm font-bold text-slate-600 hover:bg-slate-50 hover:text-slate-800 transition"
          >
            Close
          </button>
          <button 
            v-if="!selectedFeedback.is_read"
            @click="markAsRead(selectedFeedback.id)"
            class="px-5 py-2.5 rounded-xl bg-blue-600 text-sm font-bold text-white shadow-md hover:bg-blue-700 transition"
          >
            Mark as Read
          </button>
        </div>

      </div>
    </div>

  </section>
</template>

<script>
import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api'
const AUTH_HEADER = 'Authentication-Token'

export default {
  name: 'FeedbackTab',
  data() {
    return {
      feedbacks: [],
      stats: {
        total_feedbacks: 0,
        unread_feedbacks: 0,
        average_rating: 0,
        category_breakdown: {}
      },
      loading: false,
      error: null,
      currentPage: 1,
      perPage: 10,
      totalPages: 1,
      filterStatus: '',
      filterCategory: '',
      selectedFeedback: null,
      autoRefreshTimer: null
    }
  },
  computed: {
    filteredFeedbacks() {
      return this.feedbacks.filter(feedback => {
        let match = true

        if (this.filterStatus !== '') {
          // If filter is "true" (Unread Only), we want items where is_read is false
          if(this.filterStatus === 'true') {
             if(feedback.is_read === true) match = false;
          } else {
             // User wants Read
             if(feedback.is_read === false) match = false;
          }
        }

        if (this.filterCategory !== '') {
          match = match && feedback.category === this.filterCategory
        }

        return match
      })
    }
  },
  mounted() {
    this.loadFeedbacks()
    this.startAutoRefresh()
  },
  beforeUnmount() {
    this.stopAutoRefresh()
  },
  methods: {
    getAuthToken() {
      return localStorage.getItem('authToken') || localStorage.getItem('token') || ''
    },
    startAutoRefresh() {
      if (!this.getAuthToken()) {
        return
      }
      this.stopAutoRefresh()
      this.autoRefreshTimer = setInterval(() => {
        if (!this.loading) {
          this.loadFeedbacks()
        }
      }, 30000)
    },
    stopAutoRefresh() {
      if (this.autoRefreshTimer) {
        clearInterval(this.autoRefreshTimer)
        this.autoRefreshTimer = null
      }
    },
    async loadFeedbacks() {
      this.loading = true
      this.error = null

      try {
        const authToken = this.getAuthToken()
        if (!authToken) {
          this.error = 'Please log in with an authorized account to view feedback.'
          this.stopAutoRefresh()
          this.loading = false
          return
        }

        // Load stats
        const statsResponse = await axios.get(`${API_BASE_URL}/feedback/stats`, {
          headers: { [AUTH_HEADER]: authToken }
        })
        this.stats = statsResponse.data

        // Load feedbacks
        const feedbacksResponse = await axios.get(`${API_BASE_URL}/feedback/all`, {
          params: {
            page: this.currentPage,
            per_page: this.perPage
          },
          headers: { [AUTH_HEADER]: authToken }
        })

        this.feedbacks = feedbacksResponse.data.feedbacks || []
        this.totalPages = feedbacksResponse.data.pagination?.pages || 1
      } catch (error) {
        console.error('Error loading feedbacks:', error)
        this.error = error.response?.data?.error || 'Failed to load feedbacks'
      } finally {
        this.loading = false
      }
    },
    async markAsRead(feedbackId) {
      try {
        const authToken = this.getAuthToken()
        if (!authToken) {
          this.error = 'Please log in to mark feedback as read.'
          return
        }
        await axios.put(`${API_BASE_URL}/feedback/${feedbackId}/mark-read`, {}, {
          headers: { [AUTH_HEADER]: authToken }
        })

        // Update local state
        const feedback = this.feedbacks.find(f => f.id === feedbackId)
        if (feedback) {
          feedback.is_read = true
        }
        if (this.selectedFeedback?.id === feedbackId) {
          this.selectedFeedback.is_read = true
        }

        // Refresh stats to lower unread count
        this.loadFeedbacks() 
      } catch (error) {
        console.error('Error marking feedback as read:', error)
      }
    },
    showDetails(feedback) {
      this.selectedFeedback = { ...feedback }
    },
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }
      return new Date(dateString).toLocaleDateString('en-US', options)
    }
  }
}
</script>

<style scoped>
.feedback-shell {
  background: #f6faf6;
  border-radius: 2rem;
  border: 1px solid rgba(73, 133, 40, 0.25);
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
}
.feedback-header {
  border-bottom: 1px solid rgba(73, 133, 40, 0.2);
  padding-bottom: 1rem;
}
.feedback-panel {
  border-radius: 1.75rem;
  border: 1px solid rgba(73, 133, 40, 0.3);
  background: #ffffff;
  box-shadow: 0 25px 45px rgba(15, 23, 42, 0.08);
}
.feedback-card-header {
  border-radius: 1.5rem 1.5rem 0 0;
}
.feedback-shell .flex {
  gap: 1rem;
}
</style>
