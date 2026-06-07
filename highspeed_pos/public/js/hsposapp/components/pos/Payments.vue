<!-- File Path: highspeed_pos/highspeed_pos/public/js/hsposapp/components/pos/Payments.vue -->
<template>
 <v-dialog v-model="paymentDialog" max-width="600px" persistent>
   <v-card class="elevation-0" :dir="isRTL ? 'rtl' : 'ltr'">
     <v-toolbar dense flat color="primary" dark>
       <v-toolbar-title class="text-body-1">
         <v-icon small class="me-2">mdi-cash-multiple</v-icon>
         {{ __('Payment') }}
       </v-toolbar-title>
       <v-spacer></v-spacer>
     </v-toolbar>

     <v-progress-linear 
       :active="loading" 
       :indeterminate="loading" 
       absolute 
       location="top"
       color="info">
     </v-progress-linear>

      <v-card-text class="pa-2" style="max-height: 70vh; overflow-y: auto;">
        <v-container fluid class="pa-0">
          <v-row dense v-if="invoice_doc">
            <!-- Order Number & Restaurant Selector (Moved to Payment Screen) -->
            <v-col 
              v-if="pos_profile && (pos_profile.hspos_enable_order_number || pos_profile.hspos_allow_dine_in || pos_profile.hspos_allow_takeaway || pos_profile.hspos_allow_delivery)" 
              cols="12" 
              class="mb-2 px-1"
            >
              <v-card outlined class="pa-2 border-light elevation-0 bg-light-gray">
                <v-row dense class="align-center">
                  <!-- Order Number Box -->
                  <v-col
                    v-if="pos_profile.hspos_enable_order_number"
                    cols="12"
                    sm="4"
                    class="d-flex"
                  >
                    <div class="order-number-display">
                      <v-icon size="16" class="me-1">mdi-pound</v-icon>
                      <span>{{ __("Order") }} #{{ pos_profile.hspos_next_order_number || 1 }}</span>
                    </div>
                  </v-col>

                  <!-- Restaurant Order Type Toggle -->
                  <v-col
                    v-if="pos_profile.hspos_allow_dine_in || pos_profile.hspos_allow_takeaway || pos_profile.hspos_allow_delivery"
                    cols="12"
                    :sm="pos_profile.hspos_enable_order_number ? 8 : 12"
                    class="d-flex"
                  >
                    <v-btn-toggle
                      v-model="invoice_doc.hspos_order_type"
                      mandatory
                      density="compact"
                      color="primary"
                      variant="outlined"
                      class="order-type-toggle w-100"
                      style="height: 38px;"
                    >
                      <v-btn
                        v-if="pos_profile.hspos_allow_dine_in"
                        value="Dine-in"
                        class="flex-grow-1"
                        size="small"
                        style="height: 38px; min-width: 0;"
                      >
                        <v-icon size="small" class="me-1">mdi-table-chair</v-icon>
                        <span>{{ __("Dine-in") }}<span v-if="invoice_doc.hspos_table"> ({{ invoice_doc.hspos_table }})</span></span>
                      </v-btn>
                      
                      <v-btn
                        v-if="pos_profile.hspos_allow_takeaway"
                        value="Takeaway"
                        :disabled="!!invoice_doc.hspos_table"
                        class="flex-grow-1"
                        size="small"
                        style="height: 38px; min-width: 0;"
                      >
                        <v-icon size="small" class="me-1">mdi-shopping</v-icon>
                        <span>{{ __("Takeaway") }}</span>
                      </v-btn>
                      
                      <v-btn
                        v-if="pos_profile.hspos_allow_delivery"
                        value="Delivery"
                        :disabled="!!invoice_doc.hspos_table"
                        class="flex-grow-1"
                        size="small"
                        style="height: 38px; min-width: 0;"
                      >
                        <v-icon size="small" class="me-1">mdi-truck-delivery</v-icon>
                        <span>{{ __("Delivery") }}</span>
                      </v-btn>
                    </v-btn-toggle>
                  </v-col>
                </v-row>
              </v-card>
            </v-col>

            <v-col cols="12" sm="7" class="pe-1">
             <v-card flat outlined class="pa-2">
               <div class="text-caption font-weight-medium mb-1">
                 {{ __('Payment Methods') }}
               </div>

               <div>
                 <v-row 
                   dense
                   class="mb-2 align-center" 
                   v-for="payment in invoice_doc.payments" 
                   :key="payment.name">
                   <v-col :cols="is_mpesa_c2b_payment(payment) ? 12 : (!is_mpesa_c2b_payment(payment) && (payment.type != 'Phone' || payment.amount == 0 || !request_payment_field)) ? 7 : 5">
                     <input 
                       v-if="!is_mpesa_c2b_payment(payment)"
                       class="price-input"
                       :value="payment.amount"
                       @input="handlePaymentInput(payment, $event)"
                       @blur="validatePaymentAmounts"
                       :readonly="invoice_doc.is_return && is_cashback ? true : false"
                       type="text"
                       inputmode="decimal"
                       @focus="set_rest_amount(payment.idx)">
                     <v-btn 
                       v-if="is_mpesa_c2b_payment(payment)"
                       block 
                       small
                       color="success" 
                       @click="mpesa_c2b_dialg(payment)">
                       {{ __(`Get Payments ${payment.mode_of_payment}`) }}
                     </v-btn>
                   </v-col>
                   <v-col 
                     v-if="!is_mpesa_c2b_payment(payment) && (payment.type != 'Phone' || payment.amount == 0 || !request_payment_field)" 
                     :cols="5">
                     <v-btn 
                       block 
                       small
                       class="payment-method-btn"
                       @click="handlePaymentMethodButtonClick(payment.idx)">
                       {{ payment.mode_of_payment }}
                     </v-btn>
                   </v-col>
                   <v-col 
                     v-if="payment.type == 'Phone' && payment.amount > 0 && request_payment_field && !is_mpesa_c2b_payment(payment)" 
                     :cols="2">
                     <v-btn 
                       block 
                       small
                       color="success" 
                       :disabled="payment.amount == 0" 
                       @click="(phone_dialog = true), (payment.amount = flt(payment.amount, 0))">
                       {{ __("Request") }}
                     </v-btn>
                   </v-col>
                 </v-row>
               </div>

               <v-row 
                 dense
                 v-if="invoice_doc && available_pioints_amount > 0 && !invoice_doc.is_return"
                 class="mb-1">
                 <v-col cols="7">
                   <v-text-field 
                     dense
                     outlined 
                     :label="frappe._('Redeem Loyalty Points')" 
                     hide-details 
                     v-model="loyalty_amount"
                     type="text" 
                     inputmode="decimal"
                     @input="loyalty_amount = convertArabicToLatin($event.target.value).replace(/[^0-9.]/g, '')"
                     :prefix="currencySymbol(invoice_doc.currency)">
                   </v-text-field>
                 </v-col>
                 <v-col cols="5">
                   <v-text-field 
                     dense
                     outlined 
                     :label="frappe._('You can redeem upto')"
                     hide-details 
                     :model-value="formatFloat(available_pioints_amount)"
                     type="text"
                     :prefix="currencySymbol(invoice_doc.currency)" 
                     disabled>
                   </v-text-field>
                 </v-col>
               </v-row>

               <v-row 
                 dense
                 v-if="invoice_doc && available_customer_credit > 0 && !invoice_doc.is_return && redeem_customer_credit"
                 class="mb-1">
                 <v-col cols="7">
                   <v-text-field 
                     dense
                     outlined 
                     disabled 
                     :label="frappe._('Redeemed Customer Credit')" 
                     hide-details
                     v-model="redeemed_customer_credit" 
                     type="text"
                     :prefix="currencySymbol(invoice_doc.currency)">
                   </v-text-field>
                 </v-col>
                 <v-col cols="5">
                   <v-text-field 
                     dense
                     outlined 
                     :label="frappe._('You can redeem credit upto')" 
                     hide-details
                     :model-value="formatCurrency(available_customer_credit)" 
                     type="text"
                     :prefix="currencySymbol(invoice_doc.currency)"
                     disabled>
                   </v-text-field>
                 </v-col>
               </v-row>

               <div v-if="invoice_doc && available_customer_credit > 0 && !invoice_doc.is_return && redeem_customer_credit">
                 <v-divider class="my-2"></v-divider>
                 <div class="text-caption font-weight-medium mb-1">
                   {{ __('Customer Credit Details') }}
                 </div>
                 <v-row dense v-for="(row, idx) in customer_credit_dict" :key="idx" class="mb-1">
                   <v-col cols="4">
                     <div class="pa-1 text-caption">{{ row.credit_origin }}</div>
                   </v-col>
                   <v-col cols="4">
                     <v-text-field 
                       dense
                       outlined 
                       :label="frappe._('Available Credit')"
                       hide-details 
                       :model-value="formatCurrency(row.total_credit)" 
                       type="text"
                       disabled
                       :prefix="currencySymbol(invoice_doc.currency)">
                     </v-text-field>
                   </v-col>
                   <v-col cols="4">
                     <v-text-field 
                       dense
                       outlined 
                       :label="frappe._('Redeem Credit')"
                       hide-details 
                       type="text" 
                       inputmode="decimal"
                       @input="row.credit_to_redeem = convertArabicToLatin($event.target.value).replace(/[^0-9.]/g, '')"
                       v-model="row.credit_to_redeem"
                       :prefix="currencySymbol(invoice_doc.currency)">
                     </v-text-field>
                   </v-col>
                 </v-row>
               </div>

               <v-divider class="my-2"></v-divider>

               <v-row dense>
                 <v-col cols="6" v-if="pos_profile.hspos_allow_write_off_change && diff_payment > 0 && !invoice_doc.is_return">
                   <v-switch 
                     dense
                     v-model="is_write_off_change" 
                     :label="frappe._('Write Off Difference Amount')"
                     hide-details
                     class="mt-0">
                   </v-switch>
                 </v-col>
                 <v-col cols="6" v-if="invoice_doc.is_return && pos_profile.use_cashback">
                   <v-switch 
                     dense
                     v-model="is_cashback" 
                     :label="frappe._('Cashback?')"
                     hide-details
                     class="mt-0"
                     :disabled="original_invoice && original_invoice.is_pos === 0 && !original_invoice.is_return">
                   </v-switch>
                 </v-col>
                 <v-col cols="6" v-if="!invoice_doc.is_return && pos_profile.use_customer_credit">
                   <v-switch 
                     dense
                     v-model="redeem_customer_credit" 
                     :label="frappe._('Use Customer Credit')"
                     hide-details
                     class="mt-0"
                     @update:model-value="get_available_credit($event)">
                   </v-switch>
                 </v-col>
               </v-row>
             </v-card>
           </v-col>

           <v-col cols="12" sm="5" class="ps-1">
             <v-card flat color="primary" dark class="pa-2">
               <div class="text-caption font-weight-bold mb-2 text-white">
                 {{ __('Invoice Summary') }}
               </div>

               <v-card flat class="pa-2 mb-2">
                 <v-row no-gutters>
                   <v-col cols="12" class="d-flex justify-space-between align-center py-1">
                     <span class="text-caption">{{ __('Net Total') }}</span>
                     <span class="text-caption font-weight-medium">
                       {{ formatCurrency(invoice_doc.net_total) }} {{ currencySymbol(invoice_doc.currency) }}
                     </span>
                   </v-col>
                   <v-divider class="my-1"></v-divider>
                   <v-col cols="12" class="d-flex justify-space-between align-center py-1">
                     <span class="text-caption">{{ __('Tax and Charges') }}</span>
                     <span class="text-caption font-weight-medium">
                       {{ formatCurrency(invoice_doc.total_taxes_and_charges) }} {{ currencySymbol(invoice_doc.currency) }}
                     </span>
                   </v-col>
                   <v-divider class="my-1" v-if="invoice_doc.discount_amount"></v-divider>
                   <v-col cols="12" class="d-flex justify-space-between align-center py-1" v-if="invoice_doc.discount_amount">
                     <span class="text-caption">{{ __('Discount Amount') }}</span>
                     <span class="text-caption font-weight-medium text-success">
                       -{{ formatCurrency(Math.abs(invoice_doc.discount_amount)) }} {{ currencySymbol(invoice_doc.currency) }}
                     </span>
                   </v-col>
                 </v-row>
               </v-card>

               <v-card flat class="pa-2 bg-primary-darken-1">
                 <v-row no-gutters>
                   <v-col cols="12" class="d-flex justify-space-between align-center">
                     <span class="text-body-2 font-weight-bold text-white">{{ __('Grand Total') }}</span>
                     <span class="text-h6 font-weight-bold text-white">
                       {{ formatCurrency(invoice_doc.grand_total) }} {{ currencySymbol(invoice_doc.currency) }}
                     </span>
                   </v-col>
                   <v-col cols="12" class="d-flex justify-space-between align-center mt-1" v-if="invoice_doc.rounded_total">
                     <span class="text-caption text-white-70">{{ __('Rounded Total') }}</span>
                     <span class="text-body-2 font-weight-medium text-white">
                       {{ formatCurrency(invoice_doc.rounded_total) }} {{ currencySymbol(invoice_doc.currency) }}
                     </span>
                   </v-col>
                 </v-row>
               </v-card>

               <v-divider class="my-2"></v-divider>
               
               <v-card flat class="pa-3 payment-summary-card">
                 <div class="text-caption font-weight-bold mb-2 text-center payment-summary-title">
                   {{ __('') }}
                 </div>
                 
                  <v-row dense>
                    <v-col :cols="diff_payment > 0 ? 6 : 12">
                      <v-card flat class="pa-2 text-center payment-amount-card paid-amount-card">
                        <div class="text-caption mb-1">{{ __('Paid Amount') }}</div>
                        <div class="text-h6 font-weight-bold paid-amount-value">
                          {{ formatCurrency(total_payments_display) }}
                        </div>
                        <div class="text-caption">{{ currencySymbol(invoice_doc.currency) }}</div>
                      </v-card>
                    </v-col>
                    
                    <v-col cols="6" v-if="diff_payment > 0">
                      <v-card flat class="pa-2 text-center payment-amount-card remaining-amount-card">
                        <div class="text-caption mb-1">{{ __('Remaining') }}</div>
                        <div class="text-h6 font-weight-bold remaining-amount-value">
                          {{ formatCurrency(diff_payment) }}
                        </div>
                        <div class="text-caption">{{ currencySymbol(invoice_doc.currency) }}</div>
                      </v-card>
                    </v-col>
                  </v-row>
                  
                  <v-row dense v-if="diff_payment < 0 && !invoice_doc.is_return" class="mt-2">
                    <v-col cols="6">
                      <v-card flat class="pa-2 text-center change-display-card">
                        <div class="text-caption mb-1">{{ __('Paid Change') }}</div>
                        <div class="text-h6 font-weight-bold change-value">
                          {{ formatCurrency(paid_change) }}
                        </div>
                        <div class="text-caption">{{ currencySymbol(invoice_doc.currency) }}</div>
                      </v-card>
                    </v-col>
                    <v-col cols="6">
                      <v-card flat class="pa-2 text-center change-display-card credit-change-card">
                        <div class="text-caption mb-1">{{ __('Credit Change') }}</div>
                        <div class="text-h6 font-weight-bold change-value">
                          {{ formatCurrency(credit_change) }}
                        </div>
                        <div class="text-caption">{{ currencySymbol(invoice_doc.currency) }}</div>
                      </v-card>
                    </v-col>
                  </v-row>
               </v-card>

               <v-divider class="my-2"></v-divider>

               <v-row dense v-if="pos_profile.hspos_allow_sales_order && invoiceType == 'Order'">
                 <v-col cols="12">
                   <v-menu 
                     ref="order_delivery_date" 
                     v-model="order_delivery_date" 
                     :close-on-content-click="false"
                     transition="scale-transition">
                     <template v-slot:activator="{ props }">
                       <v-text-field 
                         dense
                         v-model="invoice_doc.hspos_delivery_date" 
                         :label="frappe._('Delivery Date')" 
                         readonly
                         outlined 
                         bg-color="white" 
                         clearable 
                         hide-details
                         v-bind="props"
                         lang="en"
                         prepend-inner-icon="mdi-calendar">
                       </v-text-field>
                     </template>
                     <v-date-picker 
                       :v-model="new Date(invoice_doc.hspos_delivery_date)" 
                       no-title 
                       scrollable 
                       color="primary"
                       :min="frappe.datetime.now_date()" 
                       @input="order_delivery_date = false">
                     </v-date-picker>
                   </v-menu>
                 </v-col>

                 <v-col cols="12" v-if="invoice_doc.hspos_delivery_date" class="mt-2">
                   <v-autocomplete 
                     dense
                     clearable 
                     auto-select-first 
                     outlined 
                     :label="frappe._('Address')" 
                     v-model="invoice_doc.shipping_address_name" 
                     :items="addresses"
                     item-title="address_title" 
                     item-value="name" 
                     bg-color="white" 
                     no-data-text="Address not found"
                     hide-details 
                     :customFilter="addressFilter" 
                     append-icon="mdi-plus" 
                     @click:append="new_address">
                     <template v-slot:item="{ props, item }">
                       <v-list-item v-bind="props">
                         <v-list-item-title class="text-primary text-caption">
                           <div v-html="item.raw.address_title"></div>
                         </v-list-item-title>
                         <v-list-item-title class="text-caption">
                           <div v-html="item.raw.address_line1"></div>
                         </v-list-item-title>
                         <v-list-item-subtitle v-if="item.raw.custoaddress_line2mer_name" class="text-caption">
                           <div v-html="item.raw.address_line2"></div>
                         </v-list-item-subtitle>
                         <v-list-item-subtitle v-if="item.raw.city" class="text-caption">
                           <div v-html="item.raw.city"></div>
                         </v-list-item-subtitle>
                         <v-list-item-subtitle v-if="item.raw.state" class="text-caption">
                           <div v-html="item.raw.state"></div>
                         </v-list-item-subtitle>
                         <v-list-item-subtitle v-if="item.raw.country" class="text-caption">
                           <div v-html="item.raw.mobile_no"></div>
                         </v-list-item-subtitle>
                         <v-list-item-subtitle v-if="item.raw.address_type" class="text-caption">
                           <div v-html="item.raw.address_type"></div>
                         </v-list-item-subtitle>
                       </v-list-item>
                     </template>
                   </v-autocomplete>
                 </v-col>

                 <v-col cols="12" v-if="pos_profile.hspos_display_additional_notes" class="mt-2">
                   <v-textarea 
                     outlined 
                     dense
                     bg-color="white" 
                     clearable 
                     auto-grow 
                     rows="2" 
                     :label="frappe._('Additional Notes')" 
                     v-model="invoice_doc.hspos_notes"
                     :model-value="invoice_doc.hspos_notes">
                   </v-textarea>
                 </v-col>
               </v-row>

               <div v-if="pos_profile.hspos_allow_customer_purchase_order">
                 <v-divider class="my-2"></v-divider>
                 <v-row dense :class="{ 'flex-row-reverse': isRTL }">
                   <v-col cols="6">
                     <v-text-field 
                       dense
                       v-model="invoice_doc.po_no" 
                       :label="frappe._('Purchase Order')" 
                       outlined
                       bg-color="white" 
                       clearable 
                       lang="en"
                       hide-details>
                     </v-text-field>
                   </v-col>
                   <v-col cols="6">
                     <v-menu 
                       ref="po_date_menu" 
                       v-model="po_date_menu" 
                       :close-on-content-click="false"
                       transition="scale-transition">
                       <template v-slot:activator="{ props }">
                         <v-text-field 
                           dense
                           v-model="invoice_doc.po_date" 
                           :label="frappe._('PO Date')" 
                           readonly
                           outlined 
                           hide-details 
                           lang="en"
                           v-bind="props">
                         </v-text-field>
                       </template>
                       <v-date-picker 
                         v-model="invoice_doc.po_date" 
                         no-title 
                         scrollable 
                         color="primary"
                         @input="po_date_menu = false">
                       </v-date-picker>
                     </v-menu>
                   </v-col>
                 </v-row>
               </div>
             </v-card>
           </v-col>
         </v-row>
       </v-container>
     </v-card-text>

     <v-divider></v-divider>

     <v-card-actions class="pa-3">
       <v-btn 
         large
         text
         color="error" 
         @click="back_to_invoice">
         {{ __("Cancel Payment") }}
         <v-chip x-small outlined class="ms-1">F9</v-chip>
       </v-btn>
       <v-spacer></v-spacer>
       <v-btn 
         large
         color="primary" 
         @click="submit" 
         :disabled="vaildatPayment">
         {{ __("Submit") }}
         <v-chip x-small outlined class="ms-1">F10</v-chip>
       </v-btn>
       <v-btn 
         large
         color="success" 
         @click="submit(undefined, false, true)"
         :disabled="vaildatPayment">
         {{ __("Submit & Print") }}
         <v-chip x-small outlined class="ms-1">F12</v-chip>
       </v-btn>
     </v-card-actions>
   </v-card>

   <v-dialog v-model="phone_dialog" max-width="400px">
     <v-card>
       <v-card-title>
         <span class="text-h5 text-primary">{{ __("Confirm Mobile Number") }}</span>
       </v-card-title>
       <v-card-text class="pa-0">
         <v-container>
           <v-text-field 
             dense
             outlined 
             :label="frappe._('Mobile Number')"
             hide-details 
             v-model="invoice_doc.contact_mobile" 
             type="text"
             inputmode="tel"
             @input="invoice_doc.contact_mobile = convertArabicToLatin($event.target.value).replace(/[^0-9]/g, '')">
           </v-text-field>
         </v-container>
       </v-card-text>
       <v-card-actions>
         <v-spacer></v-spacer>
         <v-btn 
           color="error" 
           theme="dark" 
           @click="phone_dialog = false">
           {{ __("Close") }}
         </v-btn>
         <v-btn 
           color="primary" 
           theme="dark" 
           @click="request_payment">
           {{ __("Request") }}
         </v-btn>
       </v-card-actions>
     </v-card>
   </v-dialog>
 </v-dialog>
