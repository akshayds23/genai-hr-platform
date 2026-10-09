const { defineConfig } = require('@vue/cli-service')

const backendTarget = process.env.VUE_APP_BACKEND_SERVER || 'http://127.0.0.1:5000'

module.exports = defineConfig({
  transpileDependencies: true,
  
  // Performance optimizations
  configureWebpack: {
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          }
        }
      }
    }
  },
  
  devServer: {
    // Performance optimizations for dev server
    hot: true,
    liveReload: false, // Disable if hot reload is enabled
    compress: true,
    
    proxy: {
      '^/api': {
        target: backendTarget,
        changeOrigin: true,
        logLevel: 'warn' // Reduce proxy logging
      },
      '^/auth': {
        target: backendTarget,
        changeOrigin: true,
        logLevel: 'warn'
      }
    }
  }
})
