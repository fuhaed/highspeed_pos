<template>
  <!-- ? Disable dropdown if either readonly or loadingCustomers is true -->
  <div class="customer-input-wrapper">
    <v-autocomplete ref="customerDropdown" class="customer-autocomplete sleek-field" density="compact" clearable
      variant="solo" color="primary" v-model="internalCustomer" :items="customers"
      item-title="customer_name" item-value="name" bg-color="white" :no-data-text="__('Customers not found')"
      hide-details :customFilter="customFilter" :disabled="readonly || loadingCustomers"
      :menu-props="{ closeOnContentClick: false }" @update:menu="onCustomerMenuToggle"
      @update:modelValue="onCustomerChange" @keydown.enter="handleEnter">
      <!-- Edit icon (left) -->
      <template #prepend-inner>
        <v-tooltip text="Edit customer">
          <template #activator="{ on, attrs }">
            <v-icon v-bind="attrs" v-on="on" class="icon-button" @mousedown.prevent.stop @click.stop="edit_customer">
              mdi-account-edit
            </v-icon>
          </template>
        </v-tooltip>
      </template>

      <!-- Add icon (right) -->
      <template #append-inner>
        <v-tooltip text="Add new customer">
          <template #activator="{ on, attrs }">
            <v-icon v-bind="attrs" v-on="on" class="icon-button" @mousedown.prevent.stop @click.stop="new_customer">
              mdi-plus
            </v-icon>
          </template>
        </v-tooltip>
      </template>

      <!-- Dropdown display -->
      <template #item="{ props, item }">
        <v-list-item v-bind="props">
          <v-list-item-subtitle v-if="item.raw.customer_name !== item.raw.name">
            <div v-html="`ID: ${item.raw.name}`"></div>
          </v-list-item-subtitle>
          <v-list-item-subtitle v-if="item.raw.tax_id">
            <div v-html="`TAX ID: ${item.raw.tax_id}`"></div>
          </v-list-item-subtitle>
          <v-list-item-subtitle v-if="item.raw.email_id">
            <div v-html="`Email: ${item.raw.email_id}`"></div>
          </v-list-item-subtitle>
          <v-list-item-subtitle v-if="item.raw.mobile_no">
            <div v-html="`Mobile No: ${item.raw.mobile_no}`"></div>
          </v-list-item-subtitle>
          <v-list-item-subtitle v-if="item.raw.primary_address">
            <div v-html="`Primary Address: ${item.raw.primary_address}`"></div>
          </v-list-item-subtitle>
        </v-list-item>
      </template>
    </v-autocomplete>

    <!-- Update customer modal -->
    <div class="mt-4">
      <UpdateCustomer />
    </div>
  </div>
</template>