</template>

<script>

import format from "../../format";
export default {
  mixins: [format],
  data: () => ({
    paymentDialog: false,
    loading: false,
    pos_profile: "",
    invoice_doc: "",
    loyalty_amount: 0,
    credit_sales_due_date: new Date(frappe.datetime.now_date()),
    is_credit_sale: 0,
    is_write_off_change: 0,
    date_menu: false,
    po_date_menu: false,
    addresses: [],
    sales_persons: [],
    sales_person: "",
    paid_change: 0,
    order_delivery_date: false,
    paid_change_rules: [],
    is_return: false,
    is_cashback: false,
    redeem_customer_credit: false,
    customer_credit_dict: [],
    phone_dialog: false,
    invoiceType: "Invoice",
    pos_settings: "",
    customer_info: "",
    mpesa_modes: [],
    original_invoice_payments: null,
    original_invoice: null,
    isRTL: false,
  }),

  methods: {
    detectRTL() {
      const htmlDir = document.documentElement.dir;
      const lang = document.documentElement.lang;
      const bodyDir = document.body.dir;
      this.isRTL = htmlDir === 'rtl' || bodyDir === 'rtl' || ['ar', 'he', 'fa', 'ur'].includes(lang?.substring(0, 2));
    },
    back_to_invoice() {
      this.paymentDialog = false;
      this.eventBus.emit("show_payment", "false");
      this.eventBus.emit("set_customer_readonly", false);
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
    handlePaymentInput(payment, event) {
      let val = event.target.value;
      val = this.convertArabicToLatin(val);
      val = val.replace(/[^0-9.]/g, '');
      const parts = val.split('.');
      if (parts.length > 2) {
        val = parts[0] + '.' + parts.slice(1).join('');
      }
      payment.amount = val === '' ? 0 : parseFloat(val);
      if (isNaN(payment.amount)) payment.amount = 0;
      payment.base_amount = payment.amount;
      event.target.value = val;
      this.updatePaymentAmount(payment);
    },
    async loadOriginalInvoicePayments() {
      if (this.invoice_doc.is_return && this.invoice_doc.return_against) {
        try {
          const response = await frappe.call({
            method: 'frappe.client.get',
            args: {
              doctype: 'Sales Invoice',
              name: this.invoice_doc.return_against
            }
          });
          
          if (response.message) {
            this.original_invoice_payments = response.message.payments;
            this.original_invoice = response.message;
            return response.message;
          }
        } catch (error) {
          console.error('Error loading original invoice:', error);
        }
      }
      return null;
    },

    processReturnPayments() {
      // This function is intentionally minimal
      // Payment methods are set when payment dialog opens (in mounted hook)
      // and preserved to allow manual changes by user
      if (!this.invoice_doc.is_return) {
        return;
      }
      
      // Only handle basic return setup
      if (this.invoice_doc.return_against) {
        this.invoice_doc.update_stock = 1;
      }
      
      if (!this.invoice_doc.reason_for_issuing_credit_note) {
        this.invoice_doc.reason_for_issuing_credit_note = "Return";
      }
    },

    submit(event, payment_received = false, print = false) {
      const totalPaid = this.total_payments;
      
      if (!this.invoice_doc.is_return && totalPaid < 0) {
        this.eventBus.emit("show_message", {
          title: `Payments not correct`,
          color: "error",
        });
        frappe.utils.play_sound("error");
        return;
      }
      
      // Payment methods already set when payment dialog opened
      // Removed processReturnPayments() call to preserve manual payment method changes
      
      const totalAmount = Math.abs(this.invoice_doc.rounded_total || this.invoice_doc.grand_total);
      const tolerance = 0.01;
      
      this.is_credit_sale = 0;
      
      if (!this.invoice_doc.is_return && Math.abs(totalPaid - totalAmount) > tolerance && totalPaid < totalAmount) {
        this.eventBus.emit("show_message", {
          title: this.__(`Payment amount (${this.formatCurrency(totalPaid)}) does not match invoice total (${this.formatCurrency(totalAmount)})`),
          color: "error",
        });
        frappe.utils.play_sound("error");
        return;
      }
      
      let phone_payment_is_valid = true;
      if (!payment_received) {
        this.invoice_doc.payments.forEach((payment) => {
          if (
            payment.type == "Phone" &&
            ![0, "0", "", null, undefined].includes(payment.amount)
          ) {
            phone_payment_is_valid = false;
          }
        });
        if (!phone_payment_is_valid) {
          this.eventBus.emit("show_message", {
            title: this.__(
              "Please request phone payment or use other payment method"
            ),
            color: "error",
          });
          frappe.utils.play_sound("error");
          console.error("phone payment not requested");
          return;
        }
      }

      if (
        !this.invoice_doc.is_return &&
        !this.pos_profile.hspos_allow_partial_payment &&
        totalPaid < (this.invoice_doc.rounded_total || this.invoice_doc.grand_total)
      ) {
        this.eventBus.emit("show_message", {
          title: `The amount paid is not complete`,
          color: "error",
        });
        frappe.utils.play_sound("error");
        return;
      }

      if (
        this.pos_profile.hspos_allow_partial_payment &&
        totalPaid == 0
      ) {
        this.eventBus.emit("show_message", {
          title: `Please enter the amount paid`,
          color: "error",
        });
        frappe.utils.play_sound("error");
        return;
      }

      if (!this.paid_change) this.paid_change = 0;

      if (!this.invoice_doc.is_return && this.paid_change > -this.diff_payment) {
        this.eventBus.emit("show_message", {
          title: `Paid change can not be greater than total change!`,
          color: "error",
        });
        frappe.utils.play_sound("error");
        return;
      }

      let total_change = this.flt(
        this.flt(this.paid_change) + this.flt(-this.credit_change)
      );

      if (!this.invoice_doc.is_return && this.is_cashback && total_change != -this.diff_payment) {
        this.eventBus.emit("show_message", {
          title: `Error in change calculations!`,
          color: "error",
        });
        frappe.utils.play_sound("error");
        return;
      }

      let credit_calc_check = this.customer_credit_dict.filter((row) => {
        if (this.flt(row.credit_to_redeem))
          return this.flt(row.credit_to_redeem) > this.flt(row.total_credit);
        else return false;
      });

      if (credit_calc_check.length > 0) {
        this.eventBus.emit("show_message", {
          title: `redeamed credit can not greater than its total.`,
          color: "error",
        });
        frappe.utils.play_sound("error");
        return;
      }

      if (
        !this.invoice_doc.is_return &&
        this.redeemed_customer_credit >
        (this.invoice_doc.rounded_total || this.invoice_doc.grand_total)
      ) {
        this.eventBus.emit("show_message", {
          title: `can not redeam customer credit more than invoice total`,
          color: "error",
        });
        frappe.utils.play_sound("error");
        return;
      }
      
      this.is_sucessful_invoice = this.submit_invoice(print);
    },
    submit_invoice(print) {
      let totalPayedAmount = 0;
      this.invoice_doc.payments.forEach((payment) => {
        payment.amount = this.flt(payment.amount);
        payment.base_amount = this.flt(payment.base_amount || payment.amount);
        totalPayedAmount += Math.abs(payment.amount);
      });
     
      if (this.invoice_doc.is_return) {
        this.invoice_doc.reason_for_issuing_credit_note = "Return";
        
        if (this.is_cashback || totalPayedAmount == 0) {
          this.invoice_doc.is_pos = 0;
          this.invoice_doc.payments.forEach((payment) => {
            payment.amount = 0;
            payment.base_amount = 0;
          });
        } else {
          this.invoice_doc.is_pos = 1;
          
          if (!this.invoice_doc.return_against) {
            this.eventBus.emit("show_message", {
              title: `Return Against invoice is required`,
              color: "error",
            });
            return;
          }
          
          this.invoice_doc.update_stock = 1;
          
          this.invoice_doc.payments.forEach((payment) => {
            if (payment.amount > 0) {
              payment.amount = -Math.abs(payment.amount);
              payment.base_amount = -Math.abs(payment.base_amount);
            }
          });
        }
      }
     
      if (this.customer_credit_dict.length) {
        this.customer_credit_dict.forEach((row) => {
          row.credit_to_redeem = this.flt(row.credit_to_redeem);
        });
      }
      
      let data = {};
      data["total_change"] = !this.invoice_doc.is_return ? -this.diff_payment : 0;
      data["paid_change"] = !this.invoice_doc.is_return ? this.paid_change : 0;
      data["credit_change"] = -this.credit_change;
      data["redeemed_customer_credit"] = this.redeemed_customer_credit;
      data["customer_credit_dict"] = this.customer_credit_dict;
      data["is_cashback"] = this.is_cashback;

      const vm = this;
      frappe.call({
        method: "highspeed_pos.highspeed_pos.api.hsposapp.submit_invoice",
        args: {
          data: data,
          invoice: this.invoice_doc,
        },
        async: false,
        callback: function (r) {
          if (!r?.message) {
            vm.eventBus.emit("show_message", {
              title: `Error submitting invoice`,
              color: "error",
            });
            return;
          }

          if (r.message && r.message.name) {
            vm.invoice_doc.name = r.message.name;
          }

          // Set table status to Occupied in database (freed only manually from tables screen)
          if (vm.invoice_doc.hspos_table) {
            vm.updateTableStatus(vm.invoice_doc.hspos_table, "Occupied");
          }
         
          if (vm.invoice_doc.is_return && vm.invoice_doc.return_against && !vm.is_cashback) {
            frappe.call({
              method: "frappe.client.get_value",
              args: {
                doctype: "Sales Invoice",
                name: vm.invoice_doc.return_against,
                fieldname: ["outstanding_amount", "status"]
              },
              callback: function(response) {
                if (response.message) {
                  console.log("Original invoice status after return:", response.message);
                }
              }
            });
          }
          
          if (print) {
            vm.load_print_page();
          }
          
          vm.customer_credit_dict = [];
          vm.redeem_customer_credit = false;
          vm.is_cashback = false;
          vm.sales_person = "";

          vm.eventBus.emit("set_last_invoice", r.message.name);
          let successMessage = frappe._("Invoice {0} is Submitted", [r.message.name]);
          if (r.message.hspos_order_no) {
            successMessage += " | " + frappe._("Order Number") + `: ${r.message.hspos_order_no}`;
            vm.pos_profile.hspos_next_order_number = r.message.hspos_order_no + 1;
            vm.eventBus.emit("register_pos_profile", {
              pos_profile: vm.pos_profile
            });
          }
          vm.eventBus.emit("show_message", {
            title: successMessage,
            color: "success",
          });
          frappe.utils.play_sound("submit");
          vm.addresses = [];
          vm.eventBus.emit("clear_invoice");
          vm.back_to_invoice();
          return;
        }
      });
    },
    set_full_amount(idx) {
      const targetAmount = this.invoice_doc.is_return 
        ? -Math.abs(this.invoice_doc.rounded_total || this.invoice_doc.grand_total)
        : this.flt(this.invoice_doc.rounded_total || this.invoice_doc.grand_total, this.currency_precision);
      
      this.invoice_doc.payments.forEach((payment) => {
        if (payment.idx == idx) {
          payment.amount = targetAmount;
          payment.base_amount = targetAmount;
        } else {
          payment.amount = 0;
          payment.base_amount = 0;
        }
      });
      this.$forceUpdate();
    },
    set_specific_amount(idx) {
      const targetPayment = this.invoice_doc.payments.find(p => p.idx === idx);
      if (targetPayment && targetPayment.amount === 0) {
        if (this.diff_payment > 0) {
          targetPayment.amount = this.invoice_doc.is_return 
            ? -this.flt(this.diff_payment, this.currency_precision)
            : this.flt(this.diff_payment, this.currency_precision);
          targetPayment.base_amount = targetPayment.amount;
        } else {
          this.set_full_amount(idx);
        }
      } else {
        this.set_full_amount(idx);
      }
    },
    handlePaymentMethodButtonClick(idx) {
      const totalAmount = Math.abs(this.invoice_doc.rounded_total || this.invoice_doc.grand_total);
      let otherPaymentsTotal = 0;
      
      this.invoice_doc.payments.forEach((p) => {
        if (p.idx !== idx) {
          otherPaymentsTotal += Math.abs(this.flt(p.amount || 0));
        }
      });
      otherPaymentsTotal += Math.abs(this.flt(this.loyalty_amount || 0));
      otherPaymentsTotal += Math.abs(this.flt(this.redeemed_customer_credit || 0));
      
      const remaining = this.flt(totalAmount - otherPaymentsTotal, this.currency_precision);
      const targetPayment = this.invoice_doc.payments.find(p => p.idx === idx);
      
      if (targetPayment) {
        if (remaining > 0) {
          targetPayment.amount = this.invoice_doc.is_return ? -remaining : remaining;
          targetPayment.base_amount = targetPayment.amount;
        } else {
          this.set_full_amount(idx);
        }
      }
      this.$forceUpdate();
    },
    set_rest_amount(idx) {
      const targetPayment = this.invoice_doc.payments.find(p => p.idx === idx);
      if (targetPayment && targetPayment.amount == 0 && this.diff_payment > 0) {
        const totalAmount = Math.abs(this.invoice_doc.rounded_total || this.invoice_doc.grand_total);
        let otherPaymentsTotal = 0;
        
        this.invoice_doc.payments.forEach((p) => {
          if (p.idx !== idx) {
            otherPaymentsTotal += Math.abs(this.flt(p.amount || 0));
          }
        });
        
        otherPaymentsTotal += Math.abs(this.flt(this.loyalty_amount || 0));
        otherPaymentsTotal += Math.abs(this.flt(this.redeemed_customer_credit || 0));
        
        const remaining = this.flt(totalAmount - otherPaymentsTotal, this.currency_precision);
        if (remaining > 0) {
          targetPayment.amount = this.invoice_doc.is_return ? -remaining : remaining;
          targetPayment.base_amount = targetPayment.amount;
        }
      }
    },
    updatePaymentAmount(payment) {
      payment.amount = parseFloat(payment.amount || 0);
      if (isNaN(payment.amount)) {
        payment.amount = 0;
      }
      payment.base_amount = payment.amount;
      
      const totalAmount = Math.abs(this.invoice_doc.rounded_total || this.invoice_doc.grand_total);
      let currentTotal = 0;
      let lastEmptyPayment = null;
      let emptyPaymentsCount = 0;
      
      this.invoice_doc.payments.forEach((p) => {
        if (p.idx !== payment.idx) {
          if (p.amount === 0 || p.amount === '') {
            emptyPaymentsCount++;
            lastEmptyPayment = p;
          } else {
            currentTotal += Math.abs(parseFloat(p.amount || 0));
          }
        } else {
          currentTotal += Math.abs(parseFloat(payment.amount || 0));
        }
      });
      
      currentTotal += Math.abs(parseFloat(this.loyalty_amount || 0));
      currentTotal += Math.abs(parseFloat(this.redeemed_customer_credit || 0));
     
      // Check if this is a cash payment method (supports English 'cash' and Arabic 'نقدي' / 'نقد')
      const modeLower = (payment.mode_of_payment || '').toLowerCase();
      const isCash = payment.type === 'Cash' || 
                     modeLower.includes('cash') || 
                     modeLower.includes('نقدي') || 
                     modeLower.includes('نقد');

      if (currentTotal > totalAmount && !isCash) {
        this.eventBus.emit("show_message", {
          title: this.__('Payment amount exceeds invoice total!'),
          color: "error",
        });
        const maxAmount = totalAmount - (currentTotal - Math.abs(payment.amount));
        payment.amount = this.invoice_doc.is_return ? -maxAmount : maxAmount;
        payment.base_amount = payment.amount;
        if (Math.abs(payment.amount) < 0) {
          payment.amount = 0;
          payment.base_amount = 0;
        }
      } else if (emptyPaymentsCount === 1 && lastEmptyPayment) {
        const remaining = totalAmount - currentTotal;
        if (remaining > 0) {
          lastEmptyPayment.amount = this.invoice_doc.is_return ? -remaining : remaining;
          lastEmptyPayment.base_amount = lastEmptyPayment.amount;
        }
      }  
    },

    validatePaymentAmounts() {
      const totalAmount = Math.abs(this.invoice_doc.rounded_total || this.invoice_doc.grand_total);
      const totalPaid = Math.abs(this.total_payments);
      
      if (Math.abs(totalPaid - totalAmount) > 0.01 && totalPaid > 0) {
        if (totalPaid < totalAmount) {
          this.eventBus.emit("show_message", {
            title: this.__(`Payment amount is less than invoice total by ${this.formatCurrency(totalAmount - totalPaid)}`),
            color: "warning",
          });
        }
      }
    },
    clear_all_amounts() {
      this.invoice_doc.payments.forEach((payment) => {
        payment.amount = 0;
        payment.base_amount = 0;
      });
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
    load_print_page() {
      if (this.pos_profile && this.pos_profile.name) {
        frappe.call({
          method: "highspeed_pos.highspeed_pos.api.hsposapp.log_drawer_open",
          args: {
            pos_profile: this.pos_profile.name,
            sales_invoice: this.invoice_doc.name
          }
        });
      }
      const print_format =
        this.pos_profile.print_format_for_online ||
        this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url =
        frappe.urllib.get_base_url() +
        "/printview?doctype=Sales%20Invoice&name=" +
        this.invoice_doc.name +
        "&format=" +
        print_format +
        "&no_letterhead=" +
        letter_head;
      
      let printFrame = document.getElementById('print-frame');
      if (printFrame) {
        printFrame.remove();
      }
      
      printFrame = document.createElement('iframe');
      printFrame.id = 'print-frame';
      printFrame.style.position = 'absolute';
      printFrame.style.width = '0';
      printFrame.style.height = '0';
      printFrame.style.border = '0';
      printFrame.style.left = '-9999px';
      printFrame.style.top = '-9999px';
      printFrame.style.visibility = 'hidden';
      document.body.appendChild(printFrame);
      
      printFrame.onload = function() {
        setTimeout(() => {
          printFrame.contentWindow.focus();
          printFrame.contentWindow.print();
          
          setTimeout(() => {
            if (printFrame && printFrame.parentNode) {
              printFrame.remove();
            }
          }, 3000);
        }, 500);
      };
      
      printFrame.src = url;
    },
    validate_due_date() {
      const today = frappe.datetime.now_date();
      const parse_today = Date.parse(today);
      const new_date = Date.parse(this.invoice_doc.due_date);
      if (new_date < parse_today) {
        setTimeout(() => {
          this.invoice_doc.due_date = today;
        }, 0);
      }
    },
    shortPay(e) {
      if (e.key === "x" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.submit();
      }
      
      if (e.key === "F12") {
        e.preventDefault();
        if (!this.vaildatPayment) {
          this.submit(undefined, false, true);
        }
      }
      
      if (e.key === "F10") {
        e.preventDefault();
        if (!this.vaildatPayment) {
          this.submit();
        }
      }
      
      if (e.key === "F9") {
        e.preventDefault();
        this.back_to_invoice();
      }
      
      if (e.key === "Escape") {
        e.preventDefault();
        this.back_to_invoice();
      }
    },
    set_paid_change() {
      if (!this.paid_change) this.paid_change = 0;

      this.paid_change_rules = [];
      let change = -this.diff_payment;
      if (this.paid_change > change) {
        this.paid_change_rules = [
          "Paid change can not be greater than total change!",
        ];
        this.credit_change = 0;
      }
    },
    get_available_credit(e) {
      this.clear_all_amounts();
      if (e) {
        frappe
          .call("highspeed_pos.highspeed_pos.api.hsposapp.get_available_credit", {
            customer: this.invoice_doc.customer,
            company: this.pos_profile.company,
          })
          .then((r) => {
            const data = r.message;
            if (data.length) {
              const amount =
                this.invoice_doc.rounded_total || this.invoice_doc.grand_total;
              let remainAmount = amount;

              data.forEach((row) => {
                if (remainAmount > 0) {
                  if (remainAmount >= row.total_credit) {
                    row.credit_to_redeem = row.total_credit;
                    remainAmount = remainAmount - row.total_credit;
                  } else {
                    row.credit_to_redeem = remainAmount;
                    remainAmount = 0;
                  }
                } else {
                  row.credit_to_redeem = 0;
                }
              });

              this.customer_credit_dict = data;
            } else {
              this.customer_credit_dict = [];
            }
          });
      } else {
        this.customer_credit_dict = [];
      }
    },
    get_addresses() {
      const vm = this;
      if (!vm.invoice_doc) {
        return;
      }
      frappe.call({
        method: "highspeed_pos.highspeed_pos.api.hsposapp.get_customer_addresses",
        args: { customer: vm.invoice_doc.customer },
        async: true,
        callback: function (r) {
          if (!r.exc) {
            vm.addresses = r.message;
          } else {
            vm.addresses = [];
          }
        },
      });
    },
    addressFilter(item, queryText, itemText) {
      const textOne = item.address_title
        ? item.address_title.toLowerCase()
        : "";
      const textTwo = item.address_line1
        ? item.address_line1.toLowerCase()
        : "";
      const textThree = item.address_line2
        ? item.address_line2.toLowerCase()
        : "";
      const textFour = item.city ? item.city.toLowerCase() : "";
      const textFifth = item.name.toLowerCase();
      const searchText = queryText.toLowerCase();
      return (
        textOne.indexOf(searchText) > -1 ||
        textTwo.indexOf(searchText) > -1 ||
        textThree.indexOf(searchText) > -1 ||
        textFour.indexOf(searchText) > -1 ||
        textFifth.indexOf(searchText) > -1
      );
    },
    new_address() {
      this.eventBus.emit("open_new_address", this.invoice_doc.customer);
    },
    get_sales_person_names() {
      const vm = this;
      if (
        vm.pos_profile.hspos_local_storage &&
        localStorage.sales_persons_storage
      ) {
        vm.sales_persons = JSON.parse(
          localStorage.getItem("sales_persons_storage")
        );
      }
      frappe.call({
        method: "highspeed_pos.highspeed_pos.api.hsposapp.get_sales_person_names",
        callback: function (r) {
          if (r.message) {
            vm.sales_persons = r.message;
            if (vm.pos_profile.hspos_local_storage) {
              localStorage.setItem("sales_persons_storage", "");
              localStorage.setItem(
                "sales_persons_storage",
                JSON.stringify(r.message)
              );
            }
          }
        },
      });
    },
    salesPersonFilter(itemText, queryText, itemRow) {
      const item = itemRow.raw;
      const textOne = item.sales_person_name
        ? item.sales_person_name.toLowerCase()
        : "";
      const textTwo = item.name.toLowerCase();
      const searchText = queryText.toLowerCase();

      return (
        textOne.indexOf(searchText) > -1 || textTwo.indexOf(searchText) > -1
      );
    },
    request_payment() {
      this.phone_dialog = false;
      const vm = this;
      if (!this.invoice_doc.contact_mobile) {
        this.eventBus.emit("show_message", {
          title: this.__(`Pleas Set Customer Mobile Number`),
          color: "error",
        });
        this.eventBus.emit("open_edit_customer");
        this.back_to_invoice();
        return;
      }
      this.eventBus.emit("freeze", {
        title: this.__(`Waiting for payment... `),
      });
      this.invoice_doc.payments.forEach((payment) => {
        payment.amount = this.flt(payment.amount);
      });
      let formData = { ...this.invoice_doc };
      formData["total_change"] = -this.diff_payment;
      formData["paid_change"] = this.paid_change;
      formData["credit_change"] = -this.credit_change;
      formData["redeemed_customer_credit"] = this.redeemed_customer_credit;
      formData["customer_credit_dict"] = this.customer_credit_dict;
      formData["is_cashback"] = this.is_cashback;

      frappe
        .call({
          method: "highspeed_pos.highspeed_pos.api.hsposapp.update_invoice",
          args: {
            data: formData,
          },
          async: false,
          callback: function (r) {
            if (r.message) {
              vm.invoice_doc = r.message;
            }
          },
        })
        .then(() => {
          frappe
            .call({
              method: "highspeed_pos.highspeed_pos.api.hsposapp.create_payment_request",
              args: {
                doc: vm.invoice_doc,
              },
            })
            .fail(() => {
              this.eventBus.emit("unfreeze");
              this.eventBus.emit("show_message", {
                title: this.__(`Payment request failed`),
                color: "error",
              });
            })
            .then(({ message }) => {
              const payment_request_name = message.name;
              setTimeout(() => {
                frappe.db
                  .get_value("Payment Request", payment_request_name, [
                    "status",
                    "grand_total",
                  ])
                  .then(({ message }) => {
                    if (message.status != "Paid") {
                      this.eventBus.emit("unfreeze");
                      this.eventBus.emit("show_message", {
                        title: this.__(
                          `Payment Request took too long to respond. Please try requesting for payment again`
                        ),
                        color: "error",
                      });
                    } else {
                      this.eventBus.emit("unfreeze");
                      this.eventBus.emit("show_message", {
                        title: this.__("Payment of {0} received successfully.", [
                          vm.formatCurrency(
                            message.grand_total,
                            vm.invoice_doc.currency,
                            0
                          ),
                        ]),
                        color: "success",
                      });
                      frappe.db
                        .get_doc("Sales Invoice", vm.invoice_doc.name)
                        .then((doc) => {
                          vm.invoice_doc = doc;
                          vm.submit(null, true);
                        });
                    }
                  });
              }, 30000);
            });
        });
    },
    get_mpesa_modes() {
      const vm = this;
      frappe.call({
        method: "highspeed_pos.highspeed_pos.api.m_pesa.get_mpesa_mode_of_payment",
        args: { company: vm.pos_profile.company },
        async: true,
        callback: function (r) {
          if (!r.exc) {
            vm.mpesa_modes = r.message;
          } else {
            vm.mpesa_modes = [];
          }
        },
      });
    },
    is_mpesa_c2b_payment(payment) {
      if (
        this.mpesa_modes.includes(payment.mode_of_payment) &&
        payment.type == "Bank"
      ) {
        payment.amount = 0;
        return true;
      } else {
        return false;
      }
    },
    mpesa_c2b_dialg(payment) {
      const data = {
        company: this.pos_profile.company,
        mode_of_payment: payment.mode_of_payment,
        customer: this.invoice_doc.customer,
      };
      this.eventBus.emit("open_mpesa_payments", data);
    },
    set_mpesa_payment(payment) {
      this.pos_profile.use_customer_credit = 1;
      this.redeem_customer_credit = true;
      const invoiceAmount =
        this.invoice_doc.rounded_total || this.invoice_doc.grand_total;
      let amount =
        payment.unallocated_amount > invoiceAmount
          ? invoiceAmount
          : payment.unallocated_amount;
      if (amount < 0 || !amount) amount = 0;
      const advance = {
        type: "Advance",
        credit_origin: payment.name,
        total_credit: this.flt(payment.unallocated_amount),
        credit_to_redeem: this.flt(amount),
      };
      this.clear_all_amounts();
      this.customer_credit_dict.push(advance);
    },
    isNumber(v) {
      if (v == "" || v == undefined || v == null) return false;
      return !isNaN(v);
    },
    flt(value, precision) {
      if (precision === undefined) {
        precision = this.currency_precision;
      }
      
      if (typeof value === 'undefined' || value === null || value === '') {
        return 0;
      }
      
      const floatValue = parseFloat(value);
      if (isNaN(floatValue)) {
        return 0;
      }
      
      return parseFloat(floatValue.toFixed(precision));
    },
    __: function(text) {
      return frappe._(text) || text;
    }
  },

  computed: {
    currency_precision() {
      return frappe.defaults.get_default("currency_precision") || 2;
    },
    float_precision() {
      return frappe.defaults.get_default("float_precision") || 2;
    },
    total_payments() {
      let total = parseFloat(this.invoice_doc.loyalty_amount || 0);
      if (this.invoice_doc && this.invoice_doc.payments) {
        this.invoice_doc.payments.forEach((payment) => {
          total += this.flt(payment.amount || 0);
        });
      }

      total += this.flt(this.redeemed_customer_credit || 0);

      if (!this.is_cashback && this.invoice_doc.is_return) total = 0;

      return this.flt(total, this.currency_precision);
    },
    total_payments_display() {
      if (this.invoice_doc.is_return) {
        let total = parseFloat(this.invoice_doc.loyalty_amount || 0);
        if (this.invoice_doc && this.invoice_doc.payments) {
          this.invoice_doc.payments.forEach((payment) => {
            total += Math.abs(this.flt(payment.amount || 0));
          });
        }
        total += Math.abs(this.flt(this.redeemed_customer_credit || 0));
        if (!this.is_cashback && this.invoice_doc.is_return) total = 0;
        return this.flt(total, this.currency_precision);
      }
      return this.total_payments;
    },
    diff_payment() {
      const grandTotal = this.invoice_doc.rounded_total || this.invoice_doc.grand_total;
      let diff_payment = this.flt(
        grandTotal - this.total_payments,
        this.currency_precision
      );
      
      if (!this.invoice_doc.is_return) {
        this.paid_change = -diff_payment;
      }
      
      return diff_payment;
    },
    credit_change() {
      if (this.invoice_doc.is_return) return 0;
      
      let change = -this.diff_payment;
      if (this.paid_change > change) return 0;
      return this.flt(this.paid_change - change, this.currency_precision);
    },
    diff_lable() {
      let lable = this.diff_payment < 0 ? "Change" : "To Be Paid";
      return lable;
    },
    available_pioints_amount() {
      let amount = 0;
      if (this.customer_info && this.customer_info.loyalty_points) {
        amount =
          this.customer_info.loyalty_points *
          this.customer_info.conversion_factor;
      }
      return amount;
    },
    available_customer_credit() {
      let total = 0;
      this.customer_credit_dict.map((row) => {
        total += row.total_credit;
      });

      return total;
    },
    redeemed_customer_credit() {
      let total = 0;
      this.customer_credit_dict.map((row) => {
        if (this.flt(row.credit_to_redeem)) total += this.flt(row.credit_to_redeem);
        else row.credit_to_redeem = 0;
      });

      return total;
    },
    vaildatPayment() {
      if (this.pos_profile.hspos_allow_sales_order) {
        if (
          this.invoiceType == "Order" &&
          !this.invoice_doc.hspos_delivery_date
        ) {
          return true;
        } else {
          return false;
        }
      } else {
        return false;
      }
    },
    request_payment_field() {
      let res = false;
      if (!this.pos_settings || !this.pos_settings.invoice_fields || this.pos_settings.invoice_fields.length == 0) {
        res = false;
      } else {
        this.pos_settings.invoice_fields.forEach((el) => {
          if (
            el.fieldtype == "Button" &&
            el.fieldname == "request_for_payment"
          ) {
            res = true;
          }
        });
      }
      return res;
    }
  },

  mounted: function () {
    const observer = new MutationObserver(() => {
      this.detectRTL();
    });
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['dir', 'lang']
    });
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['dir']
    });
    this._dirObserver = observer;

    this.detectRTL();

    this.$watch('isRTL', (newVal) => {
      this.$nextTick(() => {
        this.$forceUpdate();
      });
    });

    this.$nextTick(function () {
      this.eventBus.on("send_invoice_doc_payment", async (invoice_doc) => {
        this.invoice_doc = invoice_doc;
        if (this.invoice_doc && (this.invoice_doc.hspos_table || !this.invoice_doc.hspos_order_type)) {
          this.invoice_doc.hspos_order_type = "Dine-in";
        }
        this.paymentDialog = true;
        
        this.is_credit_sale = 0;
        
        if (invoice_doc.is_return) {
          this.is_return = true;
          await this.loadOriginalInvoicePayments();
          
          if (this.original_invoice && this.original_invoice.is_pos === 0 && !this.original_invoice.is_return) {
            this.is_cashback = true;
            invoice_doc.payments.forEach((payment) => {
              payment.amount = 0;
              payment.base_amount = 0;
            });
            invoice_doc.is_pos = 0;
          } else if (this.is_cashback) {
            invoice_doc.payments.forEach((payment) => {
              payment.amount = 0;
              payment.base_amount = 0;
            });
            invoice_doc.is_pos = 0;
          } else {
            const totalAmount = Math.abs(invoice_doc.rounded_total || invoice_doc.grand_total);
            const defaultPayment = invoice_doc.payments.find(p => p.default == 1);
            
            if (this.original_invoice_payments) {
              const originalPaidPayment = this.original_invoice_payments.find(p => p.amount > 0);
              if (originalPaidPayment) {
                const matchingPayment = invoice_doc.payments.find(
                  p => p.mode_of_payment === originalPaidPayment.mode_of_payment
                );
                if (matchingPayment) {
                  matchingPayment.amount = -totalAmount;
                  matchingPayment.base_amount = -totalAmount;
                } else if (defaultPayment) {
                  defaultPayment.amount = -totalAmount;
                  defaultPayment.base_amount = -totalAmount;
                }
              } else if (defaultPayment) {
                defaultPayment.amount = -totalAmount;
                defaultPayment.base_amount = -totalAmount;
              }
            } else if (defaultPayment) {
              defaultPayment.amount = -totalAmount;
              defaultPayment.base_amount = -totalAmount;
            }
            
            invoice_doc.payments.forEach((payment) => {
              if (!payment.amount) {
                payment.amount = 0;
                payment.base_amount = 0;
              }
            });
          }
        } else {
          const default_payment = invoice_doc.payments.find(
            (payment) => payment.default == 1
          );
          this.is_credit_sale = 0;
          this.is_write_off_change = 0;
          if (default_payment) {
            default_payment.amount = this.flt(
              invoice_doc.rounded_total || invoice_doc.grand_total,
              this.currency_precision
            );
            default_payment.base_amount = default_payment.amount;
          }
        }
        
        this.loyalty_amount = 0;
        this.get_addresses();
        this.get_sales_person_names();
      });
      this.eventBus.on("register_pos_profile", (data) => {
        this.pos_profile = data.pos_profile;
        this.get_mpesa_modes();
      });
      this.eventBus.on("add_the_new_address", (data) => {
        this.addresses.push(data);
        this.$forceUpdate();
      });
      this.eventBus.on("update_invoice_type", (data) => {
        this.invoiceType = data;
        if (this.invoice_doc && data != "Order") {
          this.invoice_doc.hspos_delivery_date = null;
          this.invoice_doc.hspos_notes = null;
          this.invoice_doc.shipping_address_name = null;
        }
      });
    });
    this.eventBus.on("update_customer", (customer) => {
      if (this.customer != customer) {
        this.customer_credit_dict = [];
        this.redeem_customer_credit = false;
        this.is_cashback = false;
      }
    });
    this.eventBus.on("set_pos_settings", (data) => {
      this.pos_settings = data;
    });
    this.eventBus.on("set_customer_info_to_edit", (data) => {
      this.customer_info = data;
    });
    this.eventBus.on("set_mpesa_payment", (data) => {
      this.set_mpesa_payment(data);
    });
  },
  created() {
    this.detectRTL();
    this._shortPayHandler = this.shortPay.bind(this);
    document.addEventListener("keydown", this._shortPayHandler);
  },
  beforeUnmount() {
    if (this._dirObserver) {
      this._dirObserver.disconnect();
    }
    this.eventBus.off("send_invoice_doc_payment");
    this.eventBus.off("register_pos_profile");
    this.eventBus.off("add_the_new_address");
    this.eventBus.off("update_invoice_type");
    this.eventBus.off("update_customer");
    this.eventBus.off("set_pos_settings");
    this.eventBus.off("set_customer_info_to_edit");
    this.eventBus.off("update_invoice_coupons");
    this.eventBus.off("set_mpesa_payment");
  },

  unmounted() {
    if (this._shortPayHandler) {
      document.removeEventListener("keydown", this._shortPayHandler);
    }
  },

  watch: {
    'invoice_doc.hspos_order_type'(newVal) {
      if (newVal) {
        this.eventBus.emit("update_order_type", newVal);
      }
    },
    loyalty_amount(value) {
      if (value > this.available_pioints_amount) {
        this.invoice_doc.loyalty_amount = 0;
        this.invoice_doc.redeem_loyalty_points = 0;
        this.invoice_doc.loyalty_points = 0;
        this.eventBus.emit("show_message", {
          title: `Loyalty Amount can not be more then ${this.available_pioints_amount}`,
          color: "error",
        });
      } else {
        this.invoice_doc.loyalty_amount = this.flt(this.loyalty_amount);
        this.invoice_doc.redeem_loyalty_points = 1;
        this.invoice_doc.loyalty_points =
          this.flt(this.loyalty_amount) / this.customer_info.conversion_factor;
      }
    },
    is_credit_sale(value) {
      if (value) {
        this.is_credit_sale = 0;
        this.eventBus.emit("show_message", {
          title: this.__("Credit sales are not allowed"),
          color: "error",
        });
      }
    },
    credit_sales_due_date(value) {
      this.invoice_doc.due_date = frappe.datetime.get_datetime_as_string(value)
      console.log(this.invoice_doc)
    },
    is_write_off_change(value) {
      if (value == 1) {
        this.invoice_doc.write_off_amount = this.diff_payment;
        this.invoice_doc.write_off_outstanding_amount_automatically = 1;
      } else {
        this.invoice_doc.write_off_amount = 0;
        this.invoice_doc.write_off_outstanding_amount_automatically = 0;
      }
    },
    redeemed_customer_credit(value) {
      if (value > this.available_customer_credit) {
        this.eventBus.emit("show_message", {
          title: `You can redeem customer credit upto ${this.available_customer_credit}`,
          color: "error",
        });
      }
    },
    sales_person() {
      if (this.sales_person) {
        this.invoice_doc.sales_team = [
          {
            sales_person: this.sales_person,
            allocated_percentage: 100,
          },
        ];
      } else {
        this.invoice_doc.sales_team = [];
      }
    },
    is_cashback(value) {
      if (this.invoice_doc && this.invoice_doc.is_return) {
        if (this.original_invoice && this.original_invoice.is_pos === 0) {
          this.is_cashback = true;
          this.invoice_doc.payments.forEach((payment) => {
            payment.amount = 0;
            payment.base_amount = 0;
          });
          this.invoice_doc.is_pos = 0;
          this.eventBus.emit("show_message", {
            title: this.__("Original invoice was unpaid, return must be unpaid too"),
            color: "info",
          });
          return;
        }
        
        if (value) {
          this.invoice_doc.payments.forEach((payment) => {
            payment.amount = 0;
            payment.base_amount = 0;
          });
          this.invoice_doc.is_pos = 0;
        } else {
          const totalAmount = Math.abs(this.invoice_doc.rounded_total || this.invoice_doc.grand_total);
          const defaultPayment = this.invoice_doc.payments.find(p => p.default == 1);
          
          if (this.original_invoice_payments) {
            const originalPaidPayment = this.original_invoice_payments.find(p => p.amount > 0);
            if (originalPaidPayment) {
              const matchingPayment = this.invoice_doc.payments.find(
                p => p.mode_of_payment === originalPaidPayment.mode_of_payment
              );
              if (matchingPayment) {
                this.invoice_doc.payments.forEach((payment) => {
                  if (payment.mode_of_payment === originalPaidPayment.mode_of_payment) {
                    payment.amount = -totalAmount;
                    payment.base_amount = -totalAmount;
                  } else {
                    payment.amount = 0;
                    payment.base_amount = 0;
                  }
                });
              } else if (defaultPayment) {
                this.invoice_doc.payments.forEach((payment) => {
                  if (payment.idx === defaultPayment.idx) {
                    payment.amount = -totalAmount;
                    payment.base_amount = -totalAmount;
                  } else {
                    payment.amount = 0;
                    payment.base_amount = 0;
                  }
                });
              }
            }
          } else if (defaultPayment) {
            this.invoice_doc.payments.forEach((payment) => {
              if (payment.idx === defaultPayment.idx) {
                payment.amount = -totalAmount;
                payment.base_amount = -totalAmount;
              } else {
                payment.amount = 0;
                payment.base_amount = 0;
              }
            });
          } else if (this.invoice_doc.payments.length > 0) {
            this.invoice_doc.payments[0].amount = -totalAmount;
            this.invoice_doc.payments[0].base_amount = -totalAmount;
            for (let i = 1; i < this.invoice_doc.payments.length; i++) {
              this.invoice_doc.payments[i].amount = 0;
              this.invoice_doc.payments[i].base_amount = 0;
            }
          }
          
          this.invoice_doc.is_pos = 1;
        }
      }
    }
  }
}
</script>

