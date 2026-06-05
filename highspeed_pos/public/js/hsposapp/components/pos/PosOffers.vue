<template>
  <div class="offers-panel-wrapper h-100" :dir="isRTL ? 'rtl' : 'ltr'">
    <v-card class="offers-panel-card d-flex flex-column h-100 elevation-0">
      <!-- Header -->
      <v-card-title class="pa-4 bg-gradient-header flex-shrink-0">
        <div class="d-flex align-center" :class="{ 'flex-row-reverse': isRTL }">
          <v-icon :class="isRTL ? 'ml-3' : 'mr-3'" color="white" size="24">mdi-tag-multiple</v-icon>
          <span class="text-h6 text-white font-weight-medium">{{ __('Special Offers') }}</span>
        </div>
      </v-card-title>

      <!-- Statistics Bar -->
      <div class="stats-bar px-4 py-3 flex-shrink-0">
        <v-row no-gutters align="center" :class="{ 'flex-row-reverse': isRTL }">
          <v-col cols="6">
            <div class="d-flex align-center" :class="{ 'flex-row-reverse': isRTL }">
              <v-icon :class="isRTL ? 'ml-2' : 'mr-2'" size="18" color="slate-500">mdi-tag-outline</v-icon>
              <span class="text-body-2 text-slate-700">
                {{ __('Available Offers') }}: <strong class="stat-badge available">{{ offersCount }}</strong>
              </span>
            </div>
          </v-col>
          <v-col cols="6">
            <div class="d-flex align-center justify-end" :class="{ 'flex-row-reverse': isRTL }">
              <v-icon :class="isRTL ? 'ml-2' : 'mr-2'" size="18" color="success">mdi-check-circle-outline</v-icon>
              <span class="text-body-2 text-slate-700">
                {{ __('Applied') }}: <strong class="stat-badge applied">{{ appliedOffersCount }}</strong>
              </span>
            </div>
          </v-col>
        </v-row>
      </div>

      <!-- Offers List -->
      <div class="offers-list-container flex-grow-1" style="overflow-y: auto;">
        <!-- Empty State -->
        <div v-if="hspos_offers.length === 0" class="empty-state d-flex flex-column align-center justify-center py-16">
          <div class="empty-icon-wrapper mb-4">
            <v-icon size="64" color="slate-400">mdi-tag-off-outline</v-icon>
          </div>
          <h3 class="text-h6 font-weight-bold text-slate-700 mb-1">{{ __('No offers available') }}</h3>
          <p class="text-body-2 text-slate-500 text-center px-4">{{ __('Check back later for special deals') }}</p>
        </div>

        <!-- Offers Cards -->
        <v-container v-else fluid class="pa-4">
          <v-row :class="{ 'flex-row-reverse': isRTL }">
            <v-col 
              v-for="(offer, index) in hspos_offers" 
              :key="offer.row_id"
              cols="12"
              md="6"
              class="py-2">
              <v-card 
                class="offer-card h-100" 
                :class="{ 'offer-applied': offer.offer_applied }"
                variant="flat"
                @click="toggleOfferDetails(offer.row_id)">
                
                <v-card-text class="pa-4 d-flex flex-column h-100">
                  <!-- Header Row -->
                  <div class="d-flex justify-space-between align-start mb-3" :class="{ 'flex-row-reverse': isRTL }">
                    <div class="d-flex align-center" :class="{ 'flex-row-reverse': isRTL }">
                      <div class="offer-icon-container me-3" :style="{ backgroundColor: getOfferIcon(offer.offer).bgColor }">
                        <v-icon 
                          :color="getOfferIcon(offer.offer).color" 
                          size="20">
                          {{ getOfferIcon(offer.offer).icon }}
                        </v-icon>
                      </div>
                      <div class="text-start">
                        <h4 class="offer-title font-weight-bold text-slate-800">{{ offer.name }}</h4>
                        <span class="offer-type-subtitle text-caption text-slate-500">{{ __(offer.offer) }}</span>
                      </div>
                    </div>
                    
                    <div @click.stop class="d-flex align-center checkbox-wrapper">
                      <v-checkbox
                        v-model="offer.offer_applied"
                        @click.stop="toggleOfferApplied(offer)"
                        :disabled="isOfferDisabled(offer)"
                        color="success"
                        density="compact"
                        hide-details
                        class="ma-0 pa-0 inline-checkbox">
                      </v-checkbox>
                    </div>
                  </div>

                  <!-- Info Section -->
                  <div class="offer-brief-details mb-3 text-start">
                    <div class="detail-line d-flex align-center mb-1" :class="{ 'flex-row-reverse': isRTL }">
                      <span class="detail-label text-caption text-slate-500 me-2">{{ __('Applies to') }}:</span>
                      <span class="detail-val text-body-2 font-weight-medium text-slate-700">{{ offer.apply_on }}</span>
                    </div>
                    
                    <div v-if="offer.auto" class="mt-2 d-flex" :class="{ 'justify-end': isRTL }">
                      <span class="auto-badge">
                        <v-icon size="12" class="me-1">mdi-lightning-bolt</v-icon>
                        {{ __('Auto Apply') }}
                      </span>
                    </div>
                  </div>

                  <div class="flex-grow-1"></div>

                  <!-- Expand/Collapse Button -->
                  <div class="offer-expand-btn-wrapper d-flex justify-center mt-2">
                    <v-btn
                      variant="text"
                      size="x-small"
                      color="primary"
                      class="expand-btn font-weight-medium"
                      @click.stop="toggleOfferDetails(offer.row_id)">
                      <v-icon size="14" class="me-1">
                        {{ expanded.includes(offer.row_id) ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
                      </v-icon>
                      {{ expanded.includes(offer.row_id) ? __('Show Less') : __('Show More') }}
                    </v-btn>
                  </div>

                  <!-- Expanded Content -->
                  <v-expand-transition>
                    <div v-if="expanded.includes(offer.row_id)" class="expanded-content-box mt-3 pt-3 border-t text-start">
                      <div v-if="offer.description" class="offer-desc-text text-body-2 text-slate-600 mb-3 pa-3 bg-slate-50 border rounded-sm">
                        <div v-html="handleNewLine(offer.description)"></div>
                      </div>

                      <div v-if="offer.offer == 'Give Product'" class="mt-2" @click.stop>
                        <v-autocomplete
                          v-model="offer.give_item"
                          :items="get_give_items(offer)"
                          item-title="item_code"
                          variant="outlined"
                          density="compact"
                          color="primary"
                          class="give-item-autocomplete"
                          :label="__('Select free item')"
                          :disabled="offer.apply_type != 'Item Group' || offer.replace_item || offer.replace_cheapest_item"
                          hide-details>
                          <template v-slot:prepend-inner>
                            <v-icon size="16" class="text-slate-400">mdi-gift-outline</v-icon>
                          </template>
                        </v-autocomplete>
                      </div>

                      <v-alert 
                        v-if="offer.offer_applied && offer.items && offer.items.length > 0"
                        color="success"
                        variant="tonal"
                        density="compact"
                        class="mt-3 py-1 px-3 applied-alert">
                        <v-icon size="14" class="me-1">mdi-check-all</v-icon>
                        <span class="text-caption font-weight-medium">
                          {{ __('Applied to') }} {{ offer.items.length }} {{ offer.items.length === 1 ? __('item') : __('items') }}
                        </span>
                      </v-alert>
                    </div>
                  </v-expand-transition>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </div>

      <!-- Bottom Action Bar -->
      <v-card-actions class="pa-4 bg-white border-t flex-shrink-0">
        <v-row dense :class="{ 'flex-row-reverse': isRTL }" class="w-100 ma-0">
          <v-col cols="6" class="pa-1">
            <v-btn 
              block 
              size="large" 
              color="grey-darken-2" 
              variant="flat"
              class="action-btn"
              @click="back_to_invoice"
              :prepend-icon="isRTL ? '' : 'mdi-arrow-left'"
              :append-icon="isRTL ? 'mdi-arrow-right' : ''">
              {{ __('Back') }}
            </v-btn>
          </v-col>
          <v-col cols="6" class="pa-1">
            <v-btn 
              block 
              size="large" 
              color="success" 
              variant="flat"
              class="action-btn"
              @click="applyOffers"
              :disabled="appliedOffersCount === 0"
              prepend-icon="mdi-check">
              {{ __('Apply') }} ({{ appliedOffersCount }})
            </v-btn>
          </v-col>
        </v-row>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import format from '../../format';

export default {
  mixins: [format],
  data: () => ({
    loading: false,
    pos_profile: '',
    hspos_offers: [],
    allItems: [],
    discount_percentage_offer_name: null,
    expanded: [],
    isRTL: false,
  }),

  computed: {
    offersCount() {
      return this.hspos_offers.length;
    },
    appliedOffersCount() {
      return this.hspos_offers.filter((el) => !!el.offer_applied).length;
    },
  },

  methods: {
    back_to_invoice() {
      this.eventBus.emit('show_offers', 'false');
    },
    
    applyOffers() {
      this.eventBus.emit('show_message', {
        title: __('Offers applied successfully'),
        color: 'success',
      });
      this.back_to_invoice();
    },
    
    toggleOfferApplied(offer) {
      if (!this.isOfferDisabled(offer)) {
        offer.offer_applied = !offer.offer_applied;
        this.forceUpdateItem();
      }
    },

    toggleOfferDetails(row_id) {
      if (this.expanded.includes(row_id)) {
        this.expanded = this.expanded.filter(id => id !== row_id);
      } else {
        this.expanded.push(row_id);
      }
    },
    
    isOfferDisabled(offer) {
      return (offer.offer == 'Give Product' &&
        !offer.give_item &&
        (!offer.replace_cheapest_item || !offer.replace_item)) ||
        (offer.offer == 'Grand Total' &&
          this.discount_percentage_offer_name &&
          this.discount_percentage_offer_name != offer.name);
    },
    
    getOfferIcon(offerType) {
      const icons = {
        'Discount Percentage': { icon: 'mdi-percent', color: 'blue-darken-2', bgColor: '#e0f2fe' },
        'Discount Amount': { icon: 'mdi-cash-minus', color: 'green-darken-2', bgColor: '#dcfce7' },
        'Give Product': { icon: 'mdi-gift', color: 'purple-darken-2', bgColor: '#f3e8ff' },
        'Grand Total': { icon: 'mdi-calculator', color: 'orange-darken-2', bgColor: '#ffedd5' },
        'Price': { icon: 'mdi-tag', color: 'red-darken-2', bgColor: '#fee2e2' }
      };
      return icons[offerType] || { icon: 'mdi-tag', color: 'grey-darken-2', bgColor: '#f1f5f9' };
    },
    
    forceUpdateItem() {
      let list_offers = [];
      list_offers = [...this.hspos_offers];
      this.hspos_offers = list_offers;
    },
    
    makeid(length) {
      let result = '';
      const characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
      const charactersLength = characters.length;
      for (var i = 0; i < length; i++) {
        result += characters.charAt(
          Math.floor(Math.random() * charactersLength)
        );
      }
      return result;
    },
    
    updatePosOffers(offers) {
      const toRemove = [];
      this.hspos_offers.forEach((hspos_offer) => {
        const offer = offers.find((offer) => offer.name === hspos_offer.name);
        if (!offer) {
          toRemove.push(hspos_offer.row_id);
        }
      });
      this.removeOffers(toRemove);
      
      offers.forEach((offer) => {
        const hspos_offer = this.hspos_offers.find(
          (hspos_offer) => offer.name === hspos_offer.name
        );
        if (hspos_offer) {
          hspos_offer.items = offer.items;
          if (
            hspos_offer.offer === 'Grand Total' &&
            !this.discount_percentage_offer_name
          ) {
            hspos_offer.offer_applied = !!hspos_offer.auto;
          }
          if (
            offer.apply_on == 'Item Group' &&
            offer.apply_type == 'Item Group' &&
            offer.replace_cheapest_item
          ) {
            hspos_offer.give_item = offer.give_item;
            hspos_offer.apply_item_code = offer.apply_item_code;
          }
        } else {
          const newOffer = { ...offer };
          if (!offer.row_id) {
            newOffer.row_id = this.makeid(20);
          }
          if (offer.apply_type == 'Item Code') {
            newOffer.give_item = offer.apply_item_code || 'Nothing';
          }
          if (offer.offer_applied) {
            newOffer.offer_applied == !!offer.offer_applied;
          } else {
            if (
              offer.apply_type == 'Item Group' &&
              offer.offer == 'Give Product' &&
              !offer.replace_cheapest_item &&
              !offer.replace_item
            ) {
              newOffer.offer_applied = false;
            } else if (
              offer.offer === 'Grand Total' &&
              this.discount_percentage_offer_name
            ) {
              newOffer.offer_applied = false;
            } else {
              newOffer.offer_applied = !!offer.auto;
            }
          }
          if (newOffer.offer == 'Give Product' && !newOffer.give_item) {
            newOffer.give_item = this.get_give_items(newOffer)[0]?.item_code;
          }
          this.hspos_offers.push(newOffer);
          this.eventBus.emit('show_message', {
            title: __('New offer available'),
            color: 'success',
          });
        }
      });
    },
    
    removeOffers(offers_id_list) {
      this.hspos_offers = this.hspos_offers.filter(
        (offer) => !offers_id_list.includes(offer.row_id)
      );
    },
    
    handelOffers() {
      const applyedOffers = this.hspos_offers.filter(
        (offer) => offer.offer_applied
      );
      this.eventBus.emit('update_invoice_offers', applyedOffers);
    },
    
    handleNewLine(str) {
      if (str) {
        return str.replace(/(?:\r\n|\r|\n)/g, '<br />');
      } else {
        return '';
      }
    },
    
    get_give_items(offer) {
      if (offer.apply_type == 'Item Code') {
        return [{ item_code: offer.apply_item_code }];
      } else if (offer.apply_type == 'Item Group') {
        const items = this.allItems;
        let filterd_items = [];
        const filterd_items_1 = items.filter(
          (item) => item.item_group == offer.apply_item_group
        );
        if (offer.less_then > 0) {
          filterd_items = filterd_items_1.filter(
            (item) => item.rate < offer.less_then
          );
        } else {
          filterd_items = filterd_items_1;
        }
        return filterd_items;
      } else {
        return [];
      }
    },
    
    updateCounters() {
      this.eventBus.emit('update_offers_counters', {
        offersCount: this.offersCount,
        appliedOffersCount: this.appliedOffersCount,
      });
    },
    
    updatePosCoupuns() {
      const applyedOffers = this.hspos_offers.filter(
        (offer) => offer.offer_applied && offer.coupon_based
      );
      this.eventBus.emit('update_hspos_coupons', applyedOffers);
    },
  },

  watch: {
    hspos_offers: {
      deep: true,
      handler(hspos_offers) {
        this.handelOffers();
        this.updateCounters();
        this.updatePosCoupuns();
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
        this.offers = [];
      }
    });
    
    this.eventBus.on('update_hspos_offers', (data) => {
      this.updatePosOffers(data);
    });
    
    this.eventBus.on('update_discount_percentage_offer_name', (data) => {
      this.discount_percentage_offer_name = data.value;
    });
    
    this.eventBus.on('set_all_items', (data) => {
      this.allItems = data;
    });
  },
};
</script>

<style scoped>
.offers-panel-wrapper {
  background-color: #f8fafc;
}

.offers-panel-card {
  background-color: #f8fafc !important;
}

.bg-gradient-header {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
  border-radius: 4px 4px 0 0 !important;
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
  background-color: #dcfce7;
  color: #15803d;
}

.offers-list-container {
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

.offer-card {
  background-color: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 4px !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
  height: 100%;
}

.offer-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05) !important;
  border-color: #cbd5e1 !important;
}

.offer-applied {
  background-color: #ffffff !important;
  border-color: #22c55e !important;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.05) !important;
}

.offer-icon-container {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.offer-title {
  font-size: 0.95rem;
  line-height: 1.25;
}

.offer-type-subtitle {
  font-size: 0.75rem;
}

.auto-badge {
  background-color: #fef3c7;
  color: #d97706;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 3px !important;
  display: inline-flex;
  align-items: center;
}

.expand-btn {
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

.expanded-content-box {
  border-color: #f1f5f9 !important;
}

.offer-desc-text {
  font-size: 0.8rem;
  line-height: 1.4;
  border-radius: 4px !important;
  border-color: #e2e8f0 !important;
}

.give-item-autocomplete :deep(.v-field) {
  border-radius: 4px !important;
}

.applied-alert {
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

[dir="rtl"] .ms-2 {
  margin-left: 0 !important;
  margin-right: 0.5rem !important;
}

/* Support Vuetify checkboxes in compact layout */
.inline-checkbox :deep(.v-selection-control) {
  min-height: 24px;
}
.inline-checkbox :deep(.v-selection-control__wrapper) {
  width: 24px;
  height: 24px;
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