<template>
  <v-row justify="center">
    <v-dialog v-model="varaintsDialog" max-width="900px" :dir="isRTL ? 'rtl' : 'ltr'">
      <v-card class="variants-card">
        <v-card-title class="dialog-header">
          <div class="header-content">
            <v-icon size="28" color="primary" class="header-icon">mdi-shape-plus</v-icon>
            <span class="dialog-title">{{ parentItem ? parentItem.item_name : __('Select Item') }}</span>
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
        
        <v-card-text class="pa-0">
          <v-container v-if="parentItem" class="variants-container">
            <!-- Attributes Section -->
            <div class="attributes-section" v-if="parentItem.attributes && parentItem.attributes.length">
              <div 
                v-for="(attr, index) in parentItem.attributes" 
                :key="attr.attribute"
                class="attribute-group"
                :class="{ 'last-group': index === parentItem.attributes.length - 1 }"
              >
                <div class="attribute-header">
                  <v-icon size="20" color="grey-darken-1" class="attribute-icon">
                    {{ getAttributeIcon(attr.attribute) }}
                  </v-icon>
                  <span class="attribute-name">{{ attr.attribute }}</span>
                </div>
                
                <v-chip-group 
                  v-model="filters[attr.attribute]" 
                  selected-class="chip-selected"
                  class="attribute-chips"
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
                    {{ value.attribute_value }}
                  </v-chip>
                </v-chip-group>
              </div>
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
                  xl="2" 
                  lg="3" 
                  md="4" 
                  sm="6" 
                  cols="12"
                >
                  <v-card 
                    class="variant-item-card"
                    hover
                    @click.stop="add_item(item)"
                  >
                    <div class="item-image-wrapper">
                      <v-img 
                        :src="item.image || '/assets/highspeed_pos/js/hsposapp/components/pos/placeholder-image.png'"
                        class="item-image"
                        cover
                        height="140"
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
                        size="small"
                        :color="getStockColor(item.actual_qty)"
                        class="stock-badge"
                      >
                        <v-icon size="14" start>mdi-package-variant</v-icon>
                        {{ formatStock(item.actual_qty) }}
                      </v-chip>
                    </div>
                    
                    <v-card-text class="item-details">
                      <div class="item-name">{{ item.item_name }}</div>
                      <div class="item-code">{{ item.item_code }}</div>
                      
                      <div class="item-footer">
                        <div class="item-price">
                          <span class="currency">{{ item.currency || 'SAR' }}</span>
                          <span class="price">{{ formatCurrency(item.rate || 0) }}</span>
                        </div>
                        <v-chip size="x-small" variant="tonal" color="grey">
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
                  hover
                  @click.stop="add_item(parentItem)"
                  style="max-width: 300px;"
                >
                  <div class="item-image-wrapper">
                    <v-img 
                      :src="parentItem.image || '/assets/highspeed_pos/js/hsposapp/components/pos/placeholder-image.png'"
                      class="item-image"
                      cover
                      height="140"
                    >
                    </v-img>
                  </div>
                  
                  <v-card-text class="item-details">
                    <div class="item-name">{{ parentItem.item_name }}</div>
                    <div class="item-code">{{ parentItem.item_code }}</div>
                    
                    <div class="item-footer">
                      <div class="item-price">
                        <span class="currency">{{ parentItem.currency || 'SAR' }}</span>
                        <span class="price">{{ formatCurrency(parentItem.rate || 0) }}</span>
                      </div>
                      <v-chip size="x-small" variant="tonal" color="grey">
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
        // Maybe variants are in another field
        variants = this.items.filter(
          (item) => item.item_name && item.item_name.includes(this.parentItem.item_name)
        );
      }
      
      console.log('Parent item:', this.parentItem);
      console.log('Found variants:', variants);
      
      return variants;
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
    
    this.eventBus.on('open_variants_model', (item, items) => {
      console.log('Opening variants dialog for:', item);
      console.log('Available items:', items);
      console.log('Item has_variants:', item.has_variants);
      
      this.varaintsDialog = true;
      this.parentItem = item || null;
      this.items = items;
      this.filters = {};
      
      this.$nextTick(() => {
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
            if (item.variants && Array.isArray(item.variants)) {
              this.filterdItems = item.variants;
            }
          }
        }
        
        console.log('Variants items:', this.variantsItems);
        console.log('Filtered items:', this.filterdItems);
      });
    });
  },

  beforeUnmount() {
    this.eventBus.off('open_variants_model');
  },
};
</script>

<style scoped>
.variants-card {
  border-radius: 12px !important;
  overflow: hidden;
}

.dialog-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  background: white;
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dialog-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #212121;
}

.close-btn {
  transition: transform 0.2s;
}

.close-btn:hover {
  transform: rotate(90deg);
}

.variants-container {
  padding: 0 !important;
  max-height: 70vh;
  overflow-y: auto;
}

/* Attributes Section */
.attributes-section {
  background: #fafafa;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.attribute-group {
  margin-bottom: 20px;
}

.attribute-group.last-group {
  margin-bottom: 0;
}

.attribute-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.attribute-icon {
  opacity: 0.7;
}

.attribute-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #616161;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.attribute-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.attribute-chip {
  border-radius: 8px !important;
  font-size: 0.875rem;
  transition: all 0.2s;
  border-width: 2px !important;
}

.attribute-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.chip-selected {
  background: #1976d2 !important;
  color: white !important;
  border-color: #1976d2 !important;
}

/* Results Info */
.results-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  font-size: 0.875rem;
  color: #616161;
}

/* Items Section */
.items-section {
  padding: 20px;
  min-height: 300px;
}

.items-grid {
  margin: -8px;
}

.variant-item-card {
  border-radius: 12px !important;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
  user-select: none;
}

.variant-item-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
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
  top: 8px;
  right: 8px;
  font-size: 0.75rem !important;
  font-weight: 600;
  backdrop-filter: blur(8px);
  background: rgba(255,255,255,0.9) !important;
}

.item-details {
  padding: 16px !important;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: #212121;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-code {
  font-size: 0.75rem;
  color: #757575;
  font-family: monospace;
  margin-bottom: 12px;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.item-price {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.currency {
  font-size: 0.75rem;
  color: #757575;
}

.price {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1976d2;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
  padding: 40px;
}

.empty-text {
  font-size: 1rem;
  color: #757575;
  margin: 16px 0 24px;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.loading-text {
  margin-top: 16px;
  color: #757575;
}

/* RTL Support */
[dir="rtl"] .header-content {
  flex-direction: row-reverse;
}

[dir="rtl"] .attribute-header {
  flex-direction: row-reverse;
}

[dir="rtl"] .stock-badge {
  right: auto;
  left: 8px;
}

[dir="rtl"] .item-footer {
  flex-direction: row-reverse;
}

[dir="rtl"] .item-price {
  flex-direction: row-reverse;
}

[dir="rtl"] .price {
  direction: ltr;
}

[dir="rtl"] .results-info {
  flex-direction: row-reverse;
}

/* Scrollbar Styling */
.variants-container::-webkit-scrollbar {
  width: 8px;
}

.variants-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.variants-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.variants-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
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
    padding: 16px;
  }
  
  .dialog-title {
    font-size: 1.1rem;
  }
  
  .attributes-section {
    padding: 16px;
  }
  
  .items-section {
    padding: 16px;
  }
  
  .item-details {
    padding: 12px !important;
  }
  
  .price {
    font-size: 1rem;
  }
}
</style>