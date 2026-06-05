<template>
  <v-row justify="center">
    <v-dialog v-model="isOpen" persistent max-width="600px">
      <v-card class="elevation-0 rounded-lg" dir="rtl">
        <v-card-title class="pa-5 bg-grey-lighten-4">
          <v-icon class="ml-3" color="primary">mdi-cash-register</v-icon>
          <span class="text-h6">{{
            __('Create HSPOS Opening Shift')
          }}</span>
        </v-card-title>
        
        <v-divider></v-divider>
        
        <v-card-text class="pa-5">
          <v-container class="pa-0">
            <v-row>
              <v-col cols="12" class="pb-3">
                <v-autocomplete 
                  :items="companies" 
                  :label="frappe._('Company')" 
                  v-model="company"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-domain"
                  hide-details
                  required>
                </v-autocomplete>
              </v-col>
              
              <v-col cols="12" class="pb-3">
                <v-autocomplete 
                  :items="pos_profiles" 
                  :label="frappe._('POS Profile')" 
                  v-model="pos_profile"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-account"
                  hide-details
                  required>
                </v-autocomplete>
              </v-col>
              
              <v-col cols="12" class="pt-3">
                <div class="text-body-1 mb-3 text-grey-darken-1">
                  {{ __('Payment Methods') }}
                </div>
                <v-table class="border rounded" density="comfortable">
                  <thead>
                    <tr>
                      <th class="text-right bg-grey-lighten-5">{{ __('Mode of Payment') }}</th>
                      <th class="text-left bg-grey-lighten-5">{{ __('Opening Amount') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in payments_methods" :key="item.mode_of_payment">
                      <td class="text-right">{{ item.mode_of_payment }}</td>
                      <td class="text-left">
                        <v-text-field
                          v-model="item.amount"
                          type="text"
                          inputmode="decimal"
                          @input="item.amount = convertArabicToLatin($event.target.value).replace(/[^0-9.]/g, '')"
                          variant="outlined"
                          density="compact"
                          hide-details
                          single-line
                          :prefix="currencySymbol(item.currency)">
                        </v-text-field>
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        
        <v-divider></v-divider>
        
        <v-card-actions class="pa-5">
          <v-spacer></v-spacer>
          <v-btn 
            variant="text"
            color="grey-darken-1"
            @click="go_desk">
            {{ __('Cancel') }}
          </v-btn>
          <v-btn 
            variant="flat"
            color="primary" 
            :disabled="is_loading" 
            :loading="is_loading"
            class="px-5"
            @click="submit_dialog">
            {{ __('Submit') }}
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
  props: ['dialog'],
  data() {
    return {
      isOpen: this.dialog ? this.dialog : false,
      dialog_data: {},
      is_loading: false,
      companies: [],
      company: '',
      pos_profiles_data: [],
      pos_profiles: [],
      pos_profile: '',
      payments_method_data: [],
      payments_methods: [],
      max25chars: (v) => v.length <= 12 || 'Input too long!',
    };
  },
  watch: {
    company(val) {
      this.pos_profiles = [];
      this.pos_profiles_data.forEach((element) => {
        if (element.company === val) {
          this.pos_profiles.push(element.name);
        }
        if (this.pos_profiles.length) {
          this.pos_profile = this.pos_profiles[0];
        } else {
          this.pos_profile = '';
        }
      });
    },
    pos_profile(val) {
      this.payments_methods = [];
      this.payments_method_data.forEach((element) => {
        if (element.parent === val) {
          this.payments_methods.push({
            mode_of_payment: element.mode_of_payment,
            amount: 0,
            currency: element.currency,
          });
        }
      });
    },
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
    close_opening_dialog() {
      this.eventBus.emit('close_opening_dialog');
    },
    get_opening_dialog_data() {
      const vm = this;
      frappe.call({
        method: 'highspeed_pos.highspeed_pos.api.hsposapp.get_opening_dialog_data',
        args: {},
        callback: function (r) {
          if (r.message) {
            r.message.companies.forEach((element) => {
              vm.companies.push(element.name);
            });
            vm.company = vm.companies[0];
            vm.pos_profiles_data = r.message.pos_profiles_data;
            vm.payments_method_data = r.message.payments_method;
          }
        },
      });
    },
    submit_dialog() {
      if (!this.payments_methods.length || !this.company || !this.pos_profile) {
        return;
      }
      this.is_loading = true;
      var vm = this;
      return frappe
        .call('highspeed_pos.highspeed_pos.api.hsposapp.create_opening_voucher', {
          pos_profile: this.pos_profile,
          company: this.company,
          balance_details: this.payments_methods,
        })
        .then((r) => {
          if (r.message) {
            vm.eventBus.emit('register_pos_data', r.message);
            vm.eventBus.emit('set_company', r.message.company);
            vm.close_opening_dialog();
            vm.is_loading = false;
          }
        });
    },
    go_desk() {
      frappe.set_route('/');
      location.reload();
    },
  },
  created: function () {
    this.$nextTick(function () {
      this.get_opening_dialog_data();
    });
  },
};
</script>

<style scoped>
[dir="rtl"] .v-icon {
  transform: scaleX(-1);
}

[dir="rtl"] .ml-3 {
  margin-left: 0 !important;
  margin-right: 0.75rem !important;
}

[dir="rtl"] .mr-1 {
  margin-right: 0 !important;
  margin-left: 0.25rem !important;
}

[dir="rtl"] .text-left {
  text-align: right !important;
}

[dir="rtl"] .text-right {
  text-align: left !important;
}

.v-card {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.v-table {
  border: 1px solid #e0e0e0;
}

.cursor-pointer {
  cursor: pointer;
}

.hover-bg {
  transition: background-color 0.2s ease;
}

.hover-bg:hover {
  background-color: #f5f5f5;
}

.v-field--focused {
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.v-field__outline {
  color: #e0e0e0;
}

.v-btn--variant-flat {
  box-shadow: none !important;
}
</style>