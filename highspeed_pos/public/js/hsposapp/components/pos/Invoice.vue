<template>
  <div class="invoice-container" :dir="isRTL ? 'rtl' : 'ltr'">
    <v-dialog v-model="cancel_dialog" max-width="320">
      <v-card>
        <v-card-title class="text-h6 text-error">
          {{ __("Cancel Sale?") }}
        </v-card-title>
        <v-card-text class="text-body-2">
          {{ __("This will cancel and delete the current sale. To save it as Draft, click 'Save and Clear' instead.") }}
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" variant="text" @click="cancel_invoice">
            {{ __("Yes, Cancel") }}
          </v-btn>
          <v-btn color="grey" variant="text" @click="cancel_dialog = false">
            {{ __("Back") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-card class="invoice-card" :class="{ 'return-mode': invoiceType === 'Return' || invoice_doc.is_return }" elevation="2">
      <!-- Active Draft Alert Banner -->
      <div v-if="invoice_doc && invoice_doc.docstatus === 0" class="d-flex align-center justify-space-between px-3 py-2 border-b w-100" style="background-color: #fff9db; border-bottom: 1.5px solid #ffe066 !important;">
        <div class="d-flex align-center">
          <v-icon size="18" color="amber-darken-3" class="me-2">mdi-file-clock-outline</v-icon>
          <span class="text-caption font-weight-bold text-amber-darken-4">
            {{ isRTL ? 'مسودة نشطة:' : 'Active Draft:' }} <span class="font-mono">{{ invoice_doc.name }}</span>
          </span>
        </div>
        <v-chip size="x-small" color="amber-darken-3" class="font-weight-black text-white" variant="flat">
          {{ isRTL ? 'مسودة معلقة' : 'Pending Draft' }}
        </v-chip>
      </div>

      <div class="header-section">
        <v-row dense class="pa-2">
          <v-col :cols="pos_profile.hspos_allow_sales_order ? 8 : 12">
            <Customer />
          </v-col>
          <v-col v-if="pos_profile.hspos_allow_sales_order" cols="4">
            <v-select
              v-model="invoiceType"
              :items="invoiceTypes"
              :label="__('Type')"
              variant="outlined"
              density="compact"
              hide-details
              :disabled="invoiceType == 'Return'"
              class="type-select"
            />
          </v-col>
          <!-- Table Selection Chip -->
          <v-col cols="12" v-if="pos_profile && pos_profile.hspos_enable_dining_tables && selected_table" class="pt-0">
            <v-chip
              color="teal-darken-1"
              variant="flat"
              closable
              @click:close="clear_selected_table"
              class="font-weight-bold px-2 py-1 text-subtitle-2 elevation-1 text-white w-100 justify-center"
              style="height: 36px; border-radius: 4px !important;"
            >
              <v-icon start size="16" class="me-1">mdi-table-chair</v-icon>
              {{ __("Table") }}: {{ selected_table }}
            </v-chip>
          </v-col>
        </v-row>



        <v-row v-if="pos_profile.hspos_use_hspos_delivery_charges" dense class="pa-2 pt-0">
          <v-col cols="8">
            <v-autocomplete
              v-model="selected_delivery_charge"
              :items="hspos_delivery_charges"
              item-title="name"
              item-value="name"
              return-object
              :label="__('HSPOS Delivery Charges')"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              :disabled="readonly"
              @update:model-value="update_hspos_delivery_charges()"
              class="delivery-select"
            >
              <template v-slot:item="{ props, item }">
                <v-list-item v-bind="props">
                  <v-list-item-title>{{ item.raw.name }}</v-list-item-title>
                  <v-list-item-subtitle>{{ __("Rate") }}: {{ item.raw.rate }}</v-list-item-subtitle>
                </v-list-item>
              </template>
            </v-autocomplete>
          </v-col>
          <v-col cols="4">
            <v-text-field
              :model-value="formatCurrency(hspos_delivery_charges_rate)"
              :label="__('Rate')"
              variant="outlined"
              density="compact"
              hide-details
              disabled
              class="rate-field"
            />
          </v-col>
        </v-row>

        <v-row v-if="pos_profile.hspos_allow_change_posting_date" dense class="pa-2 pt-0">
          <v-col cols="6">
            <v-menu v-model="invoice_posting_date" :close-on-content-click="false">
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="posting_date"
                  :label="__('Posting Date')"
                  variant="outlined"
                  density="compact"
                  hide-details
                  readonly
                  v-bind="props"
                  class="date-field"
                />
              </template>
              <v-date-picker
                v-model="posting_date"
                color="primary"
                :min="frappe.datetime.add_days(frappe.datetime.now_date(true), -7)"
                :max="frappe.datetime.add_days(frappe.datetime.now_date(true), 7)"
                @update:model-value="invoice_posting_date = false"
              />
            </v-menu>
          </v-col>
        </v-row>
      </div>

      <div class="items-section">
        <div v-if="items.length === 0" class="empty-cart">
          <div class="empty-cart-content">
            <div class="empty-cart-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 1H5L7.68 14.39C7.77144 14.8504 8.02191 15.264 8.38755 15.5583C8.75318 15.8526 9.2107 16.009 9.68 16H19.4C19.8693 16.009 20.3268 15.8526 20.6925 15.5583C21.0581 15.264 21.3086 14.8504 21.4 14.39L23 6H6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="8" cy="21" r="1" stroke="currentColor" stroke-width="2"/>
                <circle cx="19" cy="21" r="1" stroke="currentColor" stroke-width="2"/>
                <path d="M12 3V12M9 9L12 12L15 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3 class="empty-cart-title">{{ __("Cart is Empty") }}</h3>
            <p class="empty-cart-subtitle">{{ __("Start adding products to continue") }}</p>
          </div>
        </div>
        <div v-else class="items-list">
          <template v-for="(item, index) in items" :key="item.hspos_row_id">
            <div v-if="!item.hspos_is_addon" class="item-card">
              <div class="item-content">
                <div class="item-header-line" @click="handleItemClick(item)">
                  <div class="item-title-container">
                    <div class="item-title">
                      <span class="item-name">{{ item.item_name }}</span>
                      
                      <v-chip
                        v-if="item.is_stock_item && (!item.actual_qty || item.actual_qty <= 0)"
                        size="x-small"
                        color="error"
                        variant="flat"
                        class="ms-2 font-weight-bold"
                      >
                        {{ __("Out of Stock") }}
                      </v-chip>
                      <v-chip
                        v-else-if="item.is_stock_item && item.actual_qty <= 3"
                        size="x-small"
                        color="warning"
                        variant="flat"
                        class="ms-2 font-weight-bold"
                      >
                        {{ __("Low Stock: {0}", [item.actual_qty]) }}
                      </v-chip>
                      <v-chip
                        v-if="item.batch_no && item.batch_no_expiry_date && isExpiryClose(item.batch_no_expiry_date)"
                        size="x-small"
                        color="error"
                        variant="outlined"
                        class="ms-2 font-weight-bold"
                      >
                        {{ __("Expires soon") }}
                      </v-chip>
                    </div>
                    <div v-if="item.hspos_addons_desc" class="addons-subtitle font-weight-medium text-caption text-grey-darken-1 mt-1">
                      {{ item.hspos_addons_desc }}
                    </div>
                  </div>
                <v-chip 
                  v-if="!!item.hspos_is_offer || !!item.hspos_is_replace" 
                  size="x-small"
                  color="success"
                  class="offer-chip"
                >
                  {{ __("Offer") }}
                </v-chip>
              </div>
              
              <div class="item-data-line">
                <div class="action-group">
                  <v-btn
                    icon
                    size="x-small"
                    variant="text"
                    color="error"
                    :disabled="!!item.hspos_is_offer || !!item.hspos_is_replace"
                    @click.stop="remove_item(item)"
                    class="delete-btn"
                  >
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </div>
                
                <div class="data-group total-group">
                  <span class="total-value">{{ formatCurrency(get_combined_total(item)) }}</span>
                </div>
                
                <div class="data-group price-group" @click.stop>
                  <input
                    type="text"
                    :value="formatPrice(get_combined_rate(item))"
                    @input="handlePriceInputTemp(item, $event)"
                    @blur="handlePriceCommit(item)"
                    @keydown.enter="handlePriceCommit(item)"
                    @keydown.tab="handlePriceCommit(item)"
                    @click.stop
                    :disabled="!!item.hspos_is_offer || !!item.hspos_is_replace || !!item.hspos_offer_applied || !pos_profile.hspos_allow_user_to_edit_rate || !!invoice_doc.is_return"
                    class="price-input"
                    inputmode="decimal"
                    pattern="[0-9]*[.,]?[0-9]*"
                  />
                </div>
                
                <div class="data-group uom-group" @click.stop>
                  <v-select
                    v-model="item.uom"
                    :items="item.item_uoms || []"
                    item-title="uom"
                    item-value="uom"
                    variant="plain"
                    density="compact"
                    hide-details
                    single-line
                    :disabled="!!invoice_doc.is_return || !!item.hspos_is_offer || !!item.hspos_is_replace || !!item.hspos_is_addon"
                    @update:model-value="calc_uom(item, $event)"
                    class="uom-select"
                  />
                </div>
                
                <div class="data-group qty-group" @click.stop>
                  <v-btn
                    icon
                    size="x-small"
                    variant="text"
                    density="compact"
                    :disabled="!!item.hspos_is_offer || !!item.hspos_is_replace || !!invoice_doc.is_return || !!item.hspos_is_addon"
                    @click.stop="add_one(item)"
                    class="qty-btn"
                  >
                    <v-icon>mdi-plus</v-icon>
                  </v-btn>
                  <input
                    type="text"
                    inputmode="numeric"
                    :value="item.qty"
                    @input="handleQtyInput(item, $event)"
                    @click.stop
                    :disabled="!!invoice_doc.is_return || !!item.hspos_is_offer || !!item.hspos_is_replace || !!item.hspos_is_addon"
                    class="qty-input"
                  />
                  <v-btn
                    icon
                    size="x-small"
                    variant="text"
                    density="compact"
                    :disabled="!!item.hspos_is_offer || !!item.hspos_is_replace || !!invoice_doc.is_return || !!item.hspos_is_addon"
                    @click.stop="subtract_one(item)"
                    class="qty-btn"
                  >
                    <v-icon>mdi-minus</v-icon>
                  </v-btn>
                </div>
              </div>
            </div>

            <v-collapse-transition>
              <div v-if="isItemExpanded(item)" class="item-details">
                <v-row dense>
                  <v-col cols="4">
                    <div class="detail-field">
                      <label>{{ __("Quantity") }}</label>
                      <v-text-field
                        :model-value="item.qty"
                        type="text"
                        inputmode="numeric"
                        variant="outlined"
                        density="compact"
                        hide-details
                        :disabled="!!invoice_doc.is_return || !!item.hspos_is_offer || !!item.hspos_is_replace"
                        @input="item.qty = parseFloat(convertArabicToLatin($event.target.value).replace(/[^0-9-]/g, '')) || 0; handleQtyChange(item)"
                        class="compact-input"
                      />
                    </div>
                  </v-col>
                  
                  <v-col cols="4">
                    <div class="detail-field">
                      <label>{{ __("UOM") }}</label>
                      <v-select
                        v-model="item.uom"
                        :items="item.item_uoms || []"
                        item-title="uom"
                        item-value="uom"
                        variant="outlined"
                        density="compact"
                        hide-details
                        :disabled="!!invoice_doc.is_return || !!item.hspos_is_offer || !!item.hspos_is_replace"
                        @update:model-value="calc_uom(item, $event)"
                        class="compact-input"
                      />
                    </div>
                  </v-col>
                  
                  <v-col cols="4">
                    <div class="detail-field">
                      <label>{{ __("Rate") }}</label>
                      <v-text-field
                        :model-value="formatPrice(get_combined_rate(item))"
                        @input="handlePriceInputTemp(item, $event)"
                        @blur="handlePriceCommit(item)"
                        @keydown.enter="handlePriceCommit(item)"
                        @keydown.tab="handlePriceCommit(item)"
                        variant="outlined"
                        density="compact"
                        hide-details
                        type="text"
                        :disabled="!!item.hspos_is_offer || !!item.hspos_is_replace || !!item.hspos_offer_applied || !pos_profile.hspos_allow_user_to_edit_rate || !!invoice_doc.is_return"
                        class="compact-input"
                      />
                    </div>
                  </v-col>
                </v-row>

                <v-row dense v-if="item.has_serial_no || item.has_batch_no || (pos_profile.hspos_allow_sales_order && invoiceType == 'Order')">
                  <v-col cols="12" v-if="item.has_serial_no">
                    <v-autocomplete
                      v-model="item.serial_no_selected"
                      :items="item.serial_no_data"
                      item-title="serial_no"
                      :label="__('Serial Numbers')"
                      variant="outlined"
                      density="compact"
                      chips
                      multiple
                      hide-details
                      @update:model-value="set_serial_no(item)"
                      class="mt-2"
                    />
                  </v-col>
                  
                  <v-col cols="12" v-if="item.has_batch_no">
                    <v-autocomplete
                      v-model="item.batch_no"
                      :items="item.batch_no_data"
                      item-title="batch_no"
                      :label="__('Batch No')"
                      variant="outlined"
                      density="compact"
                      hide-details
                      @update:model-value="set_batch_qty(item, $event)"
                      class="mt-2"
                    >
                      <template v-slot:item="{ props, item }">
                        <v-list-item v-bind="props">
                          <v-list-item-title>{{ item.raw.batch_no }}</v-list-item-title>
                          <v-list-item-subtitle>
                            {{ __("Qty") }}: {{ item.raw.batch_qty }} - {{ __("Expiry") }}: {{ item.raw.expiry_date }}
                          </v-list-item-subtitle>
                        </v-list-item>
                      </template>
                    </v-autocomplete>
                  </v-col>
                  
                  <v-col cols="12" v-if="pos_profile.hspos_allow_sales_order && invoiceType == 'Order'">
                    <v-menu v-model="item.item_delivery_date" :close-on-content-click="false">
                      <template v-slot:activator="{ props }">
                        <v-text-field
                          v-model="item.hspos_delivery_date"
                          :label="__('Delivery Date')"
                          variant="outlined"
                          density="compact"
                          readonly
                          hide-details
                          v-bind="props"
                          lang="en"
                          class="mt-2"
                        />
                      </template>
                      <v-date-picker
                        v-model="item.hspos_delivery_date"
                        color="primary"
                        :min="frappe.datetime.now_date()"
                        @update:model-value="[item.item_delivery_date = false, validate_due_date(item)]"
                      />
                    </v-menu>
                  </v-col>
                </v-row>

                <div class="item-stats">
                  <div class="stat-item">
                    <span class="stat-label">{{ __("Stock") }}</span>
                    <span class="stat-value">{{ formatFloat(item.actual_qty || 0) }}</span>
                  </div>
                  <div class="stat-item" v-if="item.discount_percentage > 0">
                    <span class="stat-label">{{ __("Discount") }}</span>
                    <span class="stat-value">{{ formatFloat(item.discount_percentage) }}%</span>
                  </div>
                </div>
              </div>
            </v-collapse-transition>
          </div>
        </template>
      </div>
      </div>

      <div class="footer-section">
        <div class="totals-container">
          <div class="total-item">
            <span class="total-label">{{ __("Items") }}</span>
            <span class="total-value">{{ formatFloat(total_qty) }}</span>
          </div>
          <div class="total-item">
            <span class="total-label">{{ __("Discount") }}</span>
            <span class="total-value">{{ formatCurrency(discount_amount) }}</span>
          </div>
          <div class="total-item total-final">
            <span class="total-label">{{ __("Total") }}</span>
            <span class="total-value">{{ formatCurrency(subtotal) }}</span>
          </div>
        </div>

        <div class="action-buttons">
          <div class="secondary-actions">
            <v-btn
              color="primary"
              variant="outlined"
              size="small"
              @click="save_invoice"
              class="action-btn"
            >
              <v-icon size="small" start>mdi-content-save</v-icon>
              <span class="btn-text">
                {{ __("Save") }}
                <span class="shortcut-key">F10</span>
              </span>
            </v-btn>
            
            <v-btn
              color="orange"
              variant="outlined"
              size="small"
              @click="get_draft_invoices"
              class="action-btn"
            >
              <v-icon size="small" start>mdi-file-document</v-icon>
              <span class="btn-text">
                {{ __("Drafts") }}
                <span class="shortcut-key">F8</span>
              </span>
            </v-btn>
            
            <v-btn
              v-if="pos_profile.custom_allow_select_sales_order === 1"
              color="info"
              variant="outlined"
              size="small"
              @click="get_draft_orders"
              class="action-btn"
            >
              <v-icon size="small" start>mdi-cart</v-icon>
              <span class="btn-text">
                {{ __("Orders") }}
                <span class="shortcut-key">F7</span>
              </span>
            </v-btn>
            
            <v-btn
              color="error"
              variant="outlined"
              size="small"
              @click="cancel_dialog = true"
              class="action-btn"
            >
              <v-icon size="small" start>mdi-close</v-icon>
              <span class="btn-text">
                {{ __("Cancel") }}
                <span class="shortcut-key">F9</span>
              </span>
            </v-btn>
            
            <v-btn
              v-if="pos_profile.hspos_allow_return == 1"
              color="secondary"
              variant="outlined"
              size="small"
              @click="open_returns"
              class="action-btn"
            >
              <v-icon size="small" start>mdi-keyboard-return</v-icon>
              <span class="btn-text">
                {{ __("Return") }}
                <span class="shortcut-key">F6</span>
              </span>
            </v-btn>
            
            <v-btn
              v-if="pos_profile.hspos_allow_print_draft_invoices"
              color="purple"
              variant="outlined"
              size="small"
              @click="print_draft_invoice"
              class="action-btn"
            >
              <v-icon size="small" start>mdi-printer</v-icon>
              <span class="btn-text">
                {{ __("Print") }}
                <span class="shortcut-key">F5</span>
              </span>
            </v-btn>
          </div>
          
          <v-btn
            color="success"
            variant="flat"
            size="large"
            @click="show_payment"
            class="pay-btn"
          >
            <v-icon size="large" start>mdi-cash</v-icon>
            <span class="btn-text">
              {{ __("PAY") }}
              <span class="shortcut-key pay-shortcut">F12</span>
            </span>
          </v-btn>
        </div>
      </div>
    </v-card>

    <!-- Addons Dialog -->
    <addons-dialog
      v-model="addonsDialog"
      :item="selectedItemForAddons"
      @confirm="onAddonsConfirmed"
    />
  </div>
</template>

<script>
import format from "../../format";
import Customer from "./Customer.vue";
import AddonsDialog from "./AddonsDialog.vue";

export default {
  mixins: [format],
  components: { Customer, AddonsDialog },
  
  data() {
    return {
      pos_profile: "",
      hspos_opening_shift: "",
      stock_settings: "",
      invoice_doc: "",
      return_doc: "",
      customer: "",
      customer_info: "",
      addonsDialog: false,
      selectedItemForAddons: null,
      discount_amount: 0,
      additional_discount_percentage: 0,
      total_tax: 0,
      items: [],
      posOffers: [],
      hspos_offers: [],
      hspos_coupons: [],
      all_offers: [],
      applied_offers: [],
      allItems: [],
      discount_percentage_offer_name: null,
      invoiceTypes: ["Invoice", "Order"],
      invoiceType: "Invoice",
      cancel_dialog: false,
      float_precision: 2,
      currency_precision: 2,
      selected_table: "",
      new_line: false,
      hspos_delivery_charges: [],
      hspos_delivery_charges_rate: 0,
      selected_delivery_charge: "",
      invoice_posting_date: false,
      posting_date: frappe.datetime.nowdate(),
      readonly: false,
      isRTL: false,
      expandedItems: new Set(),
      tempPriceValues: {},
      order_type: "Dine-in",
    };
  },

  computed: {
    total_qty() {
      this.close_payments();
      let qty = 0;
      this.items.forEach((item) => {
        if (!item.hspos_is_addon) {
          qty += Math.abs(parseFloat(item.qty) || 0);
        }
      });
      return this.flt(qty, this.float_precision);
    },

    Total() {
      let sum = 0;
      this.items.forEach((item) => {
        sum += parseFloat(item.qty) * parseFloat(item.rate);
      });
      return this.flt(sum, this.currency_precision);
    },

    subtotal() {
      this.close_payments();
      let sum = 0;
      this.items.forEach((item) => {
        sum += parseFloat(item.qty) * parseFloat(item.rate);
      });
      sum -= this.flt(this.discount_amount);
      sum += this.flt(this.hspos_delivery_charges_rate);
      return this.flt(sum, this.currency_precision);
    },

    total_items_discount_amount() {
      let sum = 0;
      this.items.forEach((item) => {
        sum += Math.abs(parseFloat(item.qty)) * parseFloat(item.discount_amount);
      });
      return this.flt(sum, this.float_precision);
    },
  },

  methods: {
    getDefaultOrderType() {
      if (!this.pos_profile) return "Dine-in";
      if (this.pos_profile.hspos_allow_dine_in) return "Dine-in";
      if (this.pos_profile.hspos_allow_takeaway) return "Takeaway";
      if (this.pos_profile.hspos_allow_delivery) return "Delivery";
      return "Dine-in";
    },



    isExpiryClose(dateStr) {
      if (!dateStr) return false;
      const today = new Date();
      const expiry = new Date(dateStr);
      const timeDiff = expiry.getTime() - today.getTime();
      const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
      return daysDiff <= 30;
    },

    evaluatePromotions() {
      if (this.invoice_doc.is_return || this.invoiceType === "Return") return;
      
      const autoOffers = (this.all_offers || []).filter(o => !!o.auto);
      const manualApplied = (this.applied_offers || []).filter(o => !o.auto);
      
      const allApplied = [...autoOffers, ...manualApplied];
      
      this.applied_offers = allApplied;
      this.applyOffersToCart();
    },

    applyAutomaticOffers() {
      if (!this.all_offers || this.all_offers.length === 0) return;
      const autoOffers = this.all_offers.filter(o => !!o.auto);
      this.applied_offers = autoOffers.map(o => ({ ...o, offer_applied: true }));
      this.applyOffersToCart();
    },

    applyOffersToCart() {
      if (this.invoice_doc.is_return || this.invoiceType === "Return") return;

      // Filter out previously added offer items
      this.items = this.items.filter(item => !item.is_free_item && !item.hspos_is_offer);
      
      // Reset rates & discounts for standard items
      this.items.forEach(item => {
        item.rate = item.price_list_rate || item.rate || 0;
        item.discount_amount = 0;
        item.discount_percentage = 0;
        item.hspos_offer_applied = null;
        item.hspos_is_offer = 0;
      });

      if (!this.applied_offers || this.applied_offers.length === 0) {
        this.$forceUpdate();
        return;
      }

      this.applied_offers.forEach(offer => {
        const today = frappe.datetime.nowdate();
        if (offer.valid_from && offer.valid_from > today) return;
        if (offer.valid_upto && offer.valid_upto < today) return;
        if (offer.disable) return;

        if (offer.offer === "Item Price" || offer.offer === "Give Product") {
          const matchingItems = this.items.filter(item => {
            if (offer.apply_on === "Item Code") {
              return item.item_code === offer.item;
            } else if (offer.apply_on === "Item Group") {
              return item.item_group === offer.item_group;
            } else if (offer.apply_on === "Brand") {
              return item.brand === offer.brand;
            }
            return false;
          });

          if (matchingItems.length === 0) return;

          const totalQty = matchingItems.reduce((sum, item) => sum + Math.abs(item.qty), 0);
          const totalAmt = matchingItems.reduce((sum, item) => sum + (Math.abs(item.qty) * item.rate), 0);

          if (offer.min_qty > 0 && totalQty < offer.min_qty) return;
          if (offer.max_qty > 0 && totalQty > offer.max_qty) return;
          if (offer.min_amt > 0 && totalAmt < offer.min_amt) return;
          if (offer.max_amt > 0 && totalAmt > offer.max_amt) return;

          if (offer.offer === "Item Price") {
            matchingItems.forEach(item => {
              item.hspos_offer_applied = offer.name;
              if (offer.discount_type === "Rate") {
                item.rate = offer.rate;
                item.discount_amount = (item.price_list_rate || item.rate) - offer.rate;
                item.discount_percentage = ((item.price_list_rate - item.rate) / item.price_list_rate) * 100;
              } else if (offer.discount_type === "Discount Percentage") {
                item.discount_percentage = offer.discount_percentage;
                item.discount_amount = (item.price_list_rate || item.rate) * (offer.discount_percentage / 100);
                item.rate = (item.price_list_rate || item.rate) - item.discount_amount;
              } else if (offer.discount_type === "Discount Amount") {
                item.discount_amount = offer.discount_amount;
                item.discount_percentage = (offer.discount_amount / (item.price_list_rate || item.rate)) * 100;
                item.rate = (item.price_list_rate || item.rate) - offer.discount_amount;
              }
            });
          } else if (offer.offer === "Give Product") {
            if (offer.replace_item) {
              matchingItems.forEach(item => {
                item.rate = 0;
                item.discount_percentage = 100;
                item.discount_amount = item.price_list_rate;
                item.hspos_offer_applied = offer.name;
                item.hspos_is_offer = 1;
              });
            } else if (offer.replace_cheapest_item) {
              let cheapestItem = matchingItems[0];
              matchingItems.forEach(item => {
                if (item.rate < cheapestItem.rate) {
                  cheapestItem = item;
                }
              });
              cheapestItem.rate = 0;
              cheapestItem.discount_percentage = 100;
              cheapestItem.discount_amount = cheapestItem.price_list_rate;
              cheapestItem.hspos_offer_applied = offer.name;
              cheapestItem.hspos_is_offer = 1;
            } else if (offer.give_item) {
              const freeItemCode = offer.give_item;
              frappe.call({
                method: "highspeed_pos.highspeed_pos.api.hsposapp.get_item_detail",
                args: {
                  warehouse: this.pos_profile.warehouse,
                  price_list: this.pos_profile.price_list,
                  item: {
                    item_code: freeItemCode,
                    company: this.pos_profile.company,
                    qty: offer.given_qty || 1,
                    price_list: this.get_price_list(),
                  }
                },
                callback: (r) => {
                  if (r.message) {
                    const data = r.message;
                    const newFreeItem = {
                      item_code: data.item_code,
                      item_name: data.item_name,
                      qty: offer.given_qty || 1,
                      rate: 0,
                      price_list_rate: data.price_list_rate,
                      uom: data.stock_uom,
                      stock_uom: data.stock_uom,
                      is_free_item: 1,
                      hspos_is_offer: 1,
                      hspos_offer_applied: offer.name,
                      hspos_row_id: this.makeid(20),
                      item_uoms: data.item_uoms || [{ uom: data.stock_uom, conversion_factor: 1 }]
                    };
                    this.items.unshift(newFreeItem);
                    this.$forceUpdate();
                  }
                }
              });
            }
          }
        } else if (offer.offer === "Grand Total") {
          const currentSubtotal = this.subtotal;
          if (offer.min_amt > 0 && currentSubtotal < offer.min_amt) return;
          if (offer.max_amt > 0 && currentSubtotal > offer.max_amt) return;

          if (offer.discount_type === "Discount Percentage") {
            this.additional_discount_percentage = offer.discount_percentage;
            this.discount_amount = currentSubtotal * (offer.discount_percentage / 100);
          } else if (offer.discount_type === "Discount Amount") {
            this.discount_amount = offer.discount_amount;
            this.additional_discount_percentage = (offer.discount_amount / currentSubtotal) * 100;
          }
        }
      });

      this.$forceUpdate();
    },

    // Internationalization helper
    __(text, replacements = []) {
      // Use Frappe's translation function if available
      if (typeof frappe !== 'undefined' && frappe._ && typeof frappe._ === 'function') {
        return frappe._(text, replacements);
      }
      // Fallback to the text itself
      let result = text;
      if (replacements && replacements.length) {
        replacements.forEach((rep, index) => {
          result = result.replace(`{${index}}`, rep);
        });
      }
      return result;
    },

    formatCurrency(value) {
      const num = parseFloat(value) || 0;
      return num.toFixed(this.currency_precision);
    },

    formatPrice(value) {
      const num = parseFloat(value) || 0;
      return num.toFixed(this.currency_precision);
    },

    formatFloat(value) {
      const num = parseFloat(value) || 0;
      return num.toFixed(this.float_precision);
    },

    convertArabicToLatin(str) {
      if (str === null || str === undefined) return '';
      str = String(str);
      return str.replace(/[٠-٩]/g, function(d) {
        return d.charCodeAt(0) - 1632;
      }).replace(/[۰-۹]/g, function(d) {
        return d.charCodeAt(0) - 1776;
      });
    },

    handleQtyInput(item, event) {
      let val = event.target.value;
      val = this.convertArabicToLatin(val);
      val = val.replace(/[^0-9-]/g, '');
      item.qty = val === '' ? 0 : parseFloat(val);
      if (isNaN(item.qty)) item.qty = 0;
      event.target.value = val;
      this.handleQtyChange(item);
    },

    handlePriceInputTemp(item, event) {
      let value = event.target ? event.target.value : event;
      value = this.convertArabicToLatin(value);
      value = value.toString().replace(',', '.');
      value = value.replace(/[^0-9.]/g, '');
      
      const parts = value.split('.');
      if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
      }
      
      this.tempPriceValues[item.hspos_row_id] = value;
    },

    handlePriceCommit(item) {
      const tempValue = this.tempPriceValues[item.hspos_row_id];
      if (tempValue !== undefined) {
        if (tempValue === '' || tempValue === '.') {
          item.rate = 0;
        } else {
          const numValue = parseFloat(tempValue);
          if (!isNaN(numValue)) {
            let addons_rate = 0;
            this.items.forEach((el) => {
              if (el.hspos_is_addon && el.hspos_parent_item_row === item.hspos_row_id) {
                addons_rate += parseFloat(el.rate) || 0;
              }
            });
            item.rate = Math.max(0, numValue - addons_rate);
          }
        }
        delete this.tempPriceValues[item.hspos_row_id];
        this.handleRateChange(item);
      }
    },

    handlePriceInput(item, event) {
      let value = event.target ? event.target.value : event;
      value = value.toString().replace(',', '.');
      value = value.replace(/[^0-9.]/g, '');
      
      const parts = value.split('.');
      if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
      }
      
      if (value === '' || value === '.') {
        item.rate = 0;
      } else {
        const numValue = parseFloat(value);
        if (!isNaN(numValue)) {
          let addons_rate = 0;
          this.items.forEach((el) => {
            if (el.hspos_is_addon && el.hspos_parent_item_row === item.hspos_row_id) {
              addons_rate += parseFloat(el.rate) || 0;
            }
          });
          item.rate = Math.max(0, numValue - addons_rate);
        }
      }
      
      this.handleRateChange(item);
    },

    formatPriceOnBlur(item) {
      item.rate = parseFloat(item.rate) || 0;
      this.$forceUpdate();
    },

    detectRTL() {
      const lang = frappe.boot.lang || 'en';
      this.isRTL = ['ar', 'he', 'fa', 'ur'].includes(lang);
    },

    toggleItemDetails(item) {
      if (this.expandedItems.has(item.hspos_row_id)) {
        this.expandedItems.delete(item.hspos_row_id);
      } else {
        this.expandedItems.add(item.hspos_row_id);
      }
      this.$forceUpdate();
    },

    isItemExpanded(item) {
      return this.expandedItems.has(item.hspos_row_id);
    },

    handleKeyboardShortcuts(event) {
      if (event.key === 'F10') {
        event.preventDefault();
        this.save_invoice();
      }
      else if (event.key === 'F9') {
        event.preventDefault();
        if (this.cancel_dialog) {
          this.cancel_dialog = false;
        } else {
          this.cancel_dialog = true;
        }
      }
      else if (event.key === 'F8') {
        event.preventDefault();
        this.get_draft_invoices();
      }
      else if (event.key === 'F7' && this.pos_profile.custom_allow_select_sales_order === 1) {
        event.preventDefault();
        this.get_draft_orders();
      }
      else if (event.key === 'F6' && this.pos_profile.hspos_allow_return == 1) {
        event.preventDefault();
        this.open_returns();
      }
      else if (event.key === 'F5' && this.pos_profile.hspos_allow_print_draft_invoices) {
        event.preventDefault();
        this.print_draft_invoice();
      }
      else if (event.key === 'F12') {
        event.preventDefault();
        this.show_payment();
      }
    },

    handleItemClick(item) {
      if (item.hspos_add_ons && item.hspos_add_ons.length > 0) {
        this.selectedItemForAddons = item;
        this.addonsDialog = true;
      } else {
        this.toggleItemDetails(item);
      }
    },

    onAddonsConfirmed(addons) {
      if (!this.selectedItemForAddons) return;
      const itemToAdd = { ...this.selectedItemForAddons };
      itemToAdd.selected_addons = addons;
      
      const existingItemIndex = itemToAdd.hspos_row_id 
        ? this.items.findIndex(el => el.hspos_row_id === itemToAdd.hspos_row_id)
        : -1;
      
      if (existingItemIndex > -1) {
        const itemInCart = this.items[existingItemIndex];
        const oldUnlinkedPrice = parseFloat(itemInCart.hspos_unlinked_addons_price) || 0;
        itemInCart.rate = Math.max(0, (parseFloat(itemInCart.rate) || 0) - oldUnlinkedPrice);
        itemInCart.price_list_rate = Math.max(0, (parseFloat(itemInCart.price_list_rate) || 0) - oldUnlinkedPrice);
        
        this.items = this.items.filter(el => el.hspos_parent_item_row !== itemInCart.hspos_row_id);
        itemInCart.selected_addons = addons;
        
        let newUnlinkedExtraPrice = 0;
        addons.forEach(addon => {
          if (!addon.add_on_item) {
            newUnlinkedExtraPrice += parseFloat(addon.extra_price) || 0;
          }
        });
        itemInCart.hspos_unlinked_addons_price = newUnlinkedExtraPrice;
        itemInCart.rate = (parseFloat(itemInCart.rate) || 0) + newUnlinkedExtraPrice;
        itemInCart.price_list_rate = (parseFloat(itemInCart.price_list_rate) || 0) + newUnlinkedExtraPrice;
        
        if (addons && addons.length > 0) {
          const addonNames = addons.map(a => a.add_on_name);
          itemInCart.hspos_addons_desc = "+ " + addonNames.join(", ");
        } else {
          itemInCart.hspos_addons_desc = null;
        }
        
        const parentIndex = this.items.indexOf(itemInCart);
        if (parentIndex !== -1) {
          const linkedAddons = addons.filter(addon => !!addon.add_on_item).reverse();
          for (const addon of linkedAddons) {
            const childItem = {
              item_code: addon.add_on_item,
              item_name: "+ " + addon.add_on_name,
              qty: itemInCart.qty,
              stock_qty: itemInCart.qty,
              rate: addon.extra_price,
              price_list_rate: addon.extra_price,
              discount_amount: 0,
              discount_percentage: 0,
              uom: itemInCart.uom,
              conversion_factor: itemInCart.conversion_factor || 1,
              hspos_is_addon: 1,
              hspos_parent_item_row: itemInCart.hspos_row_id,
              hspos_addon_name: addon.add_on_name,
              hspos_row_id: this.makeid(20),
              item_uoms: [{
                uom: itemInCart.uom,
                conversion_factor: 1
              }]
            };
            this.items.splice(parentIndex + 1, 0, childItem);
            this.update_item_detail(childItem);
          }
        }
        this.update_item_detail(itemInCart);
        this.$forceUpdate();
      } else {
        this.add_item(itemToAdd);
      }
      this.selectedItemForAddons = null;
    },

    handleQtyChange(item) {
      let newQty = parseFloat(item.qty) || 0;
      
      if ((this.invoice_doc.is_return || this.invoiceType === "Return") && newQty > 0) {
        newQty = -newQty;
        item.qty = newQty;
      }
      
      if (!this.invoice_doc.is_return && this.invoiceType !== "Return" && newQty <= 0) {
        this.remove_item(item);
        return;
      }
      
      this.calc_stock_qty(item, newQty);
      this.update_item_detail(item);
      
      // Update child addons quantity
      if (item.hspos_row_id) {
        this.items.forEach((el) => {
          if (el.hspos_parent_item_row === item.hspos_row_id) {
            el.qty = item.qty;
            this.calc_stock_qty(el, el.qty);
            this.update_item_detail(el);
          }
        });
      }

      if (item.has_serial_no && item.serial_no_selected) {
        if (item.serial_no_selected.length !== Math.abs(newQty)) {
          this.eventBus.emit("show_message", {
            text: this.__("Serial numbers count ({0}) does not match quantity ({1})", [
              item.serial_no_selected.length, 
              Math.abs(newQty)
            ]),
            color: "warning",
          });
          item.qty = this.invoice_doc.is_return ? -item.serial_no_selected.length : item.serial_no_selected.length;
        }
      }
      
      if (item.has_batch_no && item.actual_batch_qty && Math.abs(newQty) > item.actual_batch_qty) {
        this.eventBus.emit("show_message", {
          text: this.__("Requested quantity ({0}) exceeds available batch quantity ({1})", [
            Math.abs(newQty), 
            item.actual_batch_qty
          ]),
          color: "warning",
        });
        item.qty = this.invoice_doc.is_return ? -item.actual_batch_qty : item.actual_batch_qty;
      }
      
      this.$forceUpdate();
    },

    handleRateChange(item) {
      let value = item.rate;
      
      if (typeof value === 'string') {
        value = value.replace(',', '.');
      }
      
      const newRate = parseFloat(value);
      
      if (!isNaN(newRate) && newRate >= 0) {
        item.rate = newRate;
        
        if (!item.price_list_rate || item.price_list_rate === 0) {
          item.price_list_rate = newRate;
        }
        
        this.recalculateDiscounts(item);
        this.$forceUpdate();
      }
    },

    recalculateDiscounts(item) {
      const rate = parseFloat(item.rate) || 0;
      const priceListRate = parseFloat(item.price_list_rate) || 0;
      
      if (priceListRate > 0 && rate < priceListRate) {
        const discountAmount = priceListRate - rate;
        const discountPercentage = (discountAmount / priceListRate) * 100;
        
        // Vue 3 compatible - direct assignment
        item.discount_amount = parseFloat(discountAmount.toFixed(this.currency_precision));
        item.discount_percentage = parseFloat(discountPercentage.toFixed(2));
      } else {
        item.discount_amount = 0;
        item.discount_percentage = 0;
        
        if (rate > priceListRate) {
          item.price_list_rate = rate;
        }
      }
      
      // Force update to ensure reactivity
      this.$forceUpdate();
    },

    remove_item(item) {
      const index = this.items.findIndex((el) => el.hspos_row_id == item.hspos_row_id);
      if (index >= 0) {
        this.items.splice(index, 1);
      }
      
      // If the removed item was a parent, remove all its child addons
      if (item.hspos_row_id) {
        this.items = this.items.filter((el) => el.hspos_parent_item_row !== item.hspos_row_id);
      }
      
      this.expandedItems.delete(item.hspos_row_id);
      this.evaluatePromotions();
    },

    add_one(item) {
      if (this.invoiceType === "Return" || this.invoice_doc.is_return) {
        item.qty++;
      } else {
        item.qty++;
      }
      
      if (item.qty == 0) {
        this.remove_item(item);
      } else {
        this.calc_stock_qty(item, item.qty);
        this.update_item_detail(item);
        
        // Update child addons quantity
        if (item.hspos_row_id) {
          this.items.forEach((el) => {
            if (el.hspos_parent_item_row === item.hspos_row_id) {
              el.qty = item.qty;
              this.calc_stock_qty(el, el.qty);
              this.update_item_detail(el);
            }
          });
        }
      }
      
      this.$forceUpdate();
    },

    subtract_one(item) {
      if (this.invoiceType === "Return" || this.invoice_doc.is_return) {
        item.qty--;
      } else {
        item.qty--;
      }
      
      if (item.qty == 0) {
        this.remove_item(item);
      } else {
        this.calc_stock_qty(item, item.qty);
        this.update_item_detail(item);
        
        // Update child addons quantity
        if (item.hspos_row_id) {
          this.items.forEach((el) => {
            if (el.hspos_parent_item_row === item.hspos_row_id) {
              el.qty = item.qty;
              this.calc_stock_qty(el, el.qty);
              this.update_item_detail(el);
            }
          });
        }
      }
      
      this.$forceUpdate();
    },

    add_item(item) {
      // Prevent template items from being added to the cart
      if (item && item.has_variants && (item.has_variants == 1 || item.has_variants === true || String(item.has_variants) === '1' || item.has_variants === 'true')) {
        if (this.eventBus) {
          this.eventBus.emit("open_variants_model", { item: item, items: this.allItems || [] });
        }
        return;
      }

      // Check if addons need to be selected
      if (item.hspos_add_ons && item.hspos_add_ons.length > 0 && !item.selected_addons) {
        this.selectedItemForAddons = item;
        this.addonsDialog = true;
        return;
      }

      if (!item.uom) {
        item.uom = item.stock_uom;
      }
      
      let index = -1;
      // If the item has addons, we always force a new line to avoid merging items with different addons.
      const hasSelectedAddons = item.selected_addons && item.selected_addons.length > 0;
      if (!this.new_line && !hasSelectedAddons) {
        index = this.items.findIndex(
          (el) =>
            el.item_code === item.item_code &&
            el.uom === item.uom &&
            !el.hspos_is_offer &&
            !el.hspos_is_replace &&
            !el.hspos_is_addon &&
            el.batch_no === item.batch_no
        );
      }
      
      let parentItem = null;
      if (index === -1 || this.new_line || hasSelectedAddons) {
        const new_item = this.get_new_item(item);
        
        if (hasSelectedAddons) {
          let unlinkedExtraPrice = 0;
          item.selected_addons.forEach(addon => {
            if (!addon.add_on_item) {
              unlinkedExtraPrice += parseFloat(addon.extra_price) || 0;
            }
          });
          new_item.hspos_unlinked_addons_price = unlinkedExtraPrice;
          new_item.rate = (parseFloat(new_item.rate) || 0) + unlinkedExtraPrice;
          new_item.price_list_rate = (parseFloat(new_item.price_list_rate) || 0) + unlinkedExtraPrice;
          
          const addonNames = item.selected_addons.map(a => a.add_on_name);
          new_item.hspos_addons_desc = "+ " + addonNames.join(", ");
        }

        if (this.invoiceType === "Return" || this.invoice_doc.is_return) {
          new_item.qty = -Math.abs(new_item.qty || 1);
          new_item.stock_qty = -Math.abs(new_item.stock_qty || 1);
        }
        
        this.items.unshift(new_item);
        this.update_item_detail(new_item);
        parentItem = new_item;
      } else {
        const cur_item = this.items[index];
        
        if (this.invoiceType === "Return" || this.invoice_doc.is_return) {
          cur_item.qty -= Math.abs(item.qty || 1);
        } else {
          cur_item.qty += (item.qty || 1);
        }
        
        this.calc_stock_qty(cur_item, cur_item.qty);
        this.update_item_detail(cur_item);
        parentItem = cur_item;
      }

      // Add the child addon rows underneath the parent item (only for LINKED addons)
      if (hasSelectedAddons && parentItem) {
        const parentIndex = this.items.indexOf(parentItem);
        if (parentIndex !== -1) {
          const linkedAddons = item.selected_addons.filter(addon => !!addon.add_on_item).reverse();
          for (const addon of linkedAddons) {
            const childItem = {
              item_code: addon.add_on_item,
              item_name: "+ " + addon.add_on_name,
              qty: parentItem.qty,
              stock_qty: parentItem.qty,
              rate: addon.extra_price,
              price_list_rate: addon.extra_price,
              discount_amount: 0,
              discount_percentage: 0,
              uom: parentItem.uom,
              conversion_factor: parentItem.conversion_factor || 1,
              hspos_is_addon: 1,
              hspos_parent_item_row: parentItem.hspos_row_id,
              hspos_addon_name: addon.add_on_name,
              hspos_row_id: this.makeid(20),
              item_uoms: [{
                uom: parentItem.uom,
                conversion_factor: 1
              }]
            };
            this.items.splice(parentIndex + 1, 0, childItem);
            this.update_item_detail(childItem);
          }
        }
      }
      
      this.$forceUpdate();
    },

    get_new_item(item) {
      const new_item = { ...item };
      if (!item.qty) {
        item.qty = 1;
      }
      new_item.stock_qty = item.qty;
      new_item.discount_amount = 0;
      new_item.discount_percentage = 0;
      new_item.price_list_rate = item.rate || 0;
      new_item.qty = item.qty;
      new_item.uom = item.uom ? item.uom : item.stock_uom;
      new_item.conversion_factor = 1;
      new_item.hspos_is_offer = item.hspos_is_offer || 0;
      new_item.hspos_is_replace = item.hspos_is_replace || null;
      new_item.is_free_item = item.is_free_item || 0;
      new_item.hspos_is_addon = item.hspos_is_addon || 0;
      new_item.hspos_parent_item_row = item.hspos_parent_item_row || null;
      new_item.hspos_addon_name = item.hspos_addon_name || null;
      new_item.hspos_notes = "";
      new_item.hspos_delivery_date = "";
      new_item.hspos_row_id = this.makeid(20);
      
      if (!new_item.item_uoms || !Array.isArray(new_item.item_uoms)) {
        new_item.item_uoms = [{
          uom: new_item.stock_uom || new_item.uom || 'Nos',
          conversion_factor: 1
        }];
      }
      
      // Apply offer pricing
      if (new_item.is_free_item || new_item.hspos_is_offer) {
        new_item.rate = 0;
        new_item.price_list_rate = 0;
      }
      
      return new_item;
    },

    clear_selected_table() {
      if (this.selected_table) {
        this.eventBus.emit("table_deselected", this.selected_table);
      }
      this.selected_table = "";
    },

    updateTableStatus(tableName, status) {
      if (!tableName) return;
      frappe.call({
        method: "frappe.client.set_value",
        args: {
          doctype: "POS Table",
          name: tableName,
          fieldname: "status",
          value: status
        }
      });
    },

    clear_invoice() {
      this.items = [];
      this.hspos_offers = [];
      this.hspos_coupons = [];
      this.all_offers = [];
      this.applied_offers = [];
      this.expandedItems.clear();
      this.tempPriceValues = {};
      this.customer = this.pos_profile.customer;
      this.invoice_doc = "";
      this.selected_table = "";
      this.return_doc = "";
      this.discount_amount = 0;
      this.additional_discount_percentage = 0;
      this.hspos_delivery_charges_rate = 0;
      this.selected_delivery_charge = "";
      this.eventBus.emit("set_customer_readonly", false);
      this.invoiceType = this.pos_profile.hspos_default_sales_order ? "Order" : "Invoice";
      this.invoiceTypes = ["Invoice", "Order"];
      this.order_type = this.getDefaultOrderType();
    },

    async cancel_invoice() {
      const doc = this.get_invoice_doc();
      this.invoiceType = this.pos_profile.hspos_default_sales_order ? "Order" : "Invoice";
      this.invoiceTypes = ["Invoice", "Order"];
      this.posting_date = frappe.datetime.nowdate();
      
      if (doc.name && this.pos_profile.hspos_allow_delete) {
        await frappe.call({
          method: "highspeed_pos.highspeed_pos.api.hsposapp.delete_invoice",
          args: { invoice: doc.name },
          async: true,
          callback: (r) => {
            if (r.message) {
              this.eventBus.emit("show_message", {
                text: r.message,
                color: "warning",
              });
            }
          },
        });
      }
      this.clear_invoice();
      this.cancel_dialog = false;
    },

    save_invoice() {
      const doc = this.get_invoice_doc();
      let saved_invoice;
      
      if (doc.name) {
        saved_invoice = this.update_invoice(doc);
      } else {
        if (doc.items.length) {
          saved_invoice = this.update_invoice(doc);
        } else {
          this.eventBus.emit("show_message", {
            title: this.__("Nothing to save"),
            color: "error",
          });
          return;
        }
      }
      
      if (!saved_invoice) {
        this.eventBus.emit("show_message", {
          title: this.__("Error saving the invoice"),
          color: "error",
        });
      } else {
        if (doc.hspos_table) {
          this.updateTableStatus(doc.hspos_table, "Occupied");
        }
        this.eventBus.emit("show_message", {
          title: this.__("Invoice saved successfully"),
          color: "success",
        });
        this.clear_invoice();
        return saved_invoice;
      }
    },

    save_and_clear_invoice() {
      const saved_invoice = this.save_invoice();
      if (saved_invoice) {
        this.clear_invoice();
      }
      return saved_invoice;
    },

    async load_invoice(data = {}) {
      this.clear_invoice();
      if (data.is_return) {
        this.eventBus.emit("set_customer_readonly", true);
        this.invoiceType = "Return";
        this.invoiceTypes = ["Return"];
      }
      this.invoice_doc = data;
      this.items = data.items;
      this.hspos_offers = data.hspos_offers || [];
      this.items.forEach((item) => {
        if (!item.hspos_row_id) {
          item.hspos_row_id = this.makeid(20);
        }
      });
      this.customer = data.customer;
      this.posting_date = data.posting_date || frappe.datetime.nowdate();
      this.discount_amount = data.discount_amount;
      this.additional_discount_percentage = data.additional_discount_percentage;
      this.order_type = data.hspos_order_type || this.getDefaultOrderType();
      this.selected_table = data.hspos_table || "";
      if (this.selected_table) {
        this.eventBus.emit("set_invoice_table", this.selected_table);
      }
    },

    async load_return_invoice(data = {}) {
      this.clear_invoice();
      if (data.items && data.items.length > 0) {
        this.eventBus.emit("set_customer_readonly", true);
        this.invoiceType = "Return";
        this.invoiceTypes = ["Return"];
        this.invoice_doc = {
          is_return: 1,
          return_against: data.name,
          customer: data.customer,
          posting_date: frappe.datetime.nowdate()
        };
        this.return_doc = data;
        
        const return_items = [];
        data.items.forEach((item) => {
          const return_item = {
            ...item,
            qty: -Math.abs(item.qty),
            stock_qty: -Math.abs(item.stock_qty),
            hspos_row_id: this.makeid(20)
          };
          return_items.push(return_item);
        });
        
        this.items = return_items;
        this.customer = data.customer;
        this.posting_date = frappe.datetime.nowdate();
        this.discount_amount = data.discount_amount || 0;
        this.additional_discount_percentage = data.additional_discount_percentage || 0;
      }
    },

    get_invoice_doc() {
      let doc = {};
      if (this.invoice_doc.name) {
        doc = { ...this.invoice_doc };
      }
      
      doc.doctype = "Sales Invoice";
      doc.is_pos = 1;
      doc.ignore_pricing_rule = 1;
      doc.company = doc.company || this.pos_profile.company;
      doc.pos_profile = doc.pos_profile || this.pos_profile.name;
      doc.campaign = doc.campaign || this.pos_profile.campaign;
      doc.currency = doc.currency || this.pos_profile.currency;
      doc.naming_series = doc.naming_series || this.pos_profile.naming_series;
      doc.customer = this.customer;
      doc.hspos_hspos_opening_shift = this.hspos_opening_shift.name;
      doc.posting_date = this.posting_date;
      doc.hspos_table = this.selected_table || "";
      
      const isReturn = this.invoiceType === 'Return' || this.invoice_doc.is_return;
      doc.is_return = isReturn ? 1 : 0;
      
      if (isReturn) {
        doc.update_stock = 1;
        if (this.invoice_doc.return_against) {
          doc.return_against = this.invoice_doc.return_against;
        }
      }
      
      doc.items = this.get_invoice_items();
      
      let total = this.Total;
      if (isReturn && total > 0) {
        total = -Math.abs(total);
      }
      
      doc.total = total;
      doc.net_total = total;
      doc.base_total = total;
      doc.base_net_total = total;
      
      let discountAmount = parseFloat(this.discount_amount) || 0;
      if (isReturn && discountAmount > 0) {
        discountAmount = -Math.abs(discountAmount);
      }
      
      doc.discount_amount = discountAmount;
      doc.base_discount_amount = discountAmount;
      doc.additional_discount_percentage = parseFloat(this.additional_discount_percentage) || 0;
      
      let grandTotal = this.subtotal;
      if (isReturn && grandTotal > 0) {
        grandTotal = -Math.abs(grandTotal);
      }
      
      doc.grand_total = grandTotal;
      doc.base_grand_total = grandTotal;
      doc.rounded_total = Math.round(grandTotal);
      doc.base_rounded_total = Math.round(grandTotal);
      
       doc.payments = this.get_payments();
      
      if (isReturn && doc.payments && doc.payments.length) {
        doc.payments.forEach(payment => {
          if (payment.amount > 0) {
            payment.amount = -Math.abs(payment.amount);
          }
          if (payment.base_amount > 0) {
            payment.base_amount = -Math.abs(payment.base_amount);
          }
        });
      }
      
      doc.taxes = [];
      doc.hspos_offers = this.hspos_offers;
      doc.hspos_coupons = this.hspos_coupons;
      doc.hspos_hspos_delivery_charges = this.selected_delivery_charge?.name || "";
      doc.hspos_hspos_delivery_charges_rate = this.hspos_delivery_charges_rate || 0;
      doc.hspos_order_type = this.order_type || "Dine-in";
      
      return doc;
    },

    get_invoice_items() {
      const items_list = [];
      const isReturn = this.invoiceType === 'Return' || this.invoice_doc.is_return;
      
      this.items.forEach((item) => {
        const new_item = {
          item_code: item.item_code,
          item_name: item.item_name || item.item_code,
          hspos_row_id: item.hspos_row_id,
          hspos_offers: item.hspos_offers,
          hspos_offer_applied: item.hspos_offer_applied,
          hspos_is_offer: item.hspos_is_offer,
          hspos_is_replace: item.hspos_is_replace,
          is_free_item: item.is_free_item,
          hspos_is_addon: item.hspos_is_addon || 0,
          hspos_parent_item_row: item.hspos_parent_item_row || null,
          hspos_addon_name: item.hspos_addon_name || null,
          hspos_addons_desc: item.hspos_addons_desc || null,
          qty: parseFloat(item.qty) || 0,
          rate: parseFloat(item.rate) || 0,
          uom: item.uom,
          amount: (parseFloat(item.qty) || 0) * (parseFloat(item.rate) || 0),
          conversion_factor: item.conversion_factor,
          serial_no: item.serial_no,
          discount_percentage: parseFloat(item.discount_percentage) || 0,
          discount_amount: parseFloat(item.discount_amount) || 0,
          batch_no: item.batch_no,
          hspos_notes: item.hspos_notes,
          hspos_delivery_date: item.hspos_delivery_date,
          price_list_rate: item.price_list_rate,
        };
        
        if (isReturn && item.sales_invoice_item) {
          new_item.sales_invoice_item = item.sales_invoice_item;
        }
        
        if (isReturn) {
          new_item.qty = -Math.abs(new_item.qty);
          new_item.amount = -Math.abs(new_item.amount);
          new_item.discount_amount = -Math.abs(new_item.discount_amount);
        }
        
        items_list.push(new_item);
      });
      
      return items_list;
    },

    get_payments() {
      const payments = [];
      this.pos_profile.payments.forEach((payment) => {
        payments.push({
          amount: 0,
          mode_of_payment: payment.mode_of_payment,
          default: payment.default,
          account: "",
        });
      });
      return payments;
    },

    update_invoice(doc, do_not_save = false) {
      var vm = this;
      frappe.call({
        method: "highspeed_pos.highspeed_pos.api.hsposapp.update_invoice",
        args: {
          data: doc,
          do_not_save: do_not_save
        },
        async: false,
        callback: function (r) {
          if (r.message) {
            vm.invoice_doc = r.message;
          }
        },
      });
      return this.invoice_doc;
    },

    async update_items_details(items) {
      if (!items?.length) return;
      if (!this.pos_profile) return;

      try {
        const response = await frappe.call({
          method: "highspeed_pos.highspeed_pos.api.hsposapp.get_items_details",
          args: {
            pos_profile: this.pos_profile,
            items_data: items
          }
        });

        if (response?.message) {
          items.forEach((item) => {
            const updated_item = response.message.find(
              (element) => element.hspos_row_id == item.hspos_row_id
            );
            if (updated_item) {
              item.actual_qty = updated_item.actual_qty;
              item.serial_no_data = updated_item.serial_no_data;
              item.batch_no_data = updated_item.batch_no_data;
              item.item_uoms = updated_item.item_uoms || [{
                uom: item.stock_uom || item.uom,
                conversion_factor: 1
              }];
              item.has_batch_no = updated_item.has_batch_no;
              item.has_serial_no = updated_item.has_serial_no;
            }
          });
        }
      } catch (error) {
        console.error("Error updating items:", error);
        this.eventBus.emit("show_message", {
          title: this.__("Error updating item details"),
          color: "error"
        });
      }
    },

    process_invoice() {
      const doc = this.get_invoice_doc();
      return this.update_invoice(doc, !doc.name);
    },

    async show_payment() {
      if (!this.customer) {
        this.eventBus.emit("show_message", {
          title: this.__("Select a customer"),
          color: "error",
        });
        return;
      }
      if (!this.items.length) {
        this.eventBus.emit("show_message", {
          title: this.__("Select items to sell"),
          color: "error",
        });
        return;
      }
      if (!await this.validate()) {
        return;
      }

      if (this.invoice_doc.is_return && this.subtotal < 0) {
        const invoice_doc = this.process_invoice();
        
        if (invoice_doc.payments && invoice_doc.payments.length > 0) {
          invoice_doc.payments[0].amount = Math.abs(this.subtotal);
          invoice_doc.payments[0].base_amount = Math.abs(this.subtotal);
        }
        
        this.eventBus.emit("show_payment", "true");
        this.eventBus.emit("send_invoice_doc_payment", invoice_doc);
      } else {
        this.eventBus.emit("show_payment", "true");
        const invoice_doc = this.process_invoice();
        this.eventBus.emit("send_invoice_doc_payment", invoice_doc);
      }
    },

    async validate() {
      let value = true;
      var vm = this;
      
      this.items.forEach((item) => {
        const absQty = Math.abs(item.qty);
        
        if (absQty == 0) {
          vm.eventBus.emit("show_message", {
            title: vm.__("Quantity for item '{0}' cannot be Zero (0)", [item.item_name]),
            color: "error",
          });
          value = false;
        }
        
        if (!this.invoice_doc.is_return && this.invoiceType !== "Return") {
          if (parseFloat(item.rate) <= 0 && !item.is_free_item && !item.hspos_is_offer) {
            vm.eventBus.emit("show_message", {
              title: vm.__("Rate cannot be zero for item '{0}'", [item.item_name]),
              color: "error",
            });
            value = false;
          }
        }
      });
      
      if (this.invoiceType === "Return" || this.invoice_doc.is_return) {
        const positiveItems = this.items.filter(item => item.qty > 0);
        if (positiveItems.length > 0) {
          vm.eventBus.emit('show_message', {
            title: vm.__('Return items must have negative quantities'),
            color: 'error'
          });
          
          positiveItems.forEach(item => {
            item.qty = -Math.abs(item.qty);
            item.stock_qty = -Math.abs(item.stock_qty);
          });
          
          this.$forceUpdate();
        }
        
        if (this.subtotal > 0) {
          vm.eventBus.emit('show_message', {
            title: vm.__('Return total must be negative'),
            color: 'warning'
          });
        }
        
        if (this.invoice_doc.return_against) {
          try {
            const original_invoice = await new Promise((resolve, reject) => {
              frappe.call({
                method: 'frappe.client.get',
                args: {
                  doctype: 'Sales Invoice',
                  name: this.invoice_doc.return_against
                },
                callback: (r) => {
                  if (r.message) {
                    resolve(r.message);
                  } else {
                    reject(new Error('Original invoice not found'));
                  }
                }
              });
            });
            
            console.log('Original invoice data:', original_invoice);
            
            for (const item of this.items) {
              const original_item = original_invoice.items.find(orig => 
                orig.item_code === item.item_code
              );
              
              if (!original_item) {
                vm.eventBus.emit('show_message', {
                  title: vm.__("Item {0} not found in original invoice", [item.item_code]),
                  color: 'error'
                });
                return false;
              }
              
              const rate_diff = Math.abs(original_item.rate - item.rate);
              if (rate_diff > 0.01) {
                vm.eventBus.emit('show_message', {
                  title: vm.__("Rate mismatch for item {0}", [item.item_code]),
                  color: 'error'
                });
                return false;
              }
              
              const return_qty = Math.abs(item.qty);
              const orig_qty = original_item.qty;
              
              if (return_qty > orig_qty) {
                vm.eventBus.emit('show_message', {
                  title: vm.__("Return quantity cannot be greater than original quantity for item {0}", [item.item_code]),
                  color: 'error'
                });
                return false;
              }
            }
            
          } catch (error) {
            console.error('Error validating return:', error);
            vm.eventBus.emit('show_message', {
              title: vm.__("Error validating return: {0}", [error.message]),
              color: 'error'
            });
            return false;
          }
        }
      }
      
      return value;
    },

    get_draft_invoices() {
      var vm = this;
      frappe.call({
        method: "highspeed_pos.highspeed_pos.api.hsposapp.get_draft_invoices",
        args: {
          hspos_opening_shift: this.hspos_opening_shift.name,
          pos_profile: this.pos_profile.name,
        },
        async: false,
        callback: function (r) {
          if (r.message && Array.isArray(r.message)) {
            vm.eventBus.emit("open_drafts", r.message);
          } else {
            vm.eventBus.emit("show_message", {
              title: vm.__("No draft invoices found"),
              color: "info",
            });
          }
        },
        error: function(r) {
          vm.eventBus.emit("show_message", {
            title: vm.__("Error loading draft invoices"),
            color: "error",
          });
        }
      });
    },

    get_draft_orders() {
      var vm = this;
      frappe.call({
        method: "highspeed_pos.highspeed_pos.api.hsposapp.search_orders",
        args: {
          company: this.pos_profile.company,
          currency: this.pos_profile.currency,
        },
        async: false,
        callback: function (r) {
          if (r.message) {
            vm.eventBus.emit("open_orders", r.message);
          }
        },
      });
    },

    open_returns() {
      this.eventBus.emit("open_returns", this.pos_profile.company);
    },

    close_payments() {
      this.eventBus.emit("show_payment", "false");
    },

    get_combined_rate(parentItem) {
      let rate = parseFloat(parentItem.rate) || 0;
      this.items.forEach((el) => {
        if (el.hspos_is_addon && el.hspos_parent_item_row === parentItem.hspos_row_id) {
          rate += parseFloat(el.rate) || 0;
        }
      });
      return rate;
    },

    get_combined_total(parentItem) {
      return (parseFloat(parentItem.qty) || 0) * this.get_combined_rate(parentItem);
    },

    update_item_detail(item) {
      if (!item.item_code || this.invoice_doc.is_return || item.hspos_is_addon) {
        return;
      }
      var vm = this;
      frappe.call({
        method: "highspeed_pos.highspeed_pos.api.hsposapp.get_item_detail",
        args: {
          warehouse: this.pos_profile.warehouse,
          price_list: this.pos_profile.price_list,
          item: {
            item_code: item.item_code,
            customer: this.customer,
            doctype: "Sales Invoice",
            name: "New Sales Invoice 1",
            company: this.pos_profile.company,
            conversion_rate: 1,
            qty: item.qty,
            price_list_rate: item.price_list_rate,
            currency: this.pos_profile.currency,
            pos_profile: this.pos_profile.name,
            uom: item.uom,
            update_stock: this.pos_profile.update_stock,
            price_list: this.get_price_list(),
            has_batch_no: item.has_batch_no,
            serial_no: item.serial_no,
            batch_no: item.batch_no,
            is_stock_item: item.is_stock_item,
          },
        },
        callback: function (r) {
          if (r.message) {
            const data = r.message;
            if (!item.is_free_item && !item.hspos_is_offer && !item.hspos_is_replace) {
              item.price_list_rate = data.price_list_rate + (parseFloat(item.hspos_unlinked_addons_price) || 0);
            }
            item.last_purchase_rate = data.last_purchase_rate;
            item.projected_qty = data.projected_qty;
            item.reserved_qty = data.reserved_qty;
            item.conversion_factor = data.conversion_factor;
            item.stock_qty = data.stock_qty;
            item.actual_qty = data.actual_qty;
            item.stock_uom = data.stock_uom;
            item.has_serial_no = data.has_serial_no;
            item.has_batch_no = data.has_batch_no;
            
            // Stock warning logs / alerts
            if (item.is_stock_item && item.actual_qty !== undefined) {
              if (item.actual_qty <= 0) {
                vm.eventBus.emit("show_message", {
                  text: vm.__("Warning: Item '{0}' is out of stock!", [item.item_name]),
                  color: "error"
                });
              } else if (item.actual_qty <= 3) {
                vm.eventBus.emit("show_message", {
                  text: vm.__("Warning: Item '{0}' has low stock (only {1} left)!", [item.item_name, item.actual_qty]),
                  color: "warning"
                });
              }
            }
            
            if (data.item_uoms && Array.isArray(data.item_uoms)) {
              item.item_uoms = data.item_uoms;
            } else {
              item.item_uoms = [{
                uom: item.stock_uom || item.uom,
                conversion_factor: 1
              }];
            }
            
            vm.calc_item_price(item);
            vm.evaluatePromotions();
          }
        },
        error: function(r) {
          console.error('Error updating item detail:', r);
        }
      });
    },

    fetch_customer_details() {
      var vm = this;
      if (this.customer) {
        frappe.call({
          method: "highspeed_pos.highspeed_pos.api.hsposapp.get_customer_info",
          args: {
            customer: vm.customer,
          },
          async: false,
          callback: (r) => {
            const message = r.message;
            if (!r.exc) {
              vm.customer_info = {
                ...message,
              };
            }
            vm.update_price_list();
          },
        });
      }
    },

    get_price_list() {
      let price_list = this.pos_profile.selling_price_list;
      if (this.customer_info && this.pos_profile) {
        const { customer_price_list, customer_group_price_list } = this.customer_info;
        const pos_price_list = this.pos_profile.selling_price_list;
        if (customer_price_list && customer_price_list != pos_price_list) {
          price_list = customer_price_list;
        } else if (customer_group_price_list && customer_group_price_list != pos_price_list) {
          price_list = customer_group_price_list;
        }
      }
      return price_list;
    },

    update_price_list() {
      let price_list = this.get_price_list();
      if (price_list == this.pos_profile.selling_price_list) {
        price_list = null;
      }
      this.eventBus.emit("update_customer_price_list", price_list);
    },

    update_discount_umount() {
      const value = parseFloat(this.additional_discount_percentage) || 0;
      if (value >= -100 && value <= 100) {
        this.discount_amount = (this.Total * value) / 100;
      } else {
        this.additional_discount_percentage = 0;
        this.discount_amount = 0;
      }
    },

    calc_item_price(item) {
      if (!item.hspos_offer_applied) {
        if (item.price_list_rate) {
          item.rate = item.price_list_rate;
        }
      }
      if (item.discount_percentage) {
        item.rate =
          parseFloat(item.price_list_rate) -
          (parseFloat(item.price_list_rate) * parseFloat(item.discount_percentage)) / 100;
        item.discount_amount = this.flt(
          parseFloat(item.price_list_rate) - parseFloat(item.rate),
          this.currency_precision
        );
      } else if (item.discount_amount) {
        item.rate = this.flt(
          parseFloat(item.price_list_rate) - parseFloat(item.discount_amount),
          this.currency_precision
        );
      }
    },

    calc_uom(item, value) {
      if (!item.item_uoms || item.item_uoms.length === 0) {
        console.warn('No UOMs available for item:', item.item_code);
        return;
      }
      
      const new_uom = item.item_uoms.find((element) => element.uom == value);
      if (!new_uom) {
        console.warn('UOM not found:', value);
        return;
      }
      
      item.conversion_factor = new_uom.conversion_factor;
      if (!item.hspos_offer_applied) {
        item.discount_amount = 0;
        item.discount_percentage = 0;
      }
      this.update_item_detail(item);
    },

    calc_stock_qty(item, value) {
      item.stock_qty = item.conversion_factor * value;
    },

    set_serial_no(item) {
      if (!item.has_serial_no) return;
      item.serial_no = "";
      item.serial_no_selected.forEach((element) => {
        item.serial_no += element + "\n";
      });
      item.serial_no_selected_count = item.serial_no_selected.length;
      if (item.serial_no_selected_count != Math.abs(item.stock_qty)) {
        item.qty = this.invoice_doc.is_return ? -item.serial_no_selected_count : item.serial_no_selected_count;
        this.calc_stock_qty(item, item.qty);
        this.$forceUpdate();
      }
    },

    set_batch_qty(item, value, update = true) {
      const existing_items = this.items.filter(
        (element) =>
          element.item_code == item.item_code &&
          element.hspos_row_id != item.hspos_row_id
      );
      const used_batches = {};
      item.batch_no_data.forEach((batch) => {
        used_batches[batch.batch_no] = {
          ...batch,
          used_qty: 0,
          remaining_qty: batch.batch_qty,
        };
        existing_items.forEach((element) => {
          if (element.batch_no && element.batch_no == batch.batch_no) {
            used_batches[batch.batch_no].used_qty += Math.abs(element.qty);
            used_batches[batch.batch_no].remaining_qty -= Math.abs(element.qty);
            used_batches[batch.batch_no].batch_qty -= Math.abs(element.qty);
          }
        });
      });

      const batch_no_data = Object.values(used_batches)
        .filter((batch) => batch.remaining_qty > 0)
        .sort((a, b) => {
          if (a.expiry_date && b.expiry_date) {
            return a.expiry_date - b.expiry_date;
          } else if (a.expiry_date) {
            return -1;
          } else if (b.expiry_date) {
            return 1;
          } else {
            return b.remaining_qty - a.remaining_qty;
          }
        });

      if (batch_no_data.length > 0) {
        let batch_to_use = null;
        if (value) {
          batch_to_use = batch_no_data.find((batch) => batch.batch_no == value);
        }
        if (!batch_to_use) {
          batch_to_use = batch_no_data[0];
        }
        item.batch_no = batch_to_use.batch_no;
        item.actual_batch_qty = batch_to_use.batch_qty;
        item.batch_no_expiry_date = batch_to_use.expiry_date;
        
        // Expiry check
        if (item.batch_no_expiry_date) {
          const today = new Date();
          const expiry = new Date(item.batch_no_expiry_date);
          const timeDiff = expiry.getTime() - today.getTime();
          const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
          if (daysDiff <= 30) {
            this.eventBus.emit("show_message", {
              text: this.__("Warning: Selected batch '{0}' for item '{1}' expires in {2} days (on {3})!", [
                item.batch_no,
                item.item_name,
                daysDiff,
                item.batch_no_expiry_date
              ]),
              color: "error"
            });
          }
        }
        
        if (update) {
          this.update_item_detail(item);
        }
      } else {
        item.batch_no = null;
        item.actual_batch_qty = null;
        item.batch_no_expiry_date = null;
      }
      item.batch_no_data = batch_no_data;
    },

    validate_due_date(item) {
      const today = frappe.datetime.now_date();
      const parse_today = Date.parse(today);
      const new_date = Date.parse(item.hspos_delivery_date);
      if (new_date < parse_today) {
        setTimeout(() => {
          item.hspos_delivery_date = today;
        }, 0);
      }
    },

    update_hspos_delivery_charges() {
      if (this.selected_delivery_charge) {
        this.hspos_delivery_charges_rate = this.selected_delivery_charge.rate;
      } else {
        this.hspos_delivery_charges_rate = 0;
      }
    },

    set_hspos_delivery_charges() {
      var vm = this;
      if (!this.pos_profile || !this.customer || !this.pos_profile.hspos_use_hspos_delivery_charges) {
        this.hspos_delivery_charges = [];
        this.hspos_delivery_charges_rate = 0;
        this.selected_delivery_charge = "";
        return;
      }
      this.hspos_delivery_charges_rate = 0;
      this.selected_delivery_charge = "";
      frappe.call({
        method: "highspeed_pos.highspeed_pos.api.hsposapp.get_applicable_hspos_delivery_charges",
        args: {
          company: this.pos_profile.company,
          pos_profile: this.pos_profile.name,
          customer: this.customer,
        },
        async: false,
        callback: function (r) {
          if (r.message) {
            if (r.message?.length) {
              vm.hspos_delivery_charges = r.message;
            }
          }
        },
      });
    },

    print_draft_invoice() {
      if (!this.pos_profile.hspos_allow_print_draft_invoices) {
        this.eventBus.emit("show_message", {
          title: this.__("You are not allowed to print draft invoices"),
          color: "error",
        });
        return;
      }
      let invoice_name = this.invoice_doc.name;
      frappe.run_serially([
        () => {
          const invoice_doc = this.save_and_clear_invoice();
          invoice_name = invoice_doc.name ? invoice_doc.name : invoice_name;
        },
        () => {
          this.load_print_page(invoice_name);
        },
      ]);
    },

    load_print_page(invoice_name) {
      const print_format = this.pos_profile.print_format_for_online || this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url = frappe.urllib.get_base_url() + 
        "/printview?doctype=Sales%20Invoice&name=" + invoice_name + 
        "&trigger_print=1&format=" + print_format + 
        "&no_letterhead=" + letter_head;
      const printWindow = window.open(url, "Print");
      printWindow.addEventListener("load", function () {
        printWindow.print();
      }, true);
    },

    makeid(length) {
      let result = "";
      const characters = "abcdefghijklmnopqrstuvwxyz0123456789";
      const charactersLength = characters.length;
      for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
      }
      return result;
    },

    isNumber(value) {
      return !isNaN(parseFloat(value)) && isFinite(value);
    },

    setFormatedFloat(target, field, precision, allowNegative, value) {
      if (typeof target === 'object') {
        target[field] = parseFloat(value).toFixed(precision || this.float_precision);
      } else {
        this[target] = parseFloat(value).toFixed(precision || this.currency_precision);
      }
    },

    setFormatedCurrency(target, field, precision, allowNegative, value) {
      if (typeof target === 'object') {
        target[field] = parseFloat(value).toFixed(precision || this.currency_precision);
      } else {
        this[target] = parseFloat(value).toFixed(precision || this.currency_precision);
      }
    },

    async processReturn() {
      if (!this.validate()) {
        return;
      }
      
      const doc = this.get_invoice_doc();
      
      try {
        const result = await frappe.call({
          method: "highspeed_pos.highspeed_pos.api.hsposapp.submit_return_invoice",
          args: {
            invoice: doc,
          },
        });
        
        if (result.message) {
          this.eventBus.emit("show_message", {
            title: this.__("Return processed successfully"),
            color: "success",
          });
          
          if (this.pos_profile.hspos_auto_print_return) {
            this.load_print_page(result.message.name);
          }
          
          this.clear_invoice();
          return result.message;
        }
      } catch (error) {
        this.eventBus.emit("show_message", {
          title: this.__("Error processing return: {0}", [error.message]),
          color: "error",
        });
      }
    },
  },

  mounted() {
    this.detectRTL();
    
    window.addEventListener('keydown', this.handleKeyboardShortcuts);
    
    this.eventBus.on("register_pos_profile", (data) => {
      if (data.pos_profile) this.pos_profile = data.pos_profile;
      if (data.pos_profile && data.pos_profile.customer) this.customer = data.pos_profile.customer;
      if (data.hspos_opening_shift !== undefined) this.hspos_opening_shift = data.hspos_opening_shift;
      if (data.stock_settings !== undefined) this.stock_settings = data.stock_settings;
      this.float_precision = frappe.defaults.get_default("float_precision") || 2;
      this.currency_precision = frappe.defaults.get_default("currency_precision") || 2;
      this.invoiceType = this.pos_profile.hspos_default_sales_order ? "Order" : "Invoice";
      this.order_type = this.getDefaultOrderType();
    });

    this.eventBus.on("update_order_type", (type) => {
      this.order_type = type;
    });

    this.eventBus.on("set_invoice_table", (table) => {
      this.selected_table = table || "";
    });

    this.eventBus.on("set_offers", (offers) => {
      this.all_offers = offers;
      this.applyAutomaticOffers();
    });

    this.eventBus.on("update_invoice_offers", (appliedOffers) => {
      this.applied_offers = appliedOffers;
      this.applyOffersToCart();
    });

    this.eventBus.on("add_item", (item) => {
      this.add_item(item);
    });

    this.eventBus.on("update_customer", (customer) => {
      this.customer = customer;
    });

    this.eventBus.on("fetch_customer_details", () => {
      this.fetch_customer_details();
    });

    this.eventBus.on("clear_invoice", () => {
      this.clear_invoice();
    });

    this.eventBus.on("load_invoice", (data) => {
      this.load_invoice(data);
    });

    this.eventBus.on("load_order", (data) => {
      this.load_invoice(data);
    });

    this.eventBus.on("load_return_invoice", (data) => {
      this.clear_invoice();
      
      if (data.invoice_doc) {
        this.invoice_doc = data.invoice_doc;
        this.invoiceType = "Return";
        this.invoiceTypes = ["Return"];
        
        if (data.return_doc && data.return_doc.name) {
          this.eventBus.emit("set_customer_readonly", true);
          
          this.invoice_doc.return_against = data.return_doc.name;
          this.invoice_doc.customer = data.return_doc.customer;
          this.customer = data.return_doc.customer;
          this.return_doc = data.return_doc;
          
          const return_items = [];
          if (data.return_doc.items && data.return_doc.items.length > 0) {
            data.return_doc.items.forEach((item) => {
              const return_item = {
                ...item,
                sales_invoice_item: item.name,
                qty: -Math.abs(item.qty),
                stock_qty: -Math.abs(item.stock_qty),
                amount: -Math.abs(item.amount),
                hspos_row_id: this.makeid(20)
              };
              delete return_item.name;
              return_items.push(return_item);
            });
          }
          
          this.items = return_items;
          
          this.discount_amount = -Math.abs(data.return_doc.discount_amount || 0);
          this.additional_discount_percentage = data.return_doc.additional_discount_percentage || 0;
          
        } else {
          this.eventBus.emit("set_customer_readonly", false);
          this.items = [];
          this.discount_amount = 0;
          this.additional_discount_percentage = 0;
        }
        
        this.posting_date = this.invoice_doc.posting_date || frappe.datetime.nowdate();
        
        if (this.items.length > 0) {
          this.update_items_details(this.items);
        }
        
      }
    });

    this.eventBus.on("set_new_line", (data) => {
      this.new_line = data;
    });

    this.eventBus.on("set_all_items", (data) => {
      this.allItems = data;
      this.items.forEach((item) => {
        this.update_item_detail(item);
      });
    });
  },

  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeyboardShortcuts);
    
    this.eventBus.off("register_pos_profile");
    this.eventBus.off("add_item");
    this.eventBus.off("update_customer");
    this.eventBus.off("fetch_customer_details");
    this.eventBus.off("clear_invoice");
    this.eventBus.off("load_invoice");
    this.eventBus.off("load_order");
    this.eventBus.off("load_return_invoice");
    this.eventBus.off("set_new_line");
    this.eventBus.off("set_all_items");
    this.eventBus.off("update_order_type");
    this.eventBus.off("set_invoice_table");
  },

  watch: {
    customer() {
      this.close_payments();
      this.eventBus.emit("set_customer", this.customer);
      this.fetch_customer_details();
      this.set_hspos_delivery_charges();
    },

    customer_info() {
      this.eventBus.emit("set_customer_info_to_edit", this.customer_info);
    },

    items: {
      deep: true,
      immediate: true,
      handler(items) {
        this.$forceUpdate();
        this.eventBus.emit("cart_items_updated", items);
      },
    },

    invoiceType() {
      this.eventBus.emit("update_invoice_type", this.invoiceType);
    },

    discount_amount() {
      if (!this.discount_amount || this.discount_amount == 0) {
        this.additional_discount_percentage = 0;
      } else if (this.pos_profile.hspos_use_percentage_discount) {
        this.additional_discount_percentage = (this.discount_amount / this.Total) * 100;
      } else {
        this.additional_discount_percentage = 0;
      }
    },
  },
};
</script>

