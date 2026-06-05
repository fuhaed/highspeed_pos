<template>
  <div class="coupons-panel-wrapper h-100" :dir="isRTL ? 'rtl' : 'ltr'">
    <v-card class="coupons-panel-card d-flex flex-column h-100 elevation-0">
      <!-- Header Section -->
      <v-card-title class="pa-4 bg-gradient-header flex-shrink-0">
        <div class="d-flex align-center" :class="{ 'flex-row-reverse': isRTL }">
          <v-icon :class="isRTL ? 'ml-3' : 'mr-3'" color="white" size="24">mdi-ticket-percent</v-icon>
          <span class="text-h6 text-white font-weight-medium">{{ __('Coupons') }}</span>
        </div>
      </v-card-title>

      <!-- Coupon Input Section (Below Header) -->
      <div class="coupon-input-section px-4 py-3 flex-shrink-0 border-b">
        <v-row no-gutters align="center" :class="{ 'flex-row-reverse': isRTL }">
          <v-col cols="9" class="pa-1">
            <v-text-field 
              density="compact" 
              variant="outlined" 
              :label="__('Enter Coupon Code')"
              bg-color="white" 
              hide-details 
              v-model="new_coupon" 
              class="coupon-text-field"
              prepend-inner-icon="mdi-barcode-scan"
              @keyup.enter="add_coupon(new_coupon)"
              clearable>
            </v-text-field>
          </v-col>
          <v-col cols="3" class="pa-1">
            <v-btn 
              block
              height="40px"
              color="primary" 
              variant="flat"
              class="add-coupon-btn font-weight-medium"
              @click="add_coupon(new_coupon)"
              :disabled="!new_coupon">
              <v-icon size="18" class="me-1">mdi-plus</v-icon>
              {{ __('Add') }}
            </v-btn>
          </v-col>
        </v-row>
      </div>

      <!-- Statistics Bar -->
      <div class="stats-bar px-4 py-2 flex-shrink-0">
        <v-row no-gutters align="center" :class="{ 'flex-row-reverse': isRTL }">
          <v-col cols="6">
            <div class="d-flex align-center" :class="{ 'flex-row-reverse': isRTL }">
              <v-icon :class="isRTL ? 'ml-2' : 'mr-2'" size="18" color="slate-500">mdi-ticket-outline</v-icon>
              <span class="text-body-2 text-slate-700">
                {{ __('Total Coupons') }}: <strong class="stat-badge available">{{ couponsCount }}</strong>
              </span>
            </div>
          </v-col>
          <v-col cols="6">
            <div class="d-flex align-center justify-end" :class="{ 'flex-row-reverse': isRTL }">
              <v-icon :class="isRTL ? 'ml-2' : 'mr-2'" size="18" color="teal">mdi-check-circle-outline</v-icon>
              <span class="text-body-2 text-slate-700">
                {{ __('Applied') }}: <strong class="stat-badge applied">{{ appliedCouponsCount }}</strong>
              </span>
            </div>
          </v-col>
        </v-row>
      </div>

      <!-- Coupons List -->
      <div class="coupons-list-container flex-grow-1" style="overflow-y: auto;">
        <!-- Empty State -->
        <div v-if="hspos_coupons.length === 0" class="empty-state d-flex flex-column align-center justify-center py-16">
          <div class="empty-icon-wrapper mb-4">
            <v-icon size="64" color="slate-400">mdi-ticket-percent-outline</v-icon>
          </div>
          <h3 class="text-h6 font-weight-bold text-slate-700 mb-1">{{ __('No coupons added yet') }}</h3>
          <p class="text-body-2 text-slate-500 text-center px-4">{{ __('Enter a coupon code above to get started') }}</p>
        </div>

        <!-- Coupon Cards -->
        <v-container v-else fluid class="pa-4">
          <v-row :class="{ 'flex-row-reverse': isRTL }">
            <v-col 
              v-for="(coupon, index) in hspos_coupons" 
              :key="coupon.coupon"
              cols="12"
              class="py-1">
              <v-card 
                class="coupon-ticket-card" 
                :class="{ 'applied-coupon': coupon.applied }"
                flat>
                <v-card-text class="pa-3">
                  <v-row no-gutters align="center" :class="{ 'flex-row-reverse': isRTL }">
                    <v-col cols="12" sm="5">
                      <div class="d-flex align-center" :class="{ 'flex-row-reverse': isRTL }">
                        <div class="ticket-icon-wrapper me-3">
                          <v-icon 
                            :color="coupon.applied ? 'teal-darken-1' : 'slate-500'" 
                            size="20">
                            {{ coupon.applied ? 'mdi-check-circle' : 'mdi-ticket-percent' }}
                          </v-icon>
                        </div>
                        <div class="text-start">
                          <div class="coupon-code font-weight-bold text-slate-800">{{ coupon.coupon_code }}</div>
                          <div class="offer-name text-caption text-slate-500">{{ coupon.hspos_offer }}</div>
                        </div>
                      </div>
                    </v-col>
                    
                    <v-col cols="6" sm="3" class="text-center py-1">
                      <v-chip 
                        :color="coupon.type === 'Promotional' ? 'deep-purple-lighten-5' : 'orange-lighten-5'" 
                        :text-color="coupon.type === 'Promotional' ? 'deep-purple-darken-3' : 'orange-darken-3'"
                        variant="flat"
                        size="small"
                        class="font-weight-medium">
                        {{ coupon.type }}
                      </v-chip>
                    </v-col>
                    
                    <v-col cols="6" sm="4" class="d-flex align-center justify-end py-1" :class="{ 'flex-row-reverse': isRTL }">
                      <div class="me-3">
                        <span 
                          v-if="coupon.applied"
                          class="applied-status-badge text-teal-darken-1 font-weight-medium">
                          <v-icon size="14" class="me-1">mdi-check</v-icon>
                          {{ __('Applied') }}
                        </span>
                        <span 
                          v-else
                          class="applied-status-badge text-slate-400">
                          {{ __('Not Applied') }}
                        </span>
                      </div>
                      <v-btn
                        icon="mdi-delete-outline"
                        variant="text"
                        color="red-darken-1"
                        size="small"
                        density="comfortable"
                        class="delete-coupon-btn"
                        @click.stop="deleteCoupon(coupon)">
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </div>

      <!-- Footer Actions -->
      <v-card-actions class="pa-4 bg-white border-t flex-shrink-0">
        <v-btn 
          block 
          size="large" 
          color="grey-darken-2" 
          variant="flat"
          class="action-btn"
          @click="back_to_invoice"
          :prepend-icon="isRTL ? '' : 'mdi-arrow-left'"
          :append-icon="isRTL ? 'mdi-arrow-right' : ''">
          {{ __('Back to Invoice') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
export default {
  data: () => ({
    loading: false,
    pos_profile: '',
    customer: '',
    hspos_coupons: [],
    new_coupon: null,
    itemsPerPage: 1000,
    singleExpand: true,
    isRTL: false,
  }),

  computed: {
    couponsCount() {
      return this.hspos_coupons.length;
    },
    appliedCouponsCount() {
      return this.hspos_coupons.filter((el) => !!el.applied).length;
    },
  },

  methods: {
    back_to_invoice() {
      this.eventBus.emit('show_coupons', 'false');
    },
    
    add_coupon(new_coupon) {
      if (!this.customer || !new_coupon) {
        this.eventBus.emit('show_message', {
          title: __('Select a customer to use coupon'),
          color: 'error',
        });
        return;
      };
      const exist = this.hspos_coupons.find(
        (el) => el.coupon_code == new_coupon
      );
      if (exist) {
        this.eventBus.emit('show_message', {
          title: __('This coupon already used !'),
          color: 'error',
        });
        return;
      }
      const vm = this;
      frappe.call({
        method: 'highspeed_pos.highspeed_pos.api.hsposapp.get_hspos_coupon',
        args: {
          coupon: new_coupon,
          customer: vm.customer,
          company: vm.pos_profile.company,
        },
        callback: function (r) {
          if (r.message) {
            const res = r.message;
            if (res.msg != 'Apply' || !res.coupon) {
              vm.eventBus.emit('show_message', {
                text: res.msg,
                color: 'error',
              });
            } else {
              vm.new_coupon = null;
              const coupon = res.coupon;
              vm.hspos_coupons.push({
                coupon: coupon.name,
                coupon_code: coupon.coupon_code,
                type: coupon.coupon_type,
                applied: 0,
                hspos_offer: coupon.hspos_offer,
                customer: coupon.customer || vm.customer,
              });
            }
          }
        },
      });
    },

    deleteCoupon(coupon) {
      this.hspos_coupons = this.hspos_coupons.filter(
        (c) => c.coupon !== coupon.coupon
      );
      this.eventBus.emit('show_message', {
        title: __('Coupon removed'),
        color: 'info',
      });
    },
    
    setActiveGiftCoupons() {
      if (!this.customer) return;
      const vm = this;
      frappe.call({
        method: 'highspeed_pos.highspeed_pos.api.hsposapp.get_active_gift_coupons',
        args: {
          customer: vm.customer,
          company: vm.pos_profile.company,
        },
        callback: function (r) {
          if (r.message) {
            const coupons = r.message;
            coupons.forEach((coupon_code) => {
              vm.add_coupon(coupon_code);
            });
          }
        },
      });
    },

    updatePosCoupons(offers) {
      this.hspos_coupons.forEach((coupon) => {
        const offer = offers.find(
          (el) => el.offer_applied && el.coupon == coupon.coupon
        );
        if (offer) {
          coupon.applied = 1;
        } else {
          coupon.applied = 0;
        }
      });
    },

    removeCoupon(reomove_list) {
      this.hspos_coupons = this.hspos_coupons.filter(
        (coupon) => !reomove_list.includes(coupon.coupon)
      );
    },
    
    updateInvoice() {
      this.eventBus.emit('update_invoice_coupons', this.hspos_coupons);
    },
    
    updateCounters() {
      this.eventBus.emit('update_coupons_counters', {
        couponsCount: this.couponsCount,
        appliedCouponsCount: this.appliedCouponsCount,
      });
    },
  },

  watch: {
    hspos_coupons: {
      deep: true,
      handler() {
        this.updateInvoice();
        this.updateCounters();
      },
    },
  },

  created: function () {
    const lang = frappe.boot.lang;
    const htmlDir = document.documentElement.getAttribute('dir');
    const bodyDir = document.body.getAttribute('dir');
    this.isRTL = htmlDir === 'rtl' || bodyDir === 'rtl' || ['ar', 'he', 'fa', 'ur'].includes(lang?.substring(0, 2));

    this.$nextTick(function () {
      this.eventBus.on('register_pos_profile', (data) => {
        this.pos_profile = data.pos_profile;
      });
    });
    this.eventBus.on('update_customer', (customer) => {
      if (this.customer != customer) {
        const to_remove = [];
        this.hspos_coupons.forEach((el) => {
          if (el.type == 'Promotional') {
            el.customer = customer;
          } else {
            to_remove.push(el.coupon);
          }
        });
        this.customer = customer;
        if (to_remove.length) {
          this.removeCoupon(to_remove);
        }
      }
      this.setActiveGiftCoupons();
    });
    this.eventBus.on('update_hspos_coupons', (data) => {
      this.updatePosCoupons(data);
    });
    this.eventBus.on('set_hspos_coupons', (data) => {
      this.hspos_coupons = data;
    });
  },
};
</script>

<style scoped>
.coupons-panel-wrapper {
  background-color: #f8fafc;
}

.coupons-panel-card {
  background-color: #f8fafc !important;
}

.bg-gradient-header {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
  border-radius: 4px 4px 0 0 !important;
}

.coupon-input-section {
  background-color: #ffffff;
  border-bottom: 1px solid #e2e8f0;
}

.coupon-text-field :deep(.v-field) {
  border-radius: 4px !important;
}

.add-coupon-btn {
  border-radius: 4px !important;
}

.stats-bar {
  background-color: #ffffff;
  border-bottom: 1px solid #e2e8f0;
}

.stat-badge {
  display: inline-block;
  padding: 2px 8px;
  font-size: 0.8rem;
  font-weight: 600;
  border-radius: 3px !important;
}

.stat-badge.available {
  background-color: #f1f5f9;
  color: #475569;
}

.stat-badge.applied {
  background-color: #ccfbf1;
  color: #0f766e;
}

.coupons-list-container {
  background-color: #f8fafc;
}

.empty-state {
  height: 100%;
}

.empty-icon-wrapper {
  background-color: #f1f5f9;
  padding: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.coupon-ticket-card {
  background-color: #ffffff !important;
  border: 1.5px dashed #cbd5e1 !important;
  border-radius: 4px !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.coupon-ticket-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04) !important;
}

.coupon-ticket-card::before, .coupon-ticket-card::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 10px;
  height: 10px;
  background: #f8fafc;
  border-radius: 50%;
  transform: translateY(-50%);
  z-index: 3;
}

.coupon-ticket-card::before {
  left: -6px;
  box-shadow: inset -1.5px 0 0 #cbd5e1;
}

.coupon-ticket-card::after {
  right: -6px;
  box-shadow: inset 1.5px 0 0 #cbd5e1;
}

.applied-coupon {
  border-color: #0d9488 !important;
  background-color: #f0fdfa !important;
}

.applied-coupon::before {
  box-shadow: inset -1.5px 0 0 #0d9488;
}

.applied-coupon::after {
  box-shadow: inset 1.5px 0 0 #0d9488;
}

.ticket-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 4px;
  background-color: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e2e8f0;
}

.applied-coupon .ticket-icon-wrapper {
  background-color: #ffffff;
  border-color: #ccfbf1;
}

.coupon-code {
  font-size: 0.9rem;
  letter-spacing: 0.5px;
}

.offer-name {
  font-size: 0.75rem;
}

.v-chip {
  border-radius: 3px !important;
}

.applied-status-badge {
  font-size: 0.75rem;
  display: inline-flex;
  align-items: center;
}

.delete-coupon-btn {
  border-radius: 4px !important;
}

.action-btn {
  height: 44px !important;
  font-weight: 500;
  letter-spacing: 0.5px;
  border-radius: 4px !important;
}

/* RTL Helpers */
[dir="rtl"] .me-3 {
  margin-right: 0 !important;
  margin-left: 0.75rem !important;
}

[dir="rtl"] .me-1 {
  margin-right: 0 !important;
  margin-left: 0.25rem !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>