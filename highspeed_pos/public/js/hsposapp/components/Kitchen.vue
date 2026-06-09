<template>
  <v-app class="kds-app-container" :dir="currentLang === 'ar' ? 'rtl' : 'ltr'">
    <!-- Top Glassmorphic Navigation bar -->
    <v-app-bar flat class="kds-navbar px-2 px-sm-4">
      <div class="d-flex align-center w-100">
        <!-- Logo & Title -->
        <div class="d-flex align-center">
          <v-avatar color="rgba(255, 255, 255, 0.08)" size="36" class="me-2 brand-glow d-none d-sm-flex">
            <v-icon color="#58a6ff" size="18">mdi-stove</v-icon>
          </v-avatar>
          <div>
            <div class="kds-title font-weight-bold text-uppercase" style="font-size: 15px !important; letter-spacing: 1px;">
              <span class="text-white font-weight-light">HSPOS</span>
              <span class="text-primary font-weight-black ms-1">Kitchen</span>
            </div>
            <span class="text-caption text-grey-darken-1 font-mono d-none d-md-inline" style="font-size: 9px !important;">Live KDS Control</span>
          </div>
        </div>

        <v-spacer></v-spacer>

        <!-- Centered Stats Counters (visible only on large desktop screens to prevent crowding) -->
        <div class="d-flex gap-2 align-center kds-desktop-only">
          <v-chip color="error" variant="flat" class="font-weight-bold px-3" size="small">
            <v-icon start size="14">mdi-clock-alert-outline</v-icon>
            <span class="ms-1">{{ pendingCount }}</span>
            <span class="kds-label-desktop ms-1">{{ __('Pending') }}</span>
          </v-chip>
          <v-chip color="warning" variant="flat" class="font-weight-bold px-3" size="small">
            <v-icon start size="14">mdi-fire</v-icon>
            <span class="ms-1">{{ preparingCount }}</span>
            <span class="kds-label-desktop ms-1">{{ __('Preparing') }}</span>
          </v-chip>
          <v-chip color="success" variant="flat" class="font-weight-bold px-3" size="small">
            <v-icon start size="14">mdi-check-decagram-outline</v-icon>
            <span class="ms-1">{{ completedTodayCount }}</span>
            <span class="kds-label-desktop ms-1">{{ __('Done Today') }}</span>
          </v-chip>
        </div>

        <v-spacer class="kds-desktop-only"></v-spacer>

        <!-- System Time & Control buttons -->
        <div class="d-flex align-center gap-1 gap-sm-2">
          <!-- System clock (hidden on mobile) -->
          <div class="text-white font-mono me-2 d-none d-sm-block text-caption bg-glass py-1 px-3 rounded-lg border-glass">
            <v-icon start size="12" color="grey">mdi-clock-outline</v-icon>
            {{ liveTime }}
          </div>

          <!-- Refresh (always visible, icon-only on xs/mobile) -->
          <v-btn
            variant="flat"
            color="primary"
            :loading="loading"
            @click="fetchOrders(true)"
            class="rounded-lg font-weight-bold px-2 px-sm-3"
            style="min-width: unset; height: 36px;"
          >
            <v-icon class="me-0 me-sm-1" size="18">mdi-refresh</v-icon>
            <span class="d-none d-sm-inline">{{ __('Refresh') }}</span>
          </v-btn>

          <!-- Desk (always visible, icon-only on xs/mobile) -->
          <v-btn
            variant="outlined"
            color="grey-lighten-1"
            @click="goDesk"
            class="rounded-lg font-weight-bold border-glass ms-1 ms-sm-2 px-2 px-sm-3"
            style="min-width: unset; height: 36px;"
          >
            <v-icon class="me-0 me-sm-1" size="18">mdi-home</v-icon>
            <span class="d-none d-sm-inline">{{ __('Desk') }}</span>
          </v-btn>

          <!-- Language Toggle Button (always visible, compact) -->
          <v-btn
            variant="outlined"
            color="white"
            @click="toggleLanguage"
            class="rounded-lg font-weight-bold border-glass ms-1 ms-sm-2"
            size="small"
            style="min-width: 55px; height: 36px; padding: 0 8px; font-size: 11px;"
          >
            {{ currentLang === 'ar' ? 'EN' : 'عربي' }}
          </v-btn>

          <!-- Desktop Utility Buttons (visible on lg and up) -->
          <div class="d-flex align-center gap-1 kds-desktop-only">
            <v-btn
              icon
              variant="text"
              color="white"
              size="small"
              @click="toggleSound"
              :title="__('Toggle Chime Alert')"
            >
              <v-icon>{{ soundEnabled ? 'mdi-volume-high' : 'mdi-volume-off' }}</v-icon>
            </v-btn>

            <v-btn
              icon
              variant="text"
              color="white"
              size="small"
              @click="testSound"
              :title="__('Test Sound Chime')"
            >
              <v-icon color="grey-lighten-1">mdi-bell-ring</v-icon>
            </v-btn>

            <v-btn
              icon
              variant="text"
              color="white"
              size="small"
              @click="toggleFullscreen"
              :title="__('Toggle Fullscreen')"
            >
              <v-icon>{{ isFullscreen ? 'mdi-fullscreen-exit' : 'mdi-fullscreen' }}</v-icon>
            </v-btn>

            <v-btn
              icon
              variant="text"
              color="white"
              size="small"
              @click="settingsDialog = true"
              :title="__('KDS Settings')"
            >
              <v-icon>mdi-cog</v-icon>
            </v-btn>
          </div>

          <!-- Mobile/Tablet Dropdown Menu (visible on sm and down) -->
          <v-menu location="bottom end">
            <template v-slot:activator="{ props }">
              <v-btn
                icon
                variant="text"
                color="white"
                v-bind="props"
                size="small"
                class="ms-1 kds-mobile-only"
              >
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list class="bg-glass border-glass rounded-lg mt-1" density="compact" nav style="background: #0d1117 !important;">
              <v-list-item @click="toggleSound" prepend-icon="mdi-volume-high" class="text-white">
                <v-list-item-title>{{ soundEnabled ? __('Disable Sound') : __('Enable Sound') }}</v-list-item-title>
              </v-list-item>
              <v-list-item @click="testSound" prepend-icon="mdi-bell-ring" class="text-white">
                <v-list-item-title>{{ __('Test Sound Chime') }}</v-list-item-title>
              </v-list-item>
              <v-list-item @click="toggleFullscreen" :prepend-icon="isFullscreen ? 'mdi-fullscreen-exit' : 'mdi-fullscreen'" class="text-white">
                <v-list-item-title>{{ isFullscreen ? __('Exit Fullscreen') : __('Fullscreen') }}</v-list-item-title>
              </v-list-item>
              <v-list-item @click="settingsDialog = true" prepend-icon="mdi-cog" class="text-white">
                <v-list-item-title>{{ __('KDS Settings') }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
      </div>
    </v-app-bar>

    <v-main class="kds-main-bg">
      <v-container fluid class="pa-4 h-100 d-flex flex-column">
        <!-- Subheader & Filter Row -->
        <v-row class="mb-4 align-center flex-grow-0">
          <v-col cols="12" sm="6" class="d-flex align-center">
            <v-btn-toggle
              v-model="statusFilter"
              mandatory
              color="primary"
              variant="flat"
              class="border-glass rounded-lg"
              density="comfortable"
            >
              <v-btn value="all" class="font-weight-bold text-white px-4">
                {{ __('All Active') }} ({{ orders.length }})
              </v-btn>
              <v-btn value="Pending" class="font-weight-bold text-white px-4">
                {{ __('Pending') }} ({{ pendingCount }})
              </v-btn>
              <v-btn value="Preparing" class="font-weight-bold text-white px-4">
                {{ __('Preparing') }} ({{ preparingCount }})
              </v-btn>
            </v-btn-toggle>
          </v-col>
          <v-col cols="12" sm="6" class="text-sm-end">
            <span class="text-caption text-grey font-mono">
              {{ __('Auto-refreshing in') }} {{ countdown }}{{ __('s...') }}
            </span>
          </v-col>
        </v-row>

        <!-- Grid of Orders -->
        <div class="flex-grow-1 overflow-y-auto overflow-x-hidden pe-2 kds-grid-container">
          <v-row v-if="filteredOrders.length > 0">
            <v-col
              v-for="order in filteredOrders"
              :key="order.name"
              cols="12"
              sm="4"
              md="3"
              lg="2"
              class="d-flex pa-1"
            >
              <v-card
                class="kds-order-card flex-grow-1 d-flex flex-column border-glass bg-glass elevation-6"
                :class="{
                  'border-pending': order.hspos_kitchen_status === 'Pending',
                  'border-preparing': order.hspos_kitchen_status === 'Preparing',
                  'card-alert': isOrderOverdue(order.creation)
                }"
              >
                <!-- Compact Card Header -->
                <div class="pa-2 bg-glass-dark d-flex flex-column flex-grow-0 border-bottom-glass">
                  <div class="kds-card-header-grid w-100">
                    <!-- Order Number -->
                    <div class="d-flex align-center justify-start">
                      <span class="text-h6 font-weight-black text-white font-mono leading-none" style="font-size: 18px !important; text-shadow: 0 0 10px rgba(255,255,255,0.25);">
                        #{{ order.hspos_order_no || order.name.slice(-5) }}
                      </span>
                    </div>

                    <!-- Order Type (Center) -->
                    <div class="d-flex align-center justify-center">
                      <span
                        v-if="order.hspos_order_type"
                        class="order-type-badge font-weight-black"
                        :class="getOrderTypeClass(order.hspos_order_type)"
                      >
                        {{ formatOrderType(order.hspos_order_type) }}<span v-if="order.hspos_table"> ({{ order.hspos_table }})</span><span v-if="order.docstatus === 0" style="color: #ffb300; margin-left: 4px;"> (مسودة)</span>
                      </span>
                    </div>

                    <!-- Elapsed Time -->
                    <div class="d-flex align-center justify-end">
                      <div
                        class="text-caption font-weight-bold font-mono px-1.5 py-0.5 rounded leading-none"
                        :class="isOrderOverdue(order.creation) ? 'bg-red-glow text-white animate-pulse' : 'bg-grey-darken-4 text-grey-lighten-2'"
                        style="font-size: 10px !important;"
                      >
                        {{ getElapsedTime(order.creation) }}
                      </div>
                    </div>
                  </div>
                  <div class="d-flex justify-space-between align-center mt-1" style="font-size: 11px; line-height: 1.1;">
                    <div class="text-truncate text-grey-lighten-2" style="max-width: 105px;">
                      <v-icon size="11" color="grey-lighten-1" class="me-1">mdi-account</v-icon>
                      {{ order.customer || 'Walk-in' }}
                    </div>
                    <div class="text-grey-darken-1 font-mono" style="font-size: 9px;">
                      {{ order.name.slice(-7) }}
                    </div>
                  </div>
                </div>

                <!-- Card Content - Items Table Checklist -->
                <v-card-text class="pa-2 flex-grow-1 overflow-y-auto item-list-scroll">
                  <table class="kds-table w-100">
                    <thead>
                      <tr>
                        <th class="text-start text-grey-lighten-1 pb-1 font-weight-bold" style="font-size: 10px;">{{ __('Item') }}</th>
                        <th class="text-center text-grey-lighten-1 pb-1 font-weight-bold" style="width: 50px; font-size: 10px;">{{ __('Qty') }}</th>
                        <th class="text-center text-grey-lighten-1 pb-1 font-weight-bold" style="width: 40px; font-size: 10px;">{{ __('Done') }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <template v-for="item in order.items" :key="item.name">
                        <!-- Base Item Row -->
                        <tr :class="{ 'item-checked-row': checkedItems[item.name] }">
                          <td class="text-start py-0.5 border-bottom-glass" style="font-size: 11px; line-height: 1.15;">
                            <div class="font-weight-bold text-white">
                              {{ item.item_name }}
                            </div>
                            <!-- Unlinked Addons (e.g. + Cheese, Garlic) -->
                            <div v-if="item.hspos_addons_desc" class="addons-subtitle font-weight-bold text-amber-accent-2 mt-0.5" style="font-size: 10px; line-height: 1.15;">
                              {{ item.hspos_addons_desc }}
                            </div>
                            <!-- Item Level Note if any -->
                            <div v-if="item.hspos_notes" class="item-note mt-0.5 py-0.5 px-1 rounded bg-amber-darken-4-glass" style="font-size: 9px; line-height: 1.15;">
                              {{ item.hspos_notes }}
                            </div>
                          </td>
                          <td class="text-center font-weight-black text-primary py-0.5 font-mono border-bottom-glass" style="font-size: 12px;">
                            {{ item.qty }}
                          </td>
                          <td class="text-center py-0.5 border-bottom-glass cursor-pointer" @click.stop="toggleItemCheck(item.name)">
                            <v-btn
                              icon
                              variant="text"
                              :color="checkedItems[item.name] ? 'success' : 'grey-lighten-1'"
                              size="small"
                              style="width: 26px; height: 26px; min-width: unset; margin: 0; padding: 0;"
                            >
                              <v-icon size="20">
                                {{ checkedItems[item.name] ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                              </v-icon>
                            </v-btn>
                          </td>
                        </tr>

                        <!-- Addons Row (if any) -->
                        <tr v-for="addon in item.addons" :key="addon.name" :class="{ 'item-checked-row': checkedItems[addon.name] }" class="addon-row-tr">
                          <td class="text-start py-0.5 ps-3 text-amber-accent-2" style="font-size: 10px; line-height: 1.1;">
                            <div>+ {{ addon.item_name }}</div>
                          </td>
                          <td class="text-center text-amber-accent-2 font-mono py-0.5" style="font-size: 10px;">
                            {{ addon.qty }}
                          </td>
                          <td class="text-center py-0.5 cursor-pointer" @click.stop="toggleItemCheck(addon.name)">
                            <v-btn
                              icon
                              variant="text"
                              :color="checkedItems[addon.name] ? 'amber' : 'grey-lighten-2'"
                              size="x-small"
                              style="width: 26px; height: 26px; min-width: unset; margin: 0; padding: 0;"
                            >
                              <v-icon size="18">
                                {{ checkedItems[addon.name] ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                              </v-icon>
                            </v-btn>
                          </td>
                        </tr>
                      </template>
                    </tbody>
                  </table>
                </v-card-text>

                <v-divider color="rgba(255, 255, 255, 0.08)"></v-divider>

                <!-- Card Actions -->
                <v-card-actions class="pa-2 gap-1 flex-grow-0">
                  <v-btn
                    icon
                    variant="tonal"
                    color="grey-lighten-2"
                    @click="printTicket(order)"
                    class="rounded-lg border-glass"
                    size="small"
                    :title="__('Print')"
                  >
                    <v-icon size="16">mdi-printer</v-icon>
                  </v-btn>

                  <v-btn
                    v-if="order.hspos_kitchen_status === 'Pending'"
                    variant="flat"
                    color="warning"
                    class="flex-grow-1 font-weight-bold rounded-lg text-caption"
                    prepend-icon="mdi-fire"
                    size="small"
                    @click="updateStatus(order.name, 'Preparing')"
                  >
                    {{ __('Prepare') }}
                  </v-btn>

                  <v-btn
                    v-else
                    variant="flat"
                    color="success"
                    class="flex-grow-1 font-weight-bold rounded-lg text-caption"
                    prepend-icon="mdi-check"
                    size="small"
                    @click="updateStatus(order.name, 'Completed')"
                  >
                    {{ __('Done') }}
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>

          <!-- Empty State -->
          <div v-else class="empty-kds d-flex flex-column align-center justify-center py-16 flex-grow-1 text-center h-100">
            <div class="empty-icon-container mb-4">
              <v-icon size="80" color="grey-darken-2">mdi-silverware-clean</v-icon>
            </div>
            <h3 class="text-h5 text-white font-weight-bold mb-1">{{ __('Kitchen is Clear') }}</h3>
            <p class="text-body-2 text-grey-darken-1">{{ __('All active orders have been completed!') }}</p>
          </div>
        </div>
      </v-container>
    </v-main>

    <!-- Settings Dialog -->
    <v-dialog v-model="settingsDialog" max-width="500px">
      <v-card class="border-glass bg-glass text-white rounded-xl">
        <v-card-title class="pa-4 bg-primary text-white d-flex align-center">
          <v-icon class="me-2">mdi-cog</v-icon>
          <span class="font-weight-bold">{{ __('KDS Settings') }}</span>
          <v-spacer></v-spacer>
          <v-btn icon variant="text" color="white" @click="settingsDialog = false" density="compact">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider color="rgba(255, 255, 255, 0.08)"></v-divider>
        <v-card-text class="pa-5">
          <v-form>
            <!-- POS Invoices Only -->
            <v-switch
              v-model="settings.posOnly"
              :label="__('Only Show POS Orders')"
              color="primary"
              density="comfortable"
              class="mb-3"
            ></v-switch>

            <!-- POS Profile selection -->
            <v-select
              v-model="settings.posProfile"
              :items="posProfiles"
              :label="__('Filter by POS Profile')"
              variant="outlined"
              color="primary"
              class="mb-3"
              density="comfortable"
            ></v-select>

            <!-- Max Order Age selection -->
            <v-select
              v-model="settings.maxAgeMins"
              :items="[
                { title: __('1 Hour'), value: 60 },
                { title: __('2 Hours'), value: 120 },
                { title: __('6 Hours'), value: 360 },
                { title: __('12 Hours'), value: 720 },
                { title: __('24 Hours'), value: 1440 },
                { title: __('All Active'), value: 'All' }
              ]"
              item-title="title"
              item-value="value"
              :label="__('Max Order Age')"
              variant="outlined"
              color="primary"
              class="mb-3"
              density="comfortable"
            ></v-select>

            <!-- Default view filter -->
            <v-select
              v-model="settings.defaultStatus"
              :items="[
                { title: __('All Active'), value: 'all' },
                { title: __('Pending Only'), value: 'Pending' },
                { title: __('Preparing Only'), value: 'Preparing' }
              ]"
              item-title="title"
              item-value="value"
              :label="__('Default Status on Load')"
              variant="outlined"
              color="primary"
              density="comfortable"
            ></v-select>
          </v-form>
        </v-card-text>
        <v-divider color="rgba(255, 255, 255, 0.08)"></v-divider>
        <v-card-actions class="pa-4 justify-end">
          <v-btn
            variant="text"
            color="grey-lighten-1"
            @click="settingsDialog = false"
            class="font-weight-bold"
          >
            {{ __('Cancel') }}
          </v-btn>
          <v-btn
            variant="flat"
            color="primary"
            @click="saveSettings"
            class="font-weight-bold px-6 rounded-lg"
          >
            {{ __('Save Settings') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script>
const translations = {
  ar: {
    'Kitchen Display System': 'شاشة المطبخ',
    'Live KDS Control': 'التحكم المباشر بالمطبخ',
    'Done Today': 'تم اليوم',
    'Preparing': 'تحت التجهيز',
    'Pending': 'قيد الانتظار',
    'All Active': 'الكل نشط',
    'Item': 'الصنف',
    'Qty': 'الكمية',
    'Done': 'تم',
    'Prepare': 'تجهيز',
    'Complete': 'إنهاء',
    'Print': 'طباعة',
    'Settings': 'الإعدادات',
    'Auto-refreshing in': 'تحديث تلقائي خلال ',
    's...': ' ثوانٍ...',
    'Kitchen is Clear': 'المطبخ خالٍ من الطلبات',
    'All active orders have been completed!': 'تم الانتهاء من جميع الطلبات النشطة!',
    'Refresh': 'تحديث',
    'Desk': 'الرئيسية',
    'Close': 'إغلاق',
    'Save Settings': 'حفظ الإعدادات',
    'Cancel': 'إلغاء',
    'Only Show POS Orders': 'تصفية طلبات نقاط البيع فقط',
    'Filter by POS Profile': 'تصفية حسب ملف نقطة البيع',
    '1 Hour': 'ساعة واحدة',
    '2 Hours': 'ساعتين',
    '6 Hours': '6 ساعات',
    '12 Hours': '12 ساعة',
    '24 Hours': '24 ساعة',
    'Max Order Age': 'أقصى عمر للطلب',
    'Default Status on Load': 'الحالة الافتراضية عند الفتح',
    'Pending Only': 'قيد الانتظار فقط',
    'Preparing Only': 'تحت التجهيز فقط',
    'POS Profile': 'ملف نقطة البيع',
    'Dine-in': 'محلي',
    'Takeaway': 'سفري',
    'Delivery': 'توصيل',
    'KITCHEN TICKET': 'تذكرة المطبخ',
    'Date': 'التاريخ',
    'Customer': 'العميل',
    'Invoice': 'الفاتورة',
    'Note': 'ملاحظة',
    'Sound Alerts': 'التنبيهات الصوتية',
    'Sound enabled': 'تفعيل الصوت',
    'Walk-in': 'عميل سفري',
    'Toggle Chime Alert': 'تفعيل/كتم صوت التنبيه',
    'Test Sound Chime': 'تجربة رنين التنبيه',
    'Toggle Fullscreen': 'كامل الشاشة',
    'KDS Settings': 'إعدادات المطبخ'
  },
  en: {
    'Kitchen Display System': 'Kitchen Display System',
    'Live KDS Control': 'Live KDS Control',
    'Done Today': 'Done Today',
    'Preparing': 'Preparing',
    'Pending': 'Pending',
    'All Active': 'All Active',
    'Item': 'Item',
    'Qty': 'Qty',
    'Done': 'Done',
    'Prepare': 'Prepare',
    'Complete': 'Complete',
    'Print': 'Print',
    'Settings': 'Settings',
    'Auto-refreshing in': 'Auto-refreshing in ',
    's...': 's...',
    'Kitchen is Clear': 'Kitchen is Clear',
    'All active orders have been completed!': 'All active orders have been completed!',
    'Refresh': 'Refresh',
    'Desk': 'Desk',
    'Close': 'Close',
    'Save Settings': 'Save Settings',
    'Cancel': 'Cancel',
    'Only Show POS Orders': 'Only Show POS Orders',
    'Filter by POS Profile': 'Filter by POS Profile',
    '1 Hour': '1 Hour',
    '2 Hours': '2 Hours',
    '6 Hours': '6 Hours',
    '12 Hours': '12 Hours',
    '24 Hours': '24 Hours',
    'Max Order Age': 'Max Order Age',
    'Default Status on Load': 'Default Status on Load',
    'Pending Only': 'Pending Only',
    'Preparing Only': 'Preparing Only',
    'POS Profile': 'POS Profile',
    'Dine-in': 'Dine-in',
    'Takeaway': 'Takeaway',
    'Delivery': 'Delivery',
    'KITCHEN TICKET': 'KITCHEN TICKET',
    'Date': 'Date',
    'Customer': 'Customer',
    'Invoice': 'Invoice',
    'Note': 'Note',
    'Sound Alerts': 'Sound Alerts',
    'Sound enabled': 'Sound enabled',
    'Walk-in': 'Walk-in',
    'Toggle Chime Alert': 'Toggle Chime Alert',
    'Test Sound Chime': 'Test Sound Chime',
    'Toggle Fullscreen': 'Toggle Fullscreen',
    'KDS Settings': 'KDS Settings'
  }
};

export default {
  name: 'KDS',
  data() {
    return {
      currentLang: localStorage.getItem('kds_lang') || (frappe.boot.lang === 'ar' || frappe.boot.lang === 'en' ? frappe.boot.lang : 'ar'),
      settingsDialog: false,
      posProfiles: ['All'],
      settings: {
        posProfile: 'All',
        maxAgeMins: 60,
        posOnly: true,
        defaultStatus: 'Pending'
      },
      orders: [],
      loading: false,
      statusFilter: 'Pending',
      currentTime: new Date(),
      countdown: 10,
      soundEnabled: true,
      isFullscreen: false,
      checkedItems: {},
      completedTodayCount: 0,
      liveTimerInterval: null,
      countdownInterval: null,
    };
  },

  computed: {
    liveTime() {
      return this.currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    },

    filteredOrders() {
      if (this.statusFilter === 'all') {
        return this.orders;
      }
      return this.orders.filter(o => o.hspos_kitchen_status === this.statusFilter);
    },

    pendingCount() {
      return this.orders.filter(o => o.hspos_kitchen_status === 'Pending').length;
    },

    preparingCount() {
      return this.orders.filter(o => o.hspos_kitchen_status === 'Preparing').length;
    }
  },

  mounted() {
    // Load local storage settings
    const storedSettings = localStorage.getItem('kds_settings');
    if (storedSettings) {
      try {
        this.settings = JSON.parse(storedSettings);
        if (this.settings.defaultStatus) {
          this.statusFilter = this.settings.defaultStatus;
        }
      } catch (e) {
        console.error("Failed to parse KDS settings", e);
      }
    }

    this.detectFullscreen();
    this.fetchOrders();
    this.loadCompletedTodayCount();
    this.fetchPosProfiles();
    this.remove_frappe_nav();

    // Start Live Clock and Elapsed Timers
    this.liveTimerInterval = setInterval(() => {
      this.currentTime = new Date();
      this.$forceUpdate(); // Force update to refresh elapsed timers on card headers
    }, 1000);

    // Start Auto-Refresh Countdown
    this.countdownInterval = setInterval(() => {
      if (this.countdown <= 1) {
        this.countdown = 10;
        this.fetchOrders(false);
      } else {
        this.countdown--;
      }
    }, 1000);

    document.addEventListener('fullscreenchange', this.detectFullscreen);

    // Periodic check to ensure standard elements remain hidden (handles dynamic route changes)
    this.navInterval = setInterval(() => {
      this.remove_frappe_nav();
    }, 1000);
  },

  unmounted() {
    if (this.liveTimerInterval) clearInterval(this.liveTimerInterval);
    if (this.countdownInterval) clearInterval(this.countdownInterval);
    if (this.navInterval) clearInterval(this.navInterval);
    document.removeEventListener('fullscreenchange', this.detectFullscreen);
    this.restore_frappe_nav();
  },

  methods: {
    __(text) {
      if (translations[this.currentLang] && translations[this.currentLang][text]) {
        return translations[this.currentLang][text];
      }
      return window.__ ? window.__(text) : text;
    },

    toggleLanguage() {
      this.currentLang = this.currentLang === 'ar' ? 'en' : 'ar';
      localStorage.setItem('kds_lang', this.currentLang);
    },

    toggleItemCheck(name) {
      this.checkedItems[name] = !this.checkedItems[name];
    },

    formatOrderType(type) {
      if (!type) return '';
      const t = type.toLowerCase();
      if (this.currentLang === 'ar') {
        if (t === 'dine-in' || t === 'dine in' || t === 'محلي') return 'محلي';
        if (t === 'takeaway' || t === 'take out' || t === 'سفري') return 'سفري';
        if (t === 'delivery' || t === 'توصيل') return 'توصيل';
      } else {
        if (t === 'dine-in' || t === 'dine in' || t === 'محلي') return 'Dine-in';
        if (t === 'takeaway' || t === 'take out' || t === 'سفري') return 'Takeaway';
        if (t === 'delivery' || t === 'توصيل') return 'Delivery';
      }
      return type;
    },

    getOrderTypeClass(type) {
      if (!type) return '';
      const t = type.toLowerCase();
      if (t === 'dine-in' || t === 'dine in' || t === 'محلي') return 'badge-dine-in';
      if (t === 'takeaway' || t === 'take out' || t === 'سفري') return 'badge-takeaway';
      if (t === 'delivery' || t === 'توصيل') return 'badge-delivery';
      return 'bg-grey-darken-4 text-grey-lighten-2 border-glass';
    },

    remove_frappe_nav() {
      this.$nextTick(() => {
        $('.page-head').hide();
        $('.navbar.navbar-default.navbar-fixed-top').hide();
        $('.navbar').hide();
        $('.title-bar').hide();
        $('.layout-side-section').hide();
        $('.app-body').css('padding-top', '0');
        
        // Hide browser scrollbars on body/html/main container
        $('html, body, .app-body, #body').css('overflow', 'hidden');
        
        // Dynamic fullscreen overrides for container selectors
        $('.page-container').css({
          'padding': '0',
          'margin': '0',
          'max-width': '100%',
          'width': '100%',
          'overflow': 'hidden'
        });
        $('.page-content').css({
          'padding': '0',
          'margin': '0',
          'max-width': '100%',
          'width': '100%',
          'overflow': 'hidden'
        });
        $('.layout-main-section').css({
          'padding': '0',
          'margin': '0',
          'max-width': '100%',
          'width': '100%',
          'overflow': 'hidden'
        });
        $('.layout-main').css({
          'padding': '0',
          'margin': '0',
          'max-width': '100%',
          'width': '100%',
          'overflow': 'hidden'
        });
        $('.container').css({
          'padding': '0',
          'margin': '0',
          'max-width': '100%',
          'width': '100%',
          'overflow': 'hidden'
        });
      });
    },

    restore_frappe_nav() {
      $('.page-head').show();
      $('.navbar.navbar-default.navbar-fixed-top').show();
      $('.navbar').show();
      $('.title-bar').show();
      $('.layout-side-section').show();
      $('.app-body').css('padding-top', '');
      
      // Restore scrollbars
      $('html, body, .app-body, #body').css('overflow', '');
      
      // Restore styles
      $('.page-container').css({'padding': '', 'margin': '', 'max-width': '', 'width': '', 'overflow': ''});
      $('.page-content').css({'padding': '', 'margin': '', 'max-width': '', 'width': '', 'overflow': ''});
      $('.layout-main-section').css({'padding': '', 'margin': '', 'max-width': '', 'width': '', 'overflow': ''});
      $('.layout-main').css({'padding': '', 'margin': '', 'max-width': '', 'width': '', 'overflow': ''});
      $('.container').css({'padding': '', 'margin': '', 'max-width': '', 'width': '', 'overflow': ''});
    },

    fetchPosProfiles() {
      frappe.call({
        method: 'frappe.client.get_list',
        args: {
          doctype: 'POS Profile',
          fields: ['name']
        },
        callback: (r) => {
          if (r.message) {
            this.posProfiles = ['All', ...r.message.map(p => p.name)];
          }
        }
      });
    },

    saveSettings() {
      localStorage.setItem('kds_settings', JSON.stringify(this.settings));
      this.settingsDialog = false;
      this.fetchOrders(true);
    },

    goDesk() {
      frappe.set_route('/');
      location.reload();
    },

    fetchOrders(manual = false) {
      if (manual) {
        this.loading = true;
        this.countdown = 10;
      }

      frappe.call({
        method: 'highspeed_pos.highspeed_pos.api.hsposapp.get_kitchen_orders',
        args: {
          pos_profile: this.settings.posProfile,
          max_age_mins: this.settings.maxAgeMins,
          pos_only: this.settings.posOnly
        },
        callback: (r) => {
          this.loading = false;
          if (r.message) {
            const oldOrderIds = new Set(this.orders.map(o => o.name));
            let hasNewOrder = false;

            r.message.forEach(order => {
              if (!oldOrderIds.has(order.name) && order.hspos_kitchen_status === 'Pending') {
                hasNewOrder = true;
              }
            });

            this.orders = r.message;

            if (hasNewOrder && this.soundEnabled) {
              this.playChime();
            }
          }
        },
        error: () => {
          this.loading = false;
        }
      });
    },

    updateStatus(invoiceName, status) {
      frappe.call({
        method: 'highspeed_pos.highspeed_pos.api.hsposapp.update_kitchen_status',
        args: {
          invoice_name: invoiceName,
          status: status
        },
        callback: (r) => {
          if (r.message && r.message.status === 'success') {
            if (status === 'Completed') {
              this.completedTodayCount++;
              // Fade out animations or remove immediately from client list
              this.orders = this.orders.filter(o => o.name !== invoiceName);
              // Store completed today count in local storage to keep state across refreshes
              localStorage.setItem('kds_completed_today', this.completedTodayCount);
            } else {
              // Set status local
              const ord = this.orders.find(o => o.name === invoiceName);
              if (ord) ord.hspos_kitchen_status = status;
            }
          }
        }
      });
    },

    loadCompletedTodayCount() {
      const stored = localStorage.getItem('kds_completed_today');
      if (stored) {
        this.completedTodayCount = parseInt(stored);
      }
    },

    getElapsedTime(creationStr) {
      if (!creationStr) return '00:00';
      const created = new Date(creationStr.replace(' ', 'T'));
      const diffMs = this.currentTime - created;
      if (diffMs < 0) return '00:00';

      const diffSecs = Math.floor(diffMs / 1000);
      const mins = Math.floor(diffSecs / 60);
      const secs = diffSecs % 60;

      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    },

    isOrderOverdue(creationStr) {
      if (!creationStr) return false;
      const created = new Date(creationStr.replace(' ', 'T'));
      const diffMs = this.currentTime - created;
      // Overdue after 15 minutes (900,000 milliseconds)
      return diffMs > 900000;
    },

    playChime() {
      try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const playTone = (freq, type, duration, startTime) => {
          const osc = audioCtx.createOscillator();
          const gain = audioCtx.createGain();
          osc.type = type;
          osc.frequency.setValueAtTime(freq, startTime);
          
          gain.gain.setValueAtTime(0.3, startTime);
          gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);
          
          osc.connect(gain);
          gain.connect(audioCtx.destination);
          osc.start(startTime);
          osc.stop(startTime + duration);
        };
        
        const now = audioCtx.currentTime;
        // Two rising bell-like clear tones (pleasant chime)
        playTone(523.25, 'sine', 0.2, now); // C5
        playTone(659.25, 'sine', 0.3, now + 0.15); // E5
      } catch (e) {
        console.error("Failed to play notification chime:", e);
      }
    },

    testSound() {
      this.playChime();
    },

    toggleSound() {
      this.soundEnabled = !this.soundEnabled;
    },

    toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().then(() => {
          this.isFullscreen = true;
        }).catch(err => {
          console.warn(`Error attempting to enable full-screen: ${err.message}`);
        });
      } else {
        document.exitFullscreen().then(() => {
          this.isFullscreen = false;
        });
      }
    },

    detectFullscreen() {
      this.isFullscreen = !!document.fullscreenElement;
    },

    printTicket(order) {
      const itemsHtml = order.items.map(item => {
        let addonsStr = '';
        if (item.addons && item.addons.length) {
          addonsStr = item.addons.map(addon => `
            <div class="addon-row">+ ${addon.item_name} (x${addon.qty})</div>
          `).join('');
        } else if (item.hspos_addons_desc) {
          addonsStr = `
            <div class="addon-row">${item.hspos_addons_desc}</div>
          `;
        }
        
        let noteStr = '';
        if (item.hspos_notes) {
          noteStr = `<div class="notes">${this.__('Note')}: ${item.hspos_notes}</div>`;
        }

        return `
          <div class="item-block">
            <div class="item-row">
              <span class="item-name">${item.item_name}</span>
              <span class="item-qty">x${item.qty}</span>
            </div>
            ${addonsStr}
            ${noteStr}
          </div>
        `;
      }).join('');

      const printHtml = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body { font-family: 'Courier New', monospace; font-size: 14px; margin: 10px; color: #000; }
            .header { text-align: center; border-bottom: 2px dashed #000; padding-bottom: 8px; margin-bottom: 8px; }
            .order-no { font-size: 28px; font-weight: bold; margin: 6px 0; }
            .meta { font-size: 12px; margin-bottom: 8px; line-height: 1.4; }
            .item-block { border-bottom: 1px dashed #ccc; padding: 6px 0; }
            .item-row { display: flex; justify-content: space-between; font-size: 16px; font-weight: bold; }
            .addon-row { margin-left: 20px; font-size: 13px; font-style: italic; }
            .notes { border: 1px solid #000; padding: 4px; font-size: 12px; margin-top: 4px; font-weight: bold; background: #eee; }
            .footer { text-align: center; border-top: 2px dashed #000; padding-top: 8px; margin-top: 15px; font-size: 11px; }
            .print-order-type { font-size: 20px; font-weight: bold; margin: 5px 0; border: 2px solid #000; padding: 4px; display: inline-block; text-transform: uppercase; }
          </style>
        </head>
        <body>
          <div class="header">
            <div>*** ${this.__('KITCHEN TICKET')} ***</div>
            <div class="order-no">#${order.hspos_order_no || order.name.slice(-5)}</div>
            ${order.hspos_order_type ? `<div class="print-order-type">${this.formatOrderType(order.hspos_order_type)}${order.hspos_table ? ` (${order.hspos_table})` : ''}${order.docstatus === 0 ? ' (مسودة)' : ''}</div>` : ''}
            <div class="meta">
              <b>${this.__('Invoice')}:</b> ${order.name}<br>
              <b>${this.__('Date')}:</b> ${order.posting_date} ${order.posting_time || ''}<br>
              <b>${this.__('Customer')}:</b> ${order.customer || 'Walk-in'}
            </div>
          </div>
          <div>
            ${itemsHtml}
          </div>
          <div class="footer">
            Printed at: ${new Date().toLocaleTimeString()}
          </div>
        </body>
        </html>
      `;

      const oldFrame = document.getElementById('kds-print-iframe');
      if (oldFrame) {
        oldFrame.remove();
      }

      const printFrame = document.createElement('iframe');
      printFrame.id = 'kds-print-iframe';
      printFrame.style.position = 'absolute';
      printFrame.style.width = '0';
      printFrame.style.height = '0';
      printFrame.style.border = '0';
      printFrame.style.left = '-9999px';
      
      document.body.appendChild(printFrame);

      const frameDoc = printFrame.contentWindow.document;
      frameDoc.open();
      frameDoc.write(printHtml);
      frameDoc.close();

      setTimeout(() => {
        printFrame.contentWindow.focus();
        printFrame.contentWindow.print();
        setTimeout(() => {
          if (printFrame && printFrame.parentNode) {
            document.body.removeChild(printFrame);
          }
        }, 1000);
      }, 500);
    }
  }
};
</script>

<style scoped>
/* Responsive display helpers */
@media (max-width: 1279px) {
  .kds-desktop-only {
    display: none !important;
  }
}
@media (min-width: 1280px) {
  .kds-mobile-only {
    display: none !important;
  }
}
@media (max-width: 1599px) {
  .kds-label-desktop {
    display: none !important;
  }
}

/* Glassmorphism theme styling */
.kds-app-container {
  background-color: #080c14 !important;
  font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif !important;
  color: #f0f6fc;
}

.kds-navbar {
  background: rgba(13, 17, 23, 0.7) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
  z-index: 1000;
}

.brand-glow {
  box-shadow: 0 0 15px rgba(88, 166, 255, 0.3);
  border: 1px solid rgba(88, 166, 255, 0.4);
}

.kds-title {
  font-size: 18px;
  letter-spacing: 2px;
}

.bg-glass {
  background: rgba(22, 27, 34, 0.5) !important;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.bg-glass-dark {
  background: rgba(13, 17, 23, 0.4) !important;
}

.border-glass {
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.kds-main-bg {
  background-color: #080c14 !important;
}

.gap-2 {
  gap: 8px;
}

/* KDS Table design */
.kds-table {
  border-collapse: collapse;
  margin-top: 5px;
}

.kds-table th {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 6px;
}

.border-bottom-glass {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.item-checked-row td {
  opacity: 0.35;
}

.item-checked-row .text-white {
  text-decoration: line-through;
  color: #8b949e !important;
}

.addon-row-tr td {
  border-bottom: none;
  background: rgba(255, 255, 255, 0.01);
}

.kds-grid-container {
  max-height: calc(100vh - 140px);
}

/* Glassmorphic Order Cards */
.kds-order-card {
  border-radius: 8px !important;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  overflow: hidden;
  min-height: 160px;
  height: auto;
}

.kds-order-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5) !important;
  border-color: rgba(255, 255, 255, 0.15) !important;
}

.border-pending {
  border-inline-start: 6px solid #ff5252 !important;
}

.border-preparing {
  border-inline-start: 6px solid #fb8c00 !important;
}

/* High urgency overdue orders blink and shake slightly */
.card-alert {
  border-color: rgba(255, 82, 82, 0.5) !important;
  box-shadow: 0 0 20px rgba(255, 82, 82, 0.2) !important;
}

.bg-red-glow {
  background: #ff5252 !important;
  box-shadow: 0 0 8px #ff5252;
}

.animate-pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}

.item-list-scroll {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
}

.item-list-scroll::-webkit-scrollbar {
  width: 4px;
}

.item-list-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.item-list-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

/* Item lines and checklist states */
.item-name-line {
  transition: all 0.2s ease;
  line-height: 1.3;
}

.item-checked {
  text-decoration: line-through;
  opacity: 0.4;
  color: #8b949e !important;
}

.addons-container {
  border-left: 1px dashed rgba(255, 255, 255, 0.15);
}

.addon-line {
  display: flex;
  align-items: center;
  line-height: 1.2;
}

.item-note {
  border-left: 3px solid #ffb74d;
}

.bg-amber-darken-4-glass {
  background: rgba(255, 143, 0, 0.1) !important;
  border: 1px solid rgba(255, 143, 0, 0.15) !important;
}

/* Action button micro-animations */
.v-btn {
  text-transform: none !important;
  letter-spacing: 0.5px !important;
  transition: all 0.2s ease-in-out;
}

.v-btn:active {
  transform: scale(0.96);
}

/* Empty State visual */
.empty-kds {
  min-height: 400px;
}

.empty-icon-container {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.6);
}

.badge-dine-in {
  background: rgba(30, 144, 255, 0.25) !important;
  color: #3090ff !important;
  border: 2px solid #3090ff !important;
  font-size: 11px !important;
  padding: 1px 6px !important;
  border-radius: 4px !important;
  display: inline-block !important;
  line-height: 1.2 !important;
}

.badge-takeaway {
  background: rgba(0, 200, 83, 0.25) !important;
  color: #00c853 !important;
  border: 2px solid #00c853 !important;
  font-size: 11px !important;
  padding: 1px 6px !important;
  border-radius: 4px !important;
  display: inline-block !important;
  line-height: 1.2 !important;
}

.badge-delivery {
  background: rgba(255, 61, 0, 0.25) !important;
  color: #ff3d00 !important;
  border: 2px solid #ff3d00 !important;
  font-size: 11px !important;
  padding: 1px 6px !important;
  border-radius: 4px !important;
  display: inline-block !important;
  line-height: 1.2 !important;
}

.gap-1-5 {
  gap: 6px;
}

.kds-card-header-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  width: 100%;
  gap: 4px;
}
</style>
