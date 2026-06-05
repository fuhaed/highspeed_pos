<template>
  <v-container fluid class="pa-0 pt-3" style="height: 100%; overflow: hidden;">
    <ClosingDialog></ClosingDialog>
    <Drafts></Drafts>
    <SalesOrders></SalesOrders>
    <Returns></Returns>
    <NewAddress></NewAddress>
    <MpesaPayments></MpesaPayments>
    <Variants></Variants>
    <OpeningDialog v-if="dialog" :dialog="dialog"></OpeningDialog>
    <v-row v-show="!dialog" :class="{ 'flex-row-reverse': isRTL }" style="height: 100%; margin: 0;">
      <!-- منطقة الأصناف - 70% من المساحة -->
      <v-col v-show="!payment && !offers && !coupons" xl="8" lg="8" md="8" sm="8" cols="12" class="pos px-2 pt-2 pb-0">
        <ItemsSelector></ItemsSelector>
      </v-col>
      <v-col v-show="offers" xl="8" lg="8" md="8" sm="8" cols="12" class="pos px-2 pt-2 pb-0">
        <PosOffers></PosOffers>
      </v-col>
      <v-col v-show="coupons" xl="8" lg="8" md="8" sm="8" cols="12" class="pos px-2 pt-2 pb-0">
        <PosCoupons></PosCoupons>
      </v-col>
      <v-col v-show="payment" xl="8" lg="8" md="8" sm="8" cols="12" class="pos px-2 pt-2 pb-0">
        <Payments></Payments>
      </v-col>

      <!-- منطقة سلة المشتريات - 30% من المساحة -->
      <v-col xl="4" lg="4" md="4" sm="4" cols="12" class="pos px-2 pt-2 pb-0">
        <Invoice></Invoice>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ItemsSelector from './ItemsSelector.vue';
import Invoice from './Invoice.vue';
import OpeningDialog from './OpeningDialog.vue';
import Payments from './Payments.vue';
import PosOffers from './PosOffers.vue';
import PosCoupons from './PosCoupons.vue';
import Drafts from './Drafts.vue';
import SalesOrders from "./SalesOrders.vue";
import ClosingDialog from './ClosingDialog.vue';
import NewAddress from './NewAddress.vue';
import Variants from './Variants.vue';
import Returns from './Returns.vue';
import MpesaPayments from './Mpesa-Payments.vue';

