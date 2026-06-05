<div align="center">
    <h2>HIGHSPEED POS</h2>
</div>

#### A Point of Sale and Kitchen Display System (KDS) for [Erpnext](https://github.com/frappe/erpnext) using [Vue.js](https://github.com/vuejs/vue) and [Vuetify](https://github.com/vuetifyjs/vuetify) (VERSION 15 Support)

---
### Update Instructions

After switching branches or pulling latest changes:

1. cd apps/highspeed_pos
2. git pull
3. yarn install
4. cd ../..
5. bench build --app highspeed_pos
6. bench --site your.site migrate

### Main Features

1. Supports Erpnext Version 15
2. Supports Multi-Currency Transactions.
    Customers can be invoiced in different currencies
    Exchange Rate is fetched automatically based on selected currency
    Invoices made with highspeed_pos display Grand Total in both base and selected currency in erpnext.
    
3. User-friendly and provides a good user experience and speed of use
4. The cashier can either use list view or card view during sales transactions. Card view shows the images of the items
5. Supports enqueue invoice submission after printing the receipt for faster processing
6. Supports batch & serial numbering
7. Supports batch-based pricing
8. Supports UOM-specific barcode and pricing
9. Supports sales of scale (weighted) products
10. Ability to make returns from POS
11. Supports Making returns for either cash or customer credit
12. Supports using customer credit notes for payment
13. Supports credit sales
14. Allows the user to choose a due date for credit sales
15. Supports customer loyalty points
16. Shortcut keys
17. Supports Customer Discount
18. Supports HSPOS Offers
19. Auto-apply batches for bundle items
20. Search and add items by Serial Number
21. Create Sales Orders from POS directly
22. Supports template items with variants
23. Supports multiple languages
24. Supports Mpesa mobile payment
25. HSPOS Coupons
26. Supports HSPOS Referral Code
27. Supports Customer and Customer Group price list
28. Supports Sales Person
29. Supports HSPOS Delivery Charges
30. Search and add items by Batch Number
31. Accept new payments from customers against existing invoices
32. Payments Reconciliation
33. A lot more bug fixes from the version 14
34. Offline invoices that fail to submit are saved as draft documents
35. **Standalone Kitchen Display System (KDS)**: Real-time, dark-themed screen for kitchen staff to track and prepare orders.
36. **Dynamic & Compact KDS Cards**: Layout adjusts height automatically based on the number of products to show all items without browser scrollbars.
37. **Touchscreen-Friendly Toggles**: Circular tap buttons on checklist rows with large tap target cells tailored for tablet devices.
38. **Instant Language & Direction Switcher**: Quick toggle button between Arabic and English that automatically adjusts text layout direction (RTL / LTR).
39. **Distinct Order Types & Numbers**: Prominent order numbers and color-coded badges for Dine-in (محلي), Takeaway (سفري), and Delivery (توصيل).
40. **Linked & Unlinked Addons Support**: Renders child additions and textual modifiers clearly below the parent items.
41. **Web Audio Chime Alerts**: Synthetic dual-tone audio notifications on new order entries to alert kitchen staff.
42. **Direct KOT Thermal Printing**: Silent, popup-safe kitchen ticket printing using a hidden iframe.

---

### 🍳 Standalone Kitchen Display System (KDS) & Restaurant Enhancements
### 🍳 شاشة عرض المطبخ وإضافات المطاعم الجديدة

We have integrated a comprehensive, real-time Kitchen Display System (KDS) tailored for touchscreen restaurant environments:
لقد قمنا بدمج شاشة عرض مطبخ (KDS) متكاملة وتفاعلية مخصصة للعمل على الأجهزة اللوحية وشاشات اللمس في المطاعم:

*   **Standalone KDS Dashboard | شاشة المطبخ المستقلة**: A beautiful, dark-themed dashboard `/app/hspos_kitchen` for kitchen staff to track order preparation in real-time.
    *   شاشة مستقلة بالكامل وجذابة باللون الداكن `/app/hspos_kitchen` تتيح لطاقم المطبخ متابعة وتحديث الطلبات لحظة بلحظة.