<style scoped>
.v-toolbar {
 height: 48px !important;
}

.v-toolbar__title {
 font-size: 1rem !important;
}

.v-text-field--dense .v-input__control {
 min-height: 32px !important;
}

.v-text-field--dense input {
 padding: 4px 0 !important;
}

.v-btn--size-small {
 height: 28px !important;
 font-size: 0.75rem !important;
 padding: 0 8px !important;
}

.v-btn--size-default {
 height: 36px !important;
 font-size: 0.875rem !important;
}

.v-btn.v-size--large {
 height: 44px !important;
 font-size: 1rem !important;
 padding: 0 16px !important;
}

.v-switch--dense {
 margin-top: 0 !important;
 padding-top: 0 !important;
}

.v-switch--dense .v-input__slot {
 margin-bottom: 0 !important;
}

.text-caption {
 font-size: 0.75rem !important;
 line-height: 1.2 !important;
}

.text-body-2 {
 font-size: 0.875rem !important;
 line-height: 1.25 !important;
}

.text-body-1 {
 font-size: 1rem !important;
}

.text-h6 {
 font-size: 1.125rem !important;
 line-height: 1.375 !important;
}

.v-chip--x-small {
 font-size: 10px !important;
 height: 16px !important;
}

[dir="rtl"] .v-icon {
 transform: scaleX(-1);
}

