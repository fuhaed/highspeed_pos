<template>
  <div class="items-selector" :dir="isRTL ? 'rtl' : 'ltr'">
    <!-- UOM Selection Dialog -->
    <v-dialog v-model="uomDialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="d-flex align-center justify-space-between pa-3">
          <span class="text-h6">{{ __('Select Unit') }}</span>
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeUOMDialog"></v-btn>
        </v-card-title>
        
        <v-divider></v-divider>
        
        <v-card-text class="pa-3">
          <!-- Item Name -->
          <div class="text-center mb-3">
            <div class="text-subtitle-1 font-weight-medium">{{ selectedItemForUOM?.item_name }}</div>
            <div class="text-caption text-grey">{{ selectedItemForUOM?.item_code }}</div>
          </div>
          
          <!-- Quantity if from scale -->
          <div v-if="pendingQty > 1" class="text-center mb-3">
            <v-chip size="small" color="primary" variant="tonal">
              {{ __('Qty') }}: {{ formatNumber(pendingQty) }}
            </v-chip>
          </div>
          
          <!-- UOM Options -->
          <div class="uom-options">
            <v-btn
              v-for="(uom, index) in availableUOMs"
              :key="uom.uom"
              @click="selectUOM(uom)"
              :color="getUOMColor(index)"
              variant="flat"
              class="uom-btn"
              block
            >
              <div class="uom-btn-content">
                <div class="uom-name">{{ uom.uom }}</div>
                <div class="uom-price">{{ currencySymbol(selectedItemForUOM?.currency) }}{{ formatCurrency(calculateUOMPrice(uom)) }}</div>
                <div v-if="uom.conversion_factor && uom.conversion_factor !== 1" class="uom-factor">
                  {{ formatNumber(uom.conversion_factor) }}x
                </div>
              </div>
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-progress-linear v-if="loading" indeterminate color="primary" height="2" />

    <div class="controls-row">
      <v-row dense align="center" class="pa-2">
        <v-col cols="12">
          <div class="controls-container">
            <v-text-field
              v-if="pos_profile.hspos_input_qty"
              v-model.number="qty"
              :label="__('Qty')"
              variant="outlined"
              density="compact"
              hide-details
              type="number"
              lang="en"
              min="1"
              @keydown.enter="enter_event"
              class="qty-field"
            />

            <v-checkbox
              v-if="pos_profile.hspos_new_line"
              v-model="new_line"
              :label="__('NL')"
              density="compact"
              hide-details
              class="new-line-check"
            />

            <!-- In Stock Filter -->
            <v-btn
              @click="in_stock_only = !in_stock_only"
              :variant="in_stock_only ? 'tonal' : 'outlined'"
              :color="in_stock_only ? 'success' : 'grey'"
              size="small"
              class="action-btn px-2"
            >
              <v-icon size="small" class="me-1">
                {{ in_stock_only ? 'mdi-store-check' : 'mdi-store-outline' }}
              </v-icon>
              <span class="action-text">{{ __('In Stock Only') }}</span>
            </v-btn>


            <!-- Sort By Menu -->
            <v-menu offset-y>
              <template v-slot:activator="{ props }">
                <v-btn
                  variant="outlined"
                  size="small"
                  color="grey"
                  class="action-btn px-2"
                  v-bind="props"
                >
                  <v-icon size="small" class="me-1">mdi-sort</v-icon>
                  <span class="action-text">{{ getSortLabel(sort_by) }}</span>
                </v-btn>
              </template>
              <v-list density="compact">
                <v-list-item
                  v-for="option in sortOptions"
                  :key="option.value"
                  @click="sort_by = option.value"
                  :value="option.value"
                  :active="sort_by === option.value"
                >
                  <v-list-item-title>{{ option.title }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>

            <v-btn-toggle v-model="items_view" mandatory density="compact" class="view-toggle">
              <v-btn value="list" size="small" icon>
                <v-icon size="small">mdi-view-list</v-icon>
              </v-btn>
              <v-btn value="card" size="small" icon>
                <v-icon size="small">mdi-view-grid</v-icon>
              </v-btn>
            </v-btn-toggle>

            <v-btn @click="show_offers" variant="outlined" size="small" color="primary" class="action-btn">
              <v-icon size="small">mdi-tag</v-icon>
              <span class="action-text">{{ offersCount }}</span>
              <v-badge v-if="appliedOffersCount > 0" :content="appliedOffersCount" color="success" floating />
            </v-btn>

            <v-btn @click="show_coupons" variant="outlined" size="small" color="secondary" class="action-btn">
              <v-icon size="small">mdi-ticket</v-icon>
              <span class="action-text">{{ couponsCount }}</span>
              <v-badge v-if="appliedCouponsCount > 0" :content="appliedCouponsCount" color="success" floating />
            </v-btn>

            <div class="search-info">
              <v-chip v-if="search" size="small" color="primary" variant="outlined" closable @click:close="clearSearch">
                "{{ search.substring(0, 10) }}{{ search.length > 10 ? '...' : '' }}"
              </v-chip>
              <div v-else class="items-count">
                <v-icon size="small" color="grey">mdi-package-variant</v-icon>
                <span>{{ filtered_items.length }} {{ __('Items') }}</span>
              </div>
            </div>
          </div>
        </v-col>
      </v-row>
    </div>

    <div class="search-field-container">
      <v-text-field
        v-model="debounce_search"
        :label="__('Search Items')"
        :placeholder="__('Search by item code, barcode, or serial number...')"
        variant="outlined"
        density="compact"
        hide-details
        clearable
        autofocus
        flat
        lang="en"
        @keydown.enter="search_onchange"
        @keydown.esc="esc_event"
        ref="debounce_search"
        class="search-field-direct"
      >
        <template v-slot:prepend-inner>
          <v-icon size="20">mdi-magnify</v-icon>
        </template>
      </v-text-field>
    </div>

    <div class="groups-row" v-if="items_group && items_group.length > 0">
      <div class="groups-container pa-2">
        <v-btn
          v-for="group in items_group"
          :key="group"
          @click="selectItemGroup(group)"
          :variant="item_group === group ? 'flat' : 'outlined'"
          :color="item_group === group ? 'primary' : 'default'"
          size="small"
          class="group-btn"
        >
          <v-icon size="16" class="group-icon">{{ getGroupIcon(group) }}</v-icon>
          <span class="group-label">{{ getGroupDisplayName(group) }}</span>
        </v-btn>
      </div>
    </div>

    <div class="items-content">
      <div v-if="items_view === 'list'" class="list-view">
        <v-data-table
          :headers="getItemsHeaders()"
          :items="paginatedItems"
          item-key="item_code"
          density="compact"
          :items-per-page="itemsPerPage"
          hide-default-footer
          @click:row="click_item_row"
          class="items-table"
          hover
        >
          <template v-slot:item.item_code="{ item }">
            <div class="item-code-cell">{{ item.item_code }}</div>
          </template>
          <template v-slot:item.item_name="{ item }">
            <div class="d-flex align-center">
              <v-avatar size="32" class="mr-2">
                <v-img :src="item.image || '/assets/highspeed_pos/js/hsposapp/components/pos/placeholder-image.png'" />
              </v-avatar>
              <div>
                <div class="item-name-wrapper">
                  <span class="item-name">{{ item.item_name }}</span>
                  <v-chip 
                    v-if="item.has_variants" 
                    size="x-small" 
                    color="primary" 
                    variant="tonal"
                    class="ml-2"
                  >
                    <v-icon size="12" start>mdi-shape-plus</v-icon>
                    {{ __('Variants') }}
                  </v-chip>
                </div>
              </div>
            </div>
          </template>
          <template v-slot:item.rate="{ item }">
            <div class="price">{{ currencySymbol(item.currency) }}{{ formatCurrency(item.rate) }}</div>
          </template>
          <template v-slot:item.actual_qty="{ item }">
            <v-chip size="small" :color="getStockColor(getItemStock(item))" variant="flat">
              {{ formatStock(item) }}
            </v-chip>
          </template>
          <template v-slot:item.stock_uom="{ item }">
            <span class="text-body-2">{{ item.stock_uom || item.uom || '-' }}</span>
          </template>
        </v-data-table>
      </div>

      <div v-if="items_view === 'card'" class="grid-view">
        <v-virtual-scroll :items="virtualRows" height="calc(100vh - 270px)" class="virtual-grid-scroll">
          <template v-slot:default="{ item: row }">
            <div class="virtual-grid-row">
              <div v-for="item in row" :key="item.item_code" class="virtual-grid-col">
                <v-card
                  @click="add_item(item)"
                  class="item-card"
                  :class="{ 'in-cart': isItemInCart(item) }"
                  hover
                >
                  <div class="card-image">
                    <v-img
                      :src="item.image || '/assets/highspeed_pos/js/hsposapp/components/pos/placeholder-image.png'"
                      cover
                    />
                    
                    <v-chip
                      v-if="item.has_variants"
                      size="x-small"
                      color="primary"
                      variant="tonal"
                      class="variant-badge"
                    >
                      <v-icon size="14">mdi-shape-plus</v-icon>
                    </v-chip>

                    <v-chip
                      v-if="getItemCartQty(item) > 0"
                      size="x-small"
                      color="success"
                      variant="flat"
                      class="cart-qty-badge"
                    >
                      <v-icon size="12" class="me-1">mdi-cart</v-icon>
                      {{ getItemCartQty(item) }}
                    </v-chip>
                  </div>
                  <v-card-text class="pa-3 d-flex flex-column justify-space-between flex-grow-1">
                    <div>
                      <div class="card-name text-center font-weight-bold mb-1" :title="item.item_name">{{ item.item_name }}</div>
                      <div class="card-price text-center mb-2">{{ currencySymbol(item.currency) }}{{ formatCurrency(item.rate) }}</div>
                    </div>
                    
                    <div class="card-footer-info d-flex justify-space-between align-center">
                      <span class="card-uom">{{ item.stock_uom }}</span>
                      
                      <span class="card-qty" :style="{ color: getStockColor(getItemStock(item)) }">
                        {{ __('Qty') }}: {{ formatStock(item) }}
                      </span>
                    </div>
                  </v-card-text>
                </v-card>
              </div>
              <div v-for="n in (columnsCount - row.length)" :key="'spacer-' + n" class="virtual-grid-col spacer"></div>
            </div>
          </template>
        </v-virtual-scroll>
      </div>

      <div v-if="!loading && filtered_items.length === 0" class="empty-state">
        <v-icon size="48" color="grey">mdi-package-variant</v-icon>
        <div class="mt-2">{{ __('No items found') }}</div>
      </div>
    </div>

    <div class="pagination-bar" v-if="totalPages > 1 && items_view !== 'card'">
      <div class="pagination-container">
        <div class="results-info">
          <span class="results-text">{{ startItem }}-{{ endItem }} {{ __('of') }} {{ filtered_items.length }}</span>
        </div>

        <div class="pagination-controls">
          <v-btn
            icon
            size="small"
            variant="text"
            :disabled="currentPage === 1"
            @click="goToFirstPage"
            class="nav-btn"
            :title="__('First Page')"
          >
            <v-icon size="18" :style="{ transform: isRTL ? 'rotate(180deg)' : 'none' }">mdi-page-first</v-icon>
          </v-btn>
          
          <v-btn
            icon
            size="small"
            variant="text"
            :disabled="currentPage === 1"
            @click="previousPage"
            class="nav-btn"
            :title="__('Previous Page')"
          >
            <v-icon size="18" :style="{ transform: isRTL ? 'rotate(180deg)' : 'none' }">mdi-chevron-left</v-icon>
          </v-btn>

          <div class="current-page-indicator">
            <span class="page-number">{{ currentPage }}</span>
            <span class="page-separator">{{ __('of') }}</span>
            <span class="total-pages">{{ totalPages }}</span>
          </div>

          <v-btn
            icon
            size="small"
            variant="text"
            :disabled="currentPage === totalPages"
            @click="nextPage"
            class="nav-btn"
            :title="__('Next Page')"
          >
            <v-icon size="18" :style="{ transform: isRTL ? 'rotate(180deg)' : 'none' }">mdi-chevron-right</v-icon>
          </v-btn>
          
          <v-btn
            icon
            size="small"
            variant="text"
            :disabled="currentPage === totalPages"
            @click="goToLastPage"
            class="nav-btn"
            :title="__('Last Page')"
          >
            <v-icon size="18" :style="{ transform: isRTL ? 'rotate(180deg)' : 'none' }">mdi-page-last</v-icon>
          </v-btn>
        </div>

        <div class="items-per-page">
          <v-select
            v-model="itemsPerPage"
            :items="[20, 50, 100, 200]"
            density="compact"
            variant="outlined"
            hide-details
            class="items-select"
            @update:model-value="currentPage = 1"
          >
            <template v-slot:selection="{ item }">
              <span class="selection-text">{{ item.value }}</span>
            </template>
          </v-select>
          <span class="per-page-label">{{ __('per page') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import format from "../../format";
import _ from "lodash";
import { getCachedItems, cacheItems } from "../../../offline";

export default {
  mixins: [format],
  
  data: () => ({
    pos_profile: "",
    flags: {},
    items_view: "list",
    item_group: "ALL",
    loading: false,
    items_group: ["ALL"],
    items: [],
    search: "",
    first_search: "",
    offersCount: 0,
    appliedOffersCount: 0,
    couponsCount: 0,
    appliedCouponsCount: 0,
    customer_price_list: null,
    customer: null,
    new_line: false,
    qty: 1,
    isRTL: false,
    scale_barcode_data: null,
    currentPage: 1,
    itemsPerPage: 20,
    uomDialog: false,
    selectedItemForUOM: null,
    availableUOMs: [],
    pendingQty: 1,
    scannerTimeout: null,
    windowWidth: typeof window !== 'undefined' ? window.innerWidth : 1200,
    cartItemsMap: {},
    in_stock_only: false,
    sort_by: "default",
  }),

  computed: {
    sortOptions() {
      return [
        { title: this.__("Default"), value: "default" },
        { title: this.__("Price: Low to High"), value: "price_asc" },
        { title: this.__("Price: High to Low"), value: "price_desc" },
        { title: this.__("Name: A to Z"), value: "name_asc" },
        { title: this.__("Stock: High to Low"), value: "stock_desc" }
      ];
    },

    filtered_items() {
      this.search = this.get_search(this.first_search);
      let result = this.items;

      if (this.item_group !== "ALL") {
        result = result.filter(item => 
          item.item_group && item.item_group.toLowerCase().includes(this.item_group.toLowerCase())
        );
      }

      if (this.search && this.search.length >= 1) {
        const searchTerm = this.search.trim();
        const searchLower = searchTerm.toLowerCase();
        const originalSearchTerm = this.first_search ? this.first_search.trim() : '';
        
        const isScaleBarcode = this.isScaleBarcode(originalSearchTerm);
        
        result = result.filter(item => {
          if (item.item_barcode && item.item_barcode.length > 0) {
            const exactBarcodeMatch = item.item_barcode.some(barcode => 
              barcode.barcode === originalSearchTerm
            );
            if (exactBarcodeMatch) return true;
          }
          
          if (isScaleBarcode && this.scale_barcode_data && this.scale_barcode_data.search_keys) {
            for (const key of this.scale_barcode_data.search_keys) {
              if (item.item_code === key) return true;
              
              if (item.item_barcode && item.item_barcode.some(b => b.barcode === key)) return true;
            }
          }
          
          if (!isScaleBarcode) {
            if (item.item_code === searchTerm) return true;
            
            if (item.item_name && item.item_name.toLowerCase().includes(searchLower)) return true;
            if (item.item_code && item.item_code.toLowerCase().includes(searchLower)) return true;
          }
          
          return false;
        });
      }

      if (this.in_stock_only) {
        result = result.filter(item => this.getItemStock(item) > 0);
      }

      if (this.sort_by === "price_asc") {
        result = [...result].sort((a, b) => (a.rate || 0) - (b.rate || 0));
      } else if (this.sort_by === "price_desc") {
        result = [...result].sort((a, b) => (b.rate || 0) - (a.rate || 0));
      } else if (this.sort_by === "name_asc") {
        result = [...result].sort((a, b) => (a.item_name || "").localeCompare(b.item_name || ""));
      } else if (this.sort_by === "stock_desc") {
        result = [...result].sort((a, b) => this.getItemStock(b) - this.getItemStock(a));
      }

      return result;
    },

    columnsCount() {
      const width = this.windowWidth;
      if (width >= 1600) return 6;
      if (width >= 1200) return 5;
      if (width >= 900) return 4;
      if (width >= 600) return 3;
      return 2;
    },

    virtualRows() {
      const columns = this.columnsCount;
      const rows = [];
      for (let i = 0; i < this.filtered_items.length; i += columns) {
        rows.push(this.filtered_items.slice(i, i + columns));
      }
      return rows;
    },

    totalPages() {
      return Math.ceil(this.filtered_items.length / this.itemsPerPage);
    },

    paginatedItems() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filtered_items.slice(start, end);
    },

    startItem() {
      if (this.filtered_items.length === 0) return 0;
      return ((this.currentPage - 1) * this.itemsPerPage) + 1;
    },

    endItem() {
      const end = this.currentPage * this.itemsPerPage;
      return end > this.filtered_items.length ? this.filtered_items.length : end;
    },

    debounce_search: {
      get() { return this.first_search; },
      set: _.debounce(function (value) { 
        this.first_search = value;
        
        if (value && value.length >= 8) {
          this.checkForBarcodeMatch(value);
        }
      }, 100),
    },
  },

  methods: {
    onResize() {
      this.windowWidth = window.innerWidth;
    },
    getItemCartQty(item) {
      if (!item || !item.item_code) return 0;
      return this.cartItemsMap[item.item_code] || 0;
    },
    isItemInCart(item) {
      return this.getItemCartQty(item) > 0;
    },
    detectRTL() {
      const lang = frappe.boot.lang || 'en';
      this.isRTL = ['ar', 'he', 'fa', 'ur'].includes(lang);
    },

    getGroupIcon(group) {
      const icons = {
        'ALL': 'mdi-view-grid', 'Food': 'mdi-food', 'Electronics': 'mdi-cellphone',
        'Clothing': 'mdi-tshirt-crew', 'Books': 'mdi-book', 'Tools': 'mdi-tools',
        'Medicine': 'mdi-medical-bag', 'Furniture': 'mdi-chair-rolling'
      };
      const key = Object.keys(icons).find(k => group.toLowerCase().includes(k.toLowerCase()));
      return icons[key] || 'mdi-package-variant';
    },

    getGroupDisplayName(group) {
      if (group === 'ALL') {
        return this.__('All');
      }
      const translated = this.__(group);
      return translated.length > 8 ? translated.substring(0, 8) + '...' : translated;
    },

    getStockColor(qty) {
      const actualQty = qty || 0;
      if (actualQty <= 0) return 'error';
      if (actualQty <= 5) return 'warning';
      return 'success';
    },

    getStockClass(qty) {
      if (qty <= 0) return 'stock-out';
      if (qty <= 5) return 'stock-low';
      return 'stock-ok';
    },

    getItemStock(item) {
      return item.actual_qty || 
             item.stock_qty || 
             item.qty_available || 
             item.available_qty ||
             item.warehouse_qty ||
             item.current_qty ||
             0;
    },

    formatStock(item) {
      const qty = this.getItemStock(item);
      if (qty === 0 && item.stock_details) {
        const stockQty = item.stock_details.actual_qty || item.stock_details.qty || 0;
        return this.formatNumber(stockQty);
      }
      return this.formatNumber(qty);
    },
    
    formatNumber(value) {
      if (value === null || value === undefined) return '0';
      const num = parseFloat(value);
      if (isNaN(num)) return '0';
      return num % 1 === 0 ? num.toString() : num.toFixed(2);
    },

    hasStock(item) {
      return item.actual_qty !== undefined || 
             item.stock_qty !== undefined || 
             item.qty_available !== undefined ||
             item.available_qty !== undefined;
    },

    formatFloat(value) {
      if (value === null || value === undefined) return '0';
      const num = parseFloat(value);
      return isNaN(num) ? '0' : num.toFixed(2).replace(/\.00$/, '');
    },

    selectItemGroup(group) {
      this.item_group = group;
      if (this.pos_profile.pose_use_limit_search) {
        this.get_items();
      }
    },

    clearSearch() {
      this.first_search = '';
      this.search = '';
      this.scale_barcode_data = null;
      this.currentPage = 1;
      
      if (this.scannerTimeout) {
        clearTimeout(this.scannerTimeout);
        this.scannerTimeout = null;
      }
      
      this.$refs.debounce_search.focus();
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
      }
    },

    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },

    goToFirstPage() {
      this.currentPage = 1;
    },

    goToLastPage() {
      this.currentPage = this.totalPages;
    },

    show_offers() { this.eventBus.emit("show_offers", "true"); },
    show_coupons() { this.eventBus.emit("show_coupons", "true"); },

    click_item_row(event, { item }) { 
      if (!item) {
        console.error('No item data in click_item_row');
        return;
      }
      this.add_item(item); 
    },

    add_item(item) {
      if (!item) {
        console.error('No item to add');
        return;
      }
      
      item = { ...item };
      
      if (item.has_variants === 1 || item.has_variants === true) {
        if (!this.eventBus) {
          console.error('EventBus not available');
          return;
        }
        
        if (!this.items || this.items.length === 0) {
          console.error('Items array not available');
          return;
        }
        
        try {
          this.eventBus.emit("open_variants_model", item, this.items);
          this.clearSearch();
        } catch (error) {
          console.error('Error opening variants dialog:', error);
        }
        return;
      }
      
      if (!item.qty) {
        if (this.scale_barcode_data && this.scale_barcode_data.qty) {
          this.pendingQty = this.scale_barcode_data.qty;
        } else {
          this.pendingQty = Math.abs(this.qty) || 1;
        }
      } else {
        this.pendingQty = item.qty;
      }
      
      this.checkAndShowUOMDialog(item);
    },
    
    async checkAndShowUOMDialog(item) {
      const hasUOMData = item.uom_list || item.uoms || item.has_multiple_uoms;
      
      if (hasUOMData) {
        this.showUOMDialog(item);
        return;
      }
      
      try {
        const response = await frappe.call({
          method: "frappe.client.get",
          args: {
            doctype: "Item",
            name: item.item_code,
            fields: ["uoms", "stock_uom", "sales_uom"]
          }
        });
        
        if (response.message && response.message.uoms && response.message.uoms.length > 0) {
          item.uom_list = response.message.uoms.map(u => ({
            uom: u.uom,
            conversion_factor: u.conversion_factor
          }));
          
          this.showUOMDialog(item);
          return;
        }
      } catch (error) {
        console.error("Could not fetch item UOM details:", error);
      }
      
      item.qty = this.pendingQty;
      
      if (this.scale_barcode_data) {
        this.scale_barcode_data = null;
      }
      
      try {
        this.eventBus.emit("add_item", item);
        this.qty = 1;
        this.pendingQty = 1;
        this.clearSearch();
      } catch (error) {
        console.error('Error adding item:', error);
      }
    },
    
    showUOMDialog(item) {
      this.selectedItemForUOM = { ...item };
      
      this.availableUOMs = item.uom_list || item.uoms || [];
      
      if (this.availableUOMs.length === 0) {
        item.qty = this.pendingQty;
        this.eventBus.emit("add_item", item);
        this.qty = 1;
        this.pendingQty = 1;
        if (this.scale_barcode_data) {
          this.scale_barcode_data = null;
        }
        this.clearSearch();
        return;
      }
      
      if (!this.availableUOMs.some(u => u.uom === (item.stock_uom || item.uom))) {
        this.availableUOMs.unshift({
          uom: item.stock_uom || item.uom,
          conversion_factor: 1,
          price_list_rate: item.rate
        });
      }
      
      if (this.availableUOMs.length <= 1) {
        item.qty = this.pendingQty;
        item.uom = this.availableUOMs[0].uom;
        item.conversion_factor = this.availableUOMs[0].conversion_factor || 1;
        this.eventBus.emit("add_item", item);
        this.qty = 1;
        this.pendingQty = 1;
        if (this.scale_barcode_data) {
          this.scale_barcode_data = null;
        }
        this.clearSearch();
        return;
      }
      
      this.clearSearch();
      this.uomDialog = true;
    },
    
    calculateUOMPrice(uom) {
      if (!this.selectedItemForUOM) return 0;
      
      const basePrice = this.selectedItemForUOM.rate || 0;
      const conversionFactor = uom.conversion_factor || 1;
      
      if (uom.price_list_rate) {
        return uom.price_list_rate;
      }
      
      return basePrice * conversionFactor;
    },
    
    calculateTotalPrice(uom) {
      return this.calculateUOMPrice(uom) * this.pendingQty;
    },
    
    selectUOM(uom) {
      if (!this.selectedItemForUOM) return;
      
      const itemToAdd = { ...this.selectedItemForUOM };
      itemToAdd.uom = uom.uom;
      itemToAdd.conversion_factor = uom.conversion_factor || 1;
      itemToAdd.qty = this.pendingQty;
      
      itemToAdd.rate = this.calculateUOMPrice(uom);
      
      try {
        this.eventBus.emit("add_item", itemToAdd);
        this.qty = 1;
        this.pendingQty = 1;
        this.closeUOMDialog();
      } catch (error) {
        console.error('Error adding item with UOM:', error);
      }
    },
    
    closeUOMDialog() {
      this.uomDialog = false;
      this.selectedItemForUOM = null;
      this.availableUOMs = [];
      this.pendingQty = 1;
      
      if (this.scale_barcode_data) {
        this.scale_barcode_data = null;
      }
    },
    
    getUOMIcon(uom) {
      const uomLower = (uom || '').toLowerCase();
      const icons = {
        'kg': 'mdi-weight-kilogram',
        'g': 'mdi-weight-gram',
        'gram': 'mdi-weight-gram',
        'lb': 'mdi-weight-pound',
        'oz': 'mdi-weight',
        'l': 'mdi-cup',
        'liter': 'mdi-cup',
        'ml': 'mdi-cup-water',
        'pcs': 'mdi-numeric',
        'piece': 'mdi-numeric',
        'unit': 'mdi-numeric-1-box',
        'box': 'mdi-package-variant',
        'carton': 'mdi-package-variant-closed',
        'pack': 'mdi-package',
        'dozen': 'mdi-numeric-12-box',
        'm': 'mdi-ruler',
        'meter': 'mdi-ruler',
        'cm': 'mdi-ruler',
        'ft': 'mdi-ruler',
        'in': 'mdi-ruler',
        'nos': 'mdi-numeric',
        'pair': 'mdi-numeric-2-box',
        'set': 'mdi-group',
      };
      
      for (const [key, icon] of Object.entries(icons)) {
        if (uomLower.includes(key)) return icon;
      }
      
      return 'mdi-tape-measure';
    },

    onSearchInput(value) {
      if (value && value.length >= 8 && /^\d+$/.test(value)) {
        if (this.scannerTimeout) {
          clearTimeout(this.scannerTimeout);
        }
        
        this.scannerTimeout = setTimeout(() => {
          this.checkForBarcodeMatch(value);
        }, 50);
      }
    },
    
    enter_event() {
      if (this.scannerTimeout) {
        clearTimeout(this.scannerTimeout);
        this.scannerTimeout = null;
      }
      
      if (this.filtered_items.length === 1) {
        this.add_item(this.filtered_items[0]);
        this.clearSearch();
      } 
      else if (this.paginatedItems.length === 1) {
        this.add_item(this.paginatedItems[0]);
        this.clearSearch();
      }
      else if (this.paginatedItems.length > 0) {
        this.add_item(this.paginatedItems[0]);
        this.clearSearch();
      }
    },

    checkForBarcodeMatch(searchTerm) {
      if (!searchTerm) return;
      
      searchTerm = searchTerm.trim();
      console.log('Checking for barcode match:', searchTerm);
      
      if (this.isScaleBarcode(searchTerm)) {
        
        console.log('Scale barcode detected');
        
        const barcode_info = this.parse_scale_barcode(searchTerm);
        console.log('Parsed barcode info:', barcode_info);
        
        if (barcode_info.search_keys && barcode_info.search_keys.length > 0) {
          let foundItem = null;
          
          for (const key of barcode_info.search_keys) {
            foundItem = this.items.find(item => {
              if (item.item_code === key) return true;
              
              if (item.item_barcode && item.item_barcode.length > 0) {
                return item.item_barcode.some(b => b.barcode === key);
              }
              
              return false;
            });
            
            if (foundItem) {
              console.log('Found item for scale barcode:', foundItem);
              break;
            }
          }
          
          if (foundItem) {
            const itemToAdd = { ...foundItem };
            itemToAdd.qty = barcode_info.qty;
            
            console.log('Adding item with scale quantity:', itemToAdd);
            this.add_item(itemToAdd);
            return;
          } else {
            console.log('No item found for scale barcode keys:', barcode_info.search_keys);
            setTimeout(() => {
              this.clearSearch();
            }, 500);
          }
        }
        
        return;
      }
      
      const exactMatch = this.items.find(item => {
        if (item.item_code === searchTerm) return true;
        
        if (item.item_barcode && item.item_barcode.length > 0) {
          return item.item_barcode.some(barcode => barcode.barcode === searchTerm);
        }
        return false;
      });
      
      if (exactMatch) {
        console.log('Exact barcode match found:', exactMatch);
        this.add_item(exactMatch);
      } else {
        if (searchTerm.length >= 8 && /^\d+$/.test(searchTerm)) {
          setTimeout(() => {
            this.clearSearch();
          }, 500);
        }
      }
    },
    
    search_onchange() {
      const searchTerm = this.first_search ? this.first_search.trim() : '';
      
      if (searchTerm.length >= 8 && /^\d+$/.test(searchTerm)) {
        this.checkForBarcodeMatch(searchTerm);
        return;
      }
      
      if (this.pos_profile.pose_use_limit_search) {
        this.get_items();
      } else {
        if (this.filtered_items.length === 1) {
          this.add_item(this.filtered_items[0]);
          this.clearSearch();
        }
      }
    },

    esc_event() { this.clearSearch(); },

    async get_items() {
      if (!this.pos_profile) return;
      
      const cacheKey = `items_${this.item_group}_${this.customer || ''}`;
      
      // If local storage caching is checked, load from IndexedDB first
      if (this.pos_profile.hspos_local_storage) {
        try {
          const cached = await getCachedItems(cacheKey);
          if (cached && cached.length > 0) {
            this.items = cached;
            this.eventBus.emit("set_all_items", this.items);
            // If offline, don't query the server, just stop here
            if (navigator && !navigator.onLine) {
              return;
            }
          }
        } catch (e) {
          console.error("IndexedDB error:", e);
        }
      }

      this.loading = true;
      
      frappe.call({
        method: "highspeed_pos.highspeed_pos.api.hsposapp.get_items",
        args: {
          pos_profile: this.pos_profile,
          price_list: this.customer_price_list,
          item_group: this.item_group === "ALL" ? "" : this.item_group.toLowerCase(),
          customer: this.customer,
        },
        callback: async (r) => {
          if (r.message) {
            this.items = r.message;
            this.eventBus.emit("set_all_items", this.items);
            
            // Cache them in IndexedDB
            if (this.pos_profile.hspos_local_storage) {
              try {
                await cacheItems(cacheKey, this.items);
              } catch (e) {
                console.error("Failed to update IndexedDB items cache:", e);
              }
            }
          }
          this.loading = false;
        },
      });
    },
    
    async fetchItemUOMs() {
      if (!this.items || this.items.length === 0) return;
      
      const hasUOMData = this.items.some(item => item.uom_list && item.uom_list.length > 0);
      if (hasUOMData) {
        console.log("Items already have UOM data");
        return;
      }
      
      try {
        if (this.pos_profile && this.pos_profile.name) {
          const response = await frappe.call({
            method: "highspeed_pos.highspeed_pos.api.hsposapp.get_item_uoms",
            args: {
              items: this.items.map(item => item.item_code)
            }
          });
          
          if (response.message) {
            this.items = this.items.map(item => {
              if (response.message[item.item_code]) {
                item.uom_list = response.message[item.item_code];
              }
              return item;
            });
          }
        }
      } catch (error) {
        console.log("Could not fetch UOM details, continuing without them");
      }
    },

    async fetchStockData() {
      if (!this.items || this.items.length === 0) return;
      
      try {
        const itemCodes = this.items.map(item => item.item_code);
        const response = await frappe.call({
          method: "erpnext.stock.dashboard.item_dashboard.get_data",
          args: {
            item_code: itemCodes,
            warehouse: this.pos_profile.warehouse || null
          }
        });
        
        if (response.message) {
          this.items = this.items.map(item => {
            const stockData = response.message.find(s => s.item_code === item.item_code);
            return {
              ...item,
              actual_qty: stockData ? stockData.actual_qty : 0
            };
          });
        }
      } catch (error) {
        console.error("Error fetching stock data:", error);
      }
    },

    get_items_groups() {
      this.items_group = ["ALL"];
      
      if (this.pos_profile?.item_groups?.length > 0) {
        this.pos_profile.item_groups.forEach(element => {
          if (element.item_group && element.item_group !== "All Item Groups") {
            if (!this.items_group.includes(element.item_group)) {
              this.items_group.push(element.item_group);
            }
          }
        });
      }
      
      if (this.items_group.length === 1 && this.items.length > 0) {
        const uniqueGroups = [...new Set(this.items.map(item => item.item_group).filter(group => group))];
        this.items_group = ["ALL", ...uniqueGroups];
      }
    },

    getItemsHeaders() {
      const headers = [
        { title: this.__("Code"), key: "item_code", width: "15%" },
        { title: this.__("Item"), key: "item_name", width: "35%" },
        { title: this.__("Price"), key: "rate", width: "15%" },
        { title: this.__("Stock"), key: "actual_qty", width: "15%" },
        { title: this.__("UOM"), key: "stock_uom", width: "20%" }
      ];
      return headers;
    },

    get_search(first_search) {
      if (!first_search) return first_search;
      
      const searchTerm = first_search.trim();
      
      if (this.isScaleBarcode(searchTerm)) {
        const barcode_info = this.parse_scale_barcode(searchTerm);
        if (barcode_info.search_keys && barcode_info.search_keys.length > 0) {
          return searchTerm;
        }
      }
      
      return searchTerm;
    },

    getScaleBarcodePrefixes() {
      const prefixes = ['99', '91'];
      if (this.pos_profile && this.pos_profile.hspos_scale_barcode_start) {
        const custom_prefix = this.pos_profile.hspos_scale_barcode_start.toString().trim();
        if (custom_prefix) {
          prefixes.push(custom_prefix);
        }
      }
      return [...new Set(prefixes)];
    },

    isScaleBarcode(barcode) {
      if (!barcode || (barcode.length !== 12 && barcode.length !== 13)) return false;
      const prefixes = this.getScaleBarcodePrefixes();
      return prefixes.some(prefix => barcode.startsWith(prefix));
    },

    parse_scale_barcode(barcode) {
      const result = {
        item_code: null,
        qty: null,
        rate: null,
        search_keys: []
      };
      
      if (!this.isScaleBarcode(barcode)) {
        return result;
      }
      
      let workingBarcode = barcode;
      if (barcode.length === 13) {
        workingBarcode = barcode.slice(0, -1);
      }
      
      try {
        const value_str = workingBarcode.slice(-5);
        const value = parseFloat(value_str);
        
        const prefixes = this.getScaleBarcodePrefixes();
        let matchedPrefix = "";
        for (const prefix of prefixes) {
          if (workingBarcode.startsWith(prefix)) {
            matchedPrefix = prefix;
            break;
          }
        }
        
        const prefix_len = matchedPrefix.length;
        const code_with_prefix = workingBarcode.slice(0, -5);
        const code_without_prefix = workingBarcode.slice(prefix_len, -5);
        const parsed_int_code = parseInt(code_without_prefix, 10).toString();
        
        result.search_keys = [
          code_with_prefix,
          code_without_prefix,
          parsed_int_code
        ];
        
        result.search_keys = [...new Set(result.search_keys.filter(k => k))];
        
        // Calculate quantity based on Scale Barcode Type setting
        if (this.pos_profile && this.pos_profile.hspos_scale_barcode_type === 'Price-Based') {
          let foundItem = null;
          for (const key of result.search_keys) {
            foundItem = this.items.find(item => {
              if (item.item_code === key) return true;
              if (item.item_barcode && item.item_barcode.length > 0) {
                return item.item_barcode.some(b => b.barcode === key);
              }
              return false;
            });
            if (foundItem) break;
          }
          const price = value / 100.0;
          const rate = foundItem ? (parseFloat(foundItem.rate) || 1.0) : 1.0;
          result.qty = price / rate;
          console.log('Price-based scale barcode calculated:', { price, rate, calculated_qty: result.qty });
        } else {
          // Weight-based (Default)
          result.qty = value / 1000.0;
        }
        
        this.scale_barcode_data = result;
        
        console.log('Parsed scale barcode:', {
          original_barcode: barcode,
          working_barcode: workingBarcode,
          matched_prefix: matchedPrefix,
          search_keys: result.search_keys,
          qty: result.qty
        });
        
      } catch (error) {
        console.error('Error parsing scale barcode:', error);
      }
      
      return result;
    },

    getUOMColor(index) {
      const colors = [
        'primary',
        'secondary', 
        'success',
        'warning',
        'error',
        'info'
      ];
      return colors[index % colors.length];
    },

    getSortLabel(sortBy) {
      const option = this.sortOptions.find(o => o.value === sortBy);
      return option ? option.title : this.__("Sort");
    },
    
    __: window.__ || ((str) => str),
  },

  watch: {
    customer() { this.get_items(); },
    new_line() { this.eventBus.emit("set_new_line", this.new_line); },
    items: {
      handler() {
        this.get_items_groups();
      },
      deep: true
    },
    filtered_items() {
      this.currentPage = 1;
    },
  },

  created() {
    this.detectRTL();
    
    this.eventBus.on("register_pos_profile", (data) => {
      this.pos_profile = data.pos_profile;
      
      this.items_view = data.pos_profile.hspos_default_card_view ? "card" : "list";
      this.get_items();
      this.get_items_groups();
    });

    this.eventBus.on("set_all_items", (items) => {
      // Set all items handler
    });

    this.eventBus.on("update_offers_counters", (data) => {
      this.offersCount = data.offersCount;
      this.appliedOffersCount = data.appliedOffersCount;
    });

    this.eventBus.on("update_coupons_counters", (data) => {
      this.couponsCount = data.couponsCount;
      this.appliedCouponsCount = data.appliedCouponsCount;
    });

    this.eventBus.on("update_customer", (customer) => {
      this.customer = customer;
    });

    this.eventBus.on("update_customer_price_list", (priceList) => {
      this.customer_price_list = priceList;
    });

    this.eventBus.on("cart_items_updated", (cartItems) => {
      const map = {};
      if (cartItems && cartItems.length > 0) {
        cartItems.forEach(item => {
          if (item.item_code) {
            map[item.item_code] = (map[item.item_code] || 0) + (item.qty || 0);
            if (item.variant_of) {
              map[item.variant_of] = (map[item.variant_of] || 0) + (item.qty || 0);
            }
          }
        });
      }
      this.cartItemsMap = map;
    });
  },

  mounted() {
    window.addEventListener('resize', this.onResize);
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.onResize);
  },
};
</script>

