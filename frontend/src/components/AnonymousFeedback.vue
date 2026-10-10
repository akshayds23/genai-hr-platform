<template>
  <div class="feedback-container">
    <!-- Header -->
    <div class="feedback-header">
      <div>
        <h3 class="header-title">💬 Share Your Feedback</h3>
        <p class="header-subtitle">Help us improve by sharing your anonymous thoughts</p>
      </div>
    </div>

    <!-- Feedback Form Card -->
    <div class="form-card">
      <form @submit.prevent="submitFeedback" class="feedback-form">
        <!-- Title Input -->
        <div class="form-group">
          <label class="form-label">Feedback Title *</label>
          <input
            v-model.trim="form.title"
            type="text"
            class="form-input"
            placeholder="Brief title of your feedback"
            required
          />
        </div>

        <!-- Category Select -->
        <div class="form-group">
          <label class="form-label">Category *</label>
          <select v-model="form.category" class="form-select" required>
            <option value="">Choose a category...</option>
            <option v-for="cat in categories" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>
        </div>

        <!-- Description -->
        <div class="form-group full-width">
          <label class="form-label">Description *</label>
          <textarea
            v-model.trim="form.feedback_text"
            class="form-textarea"
            rows="5"
            placeholder="Share your detailed feedback, suggestions, or concerns..."
            required
          ></textarea>
        </div>

        <!-- Rating -->
        <div class="form-group">
          <label class="form-label">Rating</label>
          <div class="rating-group">
            <button
              v-for="star in 5"
              :key="star"
              type="button"
              @click="form.rating = star"
              :class="['rating-btn', star <= form.rating ? 'active' : '']"
            >
              ⭐
            </button>
            <span v-if="form.rating" class="rating-text">{{ form.rating }} / 5</span>
          </div>
        </div>

        <!-- Messages -->
        <div v-if="errorMsg" class="alert alert-error">
          {{ errorMsg }}
        </div>
        <div v-if="successMsg" class="alert alert-success">
          {{ successMsg }}
        </div>

        <!-- Submit Button -->
        <button type="submit" :disabled="submitting" class="submit-btn">
          {{ submitting ? '⏳ Submitting...' : '✓ Submit Feedback' }}
        </button>
      </form>

      <!-- Privacy Notice -->
      <div class="privacy-notice">
        🔒 <strong>Your Privacy is Protected</strong> - Your feedback is completely anonymous. Only HR can view it, and your identity will never be revealed.
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api'
const AUTH_HEADER = 'Authentication-Token'

export default {
  name: 'AnonymousFeedback',
  data() {
    return {
      form: {
        title: '',
        category: '',
        feedback_text: '',
        rating: 0
      },
      categories: [],
      submitting: false,
      errorMsg: '',
      successMsg: ''
    }
  },
  mounted() {
    this.fetchCategories()
  },
  methods: {
    fetchCategories() {
      const authToken = localStorage.getItem('authToken') || localStorage.getItem('token')
      if (!authToken) {
        console.warn('No auth token found')
        this.categories = [
          'Work Environment',
          'Management',
          'Benefits',
          'Culture',
          'Career Development',
          'Compensation',
          'Work-Life Balance',
          'Communication',
          'Tools & Resources',
          'Other'
        ]
        return
      }
      axios.get(`${API_BASE_URL}/feedback/categories`, {
        headers: {
          [AUTH_HEADER]: authToken
        }
      })
        .then(response => {
          this.categories = response.data.categories || []
        })
        .catch(error => {
          console.error('Error fetching categories:', error)
          // Fallback to default categories if API fails
          this.categories = [
            'Work Environment',
            'Management',
            'Benefits',
            'Culture',
            'Career Development',
            'Compensation',
            'Work-Life Balance',
            'Communication',
            'Tools & Resources',
            'Other'
          ]
        })
    },
    async submitFeedback() {
      if (!this.form.title.trim()) {
        this.errorMsg = 'Please enter a feedback title'
        return
      }
      if (!this.form.category) {
        this.errorMsg = 'Please select a category'
        return
      }
      if (!this.form.feedback_text.trim()) {
        this.errorMsg = 'Please enter your feedback'
        return
      }

      this.submitting = true
      this.errorMsg = ''
      this.successMsg = ''

      try {
        const authToken = localStorage.getItem('authToken') || localStorage.getItem('token')
        
        if (!authToken) {
          this.errorMsg = '❌ Authentication failed - please login again'
          this.submitting = false
          return
        }
        
        await axios.post(`${API_BASE_URL}/feedback/submit`, 
          this.form,
          {
            headers: {
              'Content-Type': 'application/json',
              [AUTH_HEADER]: authToken
            }
          }
        )
        
        this.successMsg = 'Thank you! Your feedback has been submitted successfully.'
        // Reset form
        this.form = {
          title: '',
          category: '',
          feedback_text: '',
          rating: 0
        }
        // Clear success message after 4 seconds
        setTimeout(() => {
          this.successMsg = ''
        }, 4000)
      } catch (error) {
        console.error('Error submitting feedback:', error)
        console.error('Error response:', error.response?.data)
        console.error('Error status:', error.response?.status)
        const errorMsg = error.response?.data?.error || error.message || 'Failed to submit feedback'
        this.errorMsg = `❌ ${errorMsg}`
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.feedback-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.feedback-header {
  margin-bottom: 40px;
  padding-bottom: 24px;
  border-bottom: 2px solid #e5e7eb;
}

.header-title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.header-subtitle {
  font-size: 16px;
  color: #6b7280;
}

.form-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  padding: 40px;
}

.feedback-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  display: block;
}

.form-input,
.form-select,
.form-textarea {
  font-size: 14px;
  padding: 12px 16px;
  border: 1.5px solid #d1d5db;
  border-radius: 8px;
  font-family: inherit;
  transition: all 0.2s ease;
  background: #f9fafb;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  background: #ffffff;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  color: #111827;
}

.form-textarea::placeholder {
  color: #9ca3af;
}

.form-input::placeholder,
.form-select::placeholder {
  color: #9ca3af;
}

.rating-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rating-btn {
  background: none;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.rating-btn:hover {
  border-color: #f59e0b;
  transform: scale(1.1);
}

.rating-btn.active {
  background: #fef3c7;
  border-color: #f59e0b;
  box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.1);
}

.rating-text {
  font-size: 14px;
  font-weight: 600;
  color: #f59e0b;
}

.alert {
  grid-column: 1 / -1;
  padding: 14px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 16px;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.alert-success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #86efac;
}

.submit-btn {
  grid-column: 1 / -1;
  padding: 14px 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.privacy-notice {
  padding: 16px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.6;
  color: #1e40af;
  text-align: center;
}

.privacy-notice strong {
  font-weight: 600;
}

@media (max-width: 768px) {
  .feedback-form {
    grid-template-columns: 1fr;
  }

  .form-card {
    padding: 24px;
  }

  .header-title {
    font-size: 24px;
  }

  .rating-btn {
    padding: 6px 10px;
    font-size: 18px;
  }
}
</style>