[dir="rtl"] .ml-1 {
 margin-left: 0 !important;
 margin-right: 0.25rem !important;
}

[dir="rtl"] .ml-2 {
 margin-left: 0 !important;
 margin-right: 0.5rem !important;
}

[dir="rtl"] .mr-2 {
 margin-right: 0 !important;
 margin-left: 0.5rem !important;
}

[dir="rtl"] .pr-1 {
 padding-right: 0 !important;
 padding-left: 4px !important;
}

[dir="rtl"] .pl-1 {
 padding-left: 0 !important;
 padding-right: 4px !important;
}

[dir="rtl"] .text-left {
 text-align: right !important;
}

[dir="rtl"] .text-right {
 text-align: left !important;
}

.v-container {
 max-width: 100%;
}

.v-row {
 margin: 0;
}

.v-col {
 padding: 2px;
}

.bg-primary-darken-1 {
 background-color: #1565C0 !important;
}

.text-white-70 {
 color: rgba(255, 255, 255, 0.7);
}

.v-divider {
 margin: 4px 0 !important;
}

.v-list-item {
 min-height: 36px !important;
 padding: 4px 12px !important;
}

.v-list-item__title {
 font-size: 0.75rem !important;
 line-height: 1.2 !important;
}

.v-list-item__subtitle {
 font-size: 0.625rem !important;
 line-height: 1.1 !important;
}

