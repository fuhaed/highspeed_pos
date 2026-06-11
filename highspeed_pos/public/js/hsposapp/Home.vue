<template>
  <v-app class="container1">
    <Navbar @changePage="setPage($event)"></Navbar>
    <v-main style="height: 100vh; overflow: hidden;">
      <keep-alive>
        <component v-bind:is="page" class="px-2 pb-0" style="height: 100%; overflow: hidden;"></component>
      </keep-alive>
    </v-main>
  </v-app>
</template>

<script>
import Navbar from './components/Navbar.vue';
import POS from './components/pos/Pos.vue';
import Payments from './components/payments/Pay.vue';
import Tables from './components/pos/PosTables.vue';

export default {
  data: function () {
    return {
      page: 'POS',
    };
  },
  components: {
    Navbar,
    POS,
    Payments,
    Tables,
  },
  methods: {
    setPage(page) {
      this.page = page;
    },
    remove_frappe_nav() {
      this.$nextTick(function () {
        $('.page-head').remove();
        $('.navbar.navbar-default.navbar-fixed-top').remove();
      });
    },
  },
  mounted() {
    this.remove_frappe_nav();
  },
  updated() { },
  created: function () {
    setTimeout(() => {
      this.remove_frappe_nav();
    }, 1000);
    this.eventBus.on("show_tables", (data) => {
      this.page = data === "true" ? "Tables" : "POS";
    });
  },
  beforeUnmount() {
    this.eventBus.off("show_tables");
  },
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Prevent browser body and Frappe page container scrolling by aligning heights exactly */
html, body, #web-page, .page-container, .main-section, .page-content, .page-content-wrapper {
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* Global Typography */
* {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* Enforce Latin digits in inputs, selectors, and textareas */
input, select, textarea, .v-text-field input, .v-field__input, .v-select__selection, .price-input, .qty-input {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  font-variant-numeric: lining-nums !important;
  font-feature-settings: "lnum" 1 !important;
  -webkit-locale: "en-US" !important;
  locale: "en-US" !important;
}

/* Also format lists, totals, numbers in Latin digits */
.price-input, .qty-input, .total-value, .card-price, .paid-amount-value, .change-amount-value, .remaining-amount-value, .v-chip, .v-data-table__td, .results-info, .pagination-container {
  font-family: 'Inter', sans-serif !important;
}

/* Premium background gradient for the page */
.v-application {
  background: linear-gradient(135deg, #f4f7f6 0%, #e9eef2 100%) !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: rgba(240, 240, 240, 0.5);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb {
  background: rgba(0, 151, 167, 0.2);
  border-radius: 4px;
  transition: all 0.3s;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 151, 167, 0.5);
}

/* Glassmorphic Cards & Elevate standard containers */
.v-card {
  border-radius: 4px !important;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.03) !important;
  border: 1px solid rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(10px);
}

/* Premium gradient headers for all toolbars and dialog titles */
.v-toolbar, .bg-primary, .v-card-title.bg-grey-lighten-4, .pa-4.bg-grey-lighten-4 {
  background: linear-gradient(90deg, #075294 0%, #0097A7 100%) !important;
  color: white !important;
}
.v-toolbar-title, .text-h6 {
  color: white !important;
  font-weight: 600 !important;
}

/* Rounded, glowing text fields */
.v-field {
  border-radius: 4px !important;
  border: 1px solid rgba(0, 0, 0, 0.06) !important;
  transition: all 0.3s ease !important;
}
.v-field--focused {
  border-color: #0097A7 !important;
  box-shadow: 0 0 0 3px rgba(0, 151, 167, 0.15) !important;
}

/* Premium Buttons */
.v-btn--variant-elevated, .v-btn--variant-flat {
  border-radius: 4px !important;
  text-transform: none !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px !important;
  box-shadow: 0 4px 12px rgba(0, 151, 167, 0.1) !important;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}

/* Boxy chips and badges */
.v-chip {
  border-radius: 3px !important;
}
.v-btn--variant-elevated:hover, .v-btn--variant-flat:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 151, 167, 0.2) !important;
}
</style>

<style scoped>
.container1 {
  margin-top: 0px;
}
</style>