<style scoped>
/* Styles remain the same as in the original file */
.invoice-container {
  height: 100%;
  width: 100%;
  background: #f4f5f7;
}

.invoice-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 4px !important;
  overflow: hidden;
}

.invoice-card.return-mode {
  border: 2px solid #ff5252 !important;
  position: relative;
}

.invoice-card.return-mode::before {
  content: 'RETURN';
  position: absolute;
  top: 0;
  right: 0;
  background-color: #ff5252;
  color: white;
  padding: 4px 12px;
  font-weight: bold;
  border-bottom-left-radius: 8px;
  z-index: 10;
  font-size: 0.75rem;
}

[dir="rtl"] .invoice-card.return-mode::before {
  right: auto;
  left: 0;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 8px;
}

.header-section {
  background: white;
  border-bottom: 2px solid #e9ecef;
  flex-shrink: 0;
  padding: 8px 0;
}

.items-section {
  flex: 1;
  overflow: hidden;
  background: #f8f9fa;
  padding: 4px;
  position: relative;
}

.empty-cart {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f4f8;
  padding: 20px;
  overflow: hidden;
}

.empty-cart::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 500px;
  height: 500px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'%3E%3Cpath d='M1 1H5L7.68 14.39C7.77144 14.8504 8.02191 15.264 8.38755 15.5583C8.75318 15.8526 9.2107 16.009 9.68 16H19.4C19.8693 16.009 20.3268 15.8526 20.6925 15.5583C21.0581 15.264 21.3086 14.8504 21.4 14.39L23 6H6M9 21C9 21.5523 8.55228 22 8 22C7.44772 22 7 21.5523 7 21C7 20.4477 7.44772 20 8 20C8.55228 20 9 20.4477 9 21ZM20 21C20 21.5523 19.5523 22 19 22C18.4477 22 18 21.5523 18 21C18 20.4477 18.4477 20 19 20C19.5523 20 20 20.4477 20 21Z' stroke='%23e2e8f0' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
  opacity: 0.15;
  animation: cartMove 20s ease-in-out infinite;
  pointer-events: none;
}