.payment-method-label {
 padding: 8px 0;
 color: #1976d2;
}

.payment-amount-field {
 background-color: #f5f5f5;
}

.payment-amount-field input {
 text-align: right;
 font-weight: 500;
}

.v-btn--icon.v-btn--size-x-small {
 width: 24px !important;
 height: 24px !important;
}

.v-icon.v-icon--size-x-small {
 font-size: 16px !important;
}

.price-input {
 width: 100%;
 height: 42px !important;
 padding: 6px 14px;
 border: 1.5px solid rgba(0, 0, 0, 0.08);
 border-radius: 4px;
 font-size: 18px;
 font-weight: 600;
 text-align: center;
 background-color: #ffffff;
 transition: all 0.3s ease;
 -webkit-appearance: none;
 -moz-appearance: textfield;
 box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.payment-method-btn {
  height: 42px !important;
  border-radius: 4px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  letter-spacing: 0px !important;
  box-shadow: 0 4px 10px rgba(0, 151, 167, 0.12) !important;
  background: linear-gradient(90deg, #075294 0%, #0097A7 100%) !important;
  color: white !important;
  border: none !important;
}

.price-input:hover {
 background-color: #fafdff;
 border-color: #0097A7;
}

.price-input:focus {
 outline: none;
 border-color: #0097A7;
 background-color: #E0F7FA;
 box-shadow: 0 0 0 3px rgba(0, 151, 167, 0.2);
}

.price-input[readonly] {
 background-color: #f5f5f5;
 cursor: not-allowed;
 opacity: 0.6;
}

.price-input::-webkit-inner-spin-button,
.price-input::-webkit-outer-spin-button {
 -webkit-appearance: none;
 margin: 0;
}

[dir="rtl"] .price-input {
 text-align: center;
 direction: ltr;
}

.payment-summary-card {
  background: rgba(255, 255, 255, 0.6) !important;
  border-radius: 4px !important;
  border: 1px solid rgba(0, 0, 0, 0.05) !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
}

.payment-summary-title {
  color: #424242;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.payment-amount-card {
  border-radius: 4px;
  transition: all 0.3s ease;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.paid-amount-card {
  background: linear-gradient(135deg, #075294 0%, #0097A7 100%) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(7, 82, 148, 0.25) !important;
}

.paid-amount-card .text-caption,
.paid-amount-card .paid-amount-value {
  color: white !important;
}

.paid-amount-value {
  font-size: 1.25rem !important;
  font-weight: 700 !important;
}

.change-amount-card {
  background: linear-gradient(135deg, #FF8F00 0%, #FFB300 100%) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(255, 143, 0, 0.25) !important;
}

.change-amount-card .text-caption,
.change-amount-card .change-amount-value {
  color: white !important;
}

.change-amount-value {
  font-size: 1.25rem !important;
  font-weight: 700 !important;
}

.remaining-amount-card {
  background: linear-gradient(135deg, #00C853 0%, #64DD17 100%) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(0, 200, 83, 0.25) !important;
}

.remaining-amount-card {
  background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(245, 124, 0, 0.25) !important;
}

.remaining-amount-card .text-caption {
  color: rgba(255, 255, 255, 0.8) !important;
}

.remaining-amount-value {
  font-size: 1.25rem !important;
  color: white !important;
  font-weight: 700 !important;
}

.change-display-card {
  min-height: 70px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9) !important;
  border: 1.5px solid rgba(0, 0, 0, 0.05) !important;
  border-radius: 4px !important;
  color: #2c3e50 !important;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04) !important;
  transition: all 0.3s ease;
}

.change-display-card:hover {
  background: rgba(255, 255, 255, 0.95) !important;
  transform: translateY(-1px);
}

.change-display-card .text-caption {
  color: #7f8c8d !important;
  font-size: 0.75rem !important;
  font-weight: 600 !important;
}

.change-display-card .change-value {
  color: #2e7d32 !important;
  font-size: 1.2rem !important;
  font-weight: 800 !important;
}

.credit-change-card .change-value {
  color: #1565c0 !important;
}

.payment-amount-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

[dir="rtl"] .payment-summary-card {
  direction: rtl;
}

.border-light {
  border: 1px solid rgba(0, 0, 0, 0.08) !important;
}
.bg-light-gray {
  background-color: #fcfcfc !important;
}
.order-type-toggle {
  display: flex;
  width: 100%;
}
.order-type-toggle :deep(.v-btn) {
  flex-grow: 1;
  text-transform: none !important;
  font-weight: 600 !important;
  letter-spacing: normal !important;
}
.order-number-display {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 38px;
  width: 100%;
  border: 1px solid rgba(7, 82, 148, 0.2);
  border-radius: 4px;
  background-color: rgba(7, 82, 148, 0.05);
  color: #075294;
  font-weight: 700;
  font-size: 13px;
  box-sizing: border-box;
}
</style>