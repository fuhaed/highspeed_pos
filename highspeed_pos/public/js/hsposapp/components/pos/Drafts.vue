<template>
  <v-row justify="center">
    <v-dialog v-model="draftsDialog" max-width="600px" transition="dialog-transition" scrollable>
      <v-locale-provider :rtl="isRTL">
        <v-card elevation="0" class="dialog-card" :dir="isRTL ? 'rtl' : 'ltr'">
          <v-card-title class="dialog-header pa-3 bg-gradient-header flex-shrink-0">
            <div class="header-content d-flex align-center" :class="{ 'flex-row-reverse': isRTL }">
              <v-icon size="24" color="white" :class="isRTL ? 'ml-3' : 'mr-3'">mdi-file-document-multiple</v-icon>
              <div class="text-start">
                <h3 class="dialog-title text-white font-weight-medium">{{ __('Load Sales Invoice') }}</h3>
                <p class="dialog-subtitle text-slate-300">{{ __('Load previously saved invoices') }}</p>
              </div>
            </div>
          </v-card-title>

          <v-divider></v-divider>

          <v-card-text class="pa-0 bg-slate-50">
            <v-container fluid class="pa-3">
              <v-row no-gutters>
                <v-col cols="12">
                  <div class="drafts-list overflow-y-auto px-1" style="max-height: 420px;">
                    <div
                      v-for="item in dialog_data"
                      :key="item.name"
                      class="mb-2 rounded-lg bg-white draft-item-card px-4 py-3 cursor-pointer d-flex align-center"
                      @click="selectDraft(item)"
                      @dblclick="loadDraft(item)"
                      :class="{ 'selected-draft-card': selected && selected[0] && selected[0].name === item.name }"
                      style="transition: all 0.2s ease; border: 1.5px solid #e2e8f0 !important;"
                    >
                      <!-- Left/Start side: Icon + Details -->
                      <div class="d-flex align-center flex-grow-1 min-width-0" style="gap: 12px;">
                        <!-- Icon -->
                        <v-avatar size="36" :color="selected && selected[0] && selected[0].name === item.name ? 'success' : 'amber-lighten-4'" class="flex-shrink-0">
                          <v-icon :color="selected && selected[0] && selected[0].name === item.name ? 'white' : 'amber-darken-3'" size="20">
                            {{ selected && selected[0] && selected[0].name === item.name ? 'mdi-check' : 'mdi-file-document-outline' }}
                          </v-icon>
                        </v-avatar>

                        <!-- Customer Info & Invoice Number -->
                        <div class="min-width-0 text-start">
                          <div class="d-flex align-center flex-wrap" style="gap: 8px;">
                            <span class="font-weight-bold text-slate-800 text-subtitle-2 text-truncate" style="max-width: 220px; line-height: 1.2;">
                              {{ item.customer_name || item.customer }}
                            </span>
                            <v-chip v-if="item.hspos_table" size="x-small" color="teal-darken-1" class="font-weight-bold text-white px-1.5" variant="flat" style="height: 18px;">
                              <v-icon start size="10" class="me-0.5">mdi-table-chair</v-icon>
                              {{ item.hspos_table }}
                            </v-chip>
                          </div>
                          <div class="text-caption text-slate-500 font-mono mt-1" style="font-size: 11px !important; line-height: 1.1;">
                            {{ item.name }}
                          </div>
                        </div>
                      </div>

                      <!-- Right/End side: Grand Total + Date/Time -->
                      <div class="text-end flex-shrink-0" style="margin-inline-start: 16px; min-width: 130px;">
                        <div class="font-weight-black text-amber-darken-4 text-subtitle-2" style="font-size: 1.1rem !important; line-height: 1.2;">
                          {{ formatCurrency(item.grand_total) }} <span class="text-caption text-slate-500 font-weight-medium" style="font-size: 10px !important;">{{ currencySymbol(item.currency) }}</span>
                        </div>
                        <div class="text-caption text-slate-400 mt-1 d-flex align-center justify-end" style="font-size: 10px !important; gap: 4px; line-height: 1.1;">
                          <v-icon size="11" class="text-slate-300">mdi-clock-outline</v-icon>
                          <span>{{ item.posting_date }} {{ item.posting_time.split('.')[0] }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>

          <v-divider></v-divider>

          <v-card-actions class="dialog-actions pa-3 bg-slate-100">
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
    selected: [],
    dialog_data: {},
    isRTL: false,
  }),
  watch: {},
  methods: {
    close_dialog() {
      this.draftsDialog = false;
    },

    selectDraft(item) {
      this.selected = [item];
    },

    loadDraft(item) {
      this.selected = [item];
      this.submit_dialog();
    },

    submit_dialog() {
      if (this.selected.length > 0) {
        this.eventBus.emit('load_invoice', this.selected[0]);
        this.draftsDialog = false;
      }
      else {
        this.eventBus.emit("show_message", {
          title: this.__('Select an invoice to load'),
          color: "error",
        });
      }
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
      this.selected = []; // Reset selection on open
    });
  },
  beforeUnmount() {
    this.eventBus.off('open_drafts');
  },
};
</script>

<style scoped>
.dialog-card {
  border-radius: 8px !important;
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

.draft-item-card {
  transition: all 0.25s ease;
}

.draft-item-card:hover {
  background-color: #f8fafc !important;
  border-color: #cbd5e1 !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
}

.selected-draft-card {
  background-color: #f0fdf4 !important;
  border-color: #22c55e !important;
  box-shadow: 0 0 0 1px #22c55e !important;
}

.selected-draft-card:hover {
  background-color: #f0fdf4 !important;
  border-color: #22c55e !important;
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
</style>