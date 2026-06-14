<template>
  <v-row justify="center">
    <v-dialog v-model="varaintsDialog" max-width="700px" width="100%" scrollable :dir="isRTL ? 'rtl' : 'ltr'">
      <v-card class="variants-card">
        <v-card-title class="dialog-header">
          <div class="header-content">
            <v-icon size="24" color="white" class="header-icon">mdi-shape-plus</v-icon>
            <span class="dialog-title"><bdi>{{ parentItem ? parentItem.item_name : __('Select Item') }}</bdi></span>
          </div>
          <v-spacer></v-spacer>
          <v-btn 
            icon 
            variant="text" 
            @click="close_dialog"
            class="close-btn"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-divider></v-divider>
        
        <v-card-text class="pa-0 scrollable-content">
          <v-container v-if="parentItem" class="variants-container">
            <!-- Attributes Section -->
            <div class="attributes-section" v-if="availableAttributes && availableAttributes.length">
              <v-row class="ma-0 pa-0">
                <v-col 
                  v-for="(attr, index) in availableAttributes" 
                  :key="attr.attribute"
                  cols="6"
                  class="pa-2"
                >
                  <div class="attribute-header">
                    <v-icon size="14" class="attribute-icon">
                      {{ getAttributeIcon(attr.attribute) }}
                    </v-icon>
                    <span class="attribute-name">{{ attr.attribute }}</span>
                  </div>
                  
                  <v-chip-group 
                    v-model="filters[attr.attribute]" 
                    selected-class="chip-selected"
                    class="attribute-chips"
                    column
                  >
                    <v-chip 
                      v-for="value in attr.values" 
                      :key="value.abbr || value.attribute_value" 
                      :value="value.attribute_value"
                      variant="outlined"
                      label
                      class="attribute-chip"
                      @click="updateFiltredItems"
                    >
                      <v-icon size="16" start v-if="filters[attr.attribute] === value.attribute_value">
                        mdi-check
                      </v-icon>
                      <bdi>{{ value.attribute_value }}</bdi>
                    </v-chip>
                  </v-chip-group>
                </v-col>
              </v-row>
            </div>

            <!-- Results Count -->
            <div class="results-info">
              <v-icon size="20" color="grey-darken-1">mdi-filter-variant</v-icon>
              <span>{{ filterdItems.length }} {{ filterdItems.length === 1 ? __('item') : __('items') }}</span>
            </div>

            <!-- Items Grid -->
            <div class="items-section">
              <!-- If there are variants -->
              <v-row v-if="filterdItems.length > 0" class="items-grid">
                <v-col 
                  v-for="(item, idx) in filterdItems" 
                  :key="idx" 
                  xl="3" 
                  lg="3" 
                  md="3" 
                  sm="4" 
                  cols="6"
                >
                  <v-card 
                    class="variant-item-card"
                    :class="{ 'no-image': !item.image }"
                    hover
                    @click.stop="add_item(item)"
                  >
                    <!-- Render image wrapper ONLY if item has image -->
                    <div v-if="item.image" class="item-image-wrapper">
                      <v-img 
                        :src="item.image"
                        class="item-image"
                        cover
                        height="100"
                      >
                        <template v-slot:placeholder>
                          <v-row class="fill-height ma-0" align="center" justify="center">
                            <v-progress-circular indeterminate color="grey-lighten-3"></v-progress-circular>
                          </v-row>
                        </template>
                      </v-img>
                      
                      <!-- Stock Badge -->
                      <v-chip 
                        v-if="item.actual_qty !== undefined"
                        size="x-small"
                        :color="getStockColor(item.actual_qty)"
                        class="stock-badge"
                      >
                        <v-icon size="12" start>mdi-package-variant</v-icon>
                        {{ formatStock(item.actual_qty) }}
                      </v-chip>
                    </div>
                    
                    <v-card-text class="item-details d-flex flex-column justify-space-between fill-height pa-3">
                      <div>
                        <div class="d-flex justify-space-between align-start mb-1">
                          <div class="item-name font-weight-bold" :title="item.item_name"><bdi>{{ item.item_name }}</bdi></div>
                          <!-- Stock badge inline for cards without images -->
                          <v-chip 
                            v-if="!item.image && item.actual_qty !== undefined"
                            size="x-small"
                            :color="getStockColor(item.actual_qty)"
                            variant="tonal"
                            class="stock-badge-inline"
                          >
                            <v-icon size="10" start>mdi-package-variant</v-icon>
                            {{ formatStock(item.actual_qty) }}
                          </v-chip>
                        </div>
                        <div class="item-code text-caption text-grey" dir="ltr">{{ item.item_code }}</div>
                        
                        <!-- Attribute pills -->
                        <div v-if="item.item_attributes && item.item_attributes.length" class="card-attributes mt-1 mb-2">
                          <v-chip
                            v-for="attr in item.item_attributes"
                            :key="attr.attribute"
                            size="x-small"
                            color="secondary"
                            variant="tonal"
                            class="attribute-pill"
                          >
                            <bdi>{{ attr.attribute_value }}</bdi>
                          </v-chip>
                        </div>
                      </div>
                      
                      <div class="item-footer d-flex justify-space-between align-center mt-2">
                        <div class="item-price">
                          <span class="price text-primary font-weight-bold">{{ formatCurrency(item.rate || 0) }}</span>
                          <span class="currency text-caption text-grey ms-1">{{ item.currency || 'SAR' }}</span>
                        </div>
                        <v-chip size="x-small" variant="outlined" color="grey">
                          {{ item.stock_uom || 'Unit' }}
                        </v-chip>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
              
              <!-- If there are no variants but the item has variants -->
              <div v-else-if="parentItem.has_variants" class="single-item-state">
                <v-card 
                  class="variant-item-card mx-auto"
                  :class="{ 'no-image': !parentItem.image }"
                  hover
                  @click.stop="add_item(parentItem)"
                  style="max-width: 300px;"
                >
                  <div v-if="parentItem.image" class="item-image-wrapper">
                    <v-img 
                      :src="parentItem.image"
                      class="item-image"
                      cover
                      height="100"
                    >
                    </v-img>
                  </div>
                  
                  <v-card-text class="item-details d-flex flex-column justify-space-between fill-height pa-3">
                    <div>
                      <div class="item-name font-weight-bold"><bdi>{{ parentItem.item_name }}</bdi></div>
                      <div class="item-code text-caption text-grey" dir="ltr">{{ parentItem.item_code }}</div>
                    </div>
                    
                    <div class="item-footer d-flex justify-space-between align-center mt-2">
                      <div class="item-price">
                        <span class="price text-primary font-weight-bold">{{ formatCurrency(parentItem.rate || 0) }}</span>
                        <span class="currency text-caption text-grey ms-1">{{ parentItem.currency || 'SAR' }}</span>
                      </div>
                      <v-chip size="x-small" variant="outlined" color="grey">
                        {{ parentItem.stock_uom || 'Unit' }}
                      </v-chip>
                    </div>
                  </v-card-text>
                </v-card>
                
                <p class="text-center mt-4 text-grey">{{ __('Click to add this item') }}</p>
              </div>
              
              <!-- Empty State -->
              <div v-else class="empty-state">
                <v-icon size="64" color="grey-lighten-1">mdi-package-variant-closed</v-icon>
                <p class="empty-text">{{ __('No matching items found') }}</p>
                <v-btn 
                  variant="text" 
                  color="primary" 
                  @click="resetFilters"
                  size="small"
                >
                  <v-icon start>mdi-refresh</v-icon>
                  {{ __('Reset Filters') }}
                </v-btn>
              </div>
            </div>
          </v-container>
          
          <!-- Loading State -->
          <div v-else class="loading-state">
            <v-progress-circular indeterminate color="primary" size="40"></v-progress-circular>
            <p class="loading-text">{{ __('Loading...') }}</p>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