@keyframes cartMove {
  0%, 100% {
    transform: translate(-50%, -50%) rotate(0deg) scale(1);
  }
  25% {
    transform: translate(-45%, -55%) rotate(5deg) scale(1.05);
  }
  50% {
    transform: translate(-55%, -50%) rotate(-5deg) scale(0.95);
  }
  75% {
    transform: translate(-50%, -45%) rotate(3deg) scale(1.02);
  }
}

.empty-cart-content {
  text-align: center;
  max-width: 400px;
  width: 100%;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 4px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transform: translateY(-20px);
  animation: fadeInUp 0.6s ease-out;
  position: relative;
  z-index: 1;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(0);
  }
  to {
    opacity: 1;
    transform: translateY(-20px);
  }
}

.empty-cart-icon {
  width: 120px;
  height: 120px;
  margin: 0 auto 24px;
  color: #3b82f6;
  animation: float 3s ease-in-out infinite;
  position: relative;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.empty-cart-icon svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 4px 6px rgba(59, 130, 246, 0.2));
}

.empty-cart-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #334155;
  margin-bottom: 12px;
  letter-spacing: -0.025em;
}

.empty-cart-subtitle {
  font-size: 1rem;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

[dir="rtl"] .empty-cart-title,
[dir="rtl"] .empty-cart-subtitle {
  font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
}

.items-list {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 2px;
}

.item-card {
  background: white;
  border: 1px solid #e4e7eb;
  border-radius: 4px;
  margin-bottom: 4px;
  transition: all 0.2s ease;
  overflow: hidden;
}

.item-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.item-content {
  padding: 8px 10px;
  background: #fffbee;
}

.item-header-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
  cursor: pointer;
}