<style scoped>
.items-selector {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
}

.controls-row {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.controls-container {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.search-field-container {
  padding: 12px 16px;
  flex-shrink: 0;
  background: transparent;
  border-bottom: none;
  overflow: visible;
}

.search-field-direct {
  margin: 0 !important;
}

.search-field-direct :deep(.v-field) {
  border-radius: 20px !important;
  border: 1px solid rgba(0,0,0,0.05) !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
  background: white !important;
  transition: all 0.3s ease !important;
}

.search-field-direct :deep(.v-field--focused) {
  border-color: #0097A7 !important;
  box-shadow: 0 4px 20px rgba(0, 151, 167, 0.12) !important;
}

.search-field-direct :deep(.v-input__details) {
  display: none !important;
}

.search-field-direct :deep(.v-field) {
  background: #faf7c7  !important;
  border: none !important;
  border-radius: 0 !important;
  height: 40px !important;
}

.search-field-direct :deep(.v-field__field) {
  height: 40px !important;
}

.search-field-direct :deep(.v-field__outline) {
  display: none !important;
}

.search-field-direct :deep(.v-field:hover) {
  background: #faf7c7 !important;
}

.search-field-direct :deep(.v-field--focused) {
  background: #faf7c7 !important;
}

.search-field-direct :deep(.v-field__input) {
  font-size: 0.875rem !important;
  padding: 0 !important;
  min-height: 40px !important;
  display: flex;
  align-items: center;
}

.search-field-direct :deep(.v-field__prepend-inner) {
  padding: 0 8px 0 12px !important;
  align-items: center !important;
  display: flex !important;
  height: 40px !important;
}

.search-field-direct :deep(.v-field__append-inner) {
  padding: 0 12px 0 0 !important;
  align-items: center !important;
  display: flex !important;
  height: 40px !important;
}

.search-field-direct :deep(.v-icon) {
  color: #666;
  opacity: 0.7;
}

.search-field-direct :deep(.v-label) {
  font-size: 0.813rem !important;
  line-height: 40px !important;
  top: 0 !important;
  transform: none !important;
}

.search-field-direct :deep(.v-field-label--floating) {
  --v-field-label-scale: 0.75em;
  top: 6px !important;
  line-height: normal !important;
}

.groups-row {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.groups-container {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 4px 8px 12px 8px;
  scrollbar-width: thin;
  -ms-overflow-style: none;
}

.groups-container::-webkit-scrollbar {
  height: 4px;
}

.groups-container::-webkit-scrollbar-thumb {
  background: rgba(0, 151, 167, 0.2);
  border-radius: 2px;
}

.group-btn {
  min-width: 90px !important;
  height: 38px !important;
  flex-shrink: 0;
  font-size: 0.8rem !important;
  border-radius: 4px !important;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
  border: 1px solid rgba(0, 151, 167, 0.15) !important;
  font-family: 'Cairo', sans-serif !important;
  font-weight: 600 !important;
}

.group-btn:not(.v-btn--variant-flat) {
  background: white !important;
  color: #4a5568 !important;
}

.group-btn.v-btn--variant-flat {
  background: linear-gradient(90deg, #075294 0%, #0097A7 100%) !important;
  color: white !important;
  box-shadow: 0 4px 15px rgba(0, 151, 167, 0.25) !important;
}

.group-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 151, 167, 0.15) !important;
}

.group-icon {
  margin-right: 6px;
}

.group-label {
  font-weight: 600;
}

.qty-field {
  width: 80px;
}

.qty-field :deep(.v-field__input) {
  text-align: center;
  font-size: 0.9rem;
}

.new-line-check :deep(.v-label) {
  font-size: 0.75rem;
}

.in-stock-check :deep(.v-label) {
  font-size: 0.75rem;
}

.view-toggle {
  height: 36px;
}

.view-toggle :deep(.v-btn) {
  min-width: 36px !important;
  height: 36px !important;
}

.action-btn {
  height: 36px !important;
  min-width: 80px !important;
  font-size: 0.8rem !important;
}

.action-text {
  margin-left: 6px;
  font-weight: 500;
}

.search-info {
  display: flex;
  align-items: center;
  min-height: 36px;
  gap: 8px;
}

.items-count {
  font-size: 0.85rem;
  color: #666;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 8px;
}

.items-content {
  flex: 1;
  overflow: hidden;
  background: white;
  margin: 0 !important;
  padding: 0 !important;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.list-view {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.items-table {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.items-table :deep(.v-table__wrapper) {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: #ccc #f5f5f5;
}

.items-table :deep(.v-table__wrapper::-webkit-scrollbar) {
  width: 8px;
}

.items-table :deep(.v-table__wrapper::-webkit-scrollbar-track) {
  background: #f5f5f5;
}

.items-table :deep(.v-table__wrapper::-webkit-scrollbar-thumb) {
  background-color: #ccc;
  border-radius: 4px;
}

.items-table :deep(.v-table__wrapper::-webkit-scrollbar-thumb:hover) {
  background-color: #999;
}

.items-table :deep(.v-data-table__td) {
  padding: 6px 10px !important;
  height: 48px !important;
}

.item-code-cell {
  font-family: monospace;
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
}

.item-name-wrapper {
  display: flex;
  align-items: center;
}

.item-name {
  font-weight: 700;
  font-size: 0.85rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.item-code {
  font-size: 0.75rem;
  color: #666;
  font-family: monospace;
}

.price {
  font-weight: 600;
  color: #1976d2;
  font-size: 0.85rem;
}

.grid-view {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px;
  scrollbar-width: thin;
  scrollbar-color: #ccc #f5f5f5;
}

.grid-view::-webkit-scrollbar {
  width: 8px;
}

.grid-view::-webkit-scrollbar-track {
  background: #f5f5f5;
}

.grid-view::-webkit-scrollbar-thumb {
  background-color: #ccc;
  border-radius: 4px;
}

.grid-view::-webkit-scrollbar-thumb:hover {
  background-color: #999;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
}

.item-card {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
  border-radius: 4px !important;
  min-height: 180px;
  background: #ffffff !important;
  border: 1px solid rgba(0, 0, 0, 0.08) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  overflow: hidden;
}

.item-card:hover {
  transform: translateY(-3px) scale(1.02);
  background: #ffffff !important;
  border-color: #0097A7 !important;
  box-shadow: 0 8px 20px rgba(0, 151, 167, 0.15) !important;
}

.item-card.in-cart {
  border: 2px solid #0097A7 !important;
  background: rgba(255, 255, 255, 0.95) !important;
  box-shadow: 0 6px 20px rgba(0, 151, 167, 0.12) !important;
}

.cart-qty-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 0.75rem !important;
  font-weight: 700;
  height: 20px !important;
  min-width: 24px !important;
  padding: 0 6px !important;
  border-radius: 3px !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  z-index: 2;
}

.card-image {
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 95px;
  flex-shrink: 0;
  border-top-left-radius: 4px !important;
  border-top-right-radius: 4px !important;
  border-bottom-left-radius: 0 !important;
  border-bottom-right-radius: 0 !important;
}

@media (max-width: 900px) {
  .item-card {
    min-height: 160px;
  }
  .card-image {
    height: 80px;
  }
}

.card-image :deep(.v-img) {
  height: 100%;
  width: 100%;
  transition: transform 0.5s ease !important;
}

.item-card:hover .card-image :deep(.v-img) {
  transform: scale(1.08) !important;
}

.card-qty {
  font-size: 0.7rem;
  font-weight: 600;
  display: inline-block;
  padding: 1px 2px;
}

.variant-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 0.7rem !important;
  height: 20px !important;
  min-width: 24px !important;
  padding: 0 6px !important;
  border-radius: 3px !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.card-name {
  font-weight: 600;
  font-size: 0.75rem;
  color: #2d3748;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'Cairo', sans-serif !important;
}

.card-price {
  font-weight: 700;
  color: #0097A7;
  font-size: 0.95rem;
  margin-bottom: 2px;
  font-family: 'Inter', sans-serif !important;
}

.card-uom {
  font-size: 0.7rem;
  color: #718096;
  font-weight: 500;
  background: rgba(0,0,0,0.03);
  display: inline-block;
  padding: 1px 6px;
  border-radius: 4px;
}

.stock-ok { color: #2e7d32; font-weight: bold; }
.stock-low { color: #ef6c00; font-weight: bold; }
.stock-out { color: #c62828; font-weight: bold; }

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666;
}

.pagination-bar {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-top: 1px solid #dee2e6;
  flex-shrink: 0;
  padding: 8px 16px;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.05);
}

.pagination-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 100%;
  gap: 16px;
}

.results-info {
  display: flex;
  align-items: center;
  min-width: fit-content;
}

.results-text {
  font-size: 0.813rem;
  color: #495057;
  font-weight: 500;
  white-space: nowrap;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  justify-content: center;
}

.nav-btn {
  width: 36px !important;
  height: 36px !important;
  border-radius: 4px !important;
  color: #6c757d !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  background: rgba(255, 255, 255, 0.7) !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
}

.nav-btn:hover:not(:disabled) {
  color: #1976d2 !important;
  background: rgba(25, 118, 210, 0.04) !important;
  border-color: rgba(25, 118, 210, 0.2) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.15);
}

.nav-btn:disabled {
  color: #adb5bd !important;
  background: rgba(248, 249, 250, 0.5) !important;
  border-color: transparent !important;
  cursor: not-allowed;
}

.nav-btn :deep(.v-btn__content) {
  opacity: 1;
}

.current-page-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(25, 118, 210, 0.08);
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid rgba(25, 118, 210, 0.2);
  margin: 0 8px;
}

.page-number {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1976d2;
  min-width: 20px;
  text-align: center;
}

.page-separator {
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: 500;
}

.total-pages {
  font-size: 0.875rem;
  font-weight: 600;
  color: #495057;
  min-width: 20px;
  text-align: center;
}

.items-per-page {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: fit-content;
}

.items-select {
  min-width: 65px;
  max-width: 80px;
}

.items-select :deep(.v-field) {
  background: rgba(255, 255, 255, 0.9) !important;
  border-radius: 3px !important;
  min-height: 32px !important;
  font-size: 0.813rem !important;
}

.items-select :deep(.v-field__input) {
  font-size: 0.813rem !important;
  font-weight: 600 !important;
  color: #495057 !important;
  text-align: center !important;
  padding: 0 4px !important;
  min-height: 32px !important;
}

.items-select :deep(.v-field__append-inner) {
  padding: 0 6px !important;
}

.items-select :deep(.v-icon) {
  font-size: 16px !important;
  color: #6c757d !important;
}

.selection-text {
  font-weight: 600;
  color: #495057;
}

.per-page-label {
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: 500;
  white-space: nowrap;
}

.pagination-controls .nav-btn,
.current-page-indicator,
.items-select {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

[dir="rtl"] .price,
[dir="rtl"] .card-price {
  direction: ltr;
  text-align: right;
}

[dir="rtl"] .stock-badge {
  right: auto;
  left: 4px;
}

[dir="rtl"] .group-icon {
  margin-right: 0;
  margin-left: 6px;
}

[dir="rtl"] .action-text {
  margin-left: 0;
  margin-right: 6px;
}

[dir="rtl"] .search-field-direct :deep(.v-field__prepend-inner) {
  padding-right: 0;
  padding-left: 12px;
}

[dir="rtl"] .pagination-container {
  direction: rtl;
}

[dir="rtl"] .results-info {
  order: 3;
}

[dir="rtl"] .pagination-controls {
  order: 2;
}

[dir="rtl"] .items-per-page {
  order: 1;
}

@media (max-width: 1200px) {
  .controls-container {
    gap: 8px;
  }
  
  .action-btn {
    min-width: 70px !important;
    font-size: 0.75rem !important;
  }
  
  .action-text {
    font-size: 0.75rem;
  }
  
  .group-btn {
    min-width: 70px !important;
    height: 34px !important;
  }
  
  .pagination-container {
    gap: 12px;
  }
  
  .nav-btn {
    width: 32px !important;
    height: 32px !important;
  }
}

@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 6px;
  }
  
  .action-text {
    display: none;
  }
  
  .action-btn {
    min-width: 40px !important;
  }
  
  .group-btn {
    min-width: 60px !important;
    height: 32px !important;
  }
  
  .group-label {
    font-size: 0.65rem;
  }
  
  .pagination-container {
    flex-direction: column;
    gap: 8px;
    align-items: center;
  }
  
  .results-info {
    order: 1;
  }
  
  .pagination-controls {
    order: 2;
    gap: 2px;
  }
  
  .items-per-page {
    order: 3;
  }
  
  .nav-btn {
    width: 28px !important;
    height: 28px !important;
  }
  
  .current-page-indicator {
    padding: 4px 8px;
    margin: 0 4px;
  }
  
  .page-number,
  .total-pages {
    font-size: 0.8rem;
  }
  
  .page-separator {
    font-size: 0.7rem;
  }
}

@media (max-width: 480px) {
  .group-label {
    display: none;
  }
  
  .group-btn {
    min-width: 40px !important;
    height: 30px !important;
  }
  
  .group-icon {
    margin: 0;
  }
  
  .action-btn {
    min-width: 36px !important;
    height: 32px !important;
  }
  
  .controls-container {
    gap: 6px;
    padding: 0 8px;
  }
  
  .per-page-label {
    display: none;
  }
  
  .results-text {
    font-size: 0.75rem;
  }
  
  .pagination-bar {
    padding: 6px 8px;
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.pagination-bar {
  animation: slideIn 0.3s ease-out;
}

.nav-btn:active {
  transform: translateY(0) !important;
  box-shadow: 0 2px 6px rgba(25, 118, 210, 0.2) !important;
}

.current-page-indicator {
  position: relative;
  overflow: hidden;
}

.current-page-indicator::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

.uom-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.uom-btn {
  text-transform: none !important;
  flex-direction: column !important;
  padding: 12px !important;
}

.uom-btn :deep(.v-btn__content) {
  flex-direction: column !important;
  width: 100%;
}

.v-dialog {
  z-index: 2000 !important;
}

.uom-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.uom-btn {
  height: auto !important;
  padding: 12px 16px !important;
  text-transform: none !important;
  letter-spacing: normal !important;
}

.uom-btn-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 12px;
}

.uom-name {
  font-size: 1rem;
  font-weight: 500;
}

.uom-price {
  font-size: 1.1rem;
  font-weight: 700;
  margin-left: auto;
}

.uom-factor {
  font-size: 0.85rem;
  opacity: 0.9;
  font-weight: 500;
  padding: 2px 8px;
  background: rgba(255,255,255,0.2);
  border-radius: 3px;
}

.v-btn--variant-flat {
  color: white !important;
}

.v-btn--variant-flat .uom-btn-content > * {
  color: white !important;
}

@media (max-width: 400px) {
  .v-dialog {
    margin: 16px !important;
  }
}

[dir="rtl"] .uom-btn-content {
  flex-direction: row-reverse;
}

[dir="rtl"] .uom-price {
  margin-left: 0;
  margin-right: auto;
}

/* HIGHSPEED POS Virtual Grid Styles */
.virtual-grid-scroll {
  overflow-y: auto;
  padding: 4px;
}

.virtual-grid-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.virtual-grid-col {
  flex: 1 1 0px;
  min-width: 0;
}

.virtual-grid-col.spacer {
  visibility: hidden;
  height: 0;
  pointer-events: none;
}
</style>