<style scoped>
.customer-input-wrapper {
  width: 100%;
  max-width: 100%;
  padding-right: 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.customer-autocomplete {
  width: 100%;
  box-sizing: border-box;
  font-size: 0.85rem;
}

/* Field Styling */
.customer-autocomplete :deep(.v-field) {
  min-height: 36px !important;
  background: white !important;
  border-radius: 6px !important;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
  box-shadow: none !important;
}

.customer-autocomplete:hover :deep(.v-field) {
  border-color: #cbd5e1;
}

.customer-autocomplete :deep(.v-field--focused) {
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

.customer-autocomplete :deep(.v-field__input) {
  padding: 0 12px !important;
  font-size: 0.85rem !important;
  min-height: 36px !important;
  color: #1e293b;
}

.customer-autocomplete :deep(.v-field__prepend-inner),
.customer-autocomplete :deep(.v-field__append-inner) {
  padding-top: 0 !important;
}

.customer-autocomplete :deep(.v-label) {
  display: none !important;
}

.customer-autocomplete :deep(.v-field--focused .v-label) {
  color: #3b82f6;
}

/* Icon Button Styling */
.icon-button {
  cursor: pointer;
  font-size: 18px !important;
  opacity: 0.6;
  transition: all 0.2s ease;
  color: #64748b;
}

.icon-button:hover {
  opacity: 1;
  color: #3b82f6 !important;
  transform: scale(1.1);
}

/* Dropdown Item Styling */
.customer-autocomplete :deep(.v-list-item) {
  min-height: auto !important;
  padding: 10px 14px !important;
  border-bottom: 1px solid #f1f5f9;
  transition: all 0.2s ease;
}

.customer-autocomplete :deep(.v-list-item:hover) {
  background: #f8fafc !important;
}

.customer-autocomplete :deep(.v-list-item:last-child) {
  border-bottom: none;
}

.customer-autocomplete :deep(.v-list-item-title) {
  font-size: 0.9rem !important;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.customer-autocomplete :deep(.v-list-item-subtitle) {
  font-size: 0.75rem !important;
  color: #64748b;
  line-height: 1.4;
  margin-top: 2px;
}

.customer-autocomplete :deep(.v-list-item-subtitle div) {
  padding: 2px 0;
}

/* Menu Styling */
.customer-autocomplete :deep(.v-menu__content) {
  border-radius: 8px !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
  border: 1px solid #e2e8f0;
  margin-top: 4px;
  max-height: 400px !important;
}

.customer-autocomplete :deep(.v-list) {
  padding: 4px !important;
  background: white;
}

/* Clear Button */
.customer-autocomplete :deep(.v-field__clearable .v-icon) {
  font-size: 18px !important;
  opacity: 0.5;
  color: #64748b;
}

.customer-autocomplete :deep(.v-field__clearable .v-icon:hover) {
  opacity: 1;
  color: #ef4444;
}

/* Loading State */
.customer-autocomplete :deep(.v-field--disabled) {
  opacity: 0.6;
}

.customer-autocomplete :deep(.v-progress-linear) {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
}

/* RTL Support */
[dir="rtl"] .customer-input-wrapper {
  padding-right: 0;
  padding-left: 0;
}

[dir="rtl"] .customer-autocomplete :deep(.v-field__prepend-inner) {
  order: 2;
}

[dir="rtl"] .customer-autocomplete :deep(.v-field__append-inner) {
  order: -1;
}

[dir="rtl"] .customer-autocomplete :deep(.v-field__input) {
  text-align: right;
}

[dir="rtl"] .customer-autocomplete :deep(.v-list-item-subtitle div) {
  text-align: right;
}

/* Responsive Design */
@media (max-width: 768px) {
  .customer-autocomplete :deep(.v-list-item) {
    padding: 8px 10px !important;
  }
  
  .customer-autocomplete :deep(.v-list-item-title) {
    font-size: 0.85rem !important;
  }
  
  .customer-autocomplete :deep(.v-list-item-subtitle) {
    font-size: 0.7rem !important;
  }
  
  .icon-button {
    font-size: 16px !important;
  }
  
  .customer-autocomplete :deep(.v-field__input) {
    font-size: 0.8rem !important;
  }
}

/* Focus States for Accessibility */
.icon-button:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
  border-radius: 4px;
}

.customer-autocomplete:focus-visible :deep(.v-field) {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.customer-autocomplete :deep(.v-list-item) {
  animation: fadeIn 0.2s ease;
}

/* Tooltip Styling */
:deep(.v-tooltip .v-overlay__content) {
  background: #1e293b !important;
  color: white !important;
  font-size: 0.75rem !important;
  padding: 4px 8px !important;
  border-radius: 4px !important;
}
</style>

<script>
import UpdateCustomer from './UpdateCustomer.vue';

export default {
  props: {
    pos_profile: Object
  },

  data: () => ({
    pos_profile: '',
    customers: [],
    customer: '',                // Selected customer
    internalCustomer: null,      // Model bound to the dropdown
    tempSelectedCustomer: null,  // Temporarily holds customer selected from dropdown
    isMenuOpen: false,           // Tracks whether dropdown menu is open
    readonly: false,
    customer_info: {},           // Used for edit modal
    loadingCustomers: false      // ? New state to track loading status
  }),

  components: {
    UpdateCustomer,
  },

  methods: {
    // Called when dropdown opens or closes
    onCustomerMenuToggle(isOpen) {
      this.isMenuOpen = isOpen;

      if (isOpen) {
        this.internalCustomer = null;

        this.$nextTick(() => {
          setTimeout(() => {
            const dropdown = this.$refs.customerDropdown?.$el?.querySelector('.v-overlay__content .v-select-list');
            if (dropdown) dropdown.scrollTop = 0;
          }, 50);
        });

      } else {
        // Restore selection if user didn't pick anything
        if (this.tempSelectedCustomer) {
          this.internalCustomer = this.tempSelectedCustomer;
          this.customer = this.tempSelectedCustomer;
          this.eventBus.emit('update_customer', this.customer);
        } else if (this.customer) {
          this.internalCustomer = this.customer;
        }

        this.tempSelectedCustomer = null;
      }
    },

    // Called when a customer is selected
    onCustomerChange(val) {
      this.tempSelectedCustomer = val;

      if (!this.isMenuOpen && val) {
        this.customer = val;
        this.eventBus.emit('update_customer', val);
      }
    },

    // Pressing Enter in input
    handleEnter(event) {
      const inputText = event.target.value?.toLowerCase() || '';

      const matched = this.customers.find(cust => {
        return (
          cust.customer_name?.toLowerCase().includes(inputText) ||
          cust.name?.toLowerCase().includes(inputText)
        );
      });

      if (matched) {
        this.tempSelectedCustomer = matched.name;
        this.internalCustomer = matched.name;
        this.customer = matched.name;
        this.eventBus.emit('update_customer', matched.name);
        this.isMenuOpen = false;

        event.target.blur();
      }
    },

    // Fetch customers list
    get_customer_names() {
      var vm = this;
      if (this.customers.length > 0) return;

      if (vm.pos_profile.hspos_local_storage && localStorage.customer_storage) {
        vm.customers = JSON.parse(localStorage.getItem('customer_storage'));
      }

      this.loadingCustomers = true; // ? Start loading
      frappe.call({
        method: 'highspeed_pos.highspeed_pos.api.hsposapp.get_customer_names',
        args: {
          pos_profile: this.pos_profile.pos_profile,
        },
        callback: function (r) {
          if (r.message) {
            vm.customers = r.message;

            if (vm.pos_profile.hspos_local_storage) {
              localStorage.setItem('customer_storage', '');
              localStorage.setItem('customer_storage', JSON.stringify(r.message));
            }
          }
          vm.loadingCustomers = false; // ? Stop loading
        },
      });
    },

    new_customer() {
      this.eventBus.emit('open_update_customer', null);
    },

    edit_customer() {
      this.eventBus.emit('open_update_customer', this.customer_info);
    },

    customFilter(itemText, queryText, itemRow) {
      const item = itemRow.raw;
      const searchText = queryText.toLowerCase();

      return (
        (item.customer_name?.toLowerCase().includes(searchText)) ||
        (item.tax_id?.toLowerCase().includes(searchText)) ||
        (item.email_id?.toLowerCase().includes(searchText)) ||
        (item.mobile_no?.toLowerCase().includes(searchText)) ||
        (item.name?.toLowerCase().includes(searchText))
      );
    },
  },

  created() {
    this.$nextTick(() => {
      this.eventBus.on('register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        this.get_customer_names();
      });

      this.eventBus.on('payments_register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        this.get_customer_names();
      });

      this.eventBus.on('set_customer', (customer) => {
        this.customer = customer;
        this.internalCustomer = customer;
      });

      this.eventBus.on('add_customer_to_list', (customer) => {
        this.customers.push(customer);
        this.customer = customer.name;
        this.internalCustomer = customer.name;
        this.eventBus.emit('update_customer', customer.name);
      });

      this.eventBus.on('set_customer_readonly', (value) => {
        this.readonly = value;
      });

      this.eventBus.on('set_customer_info_to_edit', (data) => {
        this.customer_info = data;
      });

      this.eventBus.on('fetch_customer_details', () => {
        this.get_customer_names();
      });
    });
  },
};
</script>