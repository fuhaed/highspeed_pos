<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <v-row justify="center">
    <v-dialog v-model="invoicesDialog" max-width="900px" persistent>
      <v-card class="rounded-lg">
        <!-- Header -->
        <v-card-title class="pa-0">
          <div class="pa-4 header-gradient text-white">
            <div class="d-flex align-center justify-space-between">
              <div class="d-flex align-center">
                <v-icon class="me-3" color="white" size="24">mdi-receipt-text-minus</v-icon>
                <span class="text-h6 font-weight-bold text-white">{{ __('Select Return Invoice') }}</span>
              </div>
              <v-btn 
                icon 
                variant="text" 
                size="small"
                color="white"
                @click="close_dialog">
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </div>
          </div>
        </v-card-title>

        <v-divider></v-divider>

        <v-card-text class="pa-0">
          <v-container fluid class="pa-4">
            <!-- Search Section -->
            <v-expansion-panels v-model="searchPanel" class="mb-4">
              <v-expansion-panel elevation="0">
                <v-expansion-panel-title class="filter-panel-title text-body-2">
                  <v-icon size="small" class="me-2">mdi-filter-variant</v-icon>
                  {{ __('Search Filters') }}
                  <template v-if="hasActiveFilters" v-slot:actions>
                    <v-chip size="x-small" color="primary" variant="tonal">
                      {{ activeFiltersCount }}
                    </v-chip>
                  </template>
                </v-expansion-panel-title>
                <v-expansion-panel-text class="pa-4 bg-grey-lighten-5">
                  <!-- Invoice Search -->
                  <div class="text-caption text-grey-darken-1 mb-2">{{ __('Invoice Details') }}</div>
                  <v-row class="mb-3">
                    <v-col cols="12" sm="6">
                      <v-text-field 
                        variant="outlined"
                        density="compact"
                        color="primary" 
                        :label="__('Invoice ID')" 
                        bg-color="white" 
                        hide-details
                        v-model="invoice_name" 
                        clearable
                        prepend-inner-icon="mdi-file-document-outline">
                      </v-text-field>
                    </v-col>
                    <v-col cols="6" sm="3">
                      <v-menu
                        v-model="fromDateMenu"
                        :close-on-content-click="false"
                        transition="scale-transition"
                        min-width="auto">
                        <template v-slot:activator="{ props }">
                          <v-text-field
                            variant="outlined"
                            density="compact"
                            v-model="from_date_formatted"
                            :label="__('From Date')"
                            prepend-inner-icon="mdi-calendar"
                            readonly
                            v-bind="props"
                            clearable
                            @click:clear="clearFromDate"
                            hide-details
                            color="primary"
                            bg-color="white">
                          </v-text-field>
                        </template>
                        <v-date-picker
                          v-model="from_date"
                          no-title
                          color="primary"
                          @update:model-value="fromDateMenu = false; formatFromDate();">
                        </v-date-picker>
                      </v-menu>
                    </v-col>
                    <v-col cols="6" sm="3">
                      <v-menu
                        v-model="toDateMenu"
                        :close-on-content-click="false"
                        transition="scale-transition"
                        min-width="auto">
                        <template v-slot:activator="{ props }">
                          <v-text-field
                            variant="outlined"
                            density="compact"
                            v-model="to_date_formatted"
                            :label="__('To Date')"
                            prepend-inner-icon="mdi-calendar"
                            readonly
                            v-bind="props"
                            clearable
                            @click:clear="clearToDate"
                            hide-details
                            color="primary"
                            bg-color="white">
                          </v-text-field>
                        </template>
                        <v-date-picker
                          v-model="to_date"
                          no-title
                          color="primary"
                          @update:model-value="toDateMenu = false; formatToDate();">
                        </v-date-picker>
                      </v-menu>
                    </v-col>
                  </v-row>

                  <v-divider class="my-3"></v-divider>

                  <!-- Customer Search -->
                  <div class="text-caption text-grey-darken-1 mb-2">{{ __('Customer Information') }}</div>
                  <v-row class="mb-3">
                    <v-col cols="12" sm="6">
                      <v-text-field 
                        variant="outlined"
                        density="compact"
                        color="primary" 
                        :label="__('Customer Name')" 
                        bg-color="white" 
                        hide-details
                        v-model="customer_name" 
                        clearable
                        prepend-inner-icon="mdi-account-outline">
                      </v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field 
                        variant="outlined"
                        density="compact"
                        color="primary" 
                        :label="__('Customer ID')" 
                        bg-color="white" 
                        hide-details
                        v-model="customer_id" 
                        clearable
                        prepend-inner-icon="mdi-identifier">
                      </v-text-field>
                    </v-col>
                  </v-row>
                  <v-row class="mb-3">
                    <v-col cols="12" sm="6">
                      <v-text-field 
                        variant="outlined"
                        density="compact"
                        color="primary" 
                        :label="__('Mobile Number')" 
                        bg-color="white" 
                        hide-details
                        v-model="mobile_no" 
                        clearable
                        prepend-inner-icon="mdi-cellphone">
                      </v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field 
                        variant="outlined"
                        density="compact"
                        color="primary" 
                        :label="__('Tax ID')" 
                        bg-color="white" 
                        hide-details
                        v-model="tax_id" 
                        clearable
                        prepend-inner-icon="mdi-file-certificate-outline">
                      </v-text-field>
                    </v-col>
                  </v-row>

                  <v-divider class="my-3"></v-divider>

                  <!-- Amount Filter -->
                  <div class="text-caption text-grey-darken-1 mb-2">{{ __('Amount Range') }}</div>
                  <v-row>
                    <v-col cols="12" sm="6">
                      <v-text-field 
                        variant="outlined"
                        density="compact"
                        color="primary" 
                        :label="__('Minimum Amount')" 
                        bg-color="white" 
                        hide-details
                        v-model="min_amount" 
                        clearable
                        type="text"
                        inputmode="decimal"
                        @update:model-value="val => min_amount = convertArabicToLatin(val).replace(/[^0-9.]/g, '')"
                        min="0"
                        :placeholder="__('No minimum')"
                        prepend-inner-icon="mdi-cash">
                      </v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field 
                        variant="outlined"
                        density="compact"
                        color="primary" 
                        :label="__('Maximum Amount')" 
                        bg-color="white" 
                        hide-details
                        v-model="max_amount" 
                        clearable
                        type="text"
                        inputmode="decimal"
                        @update:model-value="val => max_amount = convertArabicToLatin(val).replace(/[^0-9.]/g, '')"
                        min="0"
                        :placeholder="__('No maximum')"
                        prepend-inner-icon="mdi-cash">
                      </v-text-field>
                    </v-col>
                  </v-row>

                  <!-- Action Buttons -->
                  <v-row class="mt-4">
                    <v-col cols="12" class="d-flex justify-end gap-2">
                      <v-btn 
                        variant="text" 
                        color="grey" 
                        @click="clear_search"
                        size="small">
                        <v-icon size="small" class="me-1">mdi-refresh</v-icon>
                        {{ __('Clear Filters') }}
                      </v-btn>
                      <v-btn 
                        variant="flat" 
                        color="primary" 
                        @click="search_invoices"
                        size="small"
                        class="search-btn px-4">
                        <v-icon size="small" class="me-1">mdi-magnify</v-icon>
                        {{ __('Search') }}
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <!-- Results Section -->
            <div v-if="searched_once">
              <!-- No Results -->
              <v-alert 
                v-if="!dialog_data || dialog_data.length === 0"
                type="info"
                variant="tonal"
                class="mb-4">
                <v-icon>mdi-information-outline</v-icon>
                {{ __('No invoices found. Try different search criteria.') }}
              </v-alert>

              <!-- Results Table -->
              <v-card v-else flat class="border rounded-lg">
                <v-data-table 
                  :headers="headers" 
                  :items="dialog_data" 
                  item-key="name" 
                  show-select
                  v-model="selected" 
                  select-strategy="single" 
                  return-object
                  :footer-props="{
                    'items-per-page-options': [10, 25, 50],
                    'items-per-page-text': __('Invoices per page')
                  }"
                  :items-per-page="25"
                  class="invoice-table">
                  <template v-slot:item.customer="{ item }">
                    <div>
                      <div class="text-body-2 font-weight-medium">{{ item.customer }}</div>
                      <div class="text-caption text-grey" v-if="item.customer_name">{{ item.customer_name }}</div>
                    </div>
                  </template>
                  <template v-slot:item.posting_date="{ item }">
                    <v-chip size="small" variant="tonal" color="grey">
                      <v-icon size="x-small" class="me-1">mdi-calendar</v-icon>
                      {{ formatDateDisplay(item.posting_date) }}
                    </v-chip>
                  </template>
                  <template v-slot:item.name="{ item }">
                    <span class="text-primary font-weight-medium">{{ item.name }}</span>
                  </template>
                  <template v-slot:item.grand_total="{ item }">
                    <div class="text-right">
                      <span class="text-subtitle-2 font-weight-bold text-success">
                        {{ currencySymbol(item.currency) }}{{ formatCurrency(item.grand_total) }}
                      </span>
                    </div>
                  </template>
                </v-data-table>

                <!-- Load More -->
              <div class="text-center pa-3 bg-grey-lighten-5" v-if="has_more_invoices">
                <v-btn 
                  variant="text"
                  color="primary" 
                  :loading="loading_more" 
                  @click="load_more_invoices">
                  <v-icon size="small" class="me-1">mdi-chevron-down</v-icon>
                  {{ __('Load More Invoices') }}
                </v-btn>
              </div>
            </v-card>
          </div>

          <!-- Initial State -->
          <div v-else class="text-center py-8">
            <v-icon size="64" color="grey-lighten-2">mdi-file-search-outline</v-icon>
            <p class="text-h6 text-grey-darken-1 mt-4">{{ __('Search for invoices to return') }}</p>
            <p class="text-body-2 text-grey">{{ __('Use the filters above to find specific invoices') }}</p>
          </div>
        </v-container>
      </v-card-text>

      <v-divider></v-divider>

      <!-- Footer Actions -->
      <v-card-actions class="pa-4 bg-grey-lighten-5">
        <v-btn 
          v-if="pos_profile.hspos_allow_return_without_invoice == 1" 
          variant="text" 
          color="secondary"
          @click="return_without_invoice">
          <v-icon size="small" class="me-1">mdi-receipt-text-remove</v-icon>
          {{ __('Return without Invoice') }}
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn 
          variant="text" 
          @click="close_dialog">
          {{ __('Cancel') }}
        </v-btn>
        <v-btn 
          v-if="selected.length" 
          color="primary" 
          variant="flat"
          @click="submit_dialog"
          class="search-btn px-4">
          <v-icon size="small" class="me-1">mdi-check</v-icon>
          {{ __('Process Return') }}
        </v-btn>
      </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import format from '../../format';

