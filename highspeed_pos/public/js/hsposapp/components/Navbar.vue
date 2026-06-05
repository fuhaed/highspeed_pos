<template>
  <v-navigation-drawer
    app
      permanent
      expand-on-hover
      rail
      location="left"
      class="hspos-sidebar"
      elevation="4"
    >
      <!-- Top Branding / Logo -->
      <div class="sidebar-brand-container py-6 px-4 text-center">
        <v-avatar color="rgba(255, 255, 255, 0.08)" size="48" class="mb-2 brand-avatar">
          <v-icon color="#0097A7" size="24">mdi-flash-fast</v-icon>
        </v-avatar>
        <div class="brand-title font-weight-bold text-uppercase brand-text">
          <span class="text-white font-weight-light">HIGHSPEED</span>
          <span class="text-accent font-weight-bold ml-1" style="color: #0097A7 !important;">POS</span>
        </div>
        <v-chip variant="flat" color="rgba(255,255,255,0.08)" size="x-small" class="text-white mt-2 brand-chip">
          <v-icon size="10" start>mdi-store</v-icon>
          {{ pos_profile?.name || 'POS' }}
        </v-chip>
      </div>

      <v-divider color="rgba(255,255,255,0.1)"></v-divider>

      <!-- Navigation List -->
      <v-list density="compact" nav class="sidebar-list py-4">
        <!-- POS Page Item -->
        <v-list-item
          :active="currentPage === 'POS'"
          value="POS"
          @click="changePage('POS')"
          prepend-icon="mdi-view-dashboard"
          :title="__('POS')"
          class="mb-2 sidebar-item"
          rounded="sm"
        ></v-list-item>

        <!-- Payments Page Item -->
        <v-list-item
          v-if="pos_profile?.hspos_use_highspeed_pos_payments"
          :active="currentPage === 'Payments'"
          value="Payments"
          @click="changePage('Payments')"
          prepend-icon="mdi-cash-register"
          :title="__('Payments')"
          class="mb-2 sidebar-item"
          rounded="sm"
        ></v-list-item>

        <v-divider class="my-4" color="rgba(255,255,255,0.1)"></v-divider>

        <!-- Recent Invoices Item -->
        <v-list-item
          @click="showInvoicesDialog = true"
          :title="__('Recent Invoices')"
          class="mb-2 sidebar-item"
          rounded="sm"
        >
          <template v-slot:prepend>
            <v-badge 
              v-if="lastInvoices.length > 0" 
              :content="lastInvoices.length"
              color="error"
              dot
              offset-x="2"
              offset-y="2"
            >
              <v-icon>mdi-receipt-text</v-icon>
            </v-badge>
            <v-icon v-else>mdi-receipt-text</v-icon>
          </template>
        </v-list-item>

        <!-- Print Last Invoice Item -->
        <v-list-item
          v-if="pos_profile?.hspos_allow_print_last_invoice && last_invoice"
          @click="print_last_invoice"
          prepend-icon="mdi-printer"
          :title="__('Print Last')"
          class="mb-2 sidebar-item"
          rounded="sm"
        ></v-list-item>

        <!-- Shift Stats Item -->
        <v-list-item
          v-if="pos_profile"
          @click="showShiftStats = true"
          prepend-icon="mdi-chart-line"
          :title="__('Shift Statistics')"
          class="mb-2 sidebar-item"
          rounded="sm"
        ></v-list-item>

        <!-- Close Shift Item -->
        <v-list-item
          v-if="pos_profile && !pos_profile.hspos_hide_closing_shift"
          @click="close_shift_dialog"
          prepend-icon="mdi-content-save-move-outline"
          :title="__('Close Shift')"
          class="mb-2 sidebar-item"
          rounded="sm"
        ></v-list-item>

        <!-- Fullscreen Item -->
        <v-list-item
          @click="toggleFullScreen"
          :prepend-icon="isFullscreen ? 'mdi-fullscreen-exit' : 'mdi-fullscreen'"
          :title="isFullscreen ? __('Exit Full') : __('Fullscreen')"
          class="mb-2 sidebar-item"
          rounded="sm"
        ></v-list-item>

        <!-- Go to Desk Item -->
        <v-list-item
          @click="go_desk"
          prepend-icon="mdi-home"
          :title="__('Go to Desk')"
          class="mb-2 sidebar-item"
          rounded="sm"
        ></v-list-item>
      </v-list>

      <!-- Bottom Footer (Logout) -->
      <template v-slot:append>
        <div class="pa-4 footer-container">
          <v-list-item
            @click="logOut"
            prepend-icon="mdi-logout"
            :title="__('Logout')"
            class="sidebar-item logout-item"
            rounded="sm"
            style="color: #ff5252 !important;"
          ></v-list-item>
        </div>
      </template>
    </v-navigation-drawer>

    <!-- Recent Invoices Dialog -->
    <v-dialog v-model="showInvoicesDialog" max-width="1000" scrollable>
      <v-locale-provider :rtl="isRTL">
        <v-card class="invoice-dialog" :class="{ 'rtl': isRTL }" :dir="isRTL ? 'rtl' : 'ltr'">
          <v-card-title class="invoice-header d-flex align-center">
            <span class="text-h6 font-weight-medium text-white">{{ __('Recent Invoices') }}</span>
            <v-spacer></v-spacer>
            <v-btn icon variant="text" color="white" @click="showInvoicesDialog = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text class="pa-0">
            <v-table class="invoice-table" fixed-header height="450">
              <thead>
                <tr>
                  <th class="text-start">{{ __('Invoice') }}</th>
                  <th class="text-start">{{ __('Customer') }}</th>
                  <th class="text-start">{{ __('Date') }}</th>
                  <th v-if="pos_profile?.hspos_enable_order_number" class="text-center" width="120">{{ __('Order No') }}</th>
                  <th class="text-start" width="200">{{ __('Amount') }}</th>
                  <th class="text-center" width="150">{{ __('Actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="invoice in lastInvoices" :key="invoice.name" class="invoice-row">
                  <td class="text-start text-slate-600 font-mono">{{ invoice.name }}</td>
                  <td class="text-start text-slate-800">{{ invoice.customer_name || __('Walk-in Customer') }}</td>
                  <td class="text-start text-slate-700">{{ formatDate(invoice.posting_date) }}</td>
                  <td v-if="pos_profile?.hspos_enable_order_number" class="text-center">
                    <v-chip
                      v-if="invoice.hspos_order_no"
                      color="teal-darken-1"
                      variant="flat"
                      size="small"
                      class="font-weight-bold px-3 text-white"
                    >
                      #{{ invoice.hspos_order_no }}
                    </v-chip>
                    <span v-else class="text-grey-lighten-1">-</span>
                  </td>
                  <td class="text-start">
                    <span class="font-weight-medium text-slate-800">{{ currencySymbol(invoice.currency) }}{{ formatCurrency(invoice.grand_total) }}</span>
                  </td>
                  <td class="text-center">
                    <v-btn 
                      icon 
                      size="small" 
                      @click="printInvoiceDirect(invoice.name)"
                      color="primary"
                      variant="tonal"
                      class="ma-1 action-btn-round"
                    >
                      <v-icon size="18">mdi-printer</v-icon>
                    </v-btn>
                    <v-btn 
                      icon 
                      size="small" 
                      @click="viewInvoice(invoice.name)"
                      color="grey"
                      variant="tonal"
                      class="ma-1 action-btn-round"
                    >
                      <v-icon size="18">mdi-eye</v-icon>
                    </v-btn>
                  </td>
                </tr>
              </tbody>
            </v-table>
            
            <div v-if="lastInvoices.length === 0" class="empty-state text-center pa-8">
              <v-icon size="64" color="grey-lighten-2">mdi-receipt-text-remove</v-icon>
              <p class="text-h6 mt-4">{{ __('No invoices found') }}</p>
              <p class="text-body-2 text-grey">{{ __('Your recent invoices will appear here') }}</p>
            </div>
          </v-card-text>
        </v-card>
      </v-locale-provider>
    </v-dialog>

    <v-snackbar 
      v-model="snack" 
      :timeout="5000" 
      :color="snackColor" 
      :location="getSnackbarLocation()"
    >
      {{ snackText }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snack = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>

    <!-- Shift Statistics Dialog -->
    <v-dialog v-model="showShiftStats" max-width="700px">
      <v-card class="elevation-0 rounded-xl overflow-hidden" :class="{ 'rtl': isRTL }" :dir="isRTL ? 'rtl' : 'ltr'">
        <v-card-title class="pa-4 bg-primary text-white d-flex align-center">
          <v-icon class="ml-3" color="white">mdi-chart-line</v-icon>
          <span class="text-h6 font-weight-bold">{{ __('POS Shift Report Center') }}</span>
          <v-spacer></v-spacer>
          <v-btn 
            prepend-icon="mdi-printer" 
            variant="flat" 
            color="success" 
            class="mr-2 font-weight-bold rounded-lg"
            @click="printShiftReport" 
            v-if="shiftStats"
            size="small"
          >
            {{ __('Print Report') }}
          </v-btn>
          <v-btn icon variant="text" color="white" @click="showShiftStats = false" class="mr-2" density="compact">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-card-text class="pa-0" v-if="shiftStats">
          <v-tabs v-model="activeTab" color="primary" grow bgColor="grey-lighten-4">
            <v-tab value="summary" class="font-weight-bold">{{ __('Summary') }}</v-tab>
            <v-tab value="sales" class="font-weight-bold">{{ __('Sales by Product') }}</v-tab>
            <v-tab value="payments" class="font-weight-bold">{{ __('Payments') }}</v-tab>
            <v-tab value="addons" class="font-weight-bold">{{ __('Add-ons') }}</v-tab>
          </v-tabs>
          
          <v-window v-model="activeTab" class="pa-5">
            <!-- Summary Tab -->
            <v-window-item value="summary">
              <div class="text-subtitle-1 mb-4 font-weight-bold text-grey-darken-3">
                {{ __('Shift Status & Summary') }}
              </div>
              <v-row class="mb-4">
                <v-col cols="3" class="text-center border-right">
                  <div class="text-h6 text-primary font-weight-bold">
                    {{ currencySymbol(pos_profile.currency) }}{{ formatCurrency(shiftStats.grand_total) }}
                  </div>
                  <div class="text-caption text-grey-darken-1">{{ __('Total Sales') }}</div>
                </v-col>
                <v-col cols="3" class="text-center border-right">
                  <div class="text-h6 text-primary font-weight-bold">
                    {{ formatCurrency(shiftStats.total_quantity) }}
                  </div>
                  <div class="text-caption text-grey-darken-1">{{ __('Total Quantity') }}</div>
                </v-col>
                <v-col cols="3" class="text-center border-right">
                  <div class="text-h6 text-primary font-weight-bold">
                    {{ shiftStats.pos_transactions ? shiftStats.pos_transactions.length : 0 }}
                  </div>
                  <div class="text-caption text-grey-darken-1">{{ __('Invoices Count') }}</div>
                </v-col>
                <v-col cols="3" class="text-center">
                  <div class="text-h6 text-primary font-weight-bold">
                    {{ currencySymbol(pos_profile.currency) }}{{ formatCurrency(shiftStats.average_ticket || 0) }}
                  </div>
                  <div class="text-caption text-grey-darken-1">{{ __('Average Ticket') }}</div>
                </v-col>
              </v-row>
              
              <v-divider class="my-4" v-if="shiftStats.hspos_zatca_stats"></v-divider>
              
              <div class="text-subtitle-1 mb-3 font-weight-bold text-grey-darken-3" v-if="shiftStats.hspos_zatca_stats">
                {{ __('ZATCA Submission Summary') }}
              </div>
              
              <div class="border rounded-lg pa-4 bg-grey-lighten-5 mb-2" v-if="shiftStats.hspos_zatca_stats">
                <v-row>
                  <v-col cols="3" class="text-center">
                    <div class="text-h6 text-success font-weight-bold">{{ shiftStats.hspos_zatca_stats.cleared || 0 }}</div>
                    <div class="text-caption text-grey-darken-1">{{ __('Cleared') }}</div>
                  </v-col>
                  <v-col cols="3" class="text-center">
                    <div class="text-h6 text-success font-weight-bold">{{ shiftStats.hspos_zatca_stats.reported || 0 }}</div>
                    <div class="text-caption text-grey-darken-1">{{ __('Reported') }}</div>
                  </v-col>
                  <v-col cols="3" class="text-center">
                    <div class="text-h6 text-error font-weight-bold">{{ shiftStats.hspos_zatca_stats.rejected || 0 }}</div>
                    <div class="text-caption text-grey-darken-1">{{ __('Rejected') }}</div>
                  </v-col>
                  <v-col cols="3" class="text-center">
                    <div class="text-h6 text-warning font-weight-bold">{{ shiftStats.hspos_zatca_stats.not_sent || 0 }}</div>
                    <div class="text-caption text-grey-darken-1">{{ __('Not Sent') }}</div>
                  </v-col>
                </v-row>
              </div>
            </v-window-item>
            
            <!-- Sales by Product Tab -->
            <v-window-item value="sales">
              <v-table class="border rounded-lg" density="comfortable">
                <thead>
                  <tr>
                    <th class="text-right bg-grey-lighten-5">{{ __('Product') }}</th>
                    <th class="text-left bg-grey-lighten-5">{{ __('Quantity') }}</th>
                    <th class="text-left bg-grey-lighten-5">{{ __('Amount') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in shiftStats.product_sales" :key="item.item_code">
                    <td class="text-right font-weight-medium">{{ item.item_name }}</td>
                    <td class="text-left font-weight-medium text-grey-darken-3">{{ item.qty }}</td>
                    <td class="text-left font-weight-bold text-primary">{{ currencySymbol(pos_profile.currency) }}{{ formatCurrency(item.amount) }}</td>
                  </tr>
                  <tr v-if="!shiftStats.product_sales || shiftStats.product_sales.length === 0">
                    <td colspan="3" class="text-center text-grey py-4">{{ __('No sales transactions') }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-window-item>
            
            <!-- Payments Tab -->
            <v-window-item value="payments">
              <v-table class="border rounded-lg" density="comfortable">
                <thead>
                  <tr>
                    <th class="text-right bg-grey-lighten-5">{{ __('Mode of Payment') }}</th>
                    <th class="text-left bg-grey-lighten-5">{{ __('Opening Amount') }}</th>
                    <th class="text-left bg-grey-lighten-5">{{ __('Expected Amount') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in shiftStats.payment_reconciliation" :key="item.mode_of_payment">
                    <td class="text-right font-weight-medium">{{ __(item.mode_of_payment) }}</td>
                    <td class="text-left">{{ currencySymbol(pos_profile.currency) }}{{ formatCurrency(item.opening_amount) }}</td>
                    <td class="text-left font-weight-bold text-success">{{ currencySymbol(pos_profile.currency) }}{{ formatCurrency(item.expected_amount) }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-window-item>
            
            <!-- Add-ons Tab -->
            <v-window-item value="addons">
              <v-table class="border rounded-lg" density="comfortable">
                <thead>
                  <tr>
                    <th class="text-right bg-grey-lighten-5">{{ __('Add-on Name') }}</th>
                    <th class="text-left bg-grey-lighten-5">{{ __('Quantity') }}</th>
                    <th class="text-left bg-grey-lighten-5">{{ __('Amount') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in shiftStats.addon_sales" :key="item.addon_name">
                    <td class="text-right font-weight-medium">{{ item.addon_name }}</td>
                    <td class="text-left font-weight-medium text-grey-darken-3">{{ item.qty }}</td>
                    <td class="text-left font-weight-bold text-primary">{{ currencySymbol(pos_profile.currency) }}{{ formatCurrency(item.amount) }}</td>
                  </tr>
                  <tr v-if="!shiftStats.addon_sales || shiftStats.addon_sales.length === 0">
                    <td colspan="3" class="text-center text-grey py-4">{{ __('No add-ons sold') }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-window-item>
          </v-window>
        </v-card-text>
        <v-card-text class="pa-5 text-center" v-else>
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <div class="mt-3 text-grey">{{ __('Loading...') }}</div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog v-model="freeze" persistent max-width="320">
      <v-locale-provider :rtl="isRTL">
        <v-card :class="{ 'rtl': isRTL }" :dir="isRTL ? 'rtl' : 'ltr'">
          <v-card-title class="text-start">{{ freezeTitle }}</v-card-title>
          <v-card-text class="text-start">{{ freezeMsg }}</v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-progress-circular indeterminate color="primary" size="24"></v-progress-circular>
          </v-card-actions>
        </v-card>
      </v-locale-provider>
    </v-dialog>
</template>

<script>
export default {
  data() {
    return {
      currentPage: 'POS',
      snack: false,
      snackColor: '',
      snackText: '',
      company: 'HIGHSPEED IT',
      company_img: '/assets/erpnext/images/erpnext-logo.svg',
      pos_profile: '',
      freeze: false,
      freezeTitle: '',
      freezeMsg: '',
      last_invoice: '',
      lastInvoices: [],
      showInvoicesDialog: false,
      isFullscreen: false,
      isRTL: false,
      showShiftStats: false,
      shiftStats: null,
      opening_shift: null,
      activeTab: 'summary',
    };
  },

  watch: {
    showShiftStats(val) {
      if (val) {
        this.activeTab = 'summary';
        this.fetchShiftStats();
      }
    }
  },
  
  methods: {
    changePage(key) {
      this.currentPage = key;
      this.$emit('changePage', key);
    },
    
    go_desk() {
      frappe.set_route('/');
      location.reload();
    },
    
    close_shift_dialog() {
      this.eventBus.emit('open_closing_dialog');
    },
    
    show_message(data) {
      this.snack = true;
      this.snackColor = data.color;
      this.snackText = data.title;
    },
    
    logOut() {
      frappe.call({
        method: 'logout',
        callback: function (r) {
          if (!r.exc) {
            frappe.set_route('/login');
            location.reload();
          }
        },
      });
    },
    
    print_last_invoice() {
      if (!this.last_invoice) return;
      this.printInvoiceDirect(this.last_invoice);
    },
    
    printInvoiceDirect(invoiceName) {
      if (!invoiceName) return;
      
      const print_format = this.pos_profile.print_format_for_online || this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      
      const printFrame = document.createElement('iframe');
      printFrame.style.display = 'none';
      printFrame.src = frappe.urllib.get_base_url() +
        '/printview?doctype=Sales%20Invoice&name=' +
        invoiceName +
        '&format=' +
        print_format +
        '&no_letterhead=' +
        letter_head;
      
      document.body.appendChild(printFrame);
      
      printFrame.onload = function() {
        setTimeout(() => {
          printFrame.contentWindow.focus();
          printFrame.contentWindow.print();
          setTimeout(() => {
            if (printFrame && printFrame.parentNode) {
              document.body.removeChild(printFrame);
            }
          }, 3000);
        }, 500);
      };
    },
    
    loadLastInvoices() {
      frappe.call({
        method: 'frappe.client.get_list',
        args: {
          doctype: 'Sales Invoice',
          fields: ['name', 'customer_name', 'grand_total', 'posting_date', 'posting_time', 'currency', 'hspos_order_no'],
          filters: {
            docstatus: 1,
            pos_profile: this.pos_profile.name
          },
          order_by: 'creation desc',
          limit: 10
        },
        callback: (r) => {
          if (r.message) {
            this.lastInvoices = r.message;
          }
        }
      });
    },
    
    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleDateString('en-US');
    },
    
    viewInvoice(invoiceName) {
      const url = frappe.urllib.get_base_url() + '/app/sales-invoice/' + invoiceName;
      window.open(url, '_blank');
    },
    
    currencySymbol(currency) {
      const symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'SAR': 'ر.س',
        'AED': 'د.إ',
        'EGP': 'ج.م',
        'INR': '₹'
      };
      return symbols[currency] || currency + ' ';
    },
    
    formatCurrency(value) {
      if (!value) return '0.00';
      return parseFloat(value).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    },
    
    toggleFullScreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().then(() => {
          this.isFullscreen = true;
        }).catch((err) => {
          console.warn(`Error attempting to enable full-screen mode: ${err.message}`);
        });
      } else {
        document.exitFullscreen().then(() => {
          this.isFullscreen = false;
        });
      }
    },
    
    detectRTL() {
      const htmlDir = document.documentElement.getAttribute('dir');
      const bodyDir = document.body.getAttribute('dir');
      const lang = frappe.boot.lang || document.documentElement.lang || 'en';
      this.isRTL = htmlDir === 'rtl' || bodyDir === 'rtl' || ['ar', 'he', 'fa', 'ur'].includes(lang?.substring(0, 2));
    },
    
    getTextAlign(position) {
      if (position === 'start') {
        return this.isRTL ? 'text-right' : 'text-left';
      } else if (position === 'end') {
        return this.isRTL ? 'text-left' : 'text-right';
      }
      return 'text-center';
    },
    
    getSnackbarLocation() {
      return this.isRTL ? 'top left' : 'top right';
    },

    fetchShiftStats() {
      this.shiftStats = null;
      if (!this.opening_shift) return;
      frappe.call({
        method: 'highspeed_pos.highspeed_pos.doctype.hspos_closing_shift.hspos_closing_shift.make_closing_shift_from_opening',
        args: {
          opening_shift: this.opening_shift,
          submit_invoices: 0
        },
        callback: (r) => {
          if (r.message) {
            this.shiftStats = r.message;
          }
        }
      });
    },

    printShiftReport() {
      if (!this.shiftStats) return;
      
      const isRtl = this.isRTL;
      const currency = this.pos_profile.currency;
      const formatCurrency = this.formatCurrency;
      const currencySymbol = this.currencySymbol;
      
      let paymentsHtml = '';
      if (this.shiftStats.payment_reconciliation) {
        this.shiftStats.payment_reconciliation.forEach(p => {
          paymentsHtml += `
            <tr>
              <td>${window.__ ? window.__(p.mode_of_payment) : p.mode_of_payment}</td>
              <td class="num">${currencySymbol(currency)} ${formatCurrency(p.opening_amount)}</td>
              <td class="num">${currencySymbol(currency)} ${formatCurrency(p.expected_amount)}</td>
            </tr>
          `;
        });
      }
      
      let productsHtml = '';
      if (this.shiftStats.product_sales) {
        this.shiftStats.product_sales.forEach(p => {
          productsHtml += `
            <tr>
              <td>${p.item_name}</td>
              <td class="num">${p.qty}</td>
              <td class="num">${currencySymbol(currency)} ${formatCurrency(p.amount)}</td>
            </tr>
          `;
        });
      }
      
      let addonsHtml = '';
      if (this.shiftStats.addon_sales && this.shiftStats.addon_sales.length > 0) {
        this.shiftStats.addon_sales.forEach(a => {
          addonsHtml += `
            <tr>
              <td>${a.addon_name}</td>
              <td class="num">${a.qty}</td>
              <td class="num">${currencySymbol(currency)} ${formatCurrency(a.amount)}</td>
            </tr>
          `;
        });
      } else {
        addonsHtml = `<tr><td colspan="3" style="text-align: center;">${window.__ ? window.__('No add-ons sold') : 'No add-ons sold'}</td></tr>`;
      }
      
      let zatcaHtml = '';
      if (this.shiftStats.hspos_zatca_stats) {
        const z = this.shiftStats.hspos_zatca_stats;
        zatcaHtml = `
          <div class="line"></div>
          <div class="section-title">ملخص إرسال زاتكا / ZATCA Summary</div>
          <table class="summary-table">
            <tr><td>مقبول (Cleared)</td><td class="num">${z.cleared || 0}</td></tr>
            <tr><td>مبلغ (Reported)</td><td class="num">${z.reported || 0}</td></tr>
            <tr><td>مرفوض (Rejected)</td><td class="num text-error">${z.rejected || 0}</td></tr>
            <tr><td>لم يرسل (Not Sent)</td><td class="num">${z.not_sent || 0}</td></tr>
          </table>
        `;
      }
      
      const now = new Date();
      const dateStr = now.toLocaleDateString() + ' ' + now.toLocaleTimeString();
      
      const html = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>Shift Report</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              font-size: 11px;
              line-height: 1.3;
              margin: 0;
              padding: 5px;
              direction: ${isRtl ? 'rtl' : 'ltr'};
            }
            .shift-report-print {
              width: 72mm;
              margin: 0 auto;
            }
            .header {
              text-align: center;
              margin-bottom: 10px;
            }
            .header h2 {
              margin: 0;
              font-size: 14px;
            }
            .header h3 {
              margin: 0;
              font-size: 11px;
              font-weight: normal;
              color: #666;
            }
            .line {
              border-top: 1px dashed #000;
              margin: 8px 0;
            }
            .meta {
              font-size: 10px;
              margin-bottom: 10px;
            }
            .meta div {
              margin-bottom: 2px;
            }
            .section-title {
              font-weight: bold;
              font-size: 11px;
              margin-bottom: 5px;
              border-bottom: 1px solid #000;
              padding-bottom: 2px;
            }
            .summary-table, .report-table {
              width: 100%;
              border-collapse: collapse;
              margin-bottom: 10px;
              font-size: 10px;
            }
            .summary-table td {
              padding: 3px 0;
            }
            .report-table th, .report-table td {
              padding: 3px 2px;
              text-align: ${isRtl ? 'right' : 'left'};
            }
            .report-table th {
              border-bottom: 1px solid #000;
            }
            .report-table td {
              border-bottom: 1px dashed #eee;
            }
            .num {
              text-align: ${isRtl ? 'left' : 'right'} !important;
            }
            .text-error {
              color: #ff0000;
            }
            .footer {
              text-align: center;
              margin-top: 15px;
              font-size: 9px;
              color: #777;
            }
          </style>
        </head>
        <body>
          <div class="shift-report-print">
            <div class="header">
              <h2>تقرير الوردية المالي</h2>
              <h3>Shift Financial Report</h3>
            </div>
            <div class="line"></div>
            <div class="meta">
              <div><b>المستخدم / Cashier:</b> ${this.shiftStats.user || ''}</div>
              <div><b>الوردية / Shift:</b> ${this.opening_shift || ''}</div>
              <div><b>نقطة البيع / POS Profile:</b> ${this.pos_profile.name || ''}</div>
              <div><b>تاريخ الطباعة / Printed At:</b> ${dateStr}</div>
            </div>
            <div class="line"></div>
            
            <div class="section-title">ملخص الوردية / Shift Summary</div>
            <table class="summary-table">
              <tr><td>إجمالي المبيعات / Total Sales</td><td class="num">${currencySymbol(currency)} ${formatCurrency(this.shiftStats.grand_total)}</td></tr>
              <tr><td>الكمية الإجمالية / Total Qty</td><td class="num">${formatCurrency(this.shiftStats.total_quantity)}</td></tr>
              <tr><td>عدد الفواتير / Invoices Count</td><td class="num">${this.shiftStats.pos_transactions ? this.shiftStats.pos_transactions.length : 0}</td></tr>
              <tr><td>متوسط الفاتورة / Avg Ticket</td><td class="num">${currencySymbol(currency)} ${formatCurrency(this.shiftStats.average_ticket || 0)}</td></tr>
            </table>
            
            <div class="line"></div>
            <div class="section-title">طرق الدفع / Payments Summary</div>
            <table class="report-table">
              <thead>
                <tr>
                  <th>طريقة الدفع</th>
                  <th class="num">الافتتاحي</th>
                  <th class="num">المتوقع</th>
                </tr>
              </thead>
              <tbody>
                ${paymentsHtml}
              </tbody>
            </table>

            <div class="line"></div>
            <div class="section-title">مبيعات الأصناف / Product Sales</div>
            <table class="report-table">
              <thead>
                <tr>
                  <th>الصنف</th>
                  <th class="num">الكمية</th>
                  <th class="num">الإجمالي</th>
                </tr>
              </thead>
              <tbody>
                ${productsHtml}
              </tbody>
            </table>

            <div class="line"></div>
            <div class="section-title">تقرير الإضافات / Add-ons Summary</div>
            <table class="report-table">
              <thead>
                <tr>
                  <th>الإضافة</th>
                  <th class="num">الكمية</th>
                  <th class="num">الإجمالي</th>
                </tr>
              </thead>
              <tbody>
                ${addonsHtml}
              </tbody>
            </table>

            ${zatcaHtml}
            
            <div class="line"></div>
            <div class="footer">
              طُبع بواسطة نظام HIGHSPEED IT POS
            </div>
          </div>
          \x3Cscript>
            window.onload = function() {
              window.print();
              setTimeout(function() { window.close(); }, 500);
            };
          \x3C/script>
        </body>
        </html>
      `;
      
      const printWindow = window.open('', '_blank');
      printWindow.document.write(html);
      printWindow.document.close();
    },

    __: window.__ || ((str) => str),
  },
  
  created() {
    this.detectRTL();
    
    this.$nextTick(() => {
      this.eventBus.on('show_message', (data) => this.show_message(data));
      this.eventBus.on('set_company', (data) => {
        this.company = data.name;
        this.company_img = data.company_logo || this.company_img;
      });
      this.eventBus.on('register_pos_profile', (data) => {
        this.pos_profile = data.pos_profile;
        this.opening_shift = data.hspos_opening_shift;
        this.loadLastInvoices();
      });
      this.eventBus.on('set_last_invoice', (data) => {
        this.last_invoice = data;
        this.loadLastInvoices();
      });
      this.eventBus.on('freeze', (data) => {
        this.freeze = true;
        this.freezeTitle = data.title;
        this.freezeMsg = data.msg;
      });
      this.eventBus.on('unfreeze', () => {
        this.freeze = false;
        this.freezeTitle = '';
        this.freezeMsg = '';
      });
    });
  },
  
  mounted() {
    const observer = new MutationObserver(() => {
      this.detectRTL();
    });
    
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['dir', 'lang']
    });
    
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['dir']
    });
    
    this.$watch('isRTL', (newVal) => {
      this.$nextTick(() => {
        this.$forceUpdate();
      });
    });
  },
};
</script>

<style scoped>
.hspos-sidebar {
  background: linear-gradient(180deg, #0c1b33 0%, #030a16 100%) !important;
  border: none !important;
  color: #b0c4de !important;
  box-shadow: 0 0 25px rgba(0, 0, 0, 0.15) !important;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}

.sidebar-brand-container {
  transition: all 0.3s ease;
}

.brand-avatar {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  transition: all 0.3s ease;
}

.hspos-sidebar:hover .brand-avatar {
  transform: rotate(15deg) scale(1.05);
}

.brand-text {
  font-size: 0.95rem;
  letter-spacing: 0.5px;
  margin-top: 8px;
  transition: opacity 0.2s ease;
}

.brand-chip {
  transition: opacity 0.2s ease;
}

/* Adjust brand padding and avatar size when collapsed in rail mode */
.v-navigation-drawer--rail:not(.v-navigation-drawer--is-hovering) .sidebar-brand-container {
  padding-left: 8px !important;
  padding-right: 8px !important;
  padding-top: 16px !important;
  padding-bottom: 16px !important;
}

.v-navigation-drawer--rail:not(.v-navigation-drawer--is-hovering) .brand-avatar {
  width: 36px !important;
  height: 36px !important;
}

.v-navigation-drawer--rail:not(.v-navigation-drawer--is-hovering) .brand-avatar .v-icon {
  font-size: 20px !important;
}

/* Hide text elements in rail mode */
.v-navigation-drawer--rail:not(.v-navigation-drawer--is-hovering) .brand-text,
.v-navigation-drawer--rail:not(.v-navigation-drawer--is-hovering) .brand-chip {
  display: none !important;
}

.sidebar-item {
  color: #a0aec0 !important;
  transition: all 0.25s ease !important;
}

.sidebar-item:hover {
  background: rgba(255, 255, 255, 0.05) !important;
  color: #ffffff !important;
}

.sidebar-item.v-list-item--active {
  background: linear-gradient(90deg, #075294 0%, #0097A7 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 15px rgba(0, 151, 167, 0.3) !important;
}

.logout-item {
  margin-top: auto;
}

.invoice-dialog {
  border-radius: 4px !important;
}

.invoice-dialog.rtl {
  direction: rtl;
}

.invoice-header {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
  color: white !important;
  padding: 16px 24px;
}

.invoice-table {
  background: white;
}

.invoice-table :deep(thead) {
  background-color: #f8fafc;
}

.invoice-table :deep(th) {
  font-weight: 600 !important;
  color: #475569 !important;
  font-size: 0.8rem !important;
  padding: 12px 16px !important;
  border-bottom: 1px solid #e2e8f0 !important;
}

.invoice-row {
  transition: background-color 0.2s ease;
}

.invoice-row:hover {
  background-color: #f8fafc;
}

.invoice-row :deep(td) {
  padding: 8px 16px !important;
  border-bottom: 1px solid #f1f5f9 !important;
  font-size: 0.85rem;
}

.empty-state {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f8fafc;
}

.action-btn-round {
  border-radius: 4px !important;
}

@media (max-width: 768px) {
  .invoice-dialog {
    margin: 8px;
  }
}
</style>