export default {
  data: () => ({
    varaintsDialog: false,
    parentItem: null,
    items: null,
    filters: {},
    filterdItems: [],
    isRTL: false,
  }),

  computed: {
    variantsItems() {
      if (!this.parentItem || !this.items) {
        return [];
      }
      
      // Search for variants using different methods
      let variants = [];
      
      // First method: search by variant_of
      variants = this.items.filter(
        (item) => item.variant_of === this.parentItem.item_code
      );
      
      // If no variants found, try template
      if (variants.length === 0) {
        variants = this.items.filter(
          (item) => item.item_template === this.parentItem.item_code
        );
      }
      
      // If no variants found, try has_variants
      if (variants.length === 0 && this.parentItem.has_variants) {
        // Find by name, excluding the parent template item itself and other template items
        variants = this.items.filter(
          (item) => 
            item.item_code !== this.parentItem.item_code && 
            !item.has_variants && 
            item.item_name && 
            item.item_name.includes(this.parentItem.item_name)
        );
      }
      
      console.log('Parent item:', this.parentItem);
      console.log('Found variants:', variants);
      
      return variants;
    },

    availableAttributes() {
      if (!this.parentItem || !this.parentItem.attributes) {
        return [];
      }
      
      // Deep copy the parent attributes list
      const attributes = JSON.parse(JSON.stringify(this.parentItem.attributes));
      
      // Find all attribute values that actually exist among our variants
      const activeValuesByAttr = {};
      this.variantsItems.forEach(variant => {
        if (variant.item_attributes) {
          variant.item_attributes.forEach(attr => {
            const attrName = attr.attribute;
            const attrVal = attr.attribute_value;
            if (attrName && attrVal) {
              if (!activeValuesByAttr[attrName]) {
                activeValuesByAttr[attrName] = new Set();
              }
              activeValuesByAttr[attrName].add(attrVal.trim().toLowerCase());
            }
          });
        }
      });
      
      // Filter each attribute's values to only include the active ones
      return attributes.map(attr => {
        const activeVals = activeValuesByAttr[attr.attribute] || new Set();
        attr.values = (attr.values || []).filter(val => {
          const valName = val.attribute_value;
          return valName && activeVals.has(valName.trim().toLowerCase());
        });
        return attr;
      }).filter(attr => attr.values.length > 0);
    },
  },

  methods: {
    detectRTL() {
      const lang = frappe.boot.lang || 'en';
      this.isRTL = ['ar', 'he', 'fa', 'ur'].includes(lang);
    },

    getAttributeIcon(attribute) {
      const iconMap = {
        'اللون': 'mdi-palette',
        'Color': 'mdi-palette',
        'الحجم': 'mdi-resize',
        'Size': 'mdi-resize',
        'المقاس': 'mdi-ruler',
        'النوع': 'mdi-shape',
        'Type': 'mdi-shape',
        'المادة': 'mdi-cube-outline',
        'Material': 'mdi-cube-outline',
      };
      return iconMap[attribute] || 'mdi-tag-multiple';
    },

    getStockColor(qty) {
      if (qty <= 0) return 'error';
      if (qty <= 5) return 'warning';
      return 'success';
    },

    formatStock(qty) {
      const num = parseFloat(qty || 0);
      return num % 1 === 0 ? num.toString() : num.toFixed(2);
    },

    close_dialog() {
      this.varaintsDialog = false;
      this.resetFilters();
    },

    resetFilters() {
      this.filters = {};
      this.updateFiltredItems();
    },

    formatCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },

    updateFiltredItems() {
      this.$nextTick(function () {
        console.log('Updating filtered items with filters:', this.filters);
        
        const values = [];
        Object.entries(this.filters).forEach(([key, value]) => {
          if (value) {
            values.push(value);
          }
        });

        if (!values.length) {
          this.filterdItems = this.variantsItems;
        } else {
          const itemsList = [];
          this.filterdItems = [];
          this.variantsItems.forEach((item) => {
            let apply = true;
            
            if (item.item_attributes) {
              item.item_attributes.forEach((attr) => {
                if (
                  this.filters[attr.attribute] &&
                  this.filters[attr.attribute] != attr.attribute_value
                ) {
                  apply = false;
                }
              });
            }
            
            if (apply && !itemsList.includes(item.item_code)) {
              this.filterdItems.push(item);
              itemsList.push(item.item_code);
            }
          });
        }
        
        console.log('Filtered items result:', this.filterdItems);
      });
    },

    add_item(item) {
      console.log('Adding variant item:', item);
      
      // Verify that required data exists
      if (!item) {
        console.error('No item to add');
        return;
      }
      
      // Add default quantity if not present
      const itemToAdd = {
        ...item,
        qty: item.qty || 1
      };
      
      console.log('Emitting add_item event with:', itemToAdd);
      
      // Emit event
      this.eventBus.emit('add_item', itemToAdd);
      
      // Close dialog
      this.close_dialog();
      
      // Show success message (optional)
      if (window.frappe && window.frappe.show_alert) {
        frappe.show_alert({
          message: __('Added {0}', [item.item_name]),
          indicator: 'green'
        }, 3);
      }
    },
  },

  created: function () {
    this.detectRTL();
    
    this.eventBus.on('open_variants_model', (data) => {
      const { item, items, pos_profile } = data || {};
      console.log('Opening variants dialog for:', item);
      console.log('Available items:', items);
      console.log('Item has_variants:', item ? item.has_variants : undefined);
      
      this.varaintsDialog = true;
      this.parentItem = item || null;
      this.items = null; // show loading spinner
      this.filters = {};
      
      const fallbackItems = items || [];
      
      const setupVariants = () => {
        // If parent item has attributes, use them
        if (this.parentItem && this.parentItem.attributes && this.parentItem.attributes.length > 0) {
          console.log('Parent has attributes:', this.parentItem.attributes);
          this.filterdItems = this.variantsItems;
        } else {
          // If no attributes, try to show all variants
          console.log('No attributes found, showing all variants');
          this.filterdItems = this.variantsItems;
          
          // If no variants found, try alternative structure
          if (this.filterdItems.length === 0) {
            console.warn('No variants found. Checking data structure...');
            
            // Try finding variants another way
            if (this.parentItem && this.parentItem.variants && Array.isArray(this.parentItem.variants)) {
              this.filterdItems = this.parentItem.variants;
            }
          }
        }
        
        console.log('Variants items:', this.variantsItems);
        console.log('Filtered items:', this.filterdItems);
        this.updateFiltredItems();
      };
      
      if (item && item.item_code) {
        frappe.call({
          method: "highspeed_pos.highspeed_pos.api.hsposapp.get_item_variants",
          args: {
            parent_item_code: item.item_code,
            pos_profile: pos_profile || null,
          },
          callback: (r) => {
            if (r.message) {
              this.items = r.message.variants || [];
              if (r.message.attributes && r.message.attributes.length > 0) {
                this.parentItem.attributes = r.message.attributes;
              }
            } else {
              this.items = fallbackItems;
            }
            this.$nextTick(setupVariants);
          },
          error: (err) => {
            console.error("Failed to load variants from server, using fallback items", err);
            this.items = fallbackItems;
            this.$nextTick(setupVariants);
          }
        });
      } else {
        this.items = fallbackItems;
        this.$nextTick(setupVariants);
      }
    });
  },

  beforeUnmount() {
    this.eventBus.off('open_variants_model');
  },
};
</script>

