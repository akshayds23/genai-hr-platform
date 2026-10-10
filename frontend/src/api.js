import axios from 'axios'

const API_BASE_URL = (process.env.VUE_APP_API_BASE_URL || '/api').replace(/\/$/, '')

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

apiClient.interceptors.request.use(
  (config) => {
    const token =
      localStorage.getItem('authToken') ||
      localStorage.getItem('token')
    if (token) {
      config.headers['Authentication-Token'] = token
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      try {
        localStorage.removeItem('authToken')
        localStorage.removeItem('token')
        localStorage.removeItem('currentUser')
        localStorage.removeItem('activeUserRole')
      } catch (e) {
        // ignore
      }
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
export { API_BASE_URL }

