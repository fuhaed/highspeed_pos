<template>
  <v-row justify="center">
    <v-dialog v-model="draftsDialog" max-width="1000px" transition="dialog-transition" scrollable>
      <v-locale-provider :rtl="isRTL">
        <v-card elevation="0" class="dialog-card" :dir="isRTL ? 'rtl' : 'ltr'">
          <v-card-title class="dialog-header pa-4 bg-gradient-header flex-shrink-0">
            <div class="header-content d-flex align-center" :class="{ 'flex-row-reverse': isRTL }">
              <v-icon size="24" color="white" :class="isRTL ? 'ml-3' : 'mr-3'">mdi-file-document-multiple</v-icon>
              <div class="text-start">
                <h3 class="dialog-title text-white font-weight-medium">{{ __('Load Sales Invoice') }}</h3>
                <p class="dialog-subtitle text-slate-300">{{ __('Load previously saved invoices') }}</p>
              </div>
            </div>
          </v-card-title>

          <v-divider></v-divider>

          <v-card-text class="pa-0">
            <v-container fluid class="pa-2">
              <v-row no-gutters>
                <v-col cols="12">
                  <v-data-table 
                    :headers="headers" 
                    :items="dialog_data" 
                    item-value="name" 
                    class="invoice-table" 
                    show-select
                    v-model="selected" 
                    select-strategy="single" 
                    return-object
                    hover
                    :items-per-page-text="__('Items per page:')"
                  >
                    <template v-slot:item.customer_name="{ item }">
                      <div class="customer-cell d-flex align-center py-2" :class="{ 'flex-row-reverse': isRTL }">
                        <v-avatar size="32" color="primary" :class="isRTL ? 'ms-2' : 'me-2'">
                          <span class="text-caption text-white">
                            {{ getInitials(item.customer_name) }}
                          </span>
                        </v-avatar>
                        <div class="text-start">
                          <div class="customer-name font-weight-medium text-slate-800">{{ item.customer_name }}</div>
                          <div class="invoice-number text-caption text-slate-500 font-mono">{{ item.name }}</div>
                        </div>
                      </div>
                    </template>

                    <template v-slot:item.posting_date="{ item }">
                      <div class="date-cell d-flex align-center text-slate-700" :class="{ 'flex-row-reverse': isRTL }">
                        <v-icon size="16" :class="isRTL ? 'ml-1' : 'mr-1'" class="text-slate-400">mdi-calendar</v-icon>
                        <span>{{ item.posting_date }}</span>
                      </div>
                    </template>

                    <template v-slot:item.posting_time="{ item }">
                      <div class="time-cell d-flex align-center text-slate-700" :class="{ 'flex-row-reverse': isRTL }">
                        <v-icon size="16" :class="isRTL ? 'ml-1' : 'mr-1'" class="text-slate-400">mdi-clock-outline</v-icon>
                        <span>{{ item.posting_time.split('.')[0] }}</span>
                      </div>
                    </template>

                    <template v-slot:item.grand_total="{ item }">
                      <div class="amount-cell d-flex align-baseline font-weight-bold" :style="{ justifyContent: isRTL ? 'flex-start' : 'flex-end' }">
                        <span class="currency text-caption text-slate-500 me-1">{{ currencySymbol(item.currency) }}</span>
                        <span class="amount text-primary">{{ formatCurrency(item.grand_total) }}</span>
                      </div>
                    </template>
                  </v-data-table>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>

          <v-divider></v-divider>

          <v-card-actions class="dialog-actions pa-4 bg-slate-50">
            <v-row dense :class="{ 'flex-row-reverse': isRTL }" class="w-100 ma-0">
              <v-spacer></v-spacer>
              <v-btn 
                variant="text" 
                color="error" 
                @click="close_dialog"
                class="action-btn px-4"
                :prepend-icon="isRTL ? '' : 'mdi-close'"
                :append-icon="isRTL ? 'mdi-close' : ''"
              >
                {{ __('Close') }}
              </v-btn>
              <v-btn 
                variant="flat" 
                color="success" 
                @click="submit_dialog"
                class="action-btn primary-btn px-4"
                :prepend-icon="isRTL ? '' : 'mdi-file-import'"
                :append-icon="isRTL ? 'mdi-file-import' : ''"
                :disabled="selected.length === 0"
              >
                {{ __('Load Sale') }}
              </v-btn>
            </v-row>
          </v-card-actions>
        </v-card>
      </v-locale-provider>
    </v-dialog>
  </v-row>