<style scoped>
.variants-card {
  border-radius: 16px !important;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dialog-header {
  background: linear-gradient(135deg, #075294 0%, #0097A7 100%) !important;
  color: white !important;
  display: flex !important;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px !important;
  border-bottom: none;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 4px;
  color: white !important;
}

.dialog-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: white !important;
}

.close-btn {
  transition: transform 0.2s;
  color: white !important;
}

.close-btn:hover {
  transform: rotate(90deg);
}

.scrollable-content {
  overflow-y: auto;
  flex: 1;
}

.variants-container {
  padding: 0 !important;
}

/* Attributes Section */
.attributes-section {
  background: #f8fafc;
  padding: 8px 16px;
  border-bottom: 1px solid #f1f5f9;
}

.attribute-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.attribute-icon {
  opacity: 0.8;
  color: #64748b !important;
}

.attribute-name {
  font-size: 0.7rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.attribute-chips {
  margin-top: 4px;
}

.attribute-chip {
  border-radius: 6px !important;
  font-size: 0.825rem !important;
  font-weight: 500;
  color: #475569 !important;
  border: 1px solid #cbd5e1 !important;
  background-color: #ffffff !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 6px 14px !important;
  height: 32px !important;
}

.attribute-chip:hover {
  border-color: #0097A7 !important;
  color: #0097A7 !important;
  background-color: #f0fdfa !important;
  transform: translateY(-1px);
}

.chip-selected {
  background: linear-gradient(135deg, #075294 0%, #0097A7 100%) !important;
  color: white !important;
  border-color: transparent !important;
  box-shadow: 0 4px 10px rgba(0, 151, 167, 0.25) !important;
}

/* Results Info */
.results-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f1f5f9;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
}

/* Items Section */
.items-section {
  padding: 8px 12px;
  min-height: 200px;
}

.items-grid {
  margin: -4px;
}

.items-grid > .v-col {
  padding: 4px !important;
}

.variant-item-card {
  border-radius: 8px !important;
  overflow: hidden;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
  user-select: none;
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
}

.variant-item-card:hover {
  transform: translateY(-2px);
  border-color: #0097A7 !important;
  box-shadow: 0 10px 15px -3px rgba(0, 151, 167, 0.1), 0 4px 6px -4px rgba(0, 151, 167, 0.1) !important;
}

.item-image-wrapper {
  position: relative;
  overflow: hidden;
}

.item-image {
  transition: transform 0.3s;
}

.variant-item-card:hover .item-image {
  transform: scale(1.05);
}

.stock-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  font-size: 0.7rem !important;
  font-weight: 600;
  backdrop-filter: blur(8px);
  background: rgba(255, 255, 255, 0.85) !important;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.stock-badge-inline {
  font-size: 0.7rem !important;
  font-weight: 600;
  height: 18px !important;
  padding: 0 4px !important;
}

.item-details {
  padding: 6px 8px !important;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-name {
  font-weight: 600;
  font-size: 0.75rem;
  color: #1e293b;
  margin-bottom: 0px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-code {
  font-size: 0.65rem;
  color: #64748b;
  font-family: monospace;
  margin-bottom: 4px;
  direction: ltr !important;
  unicode-bidi: isolate;
  text-align: inherit;
}

.card-attributes {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
}

.attribute-pill {
  font-weight: 600;
  font-size: 0.65rem !important;
  height: 16px !important;
  padding: 0 4px !important;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}

.item-price {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.currency {
  font-size: 0.65rem;
  color: #64748b;
  font-weight: 500;
}

.price {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0097A7;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  text-align: center;
  padding: 30px;
}

.empty-text {
  font-size: 0.95rem;
  color: #64748b;
  margin: 12px 0 20px;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 250px;
}

.loading-text {
  margin-top: 12px;
  color: #64748b;
}

/* RTL Support */
[dir="rtl"] .stock-badge {
  right: auto;
  left: 8px;
}

[dir="rtl"] .price {
  direction: ltr;
}

/* Scrollbar Styling */
.scrollable-content::-webkit-scrollbar {
  width: 6px;
}

.scrollable-content::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.scrollable-content::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.scrollable-content::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Animations */
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

.variant-item-card {
  animation: fadeIn 0.3s ease-out;
  animation-fill-mode: both;
}

.variant-item-card:nth-child(1) { animation-delay: 0.05s; }
.variant-item-card:nth-child(2) { animation-delay: 0.1s; }
.variant-item-card:nth-child(3) { animation-delay: 0.15s; }
.variant-item-card:nth-child(4) { animation-delay: 0.2s; }
.variant-item-card:nth-child(5) { animation-delay: 0.25s; }
.variant-item-card:nth-child(6) { animation-delay: 0.3s; }

/* Responsive Design */
@media (max-width: 600px) {
  .dialog-header {
    padding: 10px 14px !important;
  }
  
  .dialog-title {
    font-size: 1rem;
  }
  
  .attributes-section {
    padding: 8px 12px;
  }
  
  .items-section {
    padding: 12px;
  }
  
  .item-details {
    padding: 6px !important;
  }
  
  .price {
    font-size: 0.9rem;
  }
}
</style>