*   **Distinct Order Types & Prominent Numbers | نوع الطلب وأرقام مميزة**: Display of large order numbers alongside color-coded high-contrast badges for Dine-in (محلي - blue), Takeaway (سفري - green), and Delivery (توصيل - orange).
    *   عرض أرقام طلبات بارزة مع شارات ملونة ذات تباين عالٍ لتمييز نوع الطلب: محلي (أزرق)، سفري (أخضر)، وتوصيل (برتقالي).
*   **Linked & Unlinked Addons Support | دعم إضافات المنتجات**: Full rendering of unlinked/custom textual additions (in amber-orange under item names) and linked checklist addons to ensure preparation accuracy.
    *   دعم عرض الإضافات النصية المخصصة (باللون البرتقالي تحت المنتج) والإضافات المرتبطة لضمان دقة التحضير.
*   **Touchscreen-Friendly Toggles | تحسينات شاشات اللمس**: Replaced small checkboxes with large, responsive circular tap buttons. Tapping anywhere on the product row's table cell triggers the check/uncheck status.
    *   استبدال خانات الاختيار الصغيرة بأزرار دائرية تفاعلية كبيرة وسهلة النقر بمجرد لمس أي جزء من خلية جدول المنتج.
*   **Arabic/English Instant Toggle & RTL/LTR Layout | تبديل فوري للغة والاتجاه**: An integrated language switch in the header that instantly updates KDS text and dynamically flips the layout direction (RTL / LTR).
    *   تبديل فوري ومباشر في ترويسة الصفحة للغة والاتجاه (من اليمين لليسار للعربية ومن اليسار لليمين للإنجليزية).
*   **No-Scroll Dynamic Card Heights | بطاقات ذكية مرنة الارتفاع**: Order cards expand dynamically based on product counts, avoiding browser scrollbars and providing a clean, single-viewport display.
    *   تمدد بطاقات الطلبات تلقائياً لتناسب عدد المنتجات دون ظهور أشرطة تمرير المتصفح لتوفير عرض مريح.
*   **Audio Chime Notifications | تنبيهات صوتية للطلبات الجديدة**: Automatic synthetic dual-tone chime sound alerts kitchen staff when a new order enters the queue.
    *   تنبيه صوتي تفاعلي تلقائي لإعلام الطهاة فور دخول طلب جديد إلى قائمة التحضير.
*   **Direct Kitchen Order Ticket (KOT) Printing | طباعة بونات التحضير المباشرة**: Silent, direct thermal printing utilizing a hidden iframe to prevent popup-blocker issues on remote servers.
    *   طباعة صامتة ومباشرة على الطابعات الحرارية عبر نافذة خفية دون مشاكل حظر النوافذ المنبثقة.


### How to Install

#### Self Hosting:

1. `bench get-app https://github.com/fuhaed/highspeed_pos.git`
2. `bench setup requirements`
3. `bench build --app highspeed_pos`
4. `bench restart`
5. `bench --site [your.site.name] install-app highspeed_pos`
6. `bench --site [your.site.name] migrate`

---

### How To Use:

[HIGHSPEED POS Wiki](https://github.com/fuhaed/highspeed_pos/wiki)

---

### Shortcuts:

- `CTRL or CMD + S` open payments
- `CTRL or CMD + X` submit payments
- `CTRL or CMD + D` remove the first item from the top
- `CTRL or CMD + A` expand the first item from the top
- `CTRL or CMD + E` focus on discount field

---

### Dependencies:

- [Frappe](https://github.com/frappe/frappe)
- [Erpnext](https://github.com/frappe/erpnext)
- [Vue.js](https://github.com/vuejs/vue)
- [Vuetify.js](https://github.com/vuetifyjs/vuetify)

---

### Contributing

1. [Issue Guidelines](https://github.com/frappe/erpnext/wiki/Issue-Guidelines)
2. [Pull Request Requirements](https://github.com/frappe/erpnext/wiki/Contribution-Guidelines)

---

### License

GNU/General Public License (see [license.txt](https://github.com/fuhaed/highspeed_pos/blob/main/license.txt))

The HIGHSPEED POS code is licensed as GNU General Public License (v3)