.item-title-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.item-title {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
}

[dir="ltr"] .item-title {
  text-align: left;
}

[dir="rtl"] .item-title {
  flex-direction: row-reverse;
  text-align: right;
}

.addons-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
  margin-top: 2px;
  line-height: 1.2;
}

[dir="rtl"] .addons-subtitle {
  text-align: right;
}

[dir="ltr"] .addons-subtitle {
  text-align: left;
}

.item-code {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 400;
  flex-shrink: 0;
}

.separator {
  color: #e2e8f0;
  font-size: 0.8rem;
  flex-shrink: 0;
  margin: 0 6px;
}

.item-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.offer-chip {
  height: 18px !important;
  font-size: 0.65rem !important;
  padding: 0 6px !important;
}

.item-data-line {
  display: flex;
  align-items: center;
  gap: 12px;
}

.data-group {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 4px 8px;
  min-height: 28px;
}

.qty-group {
  padding: 2px;
  gap: 2px;
  background: white;
}

.qty-btn {
  width: 24px !important;
  height: 24px !important;
  min-width: 24px !important;
  background: #f1f5f9 !important;
  border-radius: 3px !important;
}

.qty-btn:hover {
  background: #e2e8f0 !important;
}

.qty-btn :deep(.v-icon) {
  font-size: 0.75rem !important;
  color: #475569;
}

