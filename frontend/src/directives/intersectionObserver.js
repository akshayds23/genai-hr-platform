const intersectionObserverDirective = {
  mounted(el) {
    if (typeof IntersectionObserver === 'undefined') {
      el.classList.add('opacity-100', 'translate-y-0')
      return
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.classList.add('opacity-100', 'translate-y-0')
          el.classList.remove('opacity-0', 'translate-y-10')
          observer.disconnect()
        }
      },
      { threshold: 0.1 }
    )

    el.classList.add('transition-all', 'duration-1000', 'transform', 'opacity-0', 'translate-y-10')
    observer.observe(el)
  },
}

export default intersectionObserverDirective
