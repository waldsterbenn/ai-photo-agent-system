import "bootstrap";
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap/dist/css/bootstrap.min.css";
import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

const app = createApp(App)
app.config.errorHandler = (err, instance, info) => {
  // handle error, e.g. report to a service
  console.error('Error:', err)
  console.error('Vue component:', instance)
  console.error('Additional info:', info)
}
app.config.warnHandler = (msg, instance, trace) => {
  // `trace` is the component hierarchy trace
  console.warn('Warn:', msg)
  console.warn('Vue component:', instance)
  console.warn('Additional info:', trace)
}

app.use(createPinia())
app.use(router)

app.mount('#app')
