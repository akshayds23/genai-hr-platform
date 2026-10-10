<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { buildKolkataDate } from '@/utils/kolkataTime'

// Reactive form fields
const email = ref('')
const password = ref('')
const first_name = ref('')
const last_name = ref('')
const phone = ref('')
const address = ref('')
const organization = ref('')
const employee_id = ref('')
const job_title = ref('')
const department = ref('')
const team_number = ref('')
const role = ref('employee')
const hire_date = ref('')
const birth_date = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const isLoading = ref(false)
const router = useRouter()

// Flask backend URL
const API_URL = `${process.env.VUE_APP_API_BASE_URL || '/api'}/register`

const handleSignup = () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (!email.value || !password.value) {
    errorMessage.value = 'Please fill in email and password.'
    return
  }

  // Validate birth date and hire date
  if (!birth_date.value) {
    errorMessage.value = 'Please provide birth date. Employee must be at least 18.'
    return
  }
  // parse birth date
  const bd = new Date(birth_date.value)
  if (Number.isNaN(bd.getTime())) {
    errorMessage.value = 'Invalid birth date.'
    return
  }
  // compute age in years
  const today = new Date()
  let age = today.getFullYear() - bd.getFullYear()
  const m = today.getMonth() - bd.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < bd.getDate())) {
    age -= 1
  }
  if (age < 18) {
    errorMessage.value = 'Employee must be at least 18 years old.'
    return
  }

  if (!hire_date.value) {
    errorMessage.value = 'Please provide hire date.'
    return
  }
  const hd = new Date(hire_date.value)
  if (Number.isNaN(hd.getTime())) {
    errorMessage.value = 'Invalid hire date.'
    return
  }
  // hire date must be after birth date
  // compare dates (ignore time)
  const bdIST = buildKolkataDate(bd.getFullYear(), bd.getMonth(), bd.getDate())
  const hdIST = buildKolkataDate(hd.getFullYear(), hd.getMonth(), hd.getDate())
  if (hdIST.getTime() <= bdIST.getTime()) {
    errorMessage.value = 'Hire date must be after birth date.'
    return
  }

  isLoading.value = true

  axios.post(API_URL, {
    email: email.value,
    password: password.value,
    first_name: first_name.value,
    last_name: last_name.value,
    phone: phone.value,
    address: address.value,
    organization: organization.value
    ,
    employee_id: employee_id.value,
    job_title: job_title.value,
    department: department.value,
    team_number: team_number.value || null,
    employment_role: role.value,
    hire_date: hire_date.value || null,
    birth_date: birth_date.value || null
  }, {
    headers: {
      'Content-Type': 'application/json'
    },
    withCredentials: true
  })
    .then(() => {
      successMessage.value = 'Registration successful! You can now log in.'
      // Clear the form
      email.value = ''
      password.value = ''
      first_name.value = ''
      last_name.value = ''
      phone.value = ''
      address.value = ''
      organization.value = ''
      employee_id.value = ''
      job_title.value = ''
      department.value = ''
  team_number.value = ''
  role.value = 'employee'
      hire_date.value = ''
      birth_date.value = ''
      if (window.confirm('Registration successful! Continue to the home page?')) {
        router.push({ name: 'HomePage' })
      }
    })
    .catch(error => {
      console.error('Signup failed:', error)
      errorMessage.value =
        error.response?.data?.message ||
        error.response?.data?.error ||
        'Registration failed.'
    })
    .finally(() => {
      isLoading.value = false
    })
}
</script>