.qty-input {
  width: 45px;
  text-align: center;
  border: none;
  background: transparent;
  font-size: 0.875rem;
  font-weight: 600;
  color: #0ea5e9;
  outline: none;
  padding: 0 4px;
  -moz-appearance: textfield;
}

.qty-input::-webkit-outer-spin-button,
.qty-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.qty-input:focus {
  background: #f0f9ff;
  border-radius: 2px;
}

.uom-group {
  width: 10%;
  justify-content: center;
  padding: 0;
}

.uom-select {
  width: 100%;
  font-size: 0.75rem;
}

.uom-select :deep(.v-field__input) {
  padding: 0 !important;
  min-height: 0 !important;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
  text-align: center;
}

.uom-select :deep(.v-field__append-inner) {
  padding: 0 !important;
}

.uom-select :deep(.v-field) {
  min-height: 0 !important;
}

.uom-select :deep(.v-select__selection) {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.uom-select :deep(.v-icon) {
  font-size: 0.875rem !important;
  margin-left: 2px;
}

[dir="rtl"] .uom-select :deep(.v-icon) {
  margin-left: 0;
  margin-right: 2px;
}

.data-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.price-group {
  flex: 1;
  padding: 0;
  background: white;
  width: 20%;
}

.price-input {
  width: 100%;
  text-align: center;
  border: none;
  background: transparent;
  padding: 4px 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #059669;
  outline: none;
  -moz-appearance: textfield;
  font-feature-settings: "tnum";
  direction: ltr;
  unicode-bidi: embed;
}

.price-input::-webkit-outer-spin-button,
.price-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.price-input:focus {
  background: #f0fdf4;
  border-radius: 3px;
}

.price-input:disabled {
  background: #f8fafc;
  color: #94a3b8;
  cursor: not-allowed;
}

.total-group {
  width: 20%;
  justify-content: flex-end;
  background: #eff6ff;
  border-color: #dbeafe;
}

.total-value {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1e40af;
}

.action-group {
  display: flex;
  align-items: center;
  width: auto;
  min-width: 32px;
}

.delete-btn {
  width: 28px !important;
  height: 28px !important;
  min-width: 28px !important;
}

.delete-btn :deep(.v-icon) {
  font-size: 0.85rem !important;
}

/* RTL Support */
[dir="rtl"] .item-title {
  flex-direction: row-reverse;
}

[dir="rtl"] .item-header-line {
  flex-direction: row-reverse;
}

[dir="rtl"] .item-data-line {
  flex-direction: row-reverse;
}

[dir="rtl"] .qty-group {
  flex-direction: row-reverse;
}

[dir="rtl"] .price-input {
  direction: ltr;
  text-align: center;
}

[dir="rtl"] .total-group {
  justify-content: flex-start;
}

[dir="rtl"] .data-group {
  direction: rtl;
}

/* Item Details Section */
.item-details {
  padding: 8px 12px;
  background: #f0f4f8;
  border-top: 1px solid #e0e0e0;
}

.detail-field {
  margin-bottom: 8px;
}

.detail-field label {
  display: block;
  font-size: 0.8rem;
  color: #6c757d;
  margin-bottom: 4px;
  font-weight: 500;
}

.compact-input {
  width: 100%;
}

.compact-input :deep(.v-field) {
  min-height: 36px !important;
}

.compact-input :deep(.v-field__input) {
  padding: 0 12px !important;
  font-size: 0.9rem;
}

.item-stats {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e9ecef;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.75rem;
  color: #6c757d;
  margin-bottom: 2px;
}

.stat-value {
  font-weight: 600;
  color: #495057;
}

/* Footer Section */
.footer-section {
  background: white;
  border-top: 2px solid #e9ecef;
  flex-shrink: 0;
}

.totals-container {
  display: flex;
  justify-content: space-between;
  padding: 4px 10px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  background: linear-gradient(135deg, #f8fafd 0%, #f1f5f9 100%);
}

.total-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0px;
}

.total-item .total-label {
  font-size: 0.7rem;
  color: #718096;
  font-family: 'Cairo', sans-serif !important;
  font-weight: 600;
}

.total-item .total-value {
  font-weight: 700;
  font-size: 0.82rem;
  color: #2d3748;
}

.total-final .total-value {
  font-size: 0.95rem;
  color: #0097A7;
  font-weight: 800;
}

.action-buttons {
  padding: 3px;
}

.secondary-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 3px;
  margin-bottom: 3px;
}