export default {
  mixins: [format],
  data: () => ({
    invoicesDialog: false,
    searchPanel: 0,
    singleSelect: true,
    selected: [],
    dialog_data: [],
    company: '',
    invoice_name: '',
    customer_name: '',
    customer_id: '',
    mobile_no: '',
    tax_id: '',
    from_date: null,
    to_date: null,
    from_date_formatted: null,
    to_date_formatted: null,
    min_amount: '',
    max_amount: '',
    fromDateMenu: false,
    toDateMenu: false,
    pos_profile: '',
    page: 1,
    has_more_invoices: false,
    loading_more: false,
    searched_once: false,
    current_search_params: null,
    headers: [
      {
        title: __('Customer'),
        value: 'customer',
        align: 'start',
        sortable: true,
      },
      {
        title: __('Date'),
        align: 'center',
        sortable: true,
        value: 'posting_date',
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
        sortable: true,
      },
    ],
  }),
  
  computed: {
    hasActiveFilters() {
      return this.invoice_name || this.customer_name || this.customer_id || 
             this.mobile_no || this.tax_id || this.from_date || this.to_date || 
             this.min_amount || this.max_amount;
    },
    activeFiltersCount() {
      let count = 0;
      if (this.invoice_name) count++;
      if (this.customer_name) count++;
      if (this.customer_id) count++;
      if (this.mobile_no) count++;
      if (this.tax_id) count++;
      if (this.from_date) count++;
      if (this.to_date) count++;
      if (this.min_amount) count++;
      if (this.max_amount) count++;
      return count;
    }
  },
  
  watch: {
    from_date() {
      this.formatFromDate();
    },
    to_date() {
      this.formatToDate();
    }
  },
  
  methods: {
    convertArabicToLatin(str) {
      if (str === null || str === undefined) return '';
      str = String(str);
      return str.replace(/[٠-٩]/g, function(d) {
        return d.charCodeAt(0) - 1632;
      }).replace(/[۰-۹]/g, function(d) {
        return d.charCodeAt(0) - 1776;
      });
    },
    formatDateDisplay(dateStr) {
      if (!dateStr) return '';
      try {
        const parts = dateStr.split('-');
        if (parts.length === 3) {
          return `${parts[2]}/${parts[1]}/${parts[0]}`;
        }
      } catch (error) {
        console.error("Error formatting date:", error);
      }
      return dateStr;
    },
    
    formatFromDate() {
      if (this.from_date) {
        try {
          let dateString = '';
          
          if (typeof this.from_date === 'object' && this.from_date instanceof Date) {
            const day = String(this.from_date.getDate()).padStart(2, '0');
            const month = String(this.from_date.getMonth() + 1).padStart(2, '0');
            const year = this.from_date.getFullYear();
            dateString = `${day}/${month}/${year}`;
          }
          else if (typeof this.from_date === 'string' && this.from_date.includes('-')) {
            const parts = this.from_date.split('-');
            if (parts.length === 3) {
              dateString = `${parts[2]}/${parts[1]}/${parts[0]}`;
            } else {
              dateString = this.from_date;
            }
          } 
          else {
            dateString = String(this.from_date);
          }
          
          this.from_date_formatted = dateString;
        } catch (error) {
          console.error("Error formatting from_date:", error);
          this.from_date_formatted = String(this.from_date);
        }
      } else {
        this.from_date_formatted = null;
      }
    },
    
    formatToDate() {
      if (this.to_date) {
        try {
          let dateString = '';
          
          if (typeof this.to_date === 'object' && this.to_date instanceof Date) {
            const day = String(this.to_date.getDate()).padStart(2, '0');
            const month = String(this.to_date.getMonth() + 1).padStart(2, '0');
            const year = this.to_date.getFullYear();
            dateString = `${day}/${month}/${year}`;
          }
          else if (typeof this.to_date === 'string' && this.to_date.includes('-')) {
            const parts = this.to_date.split('-');
            if (parts.length === 3) {
              dateString = `${parts[2]}/${parts[1]}/${parts[0]}`;
            } else {
              dateString = this.to_date;
            }
          }
          else {
            dateString = String(this.to_date);
          }
          
          this.to_date_formatted = dateString;
        } catch (error) {
          console.error("Error formatting to_date:", error);
          this.to_date_formatted = String(this.to_date);
        }
      } else {
        this.to_date_formatted = null;
      }
    },
    
    clearFromDate() {
      this.from_date = null;
      this.from_date_formatted = null;
    },
    
    clearToDate() {
      this.to_date = null;
      this.to_date_formatted = null;
    },
    
    close_dialog() {
      this.invoicesDialog = false;
    },
    
    clear_search() {
      this.invoice_name = '';
      this.customer_name = '';
      this.customer_id = '';
      this.mobile_no = '';
      this.tax_id = '';
      this.from_date = null;
      this.to_date = null;
      this.from_date_formatted = null;
      this.to_date_formatted = null;
      this.min_amount = '';
      this.max_amount = '';
      this.dialog_data = [];
      this.page = 1;
      this.has_more_invoices = false;
      this.searched_once = false;
    },
    
    search_invoices() {
      this.page = 1;
      this.dialog_data = [];
      this.perform_search();
      this.searchPanel = null; // Collapse the search panel after searching
    },
    
    perform_search() {
      const vm = this;
      vm.loading_more = true;
      
      let formattedFromDate = null;
      let formattedToDate = null;
      
      if (vm.from_date) {
        if (typeof vm.from_date === 'object' && vm.from_date instanceof Date) {
          formattedFromDate = [
            vm.from_date.getFullYear(),
            String(vm.from_date.getMonth() + 1).padStart(2, '0'),
            String(vm.from_date.getDate()).padStart(2, '0')
          ].join('-');
        } else if (typeof vm.from_date === 'string') {
          if (vm.from_date.includes('/')) {
            const parts = vm.from_date.split('/');
            if (parts.length === 3) {
              formattedFromDate = `${parts[2]}-${parts[1]}-${parts[0]}`;
            }
          } else if (vm.from_date.includes('-')) {
            formattedFromDate = vm.from_date;
          } else {
            formattedFromDate = null;
          }
        }
      }
      
      if (vm.to_date) {
        if (typeof vm.to_date === 'object' && vm.to_date instanceof Date) {
          formattedToDate = [
            vm.to_date.getFullYear(),
            String(vm.to_date.getMonth() + 1).padStart(2, '0'),
            String(vm.to_date.getDate()).padStart(2, '0')
          ].join('-');
        } else if (typeof vm.to_date === 'string') {
          if (vm.to_date.includes('/')) {
            const parts = vm.to_date.split('/');
            if (parts.length === 3) {
              formattedToDate = `${parts[2]}-${parts[1]}-${parts[0]}`;
            }
          } else if (vm.to_date.includes('-')) {
            formattedToDate = vm.to_date;
          } else {
            formattedToDate = null;
          }
        }
      }
      
      let minAmount = vm.min_amount ? parseFloat(vm.min_amount) : null;
      let maxAmount = vm.max_amount ? parseFloat(vm.max_amount) : null;
      
      this.current_search_params = {
        invoice_name: vm.invoice_name,
        customer_name: vm.customer_name,
        customer_id: vm.customer_id,
        mobile_no: vm.mobile_no,
        tax_id: vm.tax_id,
        from_date: formattedFromDate,
        to_date: formattedToDate,
        min_amount: minAmount,
        max_amount: maxAmount,
        company: vm.company,
        page: vm.page
      };
      
      frappe.call({
        method: 'highspeed_pos.highspeed_pos.api.hsposapp.search_invoices_for_return',
        args: this.current_search_params,
        callback: function (r) {
          vm.loading_more = false;
          vm.searched_once = true;
          
          if (r.message) {
            if (vm.page === 1) {
              vm.dialog_data = r.message.invoices;
            } else {
              vm.dialog_data = [...vm.dialog_data, ...r.message.invoices];
            }
            
            vm.has_more_invoices = r.message.has_more;
          } else {
            vm.dialog_data = [];
            vm.has_more_invoices = false;
          }
        },
        error: function(err) {
          vm.loading_more = false;
          console.error("Error searching invoices:", err);
          vm.eventBus.emit('show_message', {
            title: __('Error searching invoices'),
            color: 'error',
          });
        }
      });
    },
    
    load_more_invoices() {
      this.page += 1;
      this.perform_search();
    },
    
    return_without_invoice() {
      const invoice_doc = {};
      invoice_doc.items = [];
      invoice_doc.is_return = 1;
      const data = { invoice_doc };
      this.eventBus.emit('load_return_invoice', data);
      this.invoicesDialog = false;
    },
    
    submit_dialog() {
      if (this.selected.length > 0) {
        const return_doc = this.selected[0];
        const invoice_doc = {};
        const items = [];
        
        return_doc.items.forEach((item) => {
          const new_item = { ...item };
          new_item.qty = item.qty > 0 ? item.qty * -1 : item.qty;
          new_item.stock_qty = item.stock_qty > 0 ? item.stock_qty * -1 : item.stock_qty;
          new_item.amount = item.amount > 0 ? item.amount * -1 : item.amount;
          items.push(new_item);
        });
        
        invoice_doc.items = items;
        invoice_doc.is_return = 1;
        invoice_doc.return_against = return_doc.name;
        invoice_doc.customer = return_doc.customer;
        
        if (return_doc.grand_total > 0) {
          invoice_doc.grand_total = return_doc.grand_total * -1;
        } else {
          invoice_doc.grand_total = return_doc.grand_total;
        }
        
        invoice_doc.update_stock = 1;
        invoice_doc.pos_profile = this.pos_profile.name;
        invoice_doc.company = this.company;
        
        const data = { invoice_doc, return_doc };
        
        this.eventBus.emit('load_return_invoice', data);
        this.invoicesDialog = false;
      }
    },
  },
  
  created: function () {
    this.eventBus.on('open_returns', (data) => {
      this.invoicesDialog = true;
      this.company = data;
      this.invoice_name = '';
      this.customer_name = '';
      this.customer_id = '';
      this.mobile_no = '';
      this.tax_id = '';
      this.from_date = null;
      this.to_date = null;
      this.from_date_formatted = null;
      this.to_date_formatted = null;
      this.min_amount = '';
      this.max_amount = '';
      this.dialog_data = [];
      this.selected = [];
      this.page = 1;
      this.has_more_invoices = false;
      this.searched_once = false;
      this.searchPanel = 0;
    });

    this.eventBus.on('register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
    });
  },
  
  beforeUnmount() {
    this.eventBus.off('open_returns');
    this.eventBus.off('register_pos_profile');
  },
};
</script>

