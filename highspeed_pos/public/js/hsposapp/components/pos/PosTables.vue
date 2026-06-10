<!-- File Path: highspeed_pos/highspeed_pos/public/js/hsposapp/components/pos/PosTables.vue -->
<template>
  <div class="tables-panel-wrapper h-100" :dir="isRTL ? 'rtl' : 'ltr'">
    <v-card class="tables-panel-card d-flex flex-column h-100 elevation-0">
      <!-- Header -->
      <v-card-title class="pa-4 bg-gradient-header flex-shrink-0">
        <div class="d-flex align-center justify-space-between" :class="{ 'flex-row-reverse': isRTL }">
          <div class="d-flex align-center" :class="{ 'flex-row-reverse': isRTL }">
            <v-icon :class="isRTL ? 'ml-3' : 'mr-3'" color="white" size="24">mdi-table-chair</v-icon>
            <span class="text-h6 text-white font-weight-medium">{{ __('Dining Tables') }}</span>
          </div>
          <!-- Search field inside header for space efficiency -->
          <v-text-field
            v-model="search"
            :label="__('Search Table')"
            density="compact"
            variant="solo"
            hide-details
            clearable
            prepend-inner-icon="mdi-magnify"
            class="header-search-field"
            style="max-width: 200px;"
          />
        </div>
      </v-card-title>

      <!-- Statistics Bar -->
      <div class="stats-bar px-4 py-3 flex-shrink-0">
        <v-row no-gutters align="center" :class="{ 'flex-row-reverse': isRTL }">
          <v-col cols="4">
            <div class="d-flex align-center" :class="{ 'flex-row-reverse': isRTL }">
              <v-icon :class="isRTL ? 'ml-2' : 'mr-2'" size="18" color="success">mdi-circle</v-icon>
              <span class="text-caption text-slate-700">
                {{ __('Available') }}: <strong class="stat-badge available">{{ availableCount }}</strong>
              </span>
            </div>
          </v-col>
          <v-col cols="4">
            <div class="d-flex align-center justify-center" :class="{ 'flex-row-reverse': isRTL }">
              <v-icon :class="isRTL ? 'ml-2' : 'mr-2'" size="18" color="error">mdi-circle</v-icon>
              <span class="text-caption text-slate-700">
                {{ __('Occupied') }}: <strong class="stat-badge occupied">{{ occupiedCount }}</strong>
              </span>
            </div>
          </v-col>
          <v-col cols="4">
            <div class="d-flex align-center justify-end" :class="{ 'flex-row-reverse': isRTL }">
              <v-icon :class="isRTL ? 'ml-2' : 'mr-2'" size="18" color="warning">mdi-circle</v-icon>
              <span class="text-caption text-slate-700">
                {{ __('Reserved') }}: <strong class="stat-badge reserved">{{ reservedCount }}</strong>
              </span>
            </div>
          </v-col>
        </v-row>
      </div>

      <!-- Tables Grid Container -->
      <div class="tables-grid-container flex-grow-1 pa-4" style="overflow-y: auto;">
        <!-- Empty State -->
        <div v-if="filteredTables.length === 0" class="empty-state d-flex flex-column align-center justify-center py-16">
          <v-icon size="64" color="slate-400">mdi-table-off</v-icon>
          <h3 class="text-h6 font-weight-bold text-slate-700 mt-2">{{ __('No tables found') }}</h3>
        </div>

        <!-- Tables Grid -->
        <v-row v-else :class="{ 'flex-row-reverse': isRTL }">
          <v-col
            v-for="table in filteredTables"
            :key="table.name"
            cols="6"
            sm="4"
            md="3"
            class="pa-2"
          >
            <v-card
              :class="['table-card', getStatusClass(table), { 'selected': selectedTable === table.name, 'has-draft': !!table.draft_name }]"
              variant="flat"
              @click="selectTable(table)"
            >
              <div class="table-card-content pa-3 text-center">
                <!-- Status Badge -->
                <div class="status-indicator"></div>
                
                <v-icon size="36" class="mb-2 table-icon">mdi-table-chair</v-icon>
                
                <div class="table-name font-weight-bold mb-1 text-truncate">{{ table.table_name }}</div>
                
                <!-- Draft Badge -->
                <div v-if="table.draft_name" class="mb-2">
                  <span class="text-caption font-weight-bold px-1.5 py-0.5 rounded text-white" style="font-size: 10px !important; background-color: #fb8c00 !important; box-shadow: 0 0 5px rgba(251,140,0,0.3);">
                    {{ isRTL ? 'مسودة' : 'Draft' }}
                  </span>
                </div>
                
                <div class="table-meta d-flex justify-space-between align-center px-1">
                  <span class="capacity-text">
                    <v-icon size="12" class="me-1">mdi-account-group</v-icon>
                    {{ table.capacity }}
                  </span>
                  <span class="status-text font-weight-medium">
                    {{ table.draft_name ? (isRTL ? 'مسودة نشطة' : 'Active Draft') : __(table.status) }}
                  </span>
                </div>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </div>

      <!-- Bottom Action Bar -->
      <v-card-actions class="pa-4 bg-white border-t flex-shrink-0">
        <v-row dense :class="{ 'flex-row-reverse': isRTL }" class="w-100 ma-0">
          <v-col cols="12" class="pa-1">
            <v-btn
              block
              size="large"
              color="grey-darken-2"
              variant="flat"
              class="action-btn"
              @click="backToInvoice"
              :prepend-icon="isRTL ? '' : 'mdi-arrow-left'"
              :append-icon="isRTL ? 'mdi-arrow-right' : ''"
            >
              {{ __('Back') }}
            </v-btn>
          </v-col>
        </v-row>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