export default {
  data: function () {
    return {
      dialog: false,
      pos_profile: '',
      hspos_opening_shift: '',
      payment: false,
      offers: false,
      coupons: false,
      isRTL: false,
    };
  },

  components: {
    ItemsSelector,
    Invoice,
    OpeningDialog,
    Payments,
    Drafts,
    ClosingDialog,
    Returns,
    PosOffers,
    PosCoupons,
    NewAddress,
    Variants,
    MpesaPayments,
    SalesOrders,
  },

  methods: {
    check_opening_entry() {
      return frappe
        .call('highspeed_pos.highspeed_pos.api.hsposapp.check_opening_shift', {
          user: frappe.session.user,
        })
        .then((r) => {
          if (r.message) {
            this.pos_profile = r.message.pos_profile;
            this.hspos_opening_shift = r.message.hspos_opening_shift;
            this.get_offers(this.pos_profile.name);
            this.eventBus.emit('register_pos_profile', r.message);
            this.eventBus.emit('set_company', r.message.company);
            console.info('LoadPosProfile');
          } else {
            this.create_opening_voucher();
          }
        });
    },
    create_opening_voucher() {
      this.dialog = true;
    },
    get_closing_data() {
      return frappe
        .call(
          'highspeed_pos.highspeed_pos.doctype.hspos_closing_shift.hspos_closing_shift.make_closing_shift_from_opening',
          {
            opening_shift: this.hspos_opening_shift,
          }
        )
        .then((r) => {
          if (r.message) {
            this.eventBus.emit('open_ClosingDialog', r.message);
          } else {
            // console.log(r);
          }
        });
    },
    submit_closing_pos(data) {
      frappe
        .call(
          'highspeed_pos.highspeed_pos.doctype.hspos_closing_shift.hspos_closing_shift.submit_closing_shift',
          {
            closing_shift: data,
          }
        )
        .then((r) => {
          if (r.message) {
            this.eventBus.emit('closing_entry_created', { name: r.message });
            this.eventBus.emit('show_message', {
              title: `POS Shift Closed`,
              color: 'success',
            });
            if (!data.auto_print_receipt) {
              this.check_opening_entry();
            }
          } else {
            console.log(r);
          }
        });
    },
    get_offers(pos_profile) {
      return frappe
        .call('highspeed_pos.highspeed_pos.api.hsposapp.get_offers', {
          profile: pos_profile,
        })
        .then((r) => {
          if (r.message) {
            console.info('LoadOffers');
            this.eventBus.emit('set_offers', r.message);
          }
        });
    },
    get_pos_setting() {
      frappe.db.get_doc('POS Settings', undefined).then((doc) => {
        this.eventBus.emit('set_pos_settings', doc);
      });
    },
    detectRTL() {
      const htmlDir = document.documentElement.dir;
      const lang = document.documentElement.lang;
      const bodyDir = document.body.dir;
      this.isRTL = htmlDir === 'rtl' || bodyDir === 'rtl' || ['ar', 'he', 'fa', 'ur'].includes(lang?.substring(0, 2));
    },
    handleCloseOpeningDialog() {
      this.dialog = false;
    },
    handleRegisterPosData(data) {
      this.pos_profile = data.pos_profile;
      this.get_offers(this.pos_profile.name);
      this.hspos_opening_shift = data.hspos_opening_shift;
      this.eventBus.emit('register_pos_profile', data);
      console.info('LoadPosProfile');
    },
    handleShowPayment(data) {
      this.payment = data === 'true';
      this.offers = false;
      this.coupons = false;
    },
    handleShowOffers(data) {
      this.offers = data === 'true';
      this.payment = false;
      this.coupons = false;
    },
    handleShowCoupons(data) {
      this.coupons = data === 'true';
      this.offers = false;
      this.payment = false;
    },
    handleOpenClosingDialog() {
      this.get_closing_data();
    },
    handleSubmitClosingPos(data) {
      this.submit_closing_pos(data);
    },
    handleClosingPrintDone() {
      this.check_opening_entry();
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
      this.check_opening_entry();
      this.get_pos_setting();
      this.eventBus.on('close_opening_dialog', this.handleCloseOpeningDialog);
      this.eventBus.on('register_pos_data', this.handleRegisterPosData);
      this.eventBus.on('show_payment', this.handleShowPayment);
      this.eventBus.on('show_offers', this.handleShowOffers);
      this.eventBus.on('show_coupons', this.handleShowCoupons);
      this.eventBus.on('open_closing_dialog', this.handleOpenClosingDialog);
      this.eventBus.on('submit_closing_pos', this.handleSubmitClosingPos);
      this.eventBus.on('closing_print_done', this.handleClosingPrintDone);
    });
  },

  beforeUnmount() {
    if (this._dirObserver) {
      this._dirObserver.disconnect();
    }
    this.eventBus.off('close_opening_dialog', this.handleCloseOpeningDialog);
    this.eventBus.off('register_pos_data', this.handleRegisterPosData);
    this.eventBus.off('show_payment', this.handleShowPayment);
    this.eventBus.off('show_offers', this.handleShowOffers);
    this.eventBus.off('show_coupons', this.handleShowCoupons);
    this.eventBus.off('open_closing_dialog', this.handleOpenClosingDialog);
    this.eventBus.off('submit_closing_pos', this.handleSubmitClosingPos);
    this.eventBus.off('closing_print_done', this.handleClosingPrintDone);
  },
};
</script>

<style scoped>
/* يمكنك إضافة أي تخصيصات CSS إضافية هنا */
.pos {
  height: 100%;
  overflow: hidden;
}
</style>