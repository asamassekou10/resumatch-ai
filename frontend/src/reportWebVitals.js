const reportWebVitals = onPerfEntry => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      // Enhanced reporting with threshold warnings
      getCLS((metric) => {
        if (metric.value > 0.1) {
          console.warn(`⚠️ Poor CLS: ${metric.value.toFixed(3)} (target < 0.1)`);
        }
        onPerfEntry(metric);
      });
      
      getFID((metric) => {
        if (metric.value > 100) {
          console.warn(`⚠️ Poor FID: ${metric.value.toFixed(2)}ms (target < 100ms)`);
        }
        onPerfEntry(metric);
      });
      
      getFCP((metric) => {
        if (metric.value > 1800) {
          console.warn(`⚠️ Poor FCP: ${metric.value.toFixed(2)}ms (target < 1800ms)`);
        }
        onPerfEntry(metric);
      });
      
      getLCP((metric) => {
        if (metric.value > 2500) {
          console.warn(`⚠️ Poor LCP: ${metric.value.toFixed(2)}ms (target < 2500ms)`);
        }
        onPerfEntry(metric);
      });
      
      getTTFB((metric) => {
        if (metric.value > 600) {
          console.warn(`⚠️ Poor TTFB: ${metric.value.toFixed(2)}ms (target < 600ms)`);
        }
        onPerfEntry(metric);
      });
    });
  }
};

export default reportWebVitals;