.action-btn {
  font-size: 0.7rem !important;
  text-transform: none !important;
  padding: 0 6px !important;
  height: 25px !important;
  position: relative;
  border-radius: 6px !important;
}

.action-btn :deep(.v-icon) {
  font-size: 0.8rem !important;
}

.btn-text {
  display: flex;
  align-items: center;
  gap: 4px;
}

.shortcut-key {
  font-size: 0.65rem;
  background: rgba(0, 0, 0, 0.1);
  padding: 1px 4px;
  border-radius: 3px;
  margin-left: 4px;
  font-weight: 600;
  opacity: 0.8;
}

[dir="rtl"] .shortcut-key {
  margin-left: 0;
  margin-right: 4px;
}

.pay-btn {
  width: 100%;
  height: 32px !important;
  font-size: 0.9rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  border-radius: 4px !important;
  background: linear-gradient(90deg, #66BB6A 0%, #43A047 100%) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.25) !important;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}

.pay-btn:hover {
  box-shadow: 0 6px 15px rgba(76, 175, 80, 0.35) !important;
  transform: translateY(-1px);
}

.pay-btn :deep(.v-icon) {
  font-size: 1.05rem !important;
}

.pay-shortcut {
  background: rgba(255, 255, 255, 0.2);
  font-size: 0.75rem;
  margin-left: 8px;
}

[dir="rtl"] .pay-shortcut {
  margin-left: 0;
  margin-right: 8px;
}

/* Scrollbar Styles */
.items-list::-webkit-scrollbar {
  width: 6px;
}

.items-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.items-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.items-list::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* Animations */
.v-enter-active,
.v-leave-active {
  transition: all 0.3s ease;
}

.v-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.v-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.item-card {
  animation: fadeIn 0.3s ease;
}

/* Form Fields */
.type-select,
.delivery-select,
.rate-field,
.date-field {
  font-size: 0.85rem;
}

.type-select :deep(.v-field),
.delivery-select :deep(.v-field),
.rate-field :deep(.v-field),
.date-field :deep(.v-field) {
  min-height: 36px !important;
}

.type-select :deep(.v-field__input),
.delivery-select :deep(.v-field__input),
.rate-field :deep(.v-field__input),
.date-field :deep(.v-field__input) {
  padding: 0 12px !important;
  font-size: 0.85rem;
}

/* Utility Classes */
input[type="number"] {
  -moz-appearance: textfield;
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.invoice-container.loading {
  opacity: 0.6;
  pointer-events: none;
}

.invoice-card {
  transition: all 0.3s ease;
}

.action-btn,
.pay-btn {
  transition: all 0.2s ease;
}

.action-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.pay-btn:active {
  transform: scale(0.98);
}

/* Media Queries */
@media (max-width: 1200px) {
  .secondary-actions {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .item-card {
    margin-bottom: 6px;
  }
  

  
  .item-data-line {
    gap: 6px !important;
  }
  
  .data-group {
    padding: 2px 4px !important;
    min-height: 24px !important;
  }
}

@media (max-width: 768px) {
  .secondary-actions {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .totals-container {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .total-item {
    flex: 1;
    min-width: 80px;
  }
  
  .item-name {
    font-size: 0.85rem;
  }
  
  .item-code {
    font-size: 0.75rem;
  }
  
  .qty-btn {
    width: 24px !important;
    height: 24px !important;
  }
  
  .delete-btn {
    width: 24px !important;
    height: 24px !important;
  }
  
  .item-data-line {
    gap: 8px;
  }
  
  .data-group {
    padding: 3px 6px;
    min-height: 26px;
  }
  
  .qty-input {
    width: 40px;
  }
  
  .price-group {
    min-width: 70px;
  }
  
  .total-group {
    min-width: 80px;
  }
  
  .empty-cart-content {
    padding: 30px 20px;
  }
  
  .empty-cart-icon {
    width: 80px;
    height: 80px;
  }
  
  .empty-cart-title {
    font-size: 1.5rem;
  }
  
  .empty-cart-subtitle {
    font-size: 0.875rem;
  }
}

/* Accessibility */
.item-header:focus-visible,
.qty-btn:focus-visible,
.delete-btn:focus-visible,
.action-btn:focus-visible,
.pay-btn:focus-visible {
  outline: 2px solid #1976d2;
  outline-offset: 2px;
}

/* Print Styles */
@media print {
  .action-buttons,
  .qty-controls,
  .delete-btn {
    display: none !important;
  }
  
  .item-card {
    break-inside: avoid;
    page-break-inside: avoid;
  }
}

/* Backdrop Filter Support */
@supports (backdrop-filter: blur(10px)) {
  .item-details {
    backdrop-filter: blur(5px);
    background: rgba(248, 249, 250, 0.9);
  }
  
  .empty-cart-content {
    backdrop-filter: blur(20px);
  }
}



/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Premium Visual Styling for Product Add-ons & Modifiers */
.addon-item-card {
  margin-top: -3px;
  border-top: none;
  border-bottom: 1px dashed #e2e8f0;
  border-radius: 0 !important;
}

[dir="ltr"] .addon-item-card {
  border-left: 4px solid var(--v-theme-primary, #6200ee) !important;
  border-right: 1px solid #e4e7eb !important;
}
[dir="ltr"] .addon-item-card .item-content {
  padding-left: 24px !important;
}

[dir="rtl"] .addon-item-card {
  border-right: 4px solid var(--v-theme-primary, #6200ee) !important;
  border-left: 1px solid #e4e7eb !important;
}
[dir="rtl"] .addon-item-card .item-content {
  padding-right: 24px !important;
}

.addon-item-card .item-content {
  background: #f8fafc !important;
}

.addon-item-card .item-name {
  font-size: 0.8rem !important;
  color: #64748b !important;
  font-weight: 500 !important;
}

.addon-item-card .item-code {
  font-size: 0.7rem !important;
  color: #cbd5e1 !important;
}

.addon-item-card .price-input, 
.addon-item-card .qty-input,
.addon-item-card .uom-select {
  color: #64748b !important;
}
</style>