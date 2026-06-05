<template>
  <v-row justify="center">
    <v-dialog v-model="draftsDialog" max-width="900px" persistent>
      <v-card class="rounded-lg">
        <!-- Header -->
        <v-card-title class="pa-0">
          <div class="pa-4 bg-gradient-blue">
            <div class="d-flex align-center justify-space-between">
              <div class="d-flex align-center">
                <v-icon class="mr-3" color="white" size="24">mdi-file-document-multiple</v-icon>
                <span class="text-h6 text-white">{{ __("Sales Orders") }}</span>
              </div>
              <v-btn 
                icon 
                variant="text" 
                size="small"
                @click="close_dialog">
                <v-icon color="white">mdi-close</v-icon>
              </v-btn>
            </div>
          </div>
        </v-card-title>

        <v-divider></v-divider>

        <!-- Search Section -->
        <v-card-text class="pa-4 bg-grey-lighten-5">
          <v-row align="center" no-gutters>
            <v-col cols="12" sm="8">
              <v-text-field 
                variant="outlined"
                density="compact"
                color="primary" 
                :label="__('Search by Order ID')"
                :placeholder="__('Enter order number')"
                bg-color="white" 
                hide-details
                v-model="order_name" 
                clearable
                prepend-inner-icon="mdi-magnify"
                @keyup.enter="search_orders">
              </v-text-field>
            </v-col>
            <v-col cols="12" sm="4" class="pl-sm-2 pt-2 pt-sm-0">
              <v-btn 
                block
                variant="flat" 
                color="primary" 
                @click="search_orders"
                :loading="searching">
                <v-icon size="small" class="mr-1">mdi-magnify</v-icon>
                {{ __("Search") }}
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider></v-divider>

        <!-- Data Table Section -->
        <v-card-text class="pa-0" style="max-height: 450px; overflow-y: auto;">
          <!-- Empty State -->
          <div v-if="!dialog_data || dialog_data.length === 0" class="text-center py-12">
            <v-icon size="64" color="grey-lighten-2">mdi-file-search-outline</v-icon>
            <p class="text-h6 text-grey-darken-1 mt-4 mb-2">{{ __('No orders found') }}</p>
            <p class="text-body-2 text-grey">
              {{ order_name ? __('Try different search criteria') : __('Search for an order to get started') }}
            </p>
          </div>

          <!-- Results Table -->
          <v-data-table 
            v-else
            :headers="headers" 
            :items="dialog_data" 
            item-key="name" 
            show-select
            v-model="selected" 
            return-object 
            select-strategy="single"
            :items-per-page="10"
            :footer-props="{
              'items-per-page-options': [10, 25, 50],
              'items-per-page-text': __('Orders per page')
            }"
            class="orders-table">
            
            <template v-slot:item.customer_name="{ item }">
              <div class="py-2">
                <div class="text-body-2 font-weight-medium">{{ item.customer_name }}</div>
                <div class="text-caption text-grey" v-if="item.customer">{{ item.customer }}</div>
              </div>
            </template>
            
            <template v-slot:item.transaction_date="{ item }">
              <v-chip size="small" variant="tonal" color="blue-grey">
                <v-icon size="x-small" class="mr-1">mdi-calendar</v-icon>
                {{ formatDate(item.transaction_date) }}
              </v-chip>
            </template>
            
            <template v-slot:item.name="{ item }">
              <div class="d-flex align-center">
                <v-icon size="small" color="primary" class="mr-2">mdi-file-document-outline</v-icon>
                <span class="text-primary font-weight-medium">{{ item.name }}</span>
              </div>
            </template>
            
            <template v-slot:item.grand_total="{ item }">
              <div class="text-right">
                <div class="text-h6 font-weight-bold text-green-darken-2">
                  {{ currencySymbol(item.currency) }}{{ formatCurrency(item.grand_total) }}
                </div>
                <div class="text-caption text-grey" v-if="item.status">
                  <v-chip size="x-small" :color="getStatusColor(item.status)" variant="tonal">
                    {{ __(item.status) }}
                  </v-chip>
                </div>
              </div>
            </template>
            
            <template v-slot:bottom>
              <div class="pa-3 bg-grey-lighten-5 d-flex align-center justify-space-between">
                <div class="text-caption text-grey-darken-1">
                  {{ __('Total Orders') }}: <strong>{{ dialog_data.length }}</strong>
                </div>
                <div v-if="selected.length" class="text-caption text-primary">
                  <v-icon size="small" class="mr-1">mdi-check-circle</v-icon>
                  {{ __('1 order selected') }}
                </div>
              </div>
            </template>
          </v-data-table>
        </v-card-text>

        <v-divider></v-divider>

        <!-- Actions -->
        <v-card-actions class="pa-4 bg-grey-lighten-5">
          <div v-if="selected.length" class="text-caption text-grey mr-3">
            <v-icon size="small" color="info" class="mr-1">mdi-information-outline</v-icon>
            {{ __('This will load the selected order into the invoice') }}
          </div>
          <v-spacer></v-spacer>
          <v-btn 
            variant="text" 
            @click="close_dialog">
            {{ __("Cancel") }}
          </v-btn>
          <v-btn 
            v-if="selected.length" 
            color="primary" 
            variant="flat"
            @click="submit_dialog"
            :loading="processing">
            <v-icon size="small" class="mr-1">mdi-check</v-icon>
            {{ __("Load Order") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import format from "../../format";

export default {
  mixins: [format],
  data: () => ({
    draftsDialog: false,
    singleSelect: true,
    pos_profile: {},
    selected: [],
    dialog_data: [],
    order_name: "",
    searching: false,
    processing: false,
    headers: [
      {
        title: __("Customer"),
        key: "customer_name",
        align: "start",
        sortable: true,
      },
      {
        title: __("Date"),
        align: "center",
        sortable: true,
        key: "transaction_date",
      },
      {
        title: __("Order"),
        key: "name",
        align: "start",
        sortable: true,
      },
      {
        title: __("Amount"),
        key: "grand_total",
        align: "end",
        sortable: true,
      },
    ],
  }),
  
  methods: {
    close_dialog() {
      this.draftsDialog = false;
      this.clearSelected();
    },

    clearSelected() {
      this.selected = [];
    },
    
    formatDate(dateStr) {
      if (!dateStr) return '';
      try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-GB', { 
          day: '2-digit', 
          month: 'short', 
          year: 'numeric' 
        });
      } catch (error) {
        return dateStr;
      }
    },
    
    getStatusColor(status) {
      const statusColors = {
        'Draft': 'grey',
        'To Deliver and Bill': 'orange',
        'To Bill': 'blue',
        'To Deliver': 'purple',
        'Completed': 'green',
        'Cancelled': 'red',
        'Closed': 'grey-darken-2'
      };
      return statusColors[status] || 'grey';
    },

    search_orders() {
      const vm = this;
      vm.searching = true;
      
      frappe.call({
        method: "highspeed_pos.highspeed_pos.api.hsposapp.search_orders",
        args: {
          order_name: vm.order_name,
          company: this.pos_profile.company,
          currency: this.pos_profile.currency,
        },
        async: false,
        callback: function (r) {
          vm.searching = false;
          if (r.message) {
            vm.dialog_data = r.message;
            if (r.message.length === 0 && vm.order_name) {
              vm.eventBus.emit('show_message', {
                title: __('No orders found with this ID'),
                color: 'info',
              });
            }
          } else {
            vm.dialog_data = [];
          }
        },
        error: function(err) {
          vm.searching = false;
          console.error("Error searching orders:", err);
          vm.eventBus.emit('show_message', {
            title: __('Error searching orders'),
            color: 'error',
          });
        }
      });
    },

    async submit_dialog() {
      if (this.selected.length > 0) {
        this.processing = true;
        var invoice_doc_for_load = {};
        
        try {
          await frappe.call({
            method: "highspeed_pos.highspeed_pos.api.hsposapp.create_sales_invoice_from_order",
            args: {
              sales_order: this.selected[0].name,
            },
            callback: function (r) {
              if (r.message) {
                invoice_doc_for_load = r.message;
              }
            },
          });
          
          if (invoice_doc_for_load.items) {
            const selectedItems = this.selected[0].items;
            const loadedItems = invoice_doc_for_load.items;

            const loadedItemsMap = {};
            loadedItems.forEach((item) => {
              loadedItemsMap[item.item_code] = item;
            });

            // Update or discard items
            for (let i = 0; i < selectedItems.length; i++) {
              const selectedItem = selectedItems[i];
              const loadedItem = loadedItemsMap[selectedItem.item_code];

              if (loadedItem) {
                selectedItem.qty = loadedItem.qty;
                selectedItem.amount = loadedItem.amount;
                selectedItem.uom = loadedItem.uom;
                selectedItem.rate = loadedItem.rate;
              } else {
                selectedItems.splice(i, 1);
                i--;
              }
            }
          }
          
          this.eventBus.emit("load_order", this.selected[0]);
          this.draftsDialog = false;
          
          // Delete the temporary invoice
          frappe.call({
            method: "highspeed_pos.highspeed_pos.api.hsposapp.delete_sales_invoice",
            args: {
              sales_invoice: invoice_doc_for_load.name,
            },
            callback: function (r) {
              // Handled
            },
          });
          
          this.eventBus.emit('show_message', {
            title: __('Order loaded successfully'),
            color: 'success',
          });
          
        } catch (error) {
          console.error("Error loading order:", error);
          this.eventBus.emit('show_message', {
            title: __('Error loading order'),
            color: 'error',
          });
        } finally {
          this.processing = false;
        }
      }
    },
  },
  
  created: function () {
    this.eventBus.on("open_orders", (data) => {
      this.clearSelected();
      this.draftsDialog = true;
      this.dialog_data = data || [];
      this.order_name = "";
    });
  },
  
  mounted() {
    this.eventBus.on("register_pos_profile", (data) => {
      this.pos_profile = data.pos_profile;
    });
  },
  
  beforeUnmount() {
    this.eventBus.off("open_orders");
    this.eventBus.off("register_pos_profile");
  },
};
</script>

<style scoped>
.orders-table :deep(.v-data-table__td) {
  padding: 8px 16px;
}

.orders-table :deep(.v-data-table-header__content) {
  font-weight: 600;
  color: #616161;
}

.bg-gradient-blue {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
}

/* تحسين مظهر الجدول */
.v-data-table {
  border: none !important;
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

/* دعم RTL */
[dir="rtl"] .mr-3 {
  margin-right: 0 !important;
  margin-left: 0.75rem !important;
}

[dir="rtl"] .mr-2 {
  margin-right: 0 !important;
  margin-left: 0.5rem !important;
}

[dir="rtl"] .mr-1 {
  margin-right: 0 !important;
  margin-left: 0.25rem !important;
}

[dir="rtl"] .pl-sm-2 {
  padding-left: 0 !important;
  padding-right: 0.5rem !important;
}

/* إزالة text-transform من الأزرار */
.v-btn {
  text-transform: none;
  letter-spacing: normal;
}

/* تحسين مظهر عند التحميل */
.v-btn--loading {
  pointer-events: none;
  opacity: 0.8;
}
</style>