export default {
  data: () => ({
    tables: [],
    search: "",
    selectedTable: "",
    isRTL: false,
    pos_profile_name: "",
  }),

  computed: {
    filteredTables() {
      if (!this.search) return this.tables;
      const q = this.search.toLowerCase().trim();
      return this.tables.filter(t => t.table_name.toLowerCase().includes(q));
    },
    availableCount() {
      return this.tables.filter(t => t.status === "Available").length;
    },
    occupiedCount() {
      return this.tables.filter(t => t.status === "Occupied").length;
    },
    reservedCount() {
      return this.tables.filter(t => t.status === "Reserved").length;
    },
  },

  methods: {
    fetchTables() {
      // First, trigger automatic release of any tables exceeded 1.5 hours in the database
      frappe.call({
        method: "highspeed_pos.highspeed_pos.api.hsposapp.auto_release_expired_tables",
        callback: () => {
          const filters = [];
          if (this.pos_profile_name) {
            filters.push(["POS Table", "pos_profile", "in", [this.pos_profile_name, "", null]]);
          }

          frappe.call({
            method: "frappe.client.get_list",
            args: {
              doctype: "POS Table",
              fields: ["name", "table_name", "status", "capacity", "pos_profile"],
              filters: filters,
              limit: 100
            },
            callback: (r) => {
              if (r.message) {
                const tablesList = r.message;
                // Fetch active draft invoices with tables for this profile
                frappe.call({
                  method: "frappe.client.get_list",
                  args: {
                    doctype: "Sales Invoice",
                    fields: ["name", "hspos_table"],
                    filters: {
                      docstatus: 0,
                      pos_profile: this.pos_profile_name || "",
                      hspos_table: ["!=", ""]
                    },
                    limit: 100
                  },
                  callback: (res) => {
                    const drafts = res.message || [];
                    const draftMap = {};
                    drafts.forEach(d => {
                      if (d.hspos_table) {
                        draftMap[d.hspos_table] = d.name;
                      }
                    });
                    
                    tablesList.forEach(t => {
                      t.draft_name = draftMap[t.table_name] || draftMap[t.name] || "";
                    });
                    
                    this.tables = tablesList;
                  }
                });
              }
            }
          });
        }
      });
    },

    selectTable(table) {
      if (table.status === "Occupied" || table.status === "Reserved") {
        frappe.confirm(
          this.__("This table is currently occupied or reserved. Do you want to set it back to Available?"),
          () => {
            this.updateTableStatus(table.name, "Available");
          },
          () => {
            if (table.draft_name) {
              // Load the active draft invoice for this table
              frappe.call({
                method: "frappe.client.get",
                args: {
                  doctype: "Sales Invoice",
                  name: table.draft_name
                },
                callback: (res) => {
                  if (res.message) {
                    this.eventBus.emit("load_invoice", res.message);
                    this.backToInvoice();
                  }
                }
              });
            } else {
              this.selectedTable = table.name;
              this.eventBus.emit("set_invoice_table", table.table_name);
              this.backToInvoice();
            }
          }
        );
        return;
      }

      this.selectedTable = table.name;
      this.eventBus.emit("set_invoice_table", table.table_name);
      this.backToInvoice();
    },

    updateTableStatus(tableName, status) {
      frappe.call({
        method: "frappe.client.set_value",
        args: {
          doctype: "POS Table",
          name: tableName,
          fieldname: "status",
          value: status
        },
        callback: () => {
          this.fetchTables();
        }
      });
    },

    backToInvoice() {
      this.eventBus.emit("show_tables", "false");
    },

    getStatusClass(table) {
      return `status-${table.status.toLowerCase()}`;
    },
  },

  created() {
    const lang = frappe.boot.lang || 'en';
    const htmlDir = document.documentElement.getAttribute('dir');
    const bodyDir = document.body.getAttribute('dir');
    this.isRTL = htmlDir === 'rtl' || bodyDir === 'rtl' || ['ar', 'he', 'fa', 'ur'].includes(lang.substring(0, 2));

    // Load active POS Profile name from cache
    const cached = localStorage.getItem("pos_opening_storage");
    if (cached) {
      try {
        const data = JSON.parse(cached);
        if (data && data.pos_profile) {
          this.pos_profile_name = data.pos_profile.name;
        }
      } catch (e) {
        console.error("Failed to parse cached opening data in PosTables", e);
      }
    }

    this.fetchTables();

    this.eventBus.on("set_invoice_table", (table) => {
      this.selectedTable = table || "";
    });

    this.eventBus.on("table_deselected", (tableName) => {
      // Free the table back to Available if deselected
      const tableToFree = tableName || this.selectedTable;
      if (tableToFree) {
        // Do not automatically free table on deselection. Releasing table is done manually from tables screen.
        // this.updateTableStatus(tableToFree, "Available");
      }
      this.selectedTable = "";
    });

    this.eventBus.on("clear_invoice", () => {
      this.selectedTable = "";
    });

    this.eventBus.on("register_pos_profile", (data) => {
      if (data && data.pos_profile) {
        this.pos_profile_name = data.pos_profile.name;
        this.fetchTables();
      }
    });
  },

  beforeUnmount() {
    this.eventBus.off("set_invoice_table");
    this.eventBus.off("table_deselected");
    this.eventBus.off("clear_invoice");
    this.eventBus.off("register_pos_profile");
  }
};
</script>