<style scoped>
.header-gradient {
  background: linear-gradient(135deg, #075294 0%, #0097A7 100%) !important;
  color: white !important;
}

.filter-panel-title {
  background-color: #f0f7ff !important;
  color: #0288d1 !important;
  font-weight: 600 !important;
}

.search-btn {
  background: linear-gradient(90deg, #075294 0%, #0097A7 100%) !important;
  color: white !important;
  font-weight: 600 !important;
  border-radius: 6px !important;
  box-shadow: 0 4px 12px rgba(0, 151, 167, 0.15) !important;
}

:deep(.v-field) {
  border-radius: 8px !important;
  transition: all 0.3s ease !important;
}

:deep(.v-field--focused) {
  box-shadow: 0 4px 12px rgba(0, 151, 167, 0.1) !important;
}

.invoice-table :deep(.v-data-table__td) {
  padding: 12px 16px;
}

.invoice-table :deep(.v-data-table-header__content) {
  font-weight: 600;
  color: #616161;
}

.gap-2 {
  gap: 8px;
}

/* تحسين مظهر expansion panel */
.v-expansion-panel-title {
  padding: 12px 16px;
  min-height: 48px;
}

.v-expansion-panel-text {
  padding: 16px;
}

/* تحسين التمرير */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f5f5f5;
}

::-webkit-scrollbar-thumb {
  background: #e0e0e0;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #d0d0d0;
}

/* إزالة text-transform من الأزرار */
.v-btn {
  text-transform: none;
  letter-spacing: normal;
}

/* تحسين مظهر الجدول */
.v-data-table {
  border: none !important;
}

.v-data-table :deep(.v-table__wrapper) {
  border-radius: 8px;
}
</style>