<template>
  <div class="signup-page">
    <div class="signup-card">
      <header class="signup-header">
        <p class="eyebrow">Human Resource Platform</p>
        <h2>HR Management Signup</h2>
        <p class="subtext">Complete your profile in one glance. All fields stay within the screen.</p>
      </header>

      <form class="signup-form" @submit.prevent="handleSignup">
        <div class="form-columns">
          <section class="form-section">
            <h3>Personal Information</h3>

            <div class="form-field">
              <label>Email</label>
              <input v-model="email" type="email" placeholder="Enter email">
            </div>

            <div class="field-row">
              <div class="form-field">
                <label>First Name</label>
                <input v-model="first_name" type="text" placeholder="First name">
              </div>
              <div class="form-field">
                <label>Last Name</label>
                <input v-model="last_name" type="text" placeholder="Last name">
              </div>
            </div>

            <div class="form-field">
              <label>Phone</label>
              <input v-model="phone" type="text" placeholder="Phone number">
            </div>

            <div class="form-field">
              <label>Address</label>
              <input v-model="address" type="text" placeholder="Address">
            </div>

            <div class="field-row">
              <div class="form-field">
                <label>Birth Date</label>
                <input v-model="birth_date" type="date">
              </div>
              <div class="form-field">
                <label>Password</label>
                <input v-model="password" type="password" placeholder="Enter password">
              </div>
            </div>
          </section>

          <section class="form-section">
            <h3>Employment Information</h3>

            <div class="form-field">
              <label>Organization</label>
              <input v-model="organization" type="text" placeholder="Organization">
            </div>

            <div class="form-field">
              <label>Employee ID</label>
              <input v-model="employee_id" type="text" placeholder="Employee ID">
            </div>

            <div class="form-field">
              <label>Job Title</label>
              <input v-model="job_title" type="text" placeholder="Job title">
            </div>

            <div class="field-row">
              <div class="form-field">
                <label>Department</label>
                <input v-model="department" type="text" placeholder="Department">
              </div>
              <div class="form-field">
                <label>Team Number</label>
                <input v-model="team_number" type="text" placeholder="Team #">
              </div>
            </div>

            <div class="form-field">
              <label>Role</label>
              <select v-model="role">
                <option value="employee">Employee</option>
                <option value="manager">Manager</option>
              </select>
            </div>

            <div class="form-field">
              <label>Hire Date</label>
              <input v-model="hire_date" type="date">
            </div>
          </section>
        </div>

        <p v-if="errorMessage" class="feedback error">{{ errorMessage }}</p>
        <p v-if="successMessage" class="feedback success">{{ successMessage }}</p>

        <button type="submit" :disabled="isLoading" class="submit-btn">
          {{ isLoading ? 'Signing up...' : 'Sign Up' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.signup-page {
  min-height: 100vh;
  background: #f0f4f8;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.signup-card {
  width: min(1100px, 95vw);
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
  padding: 2.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.signup-header .eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.signup-header h2 {
  margin: 0;
  font-size: 1.9rem;
  color: #0f172a;
}

.signup-header .subtext {
  margin-top: 0.4rem;
  color: #475569;
  font-size: 0.95rem;
}

.signup-form {
  width: 100%;
}

.form-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(260px, 1fr));
  gap: 1.25rem 2rem;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.form-section h3 {
  margin: 0;
  font-size: 1.05rem;
  color: #1e1b4b;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-row {
  display: flex;
  gap: 1rem;
}

.field-row .form-field {
  flex: 1;
}

.form-field label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #475569;
}

.form-field input,
.form-field select {
  width: 100%;
  padding: 0.65rem 0.75rem;
  border: 1px solid #cbd5f5;
  border-radius: 8px;
  background: #f8fafc;
  font-size: 0.92rem;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.form-field input:focus,
.form-field select:focus {
  outline: none;
  border-color: #4f46e5;
  background: #ffffff;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.15);
}

.feedback {
  margin: 0.5rem 0 0;
  font-size: 0.9rem;
}

.feedback.error {
  color: #dc2626;
}

.feedback.success {
  color: #059669;
}

.submit-btn {
  width: 100%;
  padding: 0.85rem;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.submit-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.submit-btn:not(:disabled):hover {
  transform: translateY(-1px);
}

@media (max-width: 1100px) {
  .signup-card {
    padding: 2rem;
  }
}

@media (max-width: 960px) {
  .form-columns {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .field-row {
    flex-direction: column;
  }
}
</style>
