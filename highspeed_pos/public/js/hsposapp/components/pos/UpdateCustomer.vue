<template>
  <v-row justify="center">
    <v-dialog v-model="customerDialog" max-width="500px" persistent>
      <v-card class="customer-card">
        <v-card-title class="customer-header">
          <v-icon size="20">{{ customer_id ? 'mdi-account-edit' : 'mdi-account-plus' }}</v-icon>
          <span>{{ customer_id ? __('Update Customer') : __('Create Customer') }}</span>
        </v-card-title>
        <v-card-text class="pa-3">
          <v-container class="pa-0">
            <v-row dense>
              <v-col cols="12">
                <v-text-field 
                  density="compact" 
                  :label="__('Customer Name') + ' *'"
                  variant="outlined"
                  hide-details
                  v-model="customer_name"
                  class="mb-3"
                ></v-text-field>
              </v-col>
              
              <v-col cols="6">
                <v-text-field 
                  density="compact" 
                  :label="__('Mobile No')" 
                  variant="outlined"
                  hide-details
                  v-model="mobile_no"
                  class="mb-3"
                ></v-text-field>
              </v-col>
              
              <v-col cols="6">
                <v-text-field 
                  density="compact" 
                  :label="__('Tax ID')" 
                  variant="outlined"
                  hide-details
                  v-model="tax_id"
                  class="mb-3"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  density="compact"
                  :label="__('Address')"
                  variant="outlined"
                  hide-details
                  v-model="address_line1"
                  class="mb-3"
                ></v-text-field>
              </v-col>
              
              <v-col cols="6">
                <v-text-field
                  v-model="city"
                  variant="outlined"
                  density="compact"
                  :label="__('City')"
                  hide-details
                  class="mb-3"
                ></v-text-field>
              </v-col>
              
              <v-col cols="6">
                <v-select
                  v-model="country"
                  :items="countries"
                  variant="outlined"
                  density="compact"
                  :label="__('Country')"
                  hide-details
                  class="mb-3"
                ></v-select>
              </v-col>
              
              <v-col cols="6">
                <v-text-field 
                  density="compact" 
                  :label="__('Email')" 
                  variant="outlined"
                  hide-details
                  v-model="email_id"
                  class="mb-3"
                  type="email"
                ></v-text-field>
              </v-col>
              
              <v-col cols="6">
                <v-select 
                  density="compact" 
                  :label="__('Gender')" 
                  :items="genders" 
                  v-model="gender"
                  variant="outlined"
                  hide-details
                  class="mb-3"
                ></v-select>
              </v-col>
              
              <v-col cols="6">
                <v-autocomplete 
                  density="compact" 
                  :label="__('Customer Group') + ' *'" 
                  v-model="group" 
                  :items="groups" 
                  variant="outlined"
                  hide-details
                  class="mb-3"
                ></v-autocomplete>
              </v-col>
              
              <v-col cols="6">
                <v-autocomplete 
                  density="compact" 
                  :label="__('Territory') + ' *'" 
                  v-model="territory" 
                  :items="territorys" 
                  variant="outlined"
                  hide-details
                  class="mb-3"
                ></v-autocomplete>
              </v-col>
              
              <v-col cols="6" v-if="loyalty_program">
                <v-text-field 
                  v-model="loyalty_program" 
                  :label="__('Loyalty Program')" 
                  density="compact" 
                  readonly
                  hide-details
                  variant="outlined"
                  class="mb-3"
                ></v-text-field>
              </v-col>
              
              <v-col cols="6" v-if="loyalty_points">
                <v-text-field 
                  v-model="loyalty_points" 
                  :label="__('Points')" 
                  density="compact" 
                  readonly
                  hide-details
                  variant="outlined"
                  class="mb-3"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions class="pa-3 pt-0">
          <v-btn 
            color="grey" 
            variant="tonal"
            @click="confirm_close"
            class="flex-grow-1"
            height="44"
          >
            {{ __('Cancel') }}
          </v-btn>
          <v-btn 
            color="primary" 
            variant="flat"
            @click="submit_dialog"
            class="flex-grow-1 ml-3"
            height="44"
            :disabled="!customer_name || !group || !territory"
          >
            {{ customer_id ? __('Update') : __('Create') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmDialog" max-width="350px">
      <v-card>
        <v-card-text class="pa-4 text-center">
          <v-icon size="48" color="warning" class="mb-3">mdi-alert-circle</v-icon>
          <div class="text-h6 mb-2">{{ __('Confirm Close') }}</div>
          <div class="text-body-2">{{ __('All entered data will be lost.') }}</div>
        </v-card-text>
        <v-card-actions class="pa-3 pt-0">
          <v-btn 
            color="grey" 
            variant="tonal"
            @click="confirmDialog = false"
            class="flex-grow-1"
            height="40"
          >
            {{ __('Back') }}
          </v-btn>
          <v-btn 
            color="error" 
            variant="flat"
            @click="confirmClose"
            class="flex-grow-1 ml-3"
            height="40"
          >
            {{ __('Close') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<style scoped>
.customer-card {
  border-radius: 8px !important;
}

.customer-header {
  background: #f5f5f5;
  padding: 12px 16px;
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.mb-3 {
  margin-bottom: 12px !important;
}

.v-text-field :deep(.v-field__input) {
  font-size: 0.9rem;
  padding-top: 10px !important;
  padding-bottom: 10px !important;
}

.v-select :deep(.v-field__input) {
  font-size: 0.9rem;
  padding-top: 10px !important;
  padding-bottom: 10px !important;
}

.v-btn {
  text-transform: none;
  font-weight: 500;
  font-size: 0.9rem;
}

@media (max-width: 500px) {
  .v-dialog {
    margin: 16px !important;
  }
}

.v-text-field :deep(.v-field) {
  min-height: 40px !important;
}

.v-select :deep(.v-field) {
  min-height: 40px !important;
}

.v-autocomplete :deep(.v-field) {
  min-height: 40px !important;
}
</style>

<script>

export default {
  data: () => ({
    customerDialog: false,
    confirmDialog: false,
    pos_profile: '',
    customer_id: '',
    customer_name: '',
    tax_id: '',
    mobile_no: '',
    address_line1: '',
    city: '',
    country: 'Saudi Arabia',
    email_id: '',
    hspos_referral_code: '',
    birthday: '',
    birthday_menu: false,
    group: '',
    groups: [],
    territory: '',
    territorys: [],
    genders: [],
    customer_type: 'Individual',
    gender: '',
    loyalty_points: null,
    loyalty_program: null,
    countries: [
      'Saudi Arabia',
      'United Arab Emirates',
      'Kuwait',
      'Bahrain',
      'Qatar',
      'Oman',
      'Egypt',
      'Jordan',
      'Lebanon',
      'Pakistan',
      'India',
      'United States',
      'United Kingdom',
      'Canada',
      'Australia',
      'Germany',
      'France',
      'Italy',
      'Spain',
      'Netherlands',
      'Belgium',
      'Switzerland',
      'Austria',
      'Sweden',
      'Norway',
      'Denmark',
      'Finland',
      'Turkey',
      'Malaysia',
      'Indonesia',
      'Singapore',
      'Thailand',
      'Philippines',
      'Japan',
      'South Korea',
      'China',
      'Bangladesh',
      'Sri Lanka',
      'Afghanistan',
      'Yemen'
    ],
  }),
  watch: {
    birthday(newVal) {
      if (newVal && /^\d{8}$/.test(newVal)) {
        try {
          const day = newVal.substring(0, 2);
          const month = newVal.substring(2, 4);
          const year = newVal.substring(4);
          
          this.birthday = `${day}-${month}-${year}`;
          
          this.updateCalendarDate(day, month, year);
        } catch (error) {
          console.error("Error processing 8-digit date:", error);
        }
      }
      else if (newVal && /^\d{2}-\d{2}-\d{4}$/.test(newVal)) {
        try {
          const parts = newVal.split('-');
          const day = parts[0];
          const month = parts[1];
          const year = parts[2];
          
          this.updateCalendarDate(day, month, year);
        } catch (error) {
          console.error("Error processing formatted date:", error);
        }
      }
    },
    
    birthday_menu(isOpen) {
      if (isOpen && this.birthday && /^\d{2}-\d{2}-\d{4}$/.test(this.birthday)) {
        try {
          const parts = this.birthday.split('-');
          const day = parts[0];
          const month = parts[1];
          const year = parts[2];
          
          this.$nextTick(() => {
            this.updateCalendarDate(day, month, year);
          });
        } catch (error) {
          console.error("Error updating calendar on menu open:", error);
        }
      }
    }
  },
  methods: {
    updateCalendarDate(day, month, year) {
      const wasOpen = this.birthday_menu;
      this.birthday_menu = false;
      
      this.$nextTick(() => {
        const tempDate = `${year}-${month}-${day}`;
        
        setTimeout(() => {
          if (this.$refs.birthday_menu) {
            this.$refs.birthday_menu.date = tempDate;
            if (wasOpen) {
              this.birthday_menu = true;
            }
          }
        }, 50);
      });
    },
    confirm_close() {
      if (this.customer_name || this.tax_id || this.mobile_no || this.address_line1 || 
          this.email_id || this.hspos_referral_code || this.birthday) {
        this.confirmDialog = true;
      } else {
        this.close_dialog();
      }
    },
    confirmClose() {
      this.confirmDialog = false;
      this.close_dialog();
    },
    close_dialog() {
      this.customerDialog = false;
      this.clear_customer();
    },
    clear_customer() {
      this.customer_name = '';
      this.tax_id = '';
      this.mobile_no = '';
      this.address_line1 = '';
      this.city = '';
      this.country = 'Saudi Arabia';
      this.email_id = '';
      this.hspos_referral_code = '';
      this.birthday = '';
      this.group = frappe.defaults.get_user_default('Customer Group');
      this.territory = frappe.defaults.get_user_default('Territory');
      this.customer_id = '';
      this.customer_type = 'Individual';
      this.gender = '';
      this.loyalty_points = null;
      this.loyalty_program = null;
    },
    getCustomerGroups() {
      if (this.groups.length > 0) return;
      const vm = this;
      frappe.db
        .get_list('Customer Group', {
          fields: ['name'],
          filters: { is_group: 0 },
          limit: 1000,
          order_by: 'name',
        })
        .then((data) => {
          if (data.length > 0) {
            data.forEach((el) => {
              vm.groups.push(el.name);
            });
          }
        });
    },
    getCustomerTerritorys() {
      if (this.territorys.length > 0) return;
      const vm = this;
      frappe.db
        .get_list('Territory', {
          fields: ['name'],
          filters: { is_group: 0 },
          limit: 5000,
          order_by: 'name',
        })
        .then((data) => {
          if (data.length > 0) {
            data.forEach((el) => {
              vm.territorys.push(el.name);
            });
          }
        });
    },
    getGenders() {
      const vm = this;
      frappe.db
        .get_list('Gender', {
          fields: ['name'],
          page_length: 10,
        })
        .then((data) => {
          if (data.length > 0) {
            data.forEach((el) => {
              vm.genders.push(el.name);
            });
          }
        });
    },
    formatBirthdayOnInput() {
      if (this.birthday && /^\d{8}$/.test(this.birthday)) {
        try {
          const day = this.birthday.substring(0, 2);
          const month = this.birthday.substring(2, 4);
          const year = this.birthday.substring(4);
          this.birthday = `${day}-${month}-${year}`;
        } catch (error) {
          console.error("Error formatting date:", error);
        }
      }
    },
    submit_dialog() {
      const vm = this;
      if (!this.customer_name) {
        frappe.throw(__('Customer Name is required'));
        return;
      }
      
      if (!this.group) {
        frappe.throw(__('Customer group is required'));
        return;
      }
      
      if (!this.territory) {
        frappe.throw(__('Customer territory is required'));
        return;
      }
      
      let formatted_birthday = null;
      if (this.birthday) {
        try {
          if (/^\d{8}$/.test(this.birthday)) {
            const day = this.birthday.substring(0, 2);
            const month = this.birthday.substring(2, 4);
            const year = this.birthday.substring(4);
            formatted_birthday = `${year}-${month}-${day}`;
          }
          else if (/^\d{1,2}-\d{1,2}-\d{4}$/.test(this.birthday)) {
            const parts = this.birthday.split('-');
            if (parts.length === 3) {
              const day = parts[0].padStart(2, '0');
              const month = parts[1].padStart(2, '0');
              const year = parts[2];
              formatted_birthday = `${year}-${month}-${day}`;
            }
          }
          else if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(this.birthday)) {
            const parts = this.birthday.split('/');
            if (parts.length === 3) {
              const day = parts[0].padStart(2, '0');
              const month = parts[1].padStart(2, '0');
              const year = parts[2];
              formatted_birthday = `${year}-${month}-${day}`;
            }
          }
          else if (this.birthday) {
            try {
              const date = new Date(this.birthday);
              if (!isNaN(date.getTime())) {
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                formatted_birthday = `${year}-${month}-${day}`;
              }
            } catch (e) {
              console.error("Failed to parse date:", e);
            }
          }
        } catch (error) {
          console.error("Error formatting date:", error);
          formatted_birthday = null;
        }
      }
      
      const args = {
        customer_id: this.customer_id,
        customer_name: this.customer_name,
        tax_id: this.tax_id,
        mobile_no: this.mobile_no,
        address_line1: this.address_line1,
        city: this.city,
        country: this.country,
        email_id: this.email_id,
        hspos_referral_code: this.hspos_referral_code,
        birthday: formatted_birthday || this.birthday,
        customer_group: this.group,
        territory: this.territory,
        customer_type: this.customer_type,
        gender: this.gender
      };
      
      frappe.call({
        method: 'highspeed_pos.highspeed_pos.api.hsposapp.create_customer',
        args: {
          customer_id: this.customer_id,
          customer_name: this.customer_name,
          tax_id: this.tax_id,
          mobile_no: this.mobile_no,
          address_line1: this.address_line1,
          city: this.city,
          country: this.country,
          email_id: this.email_id,
          hspos_referral_code: this.hspos_referral_code,
          birthday: formatted_birthday || this.birthday,
          customer_group: this.group,
          territory: this.territory,
          customer_type: this.customer_type,
          gender: this.gender,
          company: vm.pos_profile.company,
          pos_profile_doc: JSON.stringify(vm.pos_profile),
          method: this.customer_id ? 'update' : 'create',
        },
        callback: (r) => {
          if (!r.exc && r.message.name) {
            let text = __('Customer created successfully.');
            if (vm.customer_id) {
              text = __('Customer updated successfully.');
            }
            vm.eventBus.emit('show_message', {
              title: text,
              color: 'success',
            });
            args.name = r.message.name;
            frappe.utils.play_sound('submit');
            vm.eventBus.emit('add_customer_to_list', args);
            vm.eventBus.emit('set_customer', r.message.name);
            vm.eventBus.emit('fetch_customer_details');
            vm.close_dialog();
          } else {
            frappe.utils.play_sound('error');
            vm.eventBus.emit('show_message', {
              title: __('Customer creation failed.'),
              color: 'error',
            });
          }
        },
      });
    },
    onDateSelect() {
      this.birthday_menu = false;
      
      if (this.birthday) {
        try {
          let dateObj;
          if (typeof this.birthday === 'object') {
            dateObj = this.birthday;
          } else if (typeof this.birthday === 'string' && (this.birthday.includes('GMT') || this.birthday.includes('T'))) {
            dateObj = new Date(this.birthday);
          } else {
            return;
          }
          
          const year = dateObj.getFullYear();
          const month = String(dateObj.getMonth() + 1).padStart(2, '0');
          const day = String(dateObj.getDate()).padStart(2, '0');
          
          this.birthday = `${day}-${month}-${year}`;
        } catch (error) {
          console.error("Error formatting date from picker:", error);
        }
      }
    },
  },
  created: function () {
    this.eventBus.on('open_update_customer', (data) => {
      this.customerDialog = true;
      
      if (data) {
        this.customer_name = data.customer_name;
        this.customer_id = data.name;
		this.address_line1 = data.address_line1 || "";
		this.city = data.city || "";
		this.country = data.country || "Saudi Arabia";
        this.tax_id = data.tax_id;
        this.mobile_no = data.mobile_no;
        this.email_id = data.email_id;
        this.hspos_referral_code = data.hspos_referral_code;
        this.birthday = data.birthday;
        this.group = data.customer_group;
        this.territory = data.territory;
        this.loyalty_points = data.loyalty_points;
        this.loyalty_program = data.loyalty_program;
        this.gender = data.gender;
      }
    });
    this.eventBus.on('register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
    });
    this.eventBus.on('payments_register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
    });
    this.getCustomerGroups();
    this.getCustomerTerritorys();
    this.getGenders();
    this.group = frappe.defaults.get_user_default('Customer Group');
    this.territory = frappe.defaults.get_user_default('Territory');
  },
};
</script>