</template>

<script>
import format from '../../format';
export default {
  mixins: [format],
  data: () => ({
    draftsDialog: false,
    singleSelect: true,
    selected: [],
    dialog_data: {},
    isRTL: false,
    headers: [
      {
        title: __('Customer'),
        value: 'customer_name',
        align: 'start',
        sortable: true,
      },
      {
        title: __('Date'),
        align: 'start',
        sortable: true,
        value: 'posting_date',
      },
      {
        title: __('Time'),
        align: 'start',
        sortable: true,
        value: 'posting_time',
      },
      {
        title: __('Invoice'),
        value: 'name',
        align: 'start',
        sortable: true,
      },
      {
        title: __('Amount'),
        value: 'grand_total',
        align: 'end',
        sortable: false,
      },
    ],
  }),
  watch: {},
  methods: {
    close_dialog() {
      this.draftsDialog = false;
    },

    submit_dialog() {
      if (this.selected.length > 0) {
        this.eventBus.emit('load_invoice', this.selected[0]);
        this.draftsDialog = false;
      }
      else {
        this.eventBus.emit("show_message", {
          title: __('Select an invoice to load'),
          color: "error",
        });
      }
    },

    getInitials(name) {
      if (!name) return '?';
      return name
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase()
        .substring(0, 2);
    },

    __: window.__ || ((str) => str),
  },
  created: function () {
    const lang = frappe.boot.lang;
    const htmlDir = document.documentElement.getAttribute('dir');
    const bodyDir = document.body.getAttribute('dir');
    this.isRTL = htmlDir === 'rtl' || bodyDir === 'rtl' || ['ar', 'he', 'fa', 'ur'].includes(lang?.substring(0, 2));

    this.eventBus.on('open_drafts', (data) => {
      this.draftsDialog = true;
      this.dialog_data = data;
    });
  },
  beforeUnmount() {
    this.eventBus.off('open_drafts');
  },
};
</script>

<style scoped>
.dialog-card {
  border-radius: 4px !important;
  overflow: hidden;
}

.bg-gradient-header {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
}

.dialog-title {
  font-size: 1.1rem;
  margin: 0;
  line-height: 1.2;
}

.dialog-subtitle {
  font-size: 0.75rem;
  margin: 2px 0 0 0;
  font-weight: 400;
}

.invoice-table {
  background: transparent !important;
  border-radius: 0 !important;
}

.invoice-table :deep(.v-table__wrapper) {
  max-height: 400px;
  overflow-y: auto;
}

.invoice-table :deep(thead) {
  background: #f8fafc !important;
}

.invoice-table :deep(th) {
  font-weight: 600 !important;
  color: #475569 !important;
  font-size: 0.8rem !important;
  padding: 12px 16px !important;
  border-bottom: 1px solid #e2e8f0 !important;
}

.invoice-table :deep(tbody tr) {
  transition: all 0.2s ease;
}

.invoice-table :deep(tbody tr:hover) {
  background: #f8fafc !important;
}

.invoice-table :deep(tbody tr.v-data-table__selected) {
  background: #f0fdf4 !important; /* light green for selected */
}

.customer-name {
  font-size: 0.85rem;
}

.invoice-number {
  font-size: 0.7rem;
}

.date-cell,
.time-cell {
  font-size: 0.8rem;
}

.amount {
  font-size: 0.9rem;
}

.action-btn {
  height: 38px !important;
  font-weight: 500;
  border-radius: 4px !important;
  text-transform: none;
}

.primary-btn {
  box-shadow: none !important;
}

/* Scrollbar styling */
.invoice-table :deep(.v-table__wrapper)::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.invoice-table :deep(.v-table__wrapper)::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.invoice-table :deep(.v-table__wrapper)::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.invoice-table :deep(.v-table__wrapper)::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.invoice-table :deep(.v-data-table__td) {
  padding: 8px 16px !important;
  border-bottom: 1px solid #f1f5f9 !important;
}
</style>