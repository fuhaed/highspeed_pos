<template>
  <v-dialog v-model="dialog" max-width="440px" persistent>
    <v-card class="elevation-0 rounded-xl overflow-hidden" :class="{ 'rtl': isRTL }" :dir="isRTL ? 'rtl' : 'ltr'">
      <v-card-title class="pa-4 bg-primary text-white d-flex align-center">
        <v-icon :class="isRTL ? 'ml-3' : 'mr-3'" color="white">mdi-plus-circle-outline</v-icon>
        <span class="text-h6 font-weight-bold">{{ __('Select Add-ons') }}</span>
        <v-spacer></v-spacer>
        <v-btn icon variant="text" color="white" @click="close" density="compact">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text class="pa-4 bg-grey-lighten-5">
        <div class="mb-3">
          <div class="text-subtitle-1 font-weight-bold text-grey-darken-4">
            {{ item ? item.item_name : '' }}
          </div>
          <div class="text-caption text-grey-darken-2">
            {{ __('Choose optional add-ons to customize your item') }}
          </div>
        </div>

        <v-divider class="mb-3"></v-divider>

        <div v-if="addons.length > 0" class="addons-grid">
          <div
            v-for="(addon, idx) in addons"
            :key="idx"
            class="addon-card-item"
            :class="{ 'active': isSelected(addon) }"
            @click="toggleAddon(addon)"
          >
            <div class="addon-card-content">
              <div class="addon-info-group">
                <span class="addon-checkbox-circle" :class="{ 'checked': isSelected(addon) }">
                  <v-icon v-if="isSelected(addon)" size="10" color="white">mdi-check</v-icon>
                </span>
                <span class="addon-title">{{ addon.add_on_name }}</span>
              </div>
              <span class="addon-price-chip" :class="{ 'price-free': addon.extra_price <= 0 }">
                {{ addon.extra_price > 0 ? `+${formatCurrency(addon.extra_price)}` : __('Free') }}
              </span>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center py-6 text-grey">
          <v-icon size="40" class="mb-2" color="grey-lighten-1">mdi-tray-plus</v-icon>
          <div class="text-body-2">{{ __('No add-ons available for this item') }}</div>
        </div>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions class="pa-3 bg-grey-lighten-4">
        <v-btn
          variant="outlined"
          color="error"
          @click="close"
          class="px-4 rounded-lg font-weight-bold"
          density="comfortable"
        >
          {{ __('Cancel') }}
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          variant="flat"
          @click="confirm"
          class="px-5 rounded-lg font-weight-bold"
          density="comfortable"
        >
          {{ __('Confirm') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: "AddonsDialog",
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    item: {
      type: Object,
      default: () => null
    }
  },
  emits: ["update:modelValue", "confirm"],
  data() {
    return {
      selectedAddons: [],
      isRTL: false
    };
  },
  computed: {
    dialog: {
      get() {
        return this.modelValue;
      },
      set(val) {
        this.$emit("update:modelValue", val);
      }
    },
    addons() {
      if (this.item && this.item.hspos_add_ons) {
        return this.item.hspos_add_ons;
      }
      return [];
    }
  },
  watch: {
    modelValue(newVal) {
      if (newVal) {
        if (this.item && this.item.selected_addons) {
          this.selectedAddons = this.item.hspos_add_ons.filter(a => 
            this.item.selected_addons.some(sa => sa.add_on_name === a.add_on_name)
          );
        } else {
          this.selectedAddons = [];
        }
      }
    }
  },
  created() {
    const lang = (frappe.boot && frappe.boot.lang) || "en";
    this.isRTL = ["ar", "he", "fa", "ur"].includes(lang);
  },
  methods: {
    close() {
      this.dialog = false;
    },
    confirm() {
      this.$emit("confirm", this.selectedAddons);
      this.dialog = false;
    },
    isSelected(addon) {
      return this.selectedAddons.some(a => a.add_on_name === addon.add_on_name);
    },
    toggleAddon(addon) {
      const idx = this.selectedAddons.findIndex(a => a.add_on_name === addon.add_on_name);
      if (idx > -1) {
        this.selectedAddons.splice(idx, 1);
      } else {
        this.selectedAddons.push(addon);
      }
    },
    formatCurrency(val) {
      return parseFloat(val || 0).toFixed(2);
    },
    __: window.__ || ((str) => str),
  }
};
</script>

<style scoped>
.addons-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
  padding: 2px;
}

.addon-card-item {
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  position: relative;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

.addon-card-item:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.addon-card-item.active {
  background: #e6f7f6;
  border-color: #0097a7;
  box-shadow: 0 2px 6px rgba(0, 151, 167, 0.1);
}

.addon-card-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 8px;
}

.addon-info-group {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.addon-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.addon-card-item.active .addon-title {
  color: #004d40;
}

.addon-checkbox-circle {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1.5px solid #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  background: #fff;
  flex-shrink: 0;
}

.addon-checkbox-circle.checked {
  border-color: #0097a7;
  background: #0097a7;
}

.addon-price-chip {
  font-size: 0.7rem;
  font-weight: 700;
  color: #00838f;
  background: #e0f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}

.addon-price-chip.price-free {
  color: #2e7d32;
  background: #e8f5e9;
}

.addon-card-item.active .addon-price-chip {
  background: #b2ebf2;
  color: #006064;
}

.addon-card-item.active .addon-price-chip.price-free {
  background: #c8e6c9;
  color: #1b5e20;
}
</style>
