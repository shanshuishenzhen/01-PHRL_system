module.exports = {
  devServer: {
    port: 8080,
    open: true, // 自动打开浏览器
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true
      }
    }
  }
}