<style scoped>
.tables-panel-wrapper {
  background-color: #f8fafc;
}

.tables-panel-card {
  background-color: #f8fafc !important;
}

.bg-gradient-header {
  background: linear-gradient(135deg, #075294 0%, #0097A7 100%) !important;
  border-radius: 4px 4px 0 0 !important;
}

.header-search-field :deep(.v-field) {
  border-radius: 4px !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
}
.header-search-field :deep(.v-field__input) {
  color: white !important;
}
.header-search-field :deep(.v-icon) {
  color: rgba(255, 255, 255, 0.8) !important;
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
  background-color: #dcfce7;
  color: #15803d;
}

.stat-badge.occupied {
  background-color: #fee2e2;
  color: #b91c1c;
}

.stat-badge.reserved {
  background-color: #ffedd5;
  color: #c2410c;
}

.tables-grid-container {
  background-color: #f8fafc;
}

.empty-state {
  height: 100%;
}

.table-card {
  background-color: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 6px !important;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
}

.table-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
}

/* Selected highlight style */
.table-card.selected {
  border-color: #075294 !important;
  box-shadow: 0 0 0 3px rgba(7, 82, 148, 0.2) !important;
}

/* Status colors and accents */
.table-card.status-available {
  border-left: 4px solid #22c55e !important;
}
[dir="rtl"] .table-card.status-available {
  border-left: none !important;
  border-right: 4px solid #22c55e !important;
}
.table-card.status-available .table-icon {
  color: #22c55e !important;
}

.table-card.status-occupied {
  border-left: 4px solid #ef4444 !important;
}
[dir="rtl"] .table-card.status-occupied {
  border-left: none !important;
  border-right: 4px solid #ef4444 !important;
}
.table-card.status-occupied .table-icon {
  color: #ef4444 !important;
}

.table-card.status-reserved {
  border-left: 4px solid #f97316 !important;
}
[dir="rtl"] .table-card.status-reserved {
  border-left: none !important;
  border-right: 4px solid #f97316 !important;
}
.table-card.status-reserved .table-icon {
  color: #f97316 !important;
}

.table-name {
  font-size: 0.95rem;
  color: #1e293b;
}

.table-meta {
  font-size: 0.75rem;
  color: #64748b;
}

.action-btn {
  height: 44px !important;
  font-weight: 500;
  letter-spacing: 0.5px;
  border-radius: 4px !important;
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

.table-card.has-draft {
  background-color: #fffdf5 !important;
  border: 1.5px dashed #fb8c00 !important;
  box-shadow: 0 2px 6px rgba(251, 140, 0, 0.08) !important;
}

.table-card.has-draft:hover {
  box-shadow: 0 6px 16px rgba(251, 140, 0, 0.15) !important;
}

.table-card.has-draft .status-text {
  color: #fb8c00 !important;
